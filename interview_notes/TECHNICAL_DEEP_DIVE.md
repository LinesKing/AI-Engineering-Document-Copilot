# Technical Deep Dive

## Important Files and Their Roles

### `app/dashboard.py`

Streamlit frontend for the deployed app. It handles:

- page layout and styling
- local/API mode selection
- system health cards
- question input
- answer display
- citations and retrieved context

It is intentionally a thin UI layer. It calls `DocumentCopilotService` directly in deployed mode or calls FastAPI in API mode.

### `api/main.py`

FastAPI application. It exposes health, ask, ingest, and document listing endpoints. It uses `lru_cache` to keep one service instance alive per process so the index is not repeatedly loaded.

### `api/schemas.py`

Pydantic schemas for request and response validation. These schemas make the API contract explicit:

- `AskRequest`
- `AskResponse`
- `HealthResponse`
- `IngestResponse`

### `src/config.py`

Central configuration module. It defines paths, validates modes, and reads settings from environment variables or Streamlit secrets.

Important settings:

- `COPILOT_MODE=api|direct`
- `LLM_PROVIDER=demo|openai`
- `VECTOR_STORE_PATH`
- `DOCUMENT_SOURCE_PATH`
- `OPENAI_API_KEY`
- `CHAT_MODEL`

### `src/documents/loader.py`

Loads Markdown and text documents, splits them by headings, chunks section text, and attaches metadata. This is where raw documents become searchable chunks.

### `src/documents/demo.py`

Creates synthetic demo manuals for compressors, pumps, and conveyors if the default document folder is empty.

### `src/retrieval/index.py`

Builds and searches the local TF-IDF index. It uses:

- `TfidfVectorizer`
- cosine similarity
- `joblib` persistence

### `src/llm/providers.py`

Defines the answer provider layer.

`DemoGroundedLLM` is a poorly named but useful demo formatter. It is not a real LLM. It creates answers from retrieved text and extracts action sentences using keyword matching.

`OpenAILLM` is an optional provider that can call an OpenAI chat model when credentials are configured.

### `src/services/document_copilot.py`

Main orchestration service. This is the most important file to explain in an interview. It coordinates:

- demo document creation
- indexing
- index loading
- retrieval
- answer provider selection
- response formatting
- health checks

### `tests/`

Focused tests covering:

- mode validation
- document chunking
- metadata preservation
- retrieval relevance
- service response shape
- FastAPI health and ask endpoints

## How the RAG Pipeline Works

This project does not train a model. It builds a retrieval index over documents.

The pipeline is:

```text
Manuals
-> split by Markdown headings
-> chunk text
-> attach metadata
-> build TF-IDF index
-> user asks a question
-> rank chunks by cosine similarity
-> create answer from top chunks
-> return answer with citations and actions
```

## How Recommendations Work

The maintenance actions are not produced by a trained recommendation model. They are extracted from retrieved document chunks using practical action keywords:

```text
inspect, check, verify, replace, record, stop, restart, confirm
```

This gives the demo useful maintenance-style output, but it is not a production recommender.

## Key Algorithms and Logic

### Section Splitting

The loader uses Markdown headings as section boundaries. This is simple and works for the demo documents, but production manuals would need stronger parsing for PDFs, tables, figures, and scanned pages.

### Chunking

Text is split by word count with overlap:

- default max chunk size: 120 words
- default overlap: 24 words

Overlap helps preserve context when a relevant statement crosses chunk boundaries.

### TF-IDF Retrieval

The retriever uses `TfidfVectorizer` with:

- English stop words
- unigrams and bigrams
- cosine similarity

This is lightweight and deployable, but it mainly matches lexical similarity. It may miss semantically similar questions that use different wording.

### Confidence

Confidence is based on the top retrieval score:

- high if score >= 0.35
- medium if score >= 0.15
- low otherwise

This is a heuristic retrieval confidence, not a calibrated model probability.

### Demo Answer Generation

The demo provider takes the leading chunk and first sentences from top retrieved chunks. It formats a grounded answer and returns extracted actions.

This is honest demo behavior. It avoids pretending to have a real LLM when running without API keys.

## Important Engineering Decisions

### 1. Separate Service Layer

The project avoids putting retrieval logic directly in Streamlit. This makes the same logic reusable from FastAPI, Streamlit, tests, and scripts.

### 2. Dual Mode Deployment

`COPILOT_MODE=api` supports local backend development. `COPILOT_MODE=direct` supports Streamlit Cloud deployment without needing a separate backend host.

### 3. Local-First Retrieval

TF-IDF was chosen because it is simple, fast, explainable, and easy to deploy. For a portfolio MVP, this avoids binary vector database issues and API cost.

### 4. Honest Demo Provider

The default provider does not call an external model. This keeps the project deployable without secrets and avoids misleading users about model capability.

### 5. Persisted Index

The index is persisted with `joblib`, but generated index artifacts are ignored by Git. The app can rebuild the index from committed demo documents.

### 6. Safe Settings Loading

Settings read from environment variables first and Streamlit secrets second. Missing Streamlit secrets are handled safely so local runs do not crash.

## Limitations

- The document set is synthetic and small.
- The default answer provider is not a real LLM.
- Retrieval is lexical, not semantic.
- There is no PDF parser.
- There is no page-level citation from original PDFs.
- There is no authentication or user-level document access control.
- No production monitoring, feedback loop, or hallucination evaluation exists.
- OpenAI mode is present, but not deeply tested with real production manuals.
- Confidence is heuristic and not statistically calibrated.

## How I Would Improve This in Production

1. Replace or supplement TF-IDF with dense embeddings.
2. Use a vector database such as Chroma, FAISS, pgvector, or a managed vector store.
3. Add PDF ingestion with page numbers, tables, and OCR for scanned manuals.
4. Add a proper retrieval evaluation set with expected source sections.
5. Add answer evaluation for faithfulness and citation correctness.
6. Add user feedback buttons and store question/answer traces.
7. Add role-based access control for document collections.
8. Add audit logging for maintenance-critical answers.
9. Add prompt templates with stricter refusal behavior when context is weak.
10. Add observability: latency, retrieval scores, failed queries, and provider errors.
11. Add CI/CD checks and deployment smoke tests.
12. Rename `DemoGroundedLLM` to `DemoGroundedAnswerer` to avoid implying a real LLM.

## What I Personally Should Be Able to Explain

- RAG is an architecture pattern, not a trained model.
- This project indexes documents and retrieves relevant chunks.
- TF-IDF is simple lexical retrieval, not deep semantic embedding.
- The demo provider formats answers from retrieved chunks.
- The optional OpenAI provider would generate better natural-language answers, but only after retrieval provides context.
- Citations matter because they make the answer auditable.
- The service layer is what makes the project more production-style than a notebook.

