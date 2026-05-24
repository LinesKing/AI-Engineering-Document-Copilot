from __future__ import annotations

from src.config import AppSettings
from src.retrieval.index import RetrievalResult


class DemoGroundedLLM:
    provider_name = "demo"

    def answer(self, question: str, contexts: list[RetrievalResult]) -> dict[str, object]:
        if not contexts:
            return {
                "answer": "No relevant manual context was found. Rebuild the index with engineering manuals before relying on this answer.",
                "maintenance_actions": ["Verify document ingestion", "Check the question against available manuals"],
                "confidence": "LOW",
            }

        leading = contexts[0].chunk
        supporting_sentences = []
        for result in contexts[:3]:
            sentence = result.chunk.text.split(".")[0].strip()
            if sentence:
                supporting_sentences.append(sentence)

        answer = (
            f"For {leading.equipment_type.lower()} documentation, the most relevant guidance is in "
            f"{leading.source}, section '{leading.section}'. "
            f"{' '.join(sentence + '.' for sentence in supporting_sentences)}"
        )
        actions = _extract_actions(contexts)
        confidence = "HIGH" if contexts[0].score >= 0.35 else "MEDIUM" if contexts[0].score >= 0.15 else "LOW"
        return {"answer": answer, "maintenance_actions": actions, "confidence": confidence}


class OpenAILLM:
    provider_name = "openai"

    def __init__(self, settings: AppSettings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        self.settings = settings

    def answer(self, question: str, contexts: list[RetrievalResult]) -> dict[str, object]:
        from openai import OpenAI

        context_text = "\n\n".join(
            f"Source: {result.chunk.source} | Section: {result.chunk.section}\n{result.chunk.text}"
            for result in contexts
        )
        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.chat_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an engineering maintenance copilot. Answer only from the provided context, "
                        "cite source and section names, and include practical maintenance actions."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\n\nContext:\n{context_text}"},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        return {"answer": content, "maintenance_actions": _extract_actions(contexts), "confidence": "MEDIUM"}


def _extract_actions(contexts: list[RetrievalResult]) -> list[str]:
    action_terms = ("inspect", "check", "verify", "replace", "record", "stop", "restart", "confirm")
    actions: list[str] = []
    for result in contexts:
        for sentence in result.chunk.text.split("."):
            clean = sentence.strip()
            if clean and any(term in clean.lower() for term in action_terms):
                actions.append(clean)
            if len(actions) == 4:
                return actions
    return actions or ["Review the cited manual sections before taking maintenance action"]


def build_llm_provider(settings: AppSettings):
    if settings.llm_provider == "openai":
        return OpenAILLM(settings)
    return DemoGroundedLLM()
