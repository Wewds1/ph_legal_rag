from __future__ import annotations

import google.generativeai as genai
from engine.config import settings
from engine.prompts import SYSTEM_PROMPT


class Generator:
    def __init__(self):
        if settings.llm_api_key:
            genai.configure(api_key=settings.llm_api_key)
            self.model = genai.GenerativeModel(settings.llm_model)
        else:
            self.model = None

    def answer(self, query: str, cases: list[dict]) -> dict:
        """Generate answer from retrieved cases."""
        if not self.model:
            return {
                "answer": "Legal research system ready. Gemini API key not configured—showing raw case results only.",
                "precedents": cases,
                "disclaimer": "This is legal research only, not legal advice."
            }
        
        context = "\n\n".join([
            f"📋 **{c['title']}**\n🔗 G.R. No.: {c['gr_no']}\n🌐 Source: {c['source_url']}\n\nExcerpt: {c['snippet']}"
            for c in cases
        ])

        prompt = f"""Alright, here's what I found in the case law:

{context}

---

Now, someone asked me: "{query}"

Break it down for them! Explain the cases, use analogies, be funny if you can, and show them how these precedents apply. Make it feel like you're explaining it to a friend, not a law textbook."""

        response = self.model.generate_content(
            f"{SYSTEM_PROMPT}\n\n{prompt}"
        )

        return {
            "answer": response.text,
            "precedents": cases,
            "disclaimer": "This is just research, not legal advice. Talk to an actual lawyer before doing anything based on this!"
        }