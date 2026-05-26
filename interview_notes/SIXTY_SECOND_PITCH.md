# Sixty Second Pitch

## 30-Second Version

I built an AI Engineering Document Copilot for maintenance manuals. It is a RAG-style application where a user asks a technical question, the system searches indexed engineering documents, and it returns a grounded answer with citations and maintenance actions. The demo uses local TF-IDF retrieval and a simple answer formatter by default, so it is honest and deployable without API keys.

## 60-Second Version

This project is a document copilot for engineering maintenance manuals. The problem is that technicians and engineers often need to search through long manuals during equipment issues, and generic chatbot answers are not enough because the answer needs to be traceable.

I built a Streamlit dashboard, a FastAPI backend, and a shared service layer. The service ingests sample manuals, splits them into chunks, builds a local TF-IDF retrieval index, retrieves the most relevant sections for a question, and returns an answer with citations, confidence, and maintenance actions.

The deployed demo runs in Streamlit direct mode, which keeps it simple for free hosting. Locally, it can also run with a FastAPI backend to show a more production-style serving pattern. The main thing I would emphasize is that this is not a trained model. It is a RAG application with local retrieval and a demo answer generator, with an optional OpenAI provider path for a more advanced version.

## 2-Minute Technical Version

I built this as a small production-style RAG system for engineering manuals. The application has three layers: a Streamlit UI, an optional FastAPI API, and a shared `DocumentCopilotService` that owns the core workflow.

The ingestion pipeline reads Markdown/text manuals from `docs/sample_manuals`, splits them by Markdown headings, chunks the text with overlap, and attaches metadata like source, section, equipment type, and maintenance category. The retrieval layer uses scikit-learn's `TfidfVectorizer` with unigrams and bigrams. It persists the vectorizer, sparse matrix, and chunk metadata with `joblib`.

At query time, the question is vectorized with the same TF-IDF model, cosine similarity ranks the chunks, and the top results are passed to an answer provider. In the deployed demo, the provider is deterministic demo logic that formats a grounded answer and extracts maintenance actions from sentences containing words like inspect, check, verify, stop, and restart. There is also an optional OpenAI provider, but I would be clear that the default deployed version does not call a hosted LLM.

I added FastAPI endpoints for health, ask, ingest, and document listing, plus Pydantic schemas for stable request/response contracts. Streamlit Cloud runs in direct mode because it is simpler than hosting a separate API. Tests cover configuration, chunking, metadata, retrieval relevance, service responses, and API smoke behavior.

The main tradeoff is simplicity versus semantic quality. TF-IDF is easy to deploy and explain, but it is not as strong as dense embeddings. In production, I would add PDF parsing, dense embeddings, a vector database, page-level citations, evaluation datasets, user feedback, audit logging, authentication, and monitoring.

## CV Bullet Points

- Built and deployed a RAG-style engineering document copilot using Python, Streamlit, FastAPI, scikit-learn, and Pydantic.
- Implemented document ingestion, chunking, metadata enrichment, local TF-IDF retrieval, cited responses, and maintenance action extraction.
- Designed a reusable service layer used by both the Streamlit dashboard and FastAPI endpoints.
- Added dual execution modes for local API serving and Streamlit Cloud direct deployment.
- Wrote focused tests for configuration, chunking, retrieval relevance, API behavior, and response shape.

## LinkedIn Project Description

I built and deployed an AI Engineering Document Copilot, a RAG-style application for searching maintenance manuals and returning grounded answers with citations.

The project uses Python, Streamlit, FastAPI, scikit-learn, and Pydantic. It ingests sample engineering manuals, chunks the documents, builds a local TF-IDF retrieval index, and returns answer summaries with source sections and maintenance actions.

I designed it as a production-style portfolio project rather than a notebook demo: the core workflow lives in a reusable service layer, the API has typed schemas, the Streamlit app can run in direct deployment mode, and tests cover the key behavior.

Honest scope: the deployed version uses local retrieval and demo answer formatting by default. It is not a trained LLM and does not replace engineering review. In production, I would add dense embeddings, PDF parsing, stronger citation handling, evaluation datasets, user feedback, and monitoring.

## How I Would Improve This in Production

- Replace TF-IDF with dense embeddings for stronger semantic retrieval.
- Add robust PDF parsing with real page-level citations.
- Store documents, chunks, and query history in a database.
- Add authentication and document-level permissions.
- Use a real LLM with strict grounded prompting and refusal behavior.
- Add retrieval and answer quality evaluation.
- Add monitoring for latency, failed queries, low-confidence answers, and provider errors.
- Add user feedback and an audit trail for maintenance-critical answers.

