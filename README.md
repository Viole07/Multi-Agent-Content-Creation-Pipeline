# Multi-Agent Content Creation Pipeline 🤖✍️

An autonomous, full-stack Multi-Agent Content Generation system powered by **LangGraph**, **Python**, **Express.js**, and **React (Tailwind CSS v4)**. 

Instead of relying on a single large language model to generate content from scratch, this application orchestrates a **Supervisor-pattern Multi-Agent architecture** where distinct AI personas collaborate, research, critique, and iteratively refine technical documentation in real-time.

---

## 🏗️ System Architecture & Workflow

```text
[ React Frontend (UI) ] 
       │  ▲
       │  │  (Server-Sent Events - Live Terminal Streaming)
       ▼  │
[ Express.js Server (Node.js API Bridge) ]
       │
       ▼  (spawns unbuffered child process via uv)
[ LangGraph State Machine (Python Backend) ]
       │
       ├─► 1. [Researcher Node] ──► Scrapes Wikipedia (Custom User-Agent Bypass)
       │
       ├─► 2. [Writer Node]     ──► Synthesizes research into Markdown drafts
       │                            (Iteratively improves using Editor feedback)
       │
       └─► 3. [Editor Node]     ──► Strict critique & Prompt-Based Parsing
                                    ├── If Approved (True) ──► Publish Article
                                    └── If Rejected (False) ──► Loop to Writer (Max 3 iterations)

```

### The Three AI Personas:

1. **Researcher Agent:** Takes the user's topic, connects to Wikipedia using custom user-agent headers to bypass bot-detection, and extracts grounded factual notes.
2. **Writer Agent:** Uses the research notes to draft structured Markdown content. On subsequent loops, it receives its **previous draft + the Editor's critique** and actively revises the text.
3. **Editor Agent:** Acts as a strict senior editor evaluating factual accuracy, structure, and tone. Uses **Prompt-Based Parsing** (keyword extraction) instead of fragile schema-calling to evaluate the draft and output an approval decision with detailed feedback.

---

## 🛠️ Tech Stack

* **Frontend:** React (Vite), Tailwind CSS v4, Server-Sent Events (`EventSource`)
* **Backend:** Node.js, Express.js (Child Process Execution & SSE Streamer)
* **AI / ML Engine:** Python 3.10+, LangGraph, LangChain, OpenRouter API
* **Package Management:** `uv` (Ultra-fast Python environment manager), `npm`

---

## ✨ Key Engineering Highlights

* **Real-Time SSE Streaming (`EventSource`):** Solved standard HTTP timeout issues by implementing Server-Sent Events. The Express backend captures Python's `stdout` and streams live agent execution logs (`[Researcher]`, `[Writer]`, `[Editor]`) directly into the React UI.
* **Line-Buffered Python Execution:** Forced Python to run in unbuffered mode (`sys.stdout.reconfigure(line_buffering=True)` & `PYTHONUNBUFFERED=1`) so output logs don't get trapped in memory and stream line-by-line to the client.
* **Prompt-Based Parsing over Fragile JSON Schemas:** Bypassed the limitations of free-tier open-weights models (which often crash on strict function-calling / Pydantic JSON schemas) by using explicit keyword-based text parsing (`APPROVED:` / `FEEDBACK:`).
* **Graceful Fallback Logic:** Implemented a hard iteration cap (`max=3`) and a fallback return mechanism. If the AI Editor and Writer reach a deadlock without formal approval, the pipeline gracefully publishes the latest polished revision instead of returning an empty payload.
* **Bot-Detection & Scraping Protection:** Configured custom user-agent headers (`wikipedia.set_user_agent`) to reliably bypass rate-limiters and `403 Access Denied` HTML responses when scraping public documentation.

---

## 🚀 Getting Started

### Prerequisites

* [Node.js](https://nodejs.org/) (v18+)
* [Python](https://www.python.org/) (v3.10+)
* [uv](https://github.com/astral-sh/uv) (for Python virtual environment management)
* An API Key from [OpenRouter](https://openrouter.ai/)

### 1. Clone the Repository

```bash
git clone [https://github.com/Viole07/Multi-Agent-Content-Creation-Pipeline.git](https://github.com/Viole07/Multi-Agent-Content-Creation-Pipeline.git)
cd Multi-Agent-Content-Creation-Pipeline

```

### 2. Configure Environment Variables

Create a `.env` file inside the `backend/` directory and add your OpenRouter API key:

```bash
# backend/.env
OPENROUTER_API_KEY=your_openrouter_api_key_here
PORT=5000

```

*(You can reference `backend/.env.example` for required variables).*

### 3. Install & Run the Backend (Node + Python)

Open Terminal 1 and start the Express backend:

```bash
cd backend
npm install
# Ensure uv has synced the Python environment
uv venv
uv pip install -r requirements.txt
node server.js

```

### 4. Install & Run the Frontend (React)

Open Terminal 2 and start the Vite development server:

```bash
cd frontend
npm install
npm run dev

```

Open your browser and navigate to `http://localhost:5173`.

---

## 🧪 How to Use

1. Enter any complex topic into the input field (e.g., *"Zero-Knowledge Ephemeral File Sharing using AES-256-GCM and ECC"* or *"Autonomous intelligent agents in artificial intelligence"*).
2. Click **Start Research**.
3. Watch the terminal console stream the real-time collaboration between the **Researcher**, **Writer**, and **Editor**.
4. Read the Editor's critiques as it forces the Writer to refine the draft across iterations.
5. Once approved (or upon reaching the max-iteration fallback), view the final formatted Markdown article rendered in your browser.

---

## 📄 License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

```

```
