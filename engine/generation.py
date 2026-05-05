from __future__ import annotations

import google.generativeai as genai
from engine.config import settings
from prompts import SYSTEM_PROMPT

class Generator:
    def __init__(self):
        genai.configure(api_key=settings.llm_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)

    def answer(self, query: str, cases: list[dict]) -> dict:
        """Generate answer from retrieved cases."""
        # Build context from cases
        context = "\n\n".join([
            f"Case: {c['title']}\nG.R. No.: {c['gr_no']}\nURL: {c['source_url']}\nExcerpt: {c['snippet']}"
            for c in cases
        ])

        prompt = f"""Based on these Philippine court cases:

{context}

User query: {query}

Provide a brief analysis and cite the relevant precedents."""

        response = self.model.generate_content(
            f"{SYSTEM_PROMPT}\n\n{prompt}"
        )

        return {
            "answer": response.text,
            "precedents": cases,
            "disclaimer": "This is legal research only, not legal advice."
        }