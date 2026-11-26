import os
import hashlib
from typing import List, Dict, Any, Tuple


class DocumentLoader:
    """Lightweight document utilities for checksums and plain-text/markdown fallback."""

    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    @staticmethod
    def load_plain_text(file_path: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Load plain text, markdown, CSV, or JSON files without heavy PDF/DOCX parsers."""
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if not content.strip():
            return []
        return [(
            content,
            {
                "filename": filename,
                "file_type": ext.lstrip("."),
                "page_number": 1,
                "source_citation": f"[Source: {filename}]",
            },
        )]
