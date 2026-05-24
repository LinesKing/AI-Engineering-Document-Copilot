from __future__ import annotations

import sys
from pathlib import Path

import requests
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_settings, normalize_copilot_mode
from src.services import DocumentCopilotService


st.set_page_config(page_title="AI Engineering Document Copilot", page_icon="AI", layout="wide")


CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #0d1110;
    color: #eef3ed;
}
[data-testid="stSidebar"] {
    background: #111715;
    border-right: 1px solid #27312d;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.ops-header {
    border-bottom: 1px solid #2b3832;
    padding-bottom: 1rem;
    margin-bottom: 1.25rem;
}
.ops-kicker {
    display: inline-block;
    color: #9fe4c5;
    background: #14241d;
    border: 1px solid #315a49;
    border-radius: 6px;
    padding: .35rem .6rem;
    font-size: .86rem;
    text-transform: uppercase;
    letter-spacing: 0;
    font-weight: 800;
    line-height: 1.2;
    margin: .35rem 0 .55rem;
    text-shadow: 0 1px 0 #050807;
}
.ops-title {
    color: #f4fff8;
    font-size: 2.2rem;
    font-weight: 760;
    line-height: 1.05;
    margin: .2rem 0 .35rem;
}
.ops-subtitle {
    color: #aebbb4;
    max-width: 860px;
}
.status-card, .answer-panel, .citation-card {
    background: #151c19;
    border: 1px solid #2b3832;
    border-radius: 8px;
    padding: 1rem;
}
.status-label {
    color: #90a29a;
    font-size: .74rem;
    text-transform: uppercase;
    letter-spacing: .06em;
}
.status-value {
    color: #f6fff9;
    font-size: 1.55rem;
    font-weight: 740;
}
.answer-panel {
    border-left: 4px solid #41d19a;
}
.citation-card {
    margin-bottom: .6rem;
}
.confidence-HIGH { color: #41d19a; font-weight: 800; }
.confidence-MEDIUM { color: #f0c75e; font-weight: 800; }
.confidence-LOW { color: #ff7d6e; font-weight: 800; }
div.stButton > button {
    background: #41d19a;
    color: #07110d;
    border: 0;
    border-radius: 6px;
    font-weight: 760;
}
div.stButton > button:hover {
    background: #66e5b4;
    color: #07110d;
}
</style>
"""


def _api_get(path: str) -> dict[str, object]:
    settings = get_settings()
    response = requests.get(f"{settings.api_base_url}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def _api_post(path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    settings = get_settings()
    response = requests.post(f"{settings.api_base_url}{path}", json=payload or {}, timeout=30)
    response.raise_for_status()
    return response.json()


@st.cache_resource
def _direct_service() -> DocumentCopilotService:
    service = DocumentCopilotService()
    service.ensure_demo_ready()
    return service


def get_health(mode: str) -> dict[str, object]:
    if mode == "api":
        return _api_get("/health")
    return _direct_service().health()


def ingest(mode: str) -> dict[str, object]:
    if mode == "api":
        return _api_post("/ingest")
    _direct_service.clear()
    service = _direct_service()
    return service.ingest()


def ask(mode: str, question: str, top_k: int) -> dict[str, object]:
    if mode == "api":
        return _api_post("/ask", {"question": question, "top_k": top_k})
    return _direct_service().ask(question=question, top_k=top_k)


def render_metric(label: str, value: object) -> None:
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-label">{label}</div>
            <div class="status-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    settings = get_settings()

    st.sidebar.header("Control Room")
    mode = normalize_copilot_mode(st.sidebar.selectbox("Prediction Mode", ["direct", "api"], index=0 if settings.copilot_mode == "direct" else 1))
    top_k = st.sidebar.slider("Retrieved Context", min_value=2, max_value=8, value=4)
    if st.sidebar.button("Rebuild Index"):
        with st.spinner("Re-indexing engineering manuals..."):
            result = ingest(mode)
        st.sidebar.success(f"Indexed {result['chunk_count']} chunks")

    st.markdown(
        """
        <div class="ops-header">
            <div class="ops-kicker">Maintenance Intelligence Workspace</div>
            <div class="ops-title">AI Engineering Document Copilot</div>
            <div class="ops-subtitle">
                Ask grounded questions across equipment manuals, retrieve cited maintenance context,
                and turn long engineering documents into operational next steps.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        health = get_health(mode)
    except Exception as exc:
        st.error(f"Unable to reach copilot service in {mode} mode: {exc}")
        st.stop()

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric("System", str(health["status"]).upper())
    with metric_cols[1]:
        render_metric("Documents", health["document_count"])
    with metric_cols[2]:
        render_metric("Chunks", health["chunk_count"])
    with metric_cols[3]:
        render_metric("LLM Provider", str(health["llm_provider"]).upper())

    st.divider()
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.subheader("Ask the Manual Set")
        question = st.text_area(
            "Maintenance question",
            value="What should I check when a compressor bearing temperature alarm occurs?",
            height=120,
        )
        run_query = st.button("Generate Grounded Answer", use_container_width=True)

        if run_query:
            with st.spinner("Retrieving relevant maintenance context..."):
                result = ask(mode, question, top_k)
            st.session_state["last_result"] = result

        result = st.session_state.get("last_result")
        if result:
            confidence = str(result["confidence"])
            st.markdown(
                f"""
                <div class="answer-panel">
                    <div class="status-label">Grounded Answer</div>
                    <p>{result["answer"]}</p>
                    <p>Confidence: <span class="confidence-{confidence}">{confidence}</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("#### Maintenance Actions")
            for action in result["maintenance_actions"]:
                st.markdown(f"- {action}")
        else:
            st.info("Run a question to retrieve cited maintenance guidance.")

    with right:
        st.subheader("Citations")
        result = st.session_state.get("last_result")
        if result and result["citations"]:
            for citation in result["citations"]:
                st.markdown(
                    f"""
                    <div class="citation-card">
                        <strong>{citation["source"]}</strong><br>
                        Section: {citation["section"]} | Ref: {citation["page"]}<br>
                        Retrieval score: {citation["score"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with st.expander("Retrieved Context"):
                for context in result["retrieved_context"]:
                    st.caption(f"{context['source']} / {context['section']}")
                    st.write(context["text"])
        else:
            st.caption("Citations appear after a question is answered.")

    st.divider()
    st.caption(
        f"Mode: {mode} | Documents: {health['document_source_path']} | Vector store: {health['vector_store_path']}"
    )


if __name__ == "__main__":
    main()
