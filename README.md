# 🎓 University Regulations RAG AI Assistant

A Retrieval-Augmented Generation (RAG) assistant for querying university academic rulebooks, examination guidelines, attendance policies, and student handbooks. Pre-loaded with the official **VIGNAN's Foundation for Science, Technology & Research (VFSTR) R22 Academic Regulations** dataset.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49-red)
![RAG](https://img.shields.io/badge/RAG-FAISS%20%2F%20Vector%20Search-green)

---

## 🌟 Features

- **Multi-PDF Document Processing**: Ingests, parses, and cleans university policy PDFs with page-by-page metadata tracking.
- **⚡ Document Analysis & Instant Q&A**: Upload any custom PDF handbook to receive an instant analysis summary (total pages, word count, inferred category, preview) and start asking questions immediately.
- **Pre-loaded Dataset**: Turnkey access to VIGNAN R22 Academic Regulations, Attendance Policy, Examination Guidelines, and Student Code of Conduct.
- **Flexible Chunking Engine**: Recursive Character Chunking with token/character overlap to preserve cross-boundary context.
- **Embeddings & Vector Search**: High-dimensional vector representations with **FAISS `IndexFlatIP`** / NumPy dot-product Cosine Similarity search.
- **Scalar Metadata Filtering**: Restrict queries by Document Name, Category (Attendance, Examination, Academic, Handbook), and Page Number ranges.
- **Anti-Hallucination Guardrails**: Distance thresholding (< 0.15 similarity cutoff) rejects out-of-bounds queries with:
  > *"I cannot find the answer in the uploaded university documents."*
- **Source Citations**: Displays exact source citations (`Document Name`, `Page Number`, `Match Confidence %`, `Raw Text`).
- **Interactive Dark Glassmorphism UI**: Built with Streamlit, custom CSS glassmorphism cards, stat pills, confidence progress bars, and one-click chat history clearing.

---

## 📂 Project Architecture

```
scratch/rag_assistant/
├── app.py                # Main Streamlit Web Application Interface
├── document_loader.py    # Multi-PDF parser, text cleaner & category detector
├── chunker.py            # Recursive character & sentence chunking engine
├── embeddings.py         # Vector embedding engine (SentenceTransformers + TF-IDF fallback)
├── vector_store.py       # FAISS IndexFlatIP & NumPy matrix similarity search
├── rag_engine.py         # Grounded generator, anti-hallucination thresholding & citations
├── sample_generator.py   # Pre-loaded VIGNAN R22 Academic Regulations dataset
├── verify_rag.py         # Automated test verification suite
├── requirements.txt      # Python dependencies list
└── README.md             # Project documentation
```

---

## 🚀 Quick Start & Installation

### 1. Clone Repository
```bash
git clone https://github.com/majetikalyan007/University-Regulation-RAG-Model.git
cd University-Regulation-RAG-Model
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
streamlit run app.py
```

---

## 🧪 Run Automated Verification Tests

Verify all document loading, chunking, vector indexing, grounded Q&A, and anti-hallucination rejection tests:

```bash
python verify_rag.py
```

---

## 📜 Dataset Reference
- **University**: VIGNAN's Foundation for Science, Technology & Research (VFSTR)
- **Regulation**: R22 B.Tech. Academic Regulations (In Compliance with NEP 2020)
