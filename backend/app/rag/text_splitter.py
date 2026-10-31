from typing import List, Dict, Any
import re
import uuid

class RecursiveTextSplitter:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100, separators: List[str] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        chunks = []
        # Split recursively using separator hierarchy
        current_splits = [text]
        for sep in self.separators:
            next_splits = []
            for s in current_splits:
                if len(s) > self.chunk_size:
                    if sep == "":
                        # Hard character split
                        for i in range(0, len(s), self.chunk_size - self.chunk_overlap):
                            next_splits.append(s[i:i + self.chunk_size])
                    else:
                        parts = s.split(sep)
                        next_splits.extend([p for p in parts if p.strip()])
                else:
                    next_splits.append(s)
            current_splits = next_splits

        # Merge small chunks to satisfy chunk_size with overlap
        merged_chunks = []
        current_chunk = ""
        for piece in current_splits:
            piece = piece.strip()
            if not piece:
                continue
            if len(current_chunk) + len(piece) + 1 <= self.chunk_size:
                current_chunk = f"{current_chunk} {piece}".strip()
            else:
                if current_chunk:
                    merged_chunks.append(current_chunk)
                # Apply overlap from end of previous chunk if possible
                if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                    overlap_prefix = current_chunk[-self.chunk_overlap:]
                    current_chunk = f"{overlap_prefix} {piece}".strip()
                else:
                    current_chunk = piece
        if current_chunk:
            merged_chunks.append(current_chunk)

        return merged_chunks

    def create_chunks_with_metadata(
        self, 
        text: str, 
        base_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        raw_chunks = self.split_text(text)
        result = []
        for idx, chunk_content in enumerate(raw_chunks):
            chunk_meta = dict(base_metadata)
            chunk_meta["chunk_id"] = f"{base_metadata.get('document_id', 'doc')}_{idx}"
            chunk_meta["chunk_index"] = idx
            result.append({
                "chunk_id": chunk_meta["chunk_id"],
                "content": chunk_content,
                "metadata": chunk_meta
            })
        return result
