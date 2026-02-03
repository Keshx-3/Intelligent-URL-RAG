# 📖 Web-based RAG Assistant

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langchain)
[![Groq](https://img.shields.io/badge/Groq-f55036?style=flat)](https://groq.com/)

A high-performance **RAG (Retrieval-Augmented Generation)** pipeline that transforms unstructured web content into a queryable, citation-backed knowledge base. By grounding LLaMA 3.1 in real-time web data, this assistant eliminates hallucinations and provides verifiable technical answers.

---

## 🏗️ System Architecture

The application is decoupled into two primary logic loops: **Knowledge Ingestion** and **Contextual Inference**.



### 1. The Ingestion Loop (ETL)
* **Extraction:** `WebBaseLoader` pulls raw HTML/Text from user-provided URLs.
* **Transformation:** `RecursiveCharacterTextSplitter` segments data into 1500-character chunks with semantic overlap to preserve context across boundaries.
* **Vectorization:** Local embeddings via `Alibaba-NLP/gte-base-en-v1.5` map text to a 768-dimensional vector space.
* **Persistence:** ChromaDB manages the local vector store, allowing for efficient similarity searches.

### 2. The Inference Loop (RAG)
* **Semantic Search:** User queries are vectorized and compared against the vector store using Cosine Similarity.
* **Augmentation:** The top 8 most relevant context chunks are injected into a specialized system prompt.
* **Generation:** Groq-hosted LLaMA 3.1 synthesizes a response strictly based on the provided context.

---

## 🌟 Key Features

- 🔗 **Live Web Ingestion**: Instantly build a knowledge base from any valid HTTP/HTTPS source.
- 🧠 **Zero-Hallucination Logic**: System prompts enforce strict grounding—if the answer isn't in the context, the AI won't guess.
- 📚 **Source Attribution**: Transparent citation tracking showing exactly which URLs influenced the answer.
- ➗ **High-Fidelity Math Rendering**: Custom regex-based pipeline identifies and cleans LaTeX artifacts, rendering complex equations perfectly via `st.latex()`.
- ⚙️ **Optimized Performance**: Optimized for Windows environments using `asyncio` loop policies and persistent vector indexing to avoid redundant re-processing.

---

## 🛠️ Tech Stack

| Layer | Technology |
|:--- |:--- |
| **Orchestration** | LangChain |
| **Inference Engine** | Groq (LLaMA 3.1 8B Instant) |
| **Vector Database** | ChromaDB |
| **Embeddings** | HuggingFace (`gte-base-en-v1.5`) |
| **Frontend** | Streamlit |

---

## 📂 Project Structure

```text
├── main.py              # Streamlit UI, Chat Memory & LaTeX Rendering Logic
├── rag.py               # RAG Pipeline (Document ETL & Vector Search)
├── resources/
│   └── vectorstore/     # Persistent ChromaDB collection
├── .env                 # API Credentials
└── requirements.txt     # Project Dependencies

## 🚀 Getting Started
1. Clone the repo.
2. Create a `.env` file with your `GROQ_API_KEY`.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `streamlit run main.py`

## 🧠 Engineering Highlights
- **Artifact Cleaning**: Implemented regex-based cleaning to strip Wikipedia/HTML noise from technical content.
- **Async Fixes**: Integrated Windows Selector Event Loop policy to ensure stability across different OS environments.
