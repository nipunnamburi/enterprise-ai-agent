from typing import Dict, Any, Optional
from app.tools.base import BaseTool
from app.rag.vector_store import vector_store

class SearchDocumentsTool(BaseTool):
    name = "search_documents"
    description = (
        "Performs semantic similarity search across the enterprise knowledge base in Chroma. "
        "Returns relevant document text chunks, source citations (filename, page number), and relevance scores. "
        "Use this tool to find policies, employee handbooks, product documentation, SLAs, and technical manuals."
    )
    category = "knowledge_retrieval"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Semantic search query describing the information needed."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top relevant chunks to retrieve (default: 4).",
                    "default": 4
                },
                "document_filter": {
                    "type": "string",
                    "description": "Optional specific filename to filter by (e.g. 'refund_policy.pdf')."
                }
            },
            "required": ["query"]
        }

    def run(self, query: str, top_k: int = 4, document_filter: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        filter_metadata = None
        if document_filter:
            filter_metadata = {"filename": document_filter}

        results = vector_store.search(query=query, top_k=top_k, filter_metadata=filter_metadata)

        if not results:
            return {
                "success": True,
                "query": query,
                "found_count": 0,
                "results": [],
                "message": "No matching documents found in knowledge base."
            }

        citations = [r["source_citation"] for r in results]
        return {
            "success": True,
            "query": query,
            "found_count": len(results),
            "results": results,
            "citations": list(set(citations)),
            "summary_context": "\n\n".join([
                f"--- {r['source_citation']} (Score: {r['similarity_score']}) ---\n{r['content']}"
                for r in results
            ])
        }

search_documents_tool = SearchDocumentsTool()
