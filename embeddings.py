import numpy as np
import re

class EmbeddingEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension = 384
        self.use_st = False
        self.st_model = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.st_model = SentenceTransformer(model_name)
            self.dimension = self.st_model.get_sentence_embedding_dimension()
            self.use_st = True
        except Exception:
            self.use_st = False

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import normalize
        self.TfidfVectorizer = TfidfVectorizer
        self.normalize = normalize
        self.vectorizer = TfidfVectorizer(max_features=384, stop_words='english', token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2))
        self.is_fitted = False

    def fit_corpus(self, text_list):
        if not self.use_st and text_list:
            self.vectorizer.fit(text_list)
            self.is_fitted = True

    def embed_texts(self, text_list, is_query=False):
        if not text_list:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.use_st and self.st_model is not None:
            embeddings = self.st_model.encode(text_list, convert_to_numpy=True, show_progress_bar=False)
            return self.normalize(embeddings, norm='l2', axis=1).astype(np.float32)

        if not is_query or not self.is_fitted:
            self.fit_corpus(text_list)
            
        sparse_matrix = self.vectorizer.transform(text_list).toarray()
        
        if sparse_matrix.shape[1] < self.dimension:
            padded = np.zeros((sparse_matrix.shape[0], self.dimension), dtype=np.float32)
            padded[:, :sparse_matrix.shape[1]] = sparse_matrix
            matrix = padded
        else:
            matrix = sparse_matrix[:, :self.dimension]
            
        return self.normalize(matrix, norm='l2', axis=1).astype(np.float32)

    def embed_query(self, query):
        vecs = self.embed_texts([query], is_query=True)
        return vecs[0]
