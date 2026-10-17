import utils.session
import os
import sys
import json
import hashlib
from typing import Dict, List, Tuple, Optional

from dotenv import load_dotenv
import pdfplumber
from pptx import Presentation

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
load_dotenv()

FOLDER_PATH = "./Software-engineering"
INDEX_FOLDER = "faiss_index"
INDEX_METADATA_FILE = "faiss_metadata.json"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Set to None to use the default HuggingFace cache location.
HF_CACHE_FOLDER: Optional[str] = os.getenv("HF_CACHE_FOLDER")  # e.g. C:/Users/you/.cache/huggingface/hub
LLM_MODEL = "gemini-3.8-flash"
SUPPORTED_EXTENSIONS = (".pdf", ".txt", ".docx", ".csv", ".pptx")

Metadata = Dict[str, Dict]


# ----------------------------------------------------------------------------
# Hashing / persistence
# ----------------------------------------------------------------------------
def compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"❌ Error computing hash for {file_path}: {e}")
        return ""


def load_index_and_metadata(embedding_model) -> Tuple[Optional[FAISS], Metadata]:
    """Load index + metadata. If either is missing/corrupt, return a clean slate
    so the two never go out of sync (which would cause duplicate vectors)."""
    vector_store = None
    metadata: Metadata = {}

    if os.path.isdir(INDEX_FOLDER) and os.path.isfile(INDEX_METADATA_FILE):
        try:
            print(f"Loading existing FAISS index from {INDEX_FOLDER}...")
            # Safe here because we only load an index that this script wrote.
            vector_store = FAISS.load_local(
                INDEX_FOLDER, embedding_model, allow_dangerous_deserialization=True
            )
            with open(INDEX_METADATA_FILE, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"❌ Error loading index/metadata: {e}. Rebuilding from scratch.")
            vector_store, metadata = None, {}

    return vector_store, metadata


