# QA Chatbot (LangChain + FastAPI + Web UI)

A simple Q&A chatbot project built with LangChain and Cohere model integration.

It supports:
- Single-question chat with live streaming response in the webpage.
- Multi-question input (one question per line) using batch processing.
- Structured response schema (`answer`, `confidence`, `reasoning`, `follow_up_questions`, `sources_needed`).
- Optional LangSmith tracing if API key is set.

## Project Idea

The chatbot is designed as a practical QA assistant:
- User asks a question in a web interface.
- Backend sends the question to a LangChain chain.
- Model returns a structured QA response.
- Frontend shows chat-style output, with streamed answer for single-question mode.
- If user sends multiple questions (separate lines), backend uses `.batch` to answer all at once.

## Tech Stack

- Python 3.10+
- LangChain
- Cohere integration (`langchain-cohere`)
- FastAPI + Uvicorn
- Vanilla HTML/CSS/JS frontend

## Project Structure

```text
QA-Chatbot/
├── app.py                # FastAPI backend + API routes + static frontend mount
├── main.py               # QAChatbot class and LangChain logic
├── frontend/
│   ├── index.html        # UI page
│   ├── styles.css        # Dark modern styling
│   └── app.js            # Frontend logic (streaming + batch)
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions (Windows PowerShell)

### 1) Clone and open project

```powershell
git clone <your-repo-url>
cd QA-Chatbot
```

### 2) Create virtual environment

```powershell
python -m venv .venv
```

If `python` is not available, use your installed Python launcher path.

### 3) Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4) Install dependencies

```powershell
pip install -r requirements.txt
```

### 5) Configure environment variables

Create `.env` file in project root (or copy from `.env.example`) and set required keys.

Example:

```env
COHERE_API_KEY=your_cohere_api_key
LANGSMITH_API_KEY=your_langsmith_api_key_optional
LANGSMITH_PROJECT=QA-Chatbot
```

Notes:
- `COHERE_API_KEY` is required for model calls.
- `LANGSMITH_API_KEY` is optional (only for tracing/observability).
- `Provider Flexibility:` In this project i used Cohere, but it can be easily adapted to any LLM provider of your choice (e.g., OpenAI, Anthropic)

### 6) Run the app

```powershell
python -m uvicorn app:app --reload
```

If `python` command does not work:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

### 7) Open in browser

- App UI: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

## How to Use

- Single question:
  - Type one line and click **Send**.
  - You get streamed answer, then structured details.

- Multiple questions:
  - Type each question on a separate line.
  - Click **Send**.
  - App uses batch endpoint and returns all answers.
