import os
import re
import io

class DocumentLoader:
    def __init__(self):
        self.has_pypdf = False
        try:
            import pypdf
            self.pypdf = pypdf
            self.has_pypdf = True
        except ImportError:
            self.has_pypdf = False

    def detect_category(self, filename, text):
        name_lower = filename.lower()
        text_lower = text[:500].lower() if text else ""
        
        if "attendance" in name_lower or "attendance" in text_lower:
            return "Attendance Policy"
        elif "exam" in name_lower or "evaluat" in name_lower or "assessment" in text_lower:
            return "Examination Guidelines"
        elif "handbook" in name_lower or "conduct" in name_lower or "ragging" in text_lower:
            return "Student Handbook"
        elif "regulat" in name_lower or "academic" in name_lower or "r22" in name_lower:
            return "Academic Regulations"
        else:
            return "General University Document"

    def clean_text(self, text):
        if not text:
            return ""
        text = re.sub(r'VFSTR\s+[a-z0-9]+\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_section_title(self, text):
        match = re.search(r'^\s*([0-9]+\.?[0-9]*\s+[A-Z\s]{4,40})', text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "General Section"

    def load_pdf_from_bytes(self, pdf_bytes, filename):
        pages_data = []
        doc_id = filename.lower().replace(".pdf", "").replace(" ", "_")
        
        if self.has_pypdf:
            reader = self.pypdf.PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                raw_text = page.extract_text() or ""
                cleaned = self.clean_text(raw_text)
                cat = self.detect_category(filename, cleaned)
                sec = self.extract_section_title(cleaned)
                
                pages_data.append({
                    "doc_id": doc_id,
                    "doc_name": filename,
                    "page_number": page_num,
                    "total_pages": total_pages,
                    "category": cat,
                    "section": sec,
                    "raw_text": raw_text,
                    "cleaned_text": cleaned
                })
        else:
            # Simple text extractor fallback for PDF bytes
            text_content = pdf_bytes.decode('utf-8', errors='ignore')
            clean_text = self.clean_text(text_content)
            pages_data.append({
                "doc_id": doc_id,
                "doc_name": filename,
                "page_number": 1,
                "total_pages": 1,
                "category": self.detect_category(filename, clean_text),
                "section": "Document Content",
                "raw_text": text_content,
                "cleaned_text": clean_text
            })
            
        return pages_data

    def load_pdf_from_path(self, file_path):
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            return self.load_pdf_from_bytes(f.read(), filename)

    def load_multiple_pdfs(self, file_paths):
        all_pages = []
        for path in file_paths:
            all_pages.extend(self.load_pdf_from_path(path))
        return all_pages
