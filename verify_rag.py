import sys
from document_loader import DocumentLoader
from chunker import DocumentChunker
from embeddings import EmbeddingEngine
from vector_store import FAISSVectorStore
from rag_engine import RAGEngine
from sample_generator import load_preloaded_university_dataset

def test_rag_system():
    print("--- 1. Testing Document Ingestion ---")
    pages = load_preloaded_university_dataset()
    print(f"[OK] Loaded {len(pages)} document pages.")
    assert len(pages) > 0, "No pages loaded!"

    print("--- 2. Testing Document Chunking ---")
    chunker = DocumentChunker(chunk_size=600, chunk_overlap=100, strategy="recursive")
    chunks = chunker.chunk_pages(pages)
    print(f"[OK] Generated {len(chunks)} chunks.")
    assert len(chunks) > 0, "No chunks generated!"

    print("--- 3. Testing Embedding Generation ---")
    embedder = EmbeddingEngine()
    embeds = embedder.embed_texts([c["text"] for c in chunks])
    print(f"[OK] Generated embeddings array of shape: {embeds.shape}")
    assert embeds.shape[0] == len(chunks), "Embeddings count mismatch!"

    print("--- 4. Testing FAISS / Matrix Vector Store ---")
    store = FAISSVectorStore(dimension=embeds.shape[1], metric="cosine")
    store.add_embeddings(embeds, chunks)
    print(f"[OK] Vector store indexed {store.total_count()} vectors.")
    assert store.total_count() == len(chunks), "Vector store count mismatch!"

    print("--- 5. Testing Grounded RAG Query Answering ---")
    rag = RAGEngine(vector_store=store, embedding_engine=embedder, similarity_threshold=0.25)
    
    # In-domain query test (Attendance)
    res_att = rag.answer_query("What is the minimum attendance percentage required?")
    print(f"In-domain Query Answer:\n{res_att['answer'][:200]}...")
    print(f"Is Grounded: {res_att['is_grounded']} | Confidence: {res_att.get('max_confidence_pct', 0)}%")
    assert res_att["is_grounded"] == True, "In-domain query should be grounded!"
    assert len(res_att["citations"]) > 0, "Citations should be present!"

    # Out-of-domain query test (Quantum Mechanics)
    res_out = rag.answer_query("What is the quantum mechanics Schrödinger wave equation formula?")
    print(f"Out-of-domain Query Rejection Response:\n{res_out['answer']}")
    print(f"Is Grounded: {res_out['is_grounded']}")
    assert res_out["is_grounded"] == False, "Out-of-domain query should be rejected!"
    assert "cannot find the answer" in res_out["answer"].lower(), "Out-of-bounds fallback message missing!"

    print("\n[SUCCESS] ALL RAG ENGINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_rag_system()