def save_index_and_metadata(vector_store: Optional[FAISS], metadata: Metadata) -> None:
    if vector_store is not None:
        print(f"Saving FAISS index to {INDEX_FOLDER}...")
        vector_store.save_local(INDEX_FOLDER)
    print(f"Saving metadata to {INDEX_METADATA_FILE}...")
    with open(INDEX_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


# ----------------------------------------------------------------------------
# Document loading
# ----------------------------------------------------------------------------
def load_pdf(file_path: str) -> List[Document]:
    documents = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()  # called once per page
            if text and text.strip():
                documents.append(
                    Document(page_content=text, metadata={"source": file_path, "page": i + 1})
                )
    return documents


def load_pptx(file_path: str) -> List[Document]:
    documents = []
    prs = Presentation(file_path)
    for slide_no, slide in enumerate(prs.slides, start=1):
        parts = []
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
                parts.append(shape.text_frame.text)
            if getattr(shape, "has_table", False) and shape.has_table:
                for row in shape.table.rows:
                    parts.append(" | ".join(cell.text for cell in row.cells))
        content = "\n".join(parts).strip()
        if content:
            documents.append(
                Document(page_content=content, metadata={"source": file_path, "slide": slide_no})
            )
    return documents


def load_single_document(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            return load_pdf(file_path)
        if ext == ".txt":
            return TextLoader(file_path, encoding="utf-8").load()
        if ext == ".docx":
            return Docx2txtLoader(file_path).load()
        if ext == ".csv":
            return CSVLoader(file_path).load()
        if ext == ".pptx":
            return load_pptx(file_path)
        print(f"⚠️ Unsupported file: {file_path}")
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
    return []


# ----------------------------------------------------------------------------
# Incremental indexing
# ----------------------------------------------------------------------------
def scan_folder(folder_path: str) -> Metadata:
    current: Metadata = {}
    for root, _, files in os.walk(folder_path):
        for name in files:
            if name.startswith((".", "~")) or not name.lower().endswith(SUPPORTED_EXTENSIONS):
                continue
            path = os.path.join(root, name)
            file_hash = compute_file_hash(path)
            if not file_hash:
                continue
            current[path] = {
                "hash": file_hash,
                "last_modified": os.path.getmtime(path),
                "vector_ids": [],
            }
    return current


def update_index_with_folder(folder_path: str, embedding_model, text_splitter) -> Optional[FAISS]:
    vector_store, metadata = load_index_and_metadata(embedding_model)
    current_files = scan_folder(folder_path)

    deleted = [p for p in metadata if p not in current_files]
    changed = [
        p for p, info in current_files.items()
        if p not in metadata or metadata[p]["hash"] != info["hash"]
    ]

    if not deleted and not changed and vector_store is not None:
        print("Index is up to date. No files modified or deleted.")
        return vector_store

    # 1) Remove vectors belonging to deleted or modified files.
    stale_ids: List[str] = []
    for path in deleted + [p for p in changed if p in metadata]:
        stale_ids.extend(metadata[path].get("vector_ids", []))
    if vector_store is not None and stale_ids:
        print(f"Removing {len(stale_ids)} stale chunks...")
        vector_store.delete(stale_ids)
    for path in deleted:
        metadata.pop(path, None)

    # 2) Chunk and embed new/modified files.
    new_docs: List[Document] = []
    new_ids: List[str] = []
    for path in changed:
        docs = load_single_document(path)
        chunks = text_splitter.split_documents(docs) if docs else []
        if not chunks:
            metadata.pop(path, None)  # nothing indexable; retry next run if it changes
            continue
        ids = [f"{current_files[path]['hash']}-{i}" for i in range(len(chunks))]
        new_docs.extend(chunks)
        new_ids.extend(ids)
        metadata[path] = {**current_files[path], "vector_ids": ids}

    if new_docs:
        if vector_store is None:
            print(f"Building new FAISS index with {len(new_docs)} chunks...")
            vector_store = FAISS.from_documents(new_docs, embedding_model, ids=new_ids)
        else:
            print(f"Adding {len(new_docs)} chunks to the index...")
            vector_store.add_documents(new_docs, ids=new_ids)
    elif vector_store is None:
        print("No documents loaded or chunks generated.")
        return None

    save_index_and_metadata(vector_store, metadata)
    return vector_store


# ----------------------------------------------------------------------------
# RAG chain
# ----------------------------------------------------------------------------
PROMPT = ChatPromptTemplate.from_template(
    "You are a helpful assistant. Answer the question using only the context below. "
    "If the answer is not in the context, say you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)


def build_answer_fn(vector_store: FAISS, llm):
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    chain = PROMPT | llm | StrOutputParser()

    def answer_query(query: str) -> str:
        try:
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant documents found."
            context = "\n\n".join(d.page_content for d in docs)
            answer = chain.invoke({"context": context, "question": query})
            sources = sorted({
                os.path.basename(d.metadata.get("source", "unknown")) for d in docs
            })
            return f"{answer}\n\nSources: {', '.join(sources)}"
        except Exception as e:
            return f"An error occurred during query: {e}"

    return answer_query


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------
def main() -> None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("❌ GOOGLE_API_KEY is not set. Add it to your .env file.")

    if not os.path.isdir(FOLDER_PATH):
        sys.exit(f"❌ The folder '{FOLDER_PATH}' does not exist.")
    if not os.listdir(FOLDER_PATH):
        sys.exit("❌ No files found in the folder.")

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=api_key)

    print("Initializing HuggingFace embeddings...")
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        cache_folder=HF_CACHE_FOLDER,
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    print("Loading/processing documents and updating index...")
    vector_store = update_index_with_folder(FOLDER_PATH, embedding_model, text_splitter)
    if vector_store is None:
        sys.exit("❌ Vector store could not be created or loaded.")

    answer_query = build_answer_fn(vector_store, llm)

    while True:
        user_query = input("Ask a question (or type 'exit' to quit): ").strip()
        if not user_query:
            continue
        if user_query.lower() == "exit":
            break
        print("Thinking...")
        print(f"\nChatbot: {answer_query(user_query)}\n")


if __name__ == "__main__":
    main()