# 📖 Web-based RAG Assistant

An advanced Retrieval-Augmented Generation (RAG) system that allows users to chat with any web-based content in real-time. Built with a focus on high-fidelity technical content rendering (LaTeX) and efficient vector search.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-000000?style=for-the-badge&logo=chroma&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-f55036?style=for-the-badge)

## 🌟 Key Features
- **Dynamic Web Ingestion**: Provide any URL to instantly build a local knowledge base.
- **Mathematical Precision**: Custom LaTeX rendering engine that handles complex formulas (Attention mechanisms, etc.) without formatting artifacts.
- **Local Embeddings**: Uses `Alibaba-NLP/gte-base-en-v1.5` for high-quality, local vector representations.
- **Hybrid Search**: Optimized retrieval with ChromaDB to provide contextually relevant answers using Llama 3.1.
- **Source Transparency**: Every answer includes an expandable section showing the exact sources used for generation.

## 🛠️ Architecture
1. **Extraction**: `WebBaseLoader` fetches raw HTML content.
2. **Chunking**: `RecursiveCharacterTextSplitter` segments data into 1500-character chunks with semantic overlap.
3. **Vectorization**: HuggingFace embeddings transform text into 768-dimensional vectors.
4. **Storage**: Vectors are stored in a persistent ChromaDB collection.
5. **RAG Pipeline**: The system retrieves the top 8 most relevant chunks and passes them to the Groq-powered Llama 3.1 model.

## 🚀 Getting Started
1. Clone the repo.
2. Create a `.env` file with your `GROQ_API_KEY`.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `streamlit run main.py`

## 🧠 Engineering Highlights
- **Artifact Cleaning**: Implemented regex-based cleaning to strip Wikipedia/HTML noise from technical content.
- **Async Fixes**: Integrated Windows Selector Event Loop policy to ensure stability across different OS environments.
