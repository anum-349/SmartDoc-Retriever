# 🧠 SmartDoc Retriever

SmartDoc Retriever is an intelligent **Retrieval-Augmented Generation (RAG)** system that allows users to **search, index, and query knowledge from multiple documents** using state-of-the-art language models.  
It automatically reads PDFs, Word files, PowerPoints, CSVs, and text files, converts them into embeddings using **Hugging Face sentence transformers**, stores them in a **FAISS vector database**, and uses **Google Gemini (Generative AI)** for intelligent Q&A responses.

---

## 🚀 Features

✅ Supports multiple file formats: `.pdf`, `.docx`, `.pptx`, `.csv`, `.txt`  
✅ Automatically builds and updates a FAISS vector index  
✅ Detects modified or deleted files and reindexes efficiently  
✅ Uses **HuggingFace Embeddings** (`all-MiniLM-L6-v2`) for fast semantic search  
✅ Integrates **Google Gemini** for accurate and natural-language answers  
✅ Modular, extensible, and easy to adapt for other GenAI or LLM backends  

---

## 🗂️ Project Structure

```

SmartDoc-Retriever/
│
├── Software-engineering/        # Folder containing all source documents to index
│
├── RAGChatBot.py                # Main RAG chatbot implementation (console-based)
│
├── requirements.txt             # All Python dependencies
└── README.md                    # Project documentation (this file)

````

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/anum-349/SmartDoc-Retriever.git
cd SmartDoc-Retriever
````

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up your Google API key

Create a `.env` file in the project root (or set environment variable manually):

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

---

## 🧩 How It Works

1. **File Loading:**
   SmartDoc Retriever scans your document folder (default: `Software-engineering/`) and loads all supported files.

2. **Chunking:**
   Documents are split into overlapping text chunks using `RecursiveCharacterTextSplitter`.

3. **Embedding:**
   Each chunk is converted into a vector using `sentence-transformers/all-MiniLM-L6-v2`.

4. **Indexing:**
   Embeddings are stored in a **FAISS** index, allowing fast similarity search.

5. **Retrieval + Generation (RAG):**
   When you ask a question, the top relevant chunks are retrieved and passed to **Google Gemini**, which generates a contextual answer.

---

## 💬 Run the Chatbot

Run the interactive chatbot in your terminal:

```bash
python RAGChatBot.py
```

Then type your questions:

```
Ask a question (or type 'exit' to quit): What is software engineering?
Thinking...
Chatbot: Software engineering is ...
```

---


---

## 🧱 Tech Stack

| Component           | Technology Used                           |
| ------------------- | ----------------------------------------- |
| **Language Model**  | Google Gemini (`gemini-2.5-flash`)        |
| **Embeddings**      | Hugging Face Sentence Transformers        |
| **Vector Store**    | FAISS                                     |
| **File Processing** | pdfplumber, python-pptx, docx2txt, pandas |
| **Frameworks**      | LangChain                                 |
| **Language**        | Python 3.9+                               |

---

## 📈 Example Use Cases

* Intelligent document Q&A system
* Knowledge management and semantic search
* Academic or research paper summarization
* Corporate document assistant (HR, legal, or policy data)
* Foundation for building a RAG-powered chatbot or assistant

---

## 🧑‍💻 Contributors

👩‍💻 **Anum**
📍 [GitHub Profile](https://github.com/anum-349)

---

## 🌟 Acknowledgments

* [LangChain](https://www.langchain.com/) for RAG pipelines
* [Hugging Face](https://huggingface.co/) for embedding models
* [Google Generative AI](https://ai.google.dev/) for the Gemini API
* [FAISS](https://faiss.ai/) for efficient similarity search

---

## 🪄 Future Improvements

* Add web-based chat interface using Streamlit or React
* Support for PDF table extraction and OCR text
* Multi-user session management
* Improved metadata versioning system
* Integration with open-weight LLMs (LLaMA, Mistral, etc.)

