import asyncio
import sys
import time
import re
from urllib.parse import urlparse
import streamlit as st
from rag import process_urls, generate_answer

# Windows-specific event loop fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Web-based RAG Assistant",
    page_icon="📖",
    layout="wide"
)

# -------------------------------------------------
# Helpers & Validation Logic
# -------------------------------------------------
def is_valid_url(url: str) -> bool:
    try:
        url = url.strip()
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def is_supported_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    blocked_ext = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".avi", ".mkv")
    blocked_domains = ("youtube.com", "youtu.be", "vimeo.com")
    
    if path.endswith(blocked_ext): return False
    if any(domain in url for domain in blocked_domains): return False
    return True

def format_latex(text):
    """
    Robustly detects raw LaTeX strings and wraps them in $$ for proper block rendering.
    """
    # Detect common LaTeX keywords or math structures
    latex_patterns = [
        r"\\text", r"\\frac", r"\\times", r"\\sqrt", r"K\^T", r"d_k", r"softmax", r"\\left", r"\\right"
    ]
    
    # Check if any pattern exists in the text
    if any(re.search(p, text) for p in latex_patterns):
        # Clean up Wikipedia specific display tags if they exist
        clean_text = text.replace(r"{\displaystyle", "").replace(r"{\text", r"\text").rstrip("}")
        
        # If it's already wrapped in $, return as is, otherwise wrap in $$
        if clean_text.strip().startswith("$"):
            return clean_text
        return f"$$\n{clean_text.strip()}\n$$"
    
    return text

# -------------------------------------------------
# Session State Init
# -------------------------------------------------
if "urls_processed" not in st.session_state:
    st.session_state.urls_processed = False
if "last_urls" not in st.session_state:
    st.session_state.last_urls = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------
# Sidebar – URL Input & Configuration
# -------------------------------------------------
with st.sidebar:
    st.title("⚙️ Knowledge Setup")
    st.markdown("Enter URLs to build the AI context.")
    
    url1 = st.text_input("URL 1", placeholder="https://...")
    url2 = st.text_input("URL 2", placeholder="https://...")
    url3 = st.text_input("URL 3", placeholder="https://...")

    raw_urls = [u.strip() for u in (url1, url2, url3) if u.strip()]

    valid_urls = []
    for url in raw_urls:
        if is_valid_url(url) and is_supported_url(url):
            valid_urls.append(url)

    if valid_urls != st.session_state.last_urls:
        st.session_state.urls_processed = False

    st.markdown("---")
    
    process_btn = st.button("Process URLs", type="primary", use_container_width=True)
    
    if st.button("Reset App", use_container_width=True):
        st.session_state.urls_processed = False
        st.session_state.last_urls = []
        st.session_state.messages = []
        st.rerun()

    if process_btn:
        if not valid_urls:
            st.error("❌ Please enter at least one valid URL.")
        else:
            st.session_state.last_urls = valid_urls
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            step_progress = {"Initializing": 10, "Resetting": 25, "Loading": 50, "Splitting": 75, "Adding": 90}
            current_progress = 0
            
            try:
                for step in process_urls(valid_urls):
                    status_box.info(f"📋 {step}")
                    for key, target in step_progress.items():
                        if key.lower() in step.lower():
                            while current_progress < target:
                                current_progress += 1
                                progress_bar.progress(current_progress)
                                time.sleep(0.01)
                            break
                
                progress_bar.progress(100)
                st.session_state.urls_processed = True
                st.success("✅ Ready!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------------------------------
# Main Area – Q&A Interface
# -------------------------------------------------
st.title("Web-based RAG Assistant")
st.markdown("Ask questions based on your processed web content.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Q&A Logic
if not st.session_state.urls_processed:
    st.info("👈 **Setup your sources in the sidebar to begin.**")
else:
    if query := st.chat_input("Ask a question about your processed URLs..."):
        
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Analyzing..."):
                    raw_answer, sources = generate_answer(query)
                    
                    # Apply the Fix: Format any mathematical formulas
                    formatted_answer = format_latex(raw_answer)
                    st.markdown(formatted_answer)
                    
                    if sources:
                        with st.expander("📚 View Sources"):
                            for src in sources:
                                st.markdown(f"- {src}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": formatted_answer})
            except Exception as e:
                st.error(f"❌ Error: {e}")
