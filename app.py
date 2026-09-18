import os
import sys
import streamlit as st
import numpy as np

# Import RAG Modules
from document_loader import DocumentLoader
from chunker import DocumentChunker
from embeddings import EmbeddingEngine
from vector_store import FAISSVectorStore
from rag_engine import RAGEngine
from sample_generator import load_preloaded_university_dataset

# Page Configuration
st.set_page_config(
    page_title="University Regulations RAG AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Modern Dark Glassmorphism CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f172a 0%, #090d16 60%, #020617 100%);
        color: #f1f5f9;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.9) 50%, rgba(14, 165, 233, 0.25) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 4px 0;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin: 0;
    }
    
    .stat-pill-container {
        display: flex;
        gap: 10px;
        margin-top: 14px;
        flex-wrap: wrap;
    }
    .stat-pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5px 12px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #cbd5e1;
    }
    .stat-pill-highlight {
        background: rgba(14, 165, 233, 0.15);
        border-color: rgba(56, 189, 248, 0.3);
        color: #38bdf8;
    }
    
    .advanced-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        transition: all 0.3s ease;
    }
    .advanced-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.3);
    }

    .analysis-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
    }
    
    .cit-tag {
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .tag-academic { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-attendance { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .tag-exam { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .tag-handbook { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
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

# Auto-Load VIGNAN R22 Academic Regulations Dataset on First Run
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

# Calculate Live Metrics
total_docs_count = len(set(d["doc_name"] for d in st.session_state.documents))
total_pages_count = len(st.session_state.documents)
total_chunks_count = len(st.session_state.chunks)
vector_count = st.session_state.vector_store.total_count()

# Hero Header Banner
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">🎓 University Regulations RAG AI Assistant</div>
    <div class="hero-subtitle">Multi-PDF Ingestion, Document Analysis & Grounded Answering for VIGNAN R22 Regulations & Uploaded Custom Handbooks</div>
    <div class="stat-pill-container">
        <div class="stat-pill stat-pill-highlight"><span>📚 Documents:</span> <strong>{total_docs_count} PDFs</strong></div>
        <div class="stat-pill"><span>📄 Total Pages:</span> <strong>{total_pages_count} Pages</strong></div>
        <div class="stat-pill"><span>🧩 Chunks:</span> <strong>{total_chunks_count} Chunks</strong></div>
        <div class="stat-pill"><span>🎯 Vectors:</span> <strong>{vector_count} Vectors</strong></div>
        <div class="stat-pill"><span>🛡️ Anti-Hallucination:</span> <strong>Active</strong></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ RAG Control Panel")
    
    st.subheader("📁 Upload New PDF Document")
    uploaded_files = st.file_uploader("Upload Custom PDF Handbook / Regulation", type=["pdf"], accept_multiple_files=True)
    if uploaded_files and st.button("⚡ Process & Analyze Uploaded PDF", use_container_width=True, type="primary"):
        with st.spinner("Analyzing uploaded PDF document and updating vector store..."):
            loader = DocumentLoader()
            new_pages = []
            analysis_list = []
            
            for file in uploaded_files:
                pages = loader.load_pdf_from_bytes(file.read(), file.name)
                new_pages.extend(pages)
                
                # Document Analysis Metrics
                doc_text = " ".join([p["cleaned_text"] for p in pages])
                word_count = len(doc_text.split())
                char_count = len(doc_text)
                detected_cat = pages[0]["category"] if pages else "Custom PDF"
                
                analysis_list.append({
                    "filename": file.name,
                    "pages": len(pages),
                    "word_count": word_count,
                    "char_count": char_count,
                    "category": detected_cat,
                    "preview": doc_text[:250] + "..."
                })
            
            st.session_state.documents.extend(new_pages)
            chunker = DocumentChunker(chunk_size=600, chunk_overlap=100, strategy="recursive")
            chunks = chunker.chunk_pages(st.session_state.documents)
            st.session_state.chunks = chunks
            
            # Re-embed and update vector store
            embeds = st.session_state.embedding_engine.embed_texts([c["text"] for c in chunks])
            st.session_state.vector_store.clear()
            st.session_state.vector_store.add_embeddings(embeds, chunks)
            
            st.session_state.uploaded_doc_analysis = analysis_list
            st.success(f"Indexed {len(uploaded_files)} new PDF(s)! You can now ask questions about them.")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Reset Dataset", use_container_width=True):
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
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.toast("Chat and search history cleared!")
            st.rerun()

    st.divider()
    st.subheader("🎯 Vector Search & Guardrails")
    similarity_threshold = st.slider("Anti-Hallucination Threshold", 0.05, 0.60, 0.15, 0.05, help="Queries below this relevance score will be rejected.")
    top_k = st.slider("Top-K Contexts", 1, 8, 4)

    st.divider()
    st.subheader("🔍 Metadata Filter")
    doc_options = ["All Documents"] + st.session_state.vector_store.get_all_doc_names()
    selected_doc = st.selectbox("Document Filter", doc_options)
    
    cat_options = ["All Categories"] + st.session_state.vector_store.get_all_categories()
    selected_cat = st.selectbox("Category Filter", cat_options)

# Create 3 Clean Tabs (Viva Focus tab removed)
tab_chat, tab_docs, tab_search = st.tabs([
    "💬 Grounded QA Chat",
    "📁 Document Manager & Analysis",
    "🎯 Vector Search Inspector"
])

rag_engine = RAGEngine(
    vector_store=st.session_state.vector_store,
    embedding_engine=st.session_state.embedding_engine,
    similarity_threshold=similarity_threshold
)

# TAB 1: Grounded QA Chat
with tab_chat:
    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.subheader("💬 Grounded Q&A Assistant")
    with head_col2:
        if st.button("🗑️ Clear Chat History", key="clear_chat_tab_btn", use_container_width=True):
            st.session_state.chat_history = []
            st.toast("Chat history cleared!")
            st.rerun()

    # Display Newly Uploaded Document Analysis Card if present
    if st.session_state.uploaded_doc_analysis:
        for ana in st.session_state.uploaded_doc_analysis:
            st.markdown(f"""
            <div class="analysis-card">
                <span style="font-weight:700; color:#34d399; font-size:1.1rem;">⚡ Newly Analyzed Document: {ana['filename']}</span>
                <p style="margin-top:6px; color:#cbd5e1;">Category: <strong>{ana['category']}</strong> | Total Pages: <strong>{ana['pages']}</strong> | Word Count: <strong>{ana['word_count']} words</strong></p>
                <p style="font-size:0.88rem; color:#94a3b8; margin-bottom:0;"><em>Content Preview: {ana['preview']}</em></p>
            </div>
            """, unsafe_allow_html=True)

    st.write("**Quick Sample Questions:**")
    q_cols = st.columns(4)
    sample_q = None
    with q_cols[0]:
        if st.button("📌 Minimum Attendance %"):
            sample_q = "What is the minimum attendance percentage required for exam eligibility and how is shortage condoned?"
    with q_cols[1]:
        if st.button("📊 SGPA & CGPA Formula"):
            sample_q = "How is SGPA and CGPA calculated under relative grading?"
    with q_cols[2]:
        if st.button("⚠️ R Grade Rule"):
            sample_q = "What happens if a student gets an 'R' grade in a course?"
    with q_cols[3]:
        if st.button("🚪 Lateral Exit Options"):
            sample_q = "What are the rules for lateral exit with an Engineering Diploma or B.Sc. degree?"

    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "metadata" in msg and msg["metadata"]["is_grounded"]:
                with st.expander("📄 View Source Citations & Context Snippets"):
                    for cit in msg["metadata"]["citations"]:
                        cat_class = "tag-academic"
                        cat_lower = cit["category"].lower()
                        if "attendance" in cat_lower: cat_class = "tag-attendance"
                        elif "exam" in cat_lower: cat_class = "tag-exam"
                        elif "handbook" in cat_lower: cat_class = "tag-handbook"
                        
                        st.markdown(f"""
                        <div class="advanced-card">
                            <span class="cit-tag {cat_class}">{cit['category']}</span>
                            <span class="cit-tag tag-academic">📄 {cit['doc_name']}</span>
                            <span class="cit-tag tag-exam">📖 Page {cit['page_number']}</span>
                            <span class="cit-tag tag-handbook">📊 Score: {cit['similarity_pct']}%</span>
                            <p style="margin-top:10px; color:#e2e8f0; font-size:0.93rem;">{cit['raw_text']}</p>
                        </div>
                        """, unsafe_allow_html=True)

    query = st.chat_input("Ask any question about attendance, exams, grades, exit options or uploaded PDF...") or sample_q

    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching vector store & verifying grounded context..."):
                response = rag_engine.answer_query(
                    query=query,
                    top_k=top_k,
                    doc_filter=None if selected_doc == "All Documents" else selected_doc,
                    category_filter=None if selected_cat == "All Categories" else selected_cat
                )
                
                st.markdown(response["answer"])
                
                if response["is_grounded"]:
                    st.success(f"✓ Grounded Answer (Match Confidence: {response['max_confidence_pct']}%)")
                    with st.expander("📄 Source Citations & Context Snippets"):
                        for cit in response["citations"]:
                            cat_class = "tag-academic"
                            cat_lower = cit["category"].lower()
                            if "attendance" in cat_lower: cat_class = "tag-attendance"
                            elif "exam" in cat_lower: cat_class = "tag-exam"
                            elif "handbook" in cat_lower: cat_class = "tag-handbook"

                            st.markdown(f"""
                            <div class="advanced-card">
                                <span class="cit-tag {cat_class}">{cit['category']}</span>
                                <span class="cit-tag tag-academic">📄 {cit['doc_name']}</span>
                                <span class="cit-tag tag-exam">📖 Page {cit['page_number']}</span>
                                <span class="cit-tag tag-handbook">📊 Match: {cit['similarity_pct']}%</span>
                                <p style="margin-top:10px; color:#e2e8f0; font-size:0.93rem;">{cit['raw_text']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("⚠️ Out-of-Bounds Query: Answer not found in uploaded university documents.")

        st.session_state.chat_history.append({"role": "assistant", "content": response["answer"], "metadata": response})

# TAB 2: Document Manager & Analysis
with tab_docs:
    st.subheader("📁 Document Repository & Analysis Breakdown")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    col_stat1.metric("Indexed Documents", total_docs_count)
    col_stat2.metric("Document Pages", total_pages_count)
    col_stat3.metric("Semantic Chunks", total_chunks_count)
    col_stat4.metric("FAISS Vectors", vector_count)
    
    st.divider()
    st.write("### Indexed Documents Table")
    table_data = []
    for d in st.session_state.documents:
        table_data.append({
            "Document Name": d["doc_name"],
            "Page": d["page_number"],
            "Category": d["category"],
            "Section Title": d["section"],
            "Text Snippet": d["cleaned_text"][:140] + "..."
        })
    st.dataframe(table_data, use_container_width=True)

# TAB 3: Vector Search Inspector
with tab_search:
    st.subheader("🎯 Live FAISS Similarity Search Explorer")
    s_query = st.text_input("Enter Query to Test Vector Nearest Neighbors", "What is the minimum attendance required?")
    if s_query:
        vec = st.session_state.embedding_engine.embed_query(s_query)
        results = st.session_state.vector_store.search(
            query_vector=vec,
            top_k=top_k,
            doc_filter=None if selected_doc == "All Documents" else selected_doc,
            category_filter=None if selected_cat == "All Categories" else selected_cat
        )
        st.write(f"### Ranked Top-{len(results)} Nearest Neighbor Vectors")
        for idx, res in enumerate(results):
            c = res["chunk"]
            st.markdown(f"""
            <div class="advanced-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#38bdf8;">Rank #{idx+1} | 📄 {c['doc_name']} (Page {c['page_number']})</span>
                    <span style="background:#0284c7; color:white; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem;">Match Score: {res['similarity_pct']:.1f}%</span>
                </div>
                <p style="margin-top:10px; color:#cbd5e1;">{c['text']}</p>
            </div>
            """, unsafe_allow_html=True)
