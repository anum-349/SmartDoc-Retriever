# SmartDoc Retriever

SmartDoc Retriever is a command-line retrieval-augmented generation (RAG) application for asking questions about a local collection of documents. It extracts text from supported files, creates embeddings with a Hugging Face sentence-transformer, stores them in a local FAISS index, and sends relevant passages to Google Gemini to generate answers.

## Features

- Reads PDF, Word (`.docx`), PowerPoint (`.pptx`), CSV, and UTF-8 text (`.txt`) files.
- Searches document content by semantic similarity.
- Updates the local index when documents are added, changed, or removed.
- Includes the names of retrieved source files with answers.
- Runs as an interactive terminal application.

## Requirements

- Python 3.10 or later.
- A Google Gemini API key.
- Internet access for Gemini requests and the first-time download of the embedding model.

## Setup

Clone the repository and change into its directory:

```bash
git clone https://github.com/anum-349/SmartDoc-Retriever.git
cd SmartDoc-Retriever
```

Run the remaining commands from the project root.

### 1. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow it for the current terminal session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configure the API key

Copy `.env.example` to `.env` in the project root, then replace the placeholder with your Google Gemini API key. You can obtain a key from [Google AI Studio](https://aistudio.google.com/app/apikey).

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Keep `.env` private. It is excluded from version control; do not commit or share your API key.

## Add documents

Place files to index in the `Software-engineering/` folder. The application searches that folder and its subfolders. Supported formats are `.pdf`, `.docx`, `.pptx`, `.csv`, and `.txt`.

The PDF reader extracts embedded text only; scanned/image-only PDFs require OCR and will not be searchable as-is. Text files must use UTF-8 encoding.

## Run

From the project root, with your virtual environment active and `.env` configured:

```bash
python RAGChatBot.py
```

On the first run, the application downloads the embedding model if needed, processes documents, and creates a local FAISS index. Later runs reuse the index and update it for changed, added, or deleted files.

Retrieved document passages and your question are sent to Google Gemini to generate the answer. Do not index documents you are not permitted to share with that service.

Ask questions at the prompt. Type `exit` to quit:

```text
Ask a question (or type 'exit' to quit): What is software engineering?
Thinking...

Chatbot: ...

Sources: ...
```

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Yes | API key used to call Google Gemini. |
| `HF_CACHE_FOLDER` | No | Optional directory for the Hugging Face model cache. If unset, the Hugging Face default cache location is used. |

The embedding model, Gemini model, document folder, and chunking settings are currently defined in `RAGChatBot.py`.

## Generated files

The application creates `faiss_index/` and `faiss_metadata.json` in the project root. These are local generated index data and are excluded from version control. Keep them to reuse the index between runs.

## Troubleshooting

- **`GOOGLE_API_KEY is not set`**: Make sure `.env` is in the project root, contains `GOOGLE_API_KEY=...`, and that you replaced the placeholder.
- **Document folder missing or empty**: Run the script from the project root and add supported documents under `Software-engineering/`.
- **No text found in a document**: Check that the file is a supported format and, for PDFs, contains selectable text rather than scanned images.
- **Model download or API errors**: Check your internet connection, Gemini API key, and Google AI Studio API availability.

## Project files

```text
SmartDoc-Retriever/
├── Software-engineering/  # Documents to index
├── RAGChatBot.py          # CLI application and RAG pipeline
├── requirements.txt       # Python dependencies
├── .env.example           # Environment-variable template
└── README.md
```
