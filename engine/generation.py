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
            
        # If no cases found, let LLM just chat/help generally
        if not cases:
            prompt = f'User asked: "{query}"\n\nNo specific cases matched, but help them out with what you know!'
            response = self.model.generate_content(
                f"{SYSTEM_PROMPT}\n\n{prompt}"
            )
            return {
                "answer": response.text,
                "precedents": [],
                "disclaimer": "This is just research, not legal advice—talk to an actual lawyer before doing anything based on this!"
            }
        
        # If cases found, provide context but keep it concise
        context = "\n\n".join([
            f"📋 **{c['title']}**\n🔗 G.R. No.: {c['gr_no']}\n🌐 {c['source_url']}\n\n{c['snippet']}"
            for c in cases
        ])

        prompt = f"""Found these cases:
        
    

{context}

---

User asked: "{query}"

Explain how these cases relate to their question. Keep it short and conversational."""

        response = self.model.generate_content(
            f"{SYSTEM_PROMPT}\n\n{prompt}"
        )

        return {
            "answer": response.text,
            "precedents": cases,
            "disclaimer": "This is just research, not legal advice—talk to an actual lawyer before doing anything based on this!"
        }
        
        
    def answer_with_context(self, query: str, cases: list[dict], history: list[dict]) -> dict:
        """Generate answer with conversation context"""
        if not self.model:
            return {
                "answer": "Legal research system ready. Gemini API key not configured.",
                "precedents": cases,
                "disclaimer": "research only, not legal advice fr."
            }
        
        if not cases:
            # No cases found - use LLM knowledge only
            prompt = f'User asked: "{query}"\n\nNo matching cases found, but help them with what you know about Philippine law. Keep it short and casual.'
            
            response = self.model.generate_content(f"{SYSTEM_PROMPT}\n\n{prompt}")
            return {
                "answer": response.text,
                "precedents": [],
                "disclaimer": "research only, not legal advice fr."
            }
        
        # Build case context
        context = "\n\n".join([
            f"Case: {c['title']}\nG.R. No.: {c['gr_no']}\nURL: {c['source_url']}\nExcerpt: {c['snippet']}"
            for c in cases[:5]  # Limit to top 5 cases
        ])
        
        # Build conversation context
        history_text = ""
        if history:
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in history[-5:]  # Last 5 messages
            ])
            history_text += "\n\n"
        
        # Final prompt
        prompt = f"""{history_text}Found these Philippine cases:

    {context}

    User just asked: "{query}"

    Explain how these cases apply to their question. Keep it short, casual, Gen Z style."""
        
        response = self.model.generate_content(f"{SYSTEM_PROMPT}\n\n{prompt}")
        
        return {
            "answer": response.text,
            "precedents": cases,
            "disclaimer": "research only, not legal advice fr."
        }