from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.tools.base import BaseTool

class GenerateReportTool(BaseTool):
    name = "generate_report"
    description = (
        "Generates a formal, structured executive report from gathered agent results. "
        "Formats executive summaries, empirical evidence, policy citations, actions taken, "
        "and clear recommendations into an audited document."
    )
    category = "reporting"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Report title (e.g. 'Customer Refund Eligibility Audit - Order #1024')."
                },
                "summary": {
                    "type": "string",
                    "description": "Executive summary of the situation and findings."
                },
                "evidence": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of factual evidence gathered from database and calculations."
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of formal document citations and policy references."
                },
                "actions_performed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tools and verification steps performed."
                },
                "recommendation": {
                    "type": "string",
                    "description": "Actionable decision or recommendation."
                }
            },
            "required": ["title", "summary", "recommendation"]
        }

    def run(
        self, 
        title: str, 
        summary: str, 
        recommendation: str,
        evidence: Optional[List[str]] = None, 
        sources: Optional[List[str]] = None, 
        actions_performed: Optional[List[str]] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        evidence = evidence or []
        sources = sources or []
        actions_performed = actions_performed or []

        markdown_report = f"""# {title}
**Generated:** {now_str}

## Executive Summary
{summary}

## Key Evidence & Findings
"""
        for item in evidence:
            markdown_report += f"- {item}\n"
        if not evidence:
            markdown_report += "- No specific numerical evidence recorded.\n"

        markdown_report += "\n## Policy & Knowledge Sources\n"
        for src in sources:
            markdown_report += f"- {src}\n"
        if not sources:
            markdown_report += "- Direct internal policy verification.\n"

        markdown_report += "\n## Actions Executed\n"
        for act in actions_performed:
            markdown_report += f"- {act}\n"
        if not actions_performed:
            markdown_report += "- Automated agent workflow execution.\n"

        markdown_report += f"""
## Final Recommendation & Next Steps
{recommendation}
"""
        return {
            "success": True,
            "report_title": title,
            "timestamp": now_str,
            "summary": summary,
            "evidence": evidence,
            "sources": sources,
            "actions_performed": actions_performed,
            "recommendation": recommendation,
            "markdown": markdown_report
        }

generate_report_tool = GenerateReportTool()
