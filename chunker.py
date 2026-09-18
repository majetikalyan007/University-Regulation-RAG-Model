import re

class DocumentChunker:
    def __init__(self, chunk_size=600, chunk_overlap=100, strategy="recursive"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

    def recursive_split_text(self, text):
        separators = ["\n\n", "\n", ". ", "; ", ", ", " "]
        
        def _split(text, separators):
            if len(text) <= self.chunk_size:
                return [text]
            if not separators:
                # Fallback to hard split
                return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
            
            sep = separators[0]
            parts = text.split(sep)
            chunks = []
            current = ""
            
            for p in parts:
                item = p + (sep if sep != " " else " ")
                if len(current) + len(item) <= self.chunk_size:
                    current += item
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    if len(item) > self.chunk_size:
                        sub_chunks = _split(item, separators[1:])
                        chunks.extend(sub_chunks)
                        current = ""
                    else:
                        current = item
            if current.strip():
                chunks.append(current.strip())
            return chunks

        raw_chunks = _split(text, separators)
        
        # Apply overlap
        final_chunks = []
        for i, chunk in enumerate(raw_chunks):
            if i > 0 and self.chunk_overlap > 0:
                prev_overlap = raw_chunks[i-1][-self.chunk_overlap:]
                combined = (prev_overlap + " " + chunk).strip()
                final_chunks.append(combined)
            else:
                final_chunks.append(chunk)
                
        return final_chunks

    def sentence_split_text(self, text):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""
        
        for sent in sentences:
            if len(current) + len(sent) + 1 <= self.chunk_size:
                current += (" " if current else "") + sent
            else:
                if current:
                    chunks.append(current)
                current = sent
        if current:
            chunks.append(current)
        return chunks

    def chunk_pages(self, pages_data):
        all_chunks = []
        chunk_global_id = 0
        
        for page in pages_data:
            text = page["cleaned_text"]
            if not text:
                continue
                
            if self.strategy == "recursive":
                text_splits = self.recursive_split_text(text)
            elif self.strategy == "sentence":
                text_splits = self.sentence_split_text(text)
            else:
                # Fixed window
                step = self.chunk_size - self.chunk_overlap
                text_splits = [text[i:i+self.chunk_size] for i in range(0, max(1, len(text)), step)]
                
            for idx, split in enumerate(text_splits):
                if not split.strip():
                    continue
                chunk_global_id += 1
                chunk_meta = {
                    "chunk_id": f"{page['doc_id']}_p{page['page_number']}_c{idx+1}",
                    "global_id": chunk_global_id,
                    "doc_id": page["doc_id"],
                    "doc_name": page["doc_name"],
                    "page_number": page["page_number"],
                    "total_pages": page["total_pages"],
                    "category": page["category"],
                    "section": page["section"],
                    "text": split,
                    "char_count": len(split),
                    "word_count": len(split.split())
                }
                all_chunks.append(chunk_meta)
                
        return all_chunks
