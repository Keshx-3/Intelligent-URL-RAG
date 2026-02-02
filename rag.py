from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv
import os

# Fix USER_AGENT warning
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

load_dotenv()

CHUNK_SIZE = 1500
EMBEDDING_MODEL = "Alibaba-NLP/gte-base-en-v1.5"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME = "my_collection"

llm = None
vector_store = None


def initialize_components():
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.9,
            max_tokens=500,
        )

    if vector_store is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True},
        )

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(VECTORSTORE_DIR),
        )


def process_urls(urls):
    yield "Initializing components..."
    initialize_components()

    yield "Resetting vector store..."
    vector_store.reset_collection()

    yield "Loading data..."
    loader = WebBaseLoader(urls)
    documents = loader.load()

    yield "Splitting text into chunks..."
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documents)

    yield "Adding chunks to vector database..."
    ids = [str(uuid4()) for _ in chunks]
    vector_store.add_documents(chunks, ids=ids)

    yield "Vector store is ready."


def generate_answer(query: str, k: int = 8):
    global vector_store, llm

    if vector_store is None or llm is None:
        raise RuntimeError("Vector store not initialized. Process URLs first.")

    retrieved_docs = vector_store.similarity_search(query, k=k)

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    sources = list(
        {doc.metadata.get("source", "unknown") for doc in retrieved_docs}
    )

    prompt = f"""
You are a technical assistant.

STRICT RULES:
- Answer ONLY using the provided context.
- If mathematical formulas appear, rewrite them in clean LaTeX.
- Remove artifacts like {{\\displaystyle}}, {{\\rm}}, or duplicated symbols.
- Use $$ ... $$ for block equations.
- If information is missing, explicitly say so.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)
    return response.content, sources




if __name__ == "__main__":
    urls = [
        "https://www.cnbc.com/2026/01/28/snap-establishes-specs-subsidiary-for-its-ar-glasses.html",
        "https://www.cnbc.com/2026/01/28/global-chip-stocks-today-nvidia-china-asml-sk-hynix.html",
        "https://docs.langchain.com/oss/python/langchain/overview",
    ]

    for status in process_urls(urls):
        print(status)

    answer, sources = generate_answer("tell me about Nvidia china asml sk hynix")
    print(answer, sources)