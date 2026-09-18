import numpy as np

class FAISSVectorStore:
    def __init__(self, dimension=384, metric="cosine"):
        self.dimension = dimension
        self.metric = metric
        self.index = None
        self.chunks_metadata = []
        self.use_faiss = False
        self.embeddings_matrix = None
        
        try:
            import faiss
            self.faiss = faiss
            self.use_faiss = True
            self._init_faiss_index()
        except ImportError:
            print("Notice: faiss library not found. Falling back to high-performance NumPy matrix vector search.")
            self.use_faiss = False

    def _init_faiss_index(self):
        if self.use_faiss:
            if self.metric in ["cosine", "inner_product"]:
                self.index = self.faiss.IndexFlatIP(self.dimension)
            else:
                self.index = self.faiss.IndexFlatL2(self.dimension)

    def add_embeddings(self, embeddings, chunks):
        if len(embeddings) == 0:
            return
        if embeddings.shape[1] != self.dimension:
            self.dimension = embeddings.shape[1]
            if self.use_faiss:
                self._init_faiss_index()

        vecs = np.ascontiguousarray(embeddings, dtype=np.float32)
        
        if self.use_faiss and self.index is not None:
            self.index.add(vecs)
        else:
            if self.embeddings_matrix is None:
                self.embeddings_matrix = vecs
            else:
                self.embeddings_matrix = np.vstack([self.embeddings_matrix, vecs])
                
        self.chunks_metadata.extend(chunks)

    def total_count(self):
        if self.use_faiss and self.index is not None:
            return self.index.ntotal
        elif self.embeddings_matrix is not None:
            return len(self.embeddings_matrix)
        return 0

    def get_all_categories(self):
        return sorted(list(set(c["category"] for c in self.chunks_metadata if "category" in c)))

    def get_all_doc_names(self):
        return sorted(list(set(c["doc_name"] for c in self.chunks_metadata if "doc_name" in c)))

    def search(self, query_vector, top_k=5, doc_filter=None, category_filter=None, min_page=None, max_page=None):
        if self.total_count() == 0:
            return []

        query_vec = np.ascontiguousarray(query_vector, dtype=np.float32)

        if self.use_faiss and self.index is not None:
            query_arr = np.ascontiguousarray([query_vec], dtype=np.float32)
            candidate_k = min(self.total_count(), max(top_k * 5, 50))
            distances, indices = self.index.search(query_arr, candidate_k)
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.chunks_metadata):
                    continue
                chunk = self.chunks_metadata[idx]
                if self._apply_filters(chunk, doc_filter, category_filter, min_page, max_page):
                    score = float(dist)
                    if self.metric == "l2":
                        score = 1.0 / (1.0 + float(dist))
                    results.append({
                        "score": score,
                        "similarity_pct": max(0.0, min(100.0, score * 100.0)),
                        "chunk": chunk
                    })
                    if len(results) >= top_k:
                        break
            return results
        else:
            # NumPy Dot Product / Cosine Similarity Matrix Search
            if self.metric == "l2":
                dists = np.linalg.norm(self.embeddings_matrix - query_vec, axis=1)
                scores = 1.0 / (1.0 + dists)
            else:
                # Dot product of normalized vectors = Cosine Similarity
                scores = np.dot(self.embeddings_matrix, query_vec)
                
            sorted_indices = np.argsort(scores)[::-1]
            results = []
            
            for idx in sorted_indices:
                chunk = self.chunks_metadata[idx]
                if self._apply_filters(chunk, doc_filter, category_filter, min_page, max_page):
                    score = float(scores[idx])
                    results.append({
                        "score": score,
                        "similarity_pct": max(0.0, min(100.0, score * 100.0)),
                        "chunk": chunk
                    })
                    if len(results) >= top_k:
                        break
            return results

    def _apply_filters(self, chunk, doc_filter, category_filter, min_page, max_page):
        if doc_filter and doc_filter != "All Documents" and chunk.get("doc_name") != doc_filter:
            return False
        if category_filter and category_filter != "All Categories" and chunk.get("category") != category_filter:
            return False
        page_num = chunk.get("page_number", 0)
        if min_page is not None and page_num < min_page:
            return False
        if max_page is not None and page_num > max_page:
            return False
        return True

    def clear(self):
        if self.use_faiss:
            self._init_faiss_index()
        self.embeddings_matrix = None
        self.chunks_metadata = []
