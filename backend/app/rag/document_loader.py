import os
import csv
import hashlib
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

class DocumentLoader:
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def load_file(file_path: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Loads document content along with page/section level metadata.
        Returns a list of tuples: (text_content, metadata_dict)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(file_path)
        checksum = DocumentLoader.calculate_checksum(file_path)
        upload_time = datetime.now(timezone.utc).isoformat()

        base_meta = {
            "filename": filename,
            "file_size": file_size,
            "checksum": checksum,
            "document_type": ext.replace(".", ""),
            "upload_timestamp": upload_time,
        }

        results: List[Tuple[str, Dict[str, Any]]] = []

        if ext == ".pdf":
            if pypdf is None:
                raise ImportError("pypdf is required to process PDF files")
            reader = pypdf.PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                clean_text = " ".join(text.split())
                if clean_text:
                    meta = dict(base_meta)
                    meta["page_number"] = page_num
                    meta["total_pages"] = len(reader.pages)
                    results.append((clean_text, meta))

        elif ext == ".docx":
            if docx is None:
                raise ImportError("python-docx is required to process DOCX files")
            doc = docx.Document(file_path)
            full_text = []
            for p in doc.paragraphs:
                if p.text.strip():
                    full_text.append(p.text.strip())
            content = "\n\n".join(full_text)
            meta = dict(base_meta)
            meta["page_number"] = 1
            results.append((content, meta))

        elif ext == ".csv":
            with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                rows_text = []
                if headers:
                    rows_text.append(f"Columns: {', '.join(headers)}")
                for row_idx, row in enumerate(reader, start=1):
                    rows_text.append(f"Row {row_idx}: {', '.join(row)}")
            content = "\n".join(rows_text)
            meta = dict(base_meta)
            meta["page_number"] = 1
            meta["row_count"] = len(rows_text)
            results.append((content, meta))

        elif ext in [".txt", ".md", ".json"]:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            meta = dict(base_meta)
            meta["page_number"] = 1
            results.append((content, meta))

        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        return results
