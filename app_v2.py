import os
import sys
import streamlit as st
import numpy as np

# Import Core RAG Modules
from document_loader import DocumentLoader
from chunker import DocumentChunker
from embeddings import EmbeddingEngine
from vector_store import FAISSVectorStore
from rag_engine import RAGEngine
from sample_generator import load_preloaded_university_dataset

# Page Configuration - Variant 2
st.set_page_config(
    page_title="Academic Policy AI - University RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk Emerald Glassmorphism Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(ellipse at top left, #064e3b 0%, #022c22 40%, #020617 100%);
        color: #ecfdf5;
    }
    
    /* Top Header Bar */
    .top-bar {
        background: rgba(6, 78, 59, 0.4);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.6);
    }
    .top-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #34d399 0%, #2dd4bf 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .top-sub {
        color: #a7f3d0;
        font-size: 0.95rem;
        margin-top: 4px;
    }
    
    /* Emerald Card Container */
    .emerald-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        transition: all 0.3s ease;
    }
    .emerald-card:hover {
        border-color: rgba(52, 211, 153, 0.5);
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.2);
    }
    
    /* Neon Badges */
    .neon-badge {
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-emerald { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }
    .badge-teal { background: rgba(20, 184, 166, 0.2); color: #2dd4bf; border: 1px solid rgba(45, 212, 191, 0.4); }
    .badge-cyan { background: rgba(6, 182, 212, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #022c22;
        border-right: 1px solid rgba(16, 185, 129, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "documents" not in st.session_state:
    st.session_state.documents = []
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = FAISSVectorStore(dimension=384, metric="cosine")
if "embedding_engine" not in st.session_state:
    st.session_state.embedding_engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "uploaded_doc_analysis" not in st.session_state:
    st.session_state.uploaded_doc_analysis = None

# Load VIGNAN R22 Academic Regulations Dataset on First Startup
if not st.session_state.data_loaded:
    pages_data = load_preloaded_university_dataset()
    st.session_state.documents = pages_data
    
    chunker = DocumentChunker(chunk_size=600, chunk_overlap=100, strategy="recursive")
    chunks = chunker.chunk_pages(pages_data)
    st.session_state.chunks = chunks
    
    embeds = st.session_state.embedding_engine.embed_texts([c["text"] for c in chunks])
    st.session_state.vector_store.clear()
    st.session_state.vector_store.add_embeddings(embeds, chunks)
    st.session_state.data_loaded = True

# Metrics
total_docs = len(set(d["doc_name"] for d in st.session_state.documents))
total_pages = len(st.session_state.documents)
total_chunks = len(st.session_state.chunks)
vector_count = st.session_state.vector_store.total_count()

# Top Navigation Bar Header
st.markdown(f"""
<div class="top-bar">
    <div class="top-title">🤖 Academic Policy AI Assistant</div>
    <div class="top-sub">Grounded Neural Search Engine for University Regulations, Attendance Rules & Examination Handbooks</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Control Panel
with st.sidebar:
    st.header("⚙️ System Control Center")
    
    st.subheader("📁 Document Management")
    uploaded_files = st.file_uploader("Upload PDF Policy Document", type=["pdf"], accept_multiple_files=True)
    if uploaded_files and st.button("⚡ Index & Analyze PDF", use_container_width=True, type="primary"):
        with st.spinner("Processing PDF Document..."):
            loader = DocumentLoader()
            new_pages = []
            analysis_info = []
            for file in uploaded_files:
                pages = loader.load_pdf_from_bytes(file.read(), file.name)
                new_pages.extend(pages)
                
                doc_text = " ".join([p["cleaned_text"] for p in pages])
                analysis_info.append({
                    "name": file.name,
                    "pages": len(pages),
                    "words": len(doc_text.split()),
                    "category": pages[0]["category"] if pages else "Custom Policy"
                })
                
            st.session_state.documents.extend(new_pages)
            chunker = DocumentChunker(chunk_size=600, chunk_overlap=100, strategy="recursive")
            chunks = chunker.chunk_pages(st.session_state.documents)
            st.session_state.chunks = chunks
            
            embeds = st.session_state.embedding_engine.embed_texts([c["text"] for c in chunks])
            st.session_state.vector_store.clear()
            st.session_state.vector_store.add_embeddings(embeds, chunks)
            st.session_state.uploaded_doc_analysis = analysis_info
            st.success("Document Ingested & Vectorized!")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Reset Data", use_container_width=True):
            st.session_state.documents = load_preloaded_university_dataset()
            chunker = DocumentChunker(chunk_size=600, chunk_overlap=100, strategy="recursive")
            st.session_state.chunks = chunker.chunk_pages(st.session_state.documents)
            embeds = st.session_state.embedding_engine.embed_texts([c["text"] for c in st.session_state.chunks])
            st.session_state.vector_store.clear()
            st.session_state.vector_store.add_embeddings(embeds, st.session_state.chunks)
            st.session_state.chat_history = []
            st.session_state.uploaded_doc_analysis = None
            st.toast("Reset to default VIGNAN R22 Dataset!")

    with col_btn2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.toast("Chat history cleared!")
            st.rerun()

    st.divider()
    st.subheader("🎯 Search Parameters")
    similarity_threshold = st.slider("Guardrail Threshold", 0.05, 0.60, 0.15, 0.05)
    top_k = st.slider("Top-K Passages", 1, 8, 4)

    st.divider()
    st.subheader("🔍 Category & Doc Filter")
    doc_options = ["All Documents"] + st.session_state.vector_store.get_all_doc_names()
    selected_doc = st.selectbox("Select Document", doc_options)
    
    cat_options = ["All Categories"] + st.session_state.vector_store.get_all_categories()
    selected_cat = st.selectbox("Select Category", cat_options)

rag_engine = RAGEngine(
    vector_store=st.session_state.vector_store,
    embedding_engine=st.session_state.embedding_engine,
    similarity_threshold=similarity_threshold
)

# 2-Column Split Dashboard Layout (Distinct from Variant 1!)
col_left, col_right = st.columns([3, 2])

# LEFT COLUMN: Interactive Chat & Queries
with col_left:
    st.subheader("💬 Policy Q&A Console")
    
    if st.session_state.uploaded_doc_analysis:
        for a in st.session_state.uploaded_doc_analysis:
            st.info(f"⚡ **Newly Analyzed**: `{a['name']}` | **Category**: `{a['category']}` | **Pages**: `{a['pages']}` | **Words**: `{a['words']}`")

    st.write("**Quick Query Chips:**")
    qc1, qc2 = st.columns(2)
    sample_q = None
    with qc1:
        if st.button("📌 Minimum Attendance & Condonation"):
            sample_q = "What is the minimum attendance percentage required for exam eligibility and how is shortage condoned?"
        if st.button("📊 SGPA / CGPA Calculation Formula"):
            sample_q = "How is SGPA and CGPA calculated under relative grading?"
    with qc2:
        if st.button("⚠️ Consequence of 'R' Grade"):
            sample_q = "What happens if a student gets an 'R' grade in a course?"
        if st.button("🚪 Honorable Exit Options"):
            sample_q = "What are the rules for lateral exit with an Engineering Diploma or B.Sc. degree?"

    # Chat Messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "metadata" in msg and msg["metadata"]["is_grounded"]:
                with st.expander("📄 View Source Citations"):
                    for cit in msg["metadata"]["citations"]:
                        st.markdown(f"""
                        <div class="emerald-card">
                            <span class="neon-badge badge-emerald">{cit['category']}</span>
                            <span class="neon-badge badge-teal">📄 {cit['doc_name']}</span>
                            <span class="neon-badge badge-cyan">📖 Page {cit['page_number']}</span>
                            <p style="margin-top:8px; color:#ecfdf5;">{cit['raw_text']}</p>
                        </div>
                        """, unsafe_allow_html=True)

    query = st.chat_input("Ask a question about university regulations or uploaded PDF...") or sample_q

    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching neural index..."):
                response = rag_engine.answer_query(
                    query=query,
                    top_k=top_k,
                    doc_filter=None if selected_doc == "All Documents" else selected_doc,
                    category_filter=None if selected_cat == "All Categories" else selected_cat
                )
                
                st.markdown(response["answer"])
                
                if response["is_grounded"]:
                    st.success(f"✓ Grounded Answer (Match Confidence: {response['max_confidence_pct']}%)")
                    with st.expander("📄 Source Citations"):
                        for cit in response["citations"]:
                            st.markdown(f"""
                            <div class="emerald-card">
                                <span class="neon-badge badge-emerald">{cit['category']}</span>
                                <span class="neon-badge badge-teal">📄 {cit['doc_name']}</span>
                                <span class="neon-badge badge-cyan">📖 Page {cit['page_number']}</span>
                                <p style="margin-top:8px; color:#ecfdf5;">{cit['raw_text']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("⚠️ Out-of-Bounds Query: Answer not found in indexed documents.")

        st.session_state.chat_history.append({"role": "assistant", "content": response["answer"], "metadata": response})

# RIGHT COLUMN: Live Document Intelligence & Vector Inspector
with col_right:
    st.subheader("📊 Document Intelligence")
    
    st.markdown(f"""
    <div class="emerald-card">
        <h4 style="margin-top:0; color:#34d399;">System Vector Analytics</h4>
        <p>📚 Total Documents: <strong>{total_docs}</strong></p>
        <p>📄 Total Pages: <strong>{total_pages}</strong></p>
        <p>🧩 Chunks: <strong>{total_chunks}</strong></p>
        <p>🎯 FAISS Index Count: <strong>{vector_count}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔍 Vector Nearest Neighbors")
    test_search = st.text_input("Live Vector Search Inspector", "attendance shortage condonation")
    if test_search and vector_count > 0:
        vec = st.session_state.embedding_engine.embed_query(test_search)
        results = st.session_state.vector_store.search(
            query_vector=vec,
            top_k=3,
            doc_filter=None if selected_doc == "All Documents" else selected_doc,
            category_filter=None if selected_cat == "All Categories" else selected_cat
        )
        for idx, r in enumerate(results):
            c = r["chunk"]
            st.markdown(f"""
            <div class="emerald-card">
                <span class="neon-badge badge-emerald">Rank #{idx+1}</span>
                <span class="neon-badge badge-cyan">Score: {r['similarity_pct']:.1f}%</span>
                <p style="font-size:0.85rem; margin-top:6px;"><strong>{c['doc_name']} (Page {c['page_number']})</strong></p>
                <p style="font-size:0.82rem; color:#a7f3d0;">{c['text'][:150]}...</p>
            </div>
            """, unsafe_allow_html=True)
