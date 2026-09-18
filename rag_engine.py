import os
import re

class RAGEngine:
    def __init__(self, vector_store, embedding_engine, similarity_threshold=0.15):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.similarity_threshold = similarity_threshold

    def answer_query(self, query, top_k=4, doc_filter=None, category_filter=None, min_page=None, max_page=None, gemini_api_key=None):
        if self.vector_store.total_count() == 0:
            return {
                "answer": "No university documents have been indexed yet. Please upload PDF documents to ask questions.",
                "is_grounded": False,
                "max_score": 0.0,
                "citations": [],
                "retrieved_chunks": []
            }

        # 1. Embed user query
        query_vec = self.embedding_engine.embed_query(query)
        
        # 2. Retrieve top-k chunks with metadata filtering
        retrieved_results = self.vector_store.search(
            query_vector=query_vec,
            top_k=top_k,
            doc_filter=doc_filter,
            category_filter=category_filter,
            min_page=min_page,
            max_page=max_page
        )

        if not retrieved_results:
            return {
                "answer": "I cannot find the answer in the uploaded university documents matching your filter criteria.",
                "is_grounded": False,
                "max_score": 0.0,
                "citations": [],
                "retrieved_chunks": []
            }

        max_score = retrieved_results[0]["score"]
        
        # 3. Anti-Hallucination Threshold Check
        if max_score < self.similarity_threshold:
            return {
                "answer": (
                    "I cannot find the answer in the uploaded university documents. "
                    "The query does not closely match any official regulation, attendance policy, or examination rule in the knowledge base. "
                    "Please consult the Vice Chancellor's office or upload the relevant handbook."
                ),
                "is_grounded": False,
                "max_score": max_score,
                "citations": [],
                "retrieved_chunks": retrieved_results
            }

        # 4. Generate Grounded Answer & Build Citations
        context_passages = []
        citations = []
        
        for idx, item in enumerate(retrieved_results):
            c = item["chunk"]
            score_pct = item["similarity_pct"]
            ref_str = f"[{idx+1}] Doc: {c['doc_name']} (Page {c['page_number']}) - {c['category']}"
            context_passages.append(f"{ref_str}\nContent: {c['text']}")
            
            citations.append({
                "citation_id": idx + 1,
                "doc_name": c["doc_name"],
                "page_number": c["page_number"],
                "category": c["category"],
                "section": c.get("section", "General"),
                "similarity_pct": round(score_pct, 1),
                "raw_text": c["text"]
            })

        context_block = "\n\n".join(context_passages)

        # Attempt Gemini API Generation if key provided
        answer_text = None
        api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        
        if api_key:
            try:
                answer_text = self._generate_with_gemini(query, context_block, api_key)
            except Exception as e:
                print(f"Gemini API invocation error: {e}. Falling back to extractive grounded synthesizer.")

        if not answer_text:
            answer_text = self._extractive_grounded_synthesizer(query, retrieved_results)

        return {
            "answer": answer_text,
            "is_grounded": True,
            "max_score": max_score,
            "max_confidence_pct": round(retrieved_results[0]["similarity_pct"], 1),
            "citations": citations,
            "retrieved_chunks": retrieved_results
        }

    def _generate_with_gemini(self, query, context_block, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""You are an official University Academic Regulations Assistant. Answer the user's question accurately, professionally, and strictly grounded ONLY on the retrieved contexts below.

RULES:
1. Rely ONLY on the clear facts directly mentioned in the context.
2. Cite the exact document name, section, and page number for key rules, attendance numbers, credits, or grade points.
3. If the context does not contain sufficient details to answer the query fully, state clearly what is found and what is not available.

Context:
{context_block}

User Question: {query}

Answer:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()

    def _extractive_grounded_synthesizer(self, query, retrieved_results):
        top_item = retrieved_results[0]
        top_chunk = top_item["chunk"]
        
        query_words = set(re.findall(r'\w+', query.lower())) - {"what", "is", "the", "for", "in", "of", "and", "to", "a", "an", "are", "how", "does", "do", "get", "gets"}
        
        matching_sentences = []
        for res in retrieved_results:
            c = res["chunk"]
            sentences = re.split(r'(?<=[.!?])\s+|\n+', c["text"])
            for sent in sentences:
                sent_clean = sent.strip()
                if not sent_clean:
                    continue
                sent_words = set(re.findall(r'\w+', sent_clean.lower()))
                overlap = len(query_words.intersection(sent_words))
                if overlap >= 1 or len(matching_sentences) < 2:
                    if sent_clean not in [s[0] for s in matching_sentences]:
                        matching_sentences.append((sent_clean, c["doc_name"], c["page_number"], c["category"]))

        # Build grounded structured response
        response_lines = [
            f"Based on **{top_chunk['doc_name']}** (Page {top_chunk['page_number']} - *{top_chunk['category']}*):\n"
        ]
        
        added_count = 0
        for sent, doc, pg, cat in matching_sentences[:4]:
            if len(sent) > 10:
                response_lines.append(f"• **{sent}** *(Source: {doc}, Page {pg})*")
                added_count += 1
                
        if added_count == 0:
            response_lines.append(f"• {top_chunk['text'][:350]}... *(Source: {top_chunk['doc_name']}, Page {top_chunk['page_number']})*")
            
        return "\n\n".join(response_lines)
