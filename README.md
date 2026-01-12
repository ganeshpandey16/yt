# 🎥 YouTube → AI Notes → Notion → RAG Chat Pipeline

An end-to-end **AI-powered learning pipeline** that:

1. Takes a **YouTube video URL**
2. Generates **high-quality AI notes**
3. Stores notes in **Notion using MCP**
4. Indexes notes into **Qdrant (Vector DB)**
5. Allows **interactive RAG-based querying** over the notes

This project is designed with **clean architecture**, **OOP principles**, and **industry-grade separation of concerns**.

---

## ✨ Features

- 📄 Automatic transcript extraction from YouTube
- 🧠 AI-generated structured notes (Markdown)
- 🗂️ Notes stored as a **Notion page** via MCP
- 🔎 Semantic search using **Qdrant + embeddings**
- 💬 Interactive RAG chat loop on generated notes
- 🧱 Modular & extensible design

---

## 🧠 Architecture Overview

YouTube URL
↓
Transcript Service
↓
AI Notes Generator (.md)
↓
┌───────────────┬────────────────────┐
│               │                    │
│ Notion (MCP)  │ Qdrant Vector DB   │
│ Page Storage  │ Embedding Storage  │
│               │                    │
└───────────────┴────────────────────┘
↓
RAG Query Loop

## ⚙️ Prerequisites

- Python **3.9+**
- Qdrant Cloud or Local Instance
- Notion Integration Token
- Open Router API key

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

Required libraries include:

- sentence-transformers
- qdrant-client
- langchain
- fastmcp
- youtube-transcript-api
- google-generativeai

## 🚀 How It Works

1️⃣ Run the pipeline

```bash
python main.py
```

2️⃣ Enter a YouTube URL

Enter the YouTube video URL when prompted.

3️⃣ What happens automatically

- Transcript is fetched
- AI notes are generated
- Notes are saved as `output/ai_notes.md`
- A Notion page titled “Notes” is created
- Notes are embedded & stored in Qdrant

## 💬 RAG Chat Mode

After ingestion, the app enters an interactive loop:

> 🧠 RAG chat started. Type `exit` to quit.
>
> You: Explain Newton’s First Law
> 🤖 Context-based answer:
> ...

Type `exit` or `quit` to stop.

## 🧠 Design Principles

- ✅ Single Responsibility per module
- ✅ MCP used as a command interface, not SDK coupling
- ✅ Vector DB isolated from application logic
- ✅ Easy to extend to multi-doc / multi-user
- ✅ Ready for FastAPI / Agent / MCP Server wrapping

## 🔮 Possible Extensions

- 🤖 LLM answer generation on top of RAG context
- 🏷️ Metadata-aware chunking (headings, sections)
- 📚 Multi-document search
- 🧑‍🏫 Student-friendly explanation modes
- 🌐 Web + Notes hybrid RAG

---

## 🏁 Summary

This project demonstrates a real-world AI system that combines:

- Content ingestion
- Knowledge storage
- Retrieval-Augmented Generation
- Tool-based automation (MCP)

Perfect for:

- AI-powered learning tools
- Note automation platforms
- Agentic AI systems
- Portfolio / startup projects

🔥 Built for scale. Designed for clarity. Ready for production.
