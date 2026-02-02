#main.py
import asyncio
import sys
import time
from urllib.parse import urlparse

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
from rag import process_urls, generate_answer


# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Web-based Knowledge Assistant using RAG",
    layout="centered"
)
st.title("Web-based Knowledge Assistant using RAG")


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def is_supported_url(url: str) -> bool:
    path = urlparse(url).path.lower()

    blocked_ext = (
        ".png", ".jpg", ".jpeg", ".gif", ".webp",
        ".mp4", ".mov", ".avi", ".mkv"
    )

    blocked_domains = (
        "youtube.com",
        "youtu.be",
        "vimeo.com",
    )

    if path.endswith(blocked_ext):
        return False

    if any(domain in url for domain in blocked_domains):
        return False

    return True


# -------------------------------------------------
# Session State Init
# -------------------------------------------------
if "urls_processed" not in st.session_state:
    st.session_state.urls_processed = False

if "last_urls" not in st.session_state:
    st.session_state.last_urls = []


# -------------------------------------------------
# Sidebar – URL Input
# -------------------------------------------------
st.sidebar.header("🔗 Enter URLs")

url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

raw_urls = [u.strip() for u in (url1, url2, url3) if u.strip()]

valid_urls = []
invalid_urls = []
unsupported_urls = []

for url in raw_urls:
    if not is_valid_url(url):
        invalid_urls.append(url)
    elif not is_supported_url(url):
        unsupported_urls.append(url)
    else:
        valid_urls.append(url)

if invalid_urls:
    st.sidebar.warning(
        "⚠️ Invalid URLs:\n" + "\n".join(f"- {u}" for u in invalid_urls)
    )

if unsupported_urls:
    st.sidebar.info(
        "🖼️ Media / Video URLs not supported:\n" +
        "\n".join(f"- {u}" for u in unsupported_urls)
    )

# Reset if URLs changed
if valid_urls != st.session_state.last_urls:
    st.session_state.urls_processed = False


# -------------------------------------------------
# Sidebar Controls
# -------------------------------------------------
process_btn = st.sidebar.button("⚙️ Process URLs")
reset_btn = st.sidebar.button(
    "🔄 Reset",
    disabled=not (raw_urls or st.session_state.urls_processed)
)


# -------------------------------------------------
# Reset Logic
# -------------------------------------------------
if reset_btn:
    st.session_state.urls_processed = False
    st.session_state.last_urls = []
    st.rerun()


# -------------------------------------------------
# URL Processing
# -------------------------------------------------
if process_btn:
    if not valid_urls:
        st.sidebar.error("❌ Please enter at least one valid text-based URL.")
    else:
        st.session_state.last_urls = valid_urls
        st.session_state.urls_processed = False

        status_box = st.sidebar.empty()
        progress_bar = st.sidebar.progress(0)

        step_progress = {
            "Initializing components": 10,
            "Resetting vector store": 25,
            "Loading data": 50,
            "Splitting text": 75,
            "Adding chunks": 90,
        }

        current_progress = 0

        for step in process_urls(valid_urls):
            status_box.info(step)

            for key, target in step_progress.items():
                if key.lower() in step.lower():
                    while current_progress < target:
                        current_progress += 1
                        progress_bar.progress(current_progress)
                        time.sleep(0.02)
                    break

        progress_bar.progress(100)
        status_box.success("✅ Vector database is ready.")
        st.session_state.urls_processed = True


# -------------------------------------------------
# Main Area – Q&A
# -------------------------------------------------
st.divider()
st.header("❓ Ask a Question")

if not st.session_state.urls_processed:
    st.info("🛈 Please process URLs before asking questions.")
    st.text_input("Ask a question", disabled=True)
    st.button("💡 Get Answer", disabled=True)
else:
    query = st.text_input("Ask a question")
    ask_btn = st.button("💡 Get Answer")

    if ask_btn:
        if not query.strip():
            st.error("❌ Please enter a question.")
        else:
            try:
                with st.spinner("Thinking..."):
                    answer, sources = generate_answer(query)

                st.subheader("✅ Answer")
                st.markdown(answer, unsafe_allow_html=True)

                if sources:
                    st.subheader("📌 Sources")
                    for src in sources:
                        st.markdown(f"- {src}")

            except RuntimeError as e:
                # Handle "Vector store not initialized" gracefully
                st.warning(f"⚠️ {str(e)}")
                st.info("🛈 Please process URLs first before asking questions.")
