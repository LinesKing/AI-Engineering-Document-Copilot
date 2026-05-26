# Interview Q&A

## 1. What is this project?

It is a RAG-style document copilot for engineering maintenance manuals. A user asks a question, the system searches the indexed manuals, and it returns a grounded answer with citations and maintenance actions. The deployed demo uses local TF-IDF retrieval and a rule-based answer formatter by default.

## 2. Is this a trained model?

No. This project does not train a neural network or fine-tune an LLM. It builds a searchable index over documents. The default answer logic formats an answer from retrieved chunks. RAG is the system pattern: retrieve relevant context, then generate or format an answer from that context.

## 3. What documents did you use?

The project uses three synthetic demo manuals: a compressor maintenance manual, a pump overhaul guide, and conveyor troubleshooting notes. They are enough to demonstrate ingestion, retrieval, citations, and answer formatting, but they are not real manufacturer manuals.

## 4. What is the main problem it solves?

It helps users find relevant maintenance guidance faster inside long technical documents. In a real setting, this could reduce time spent searching manuals and improve traceability because the answer points back to source sections.

## 5. Who are the target users?

Maintenance engineers, reliability engineers, operators, and supervisors who need fast access to procedures, alarm response steps, troubleshooting guidance, and restart criteria.

## 6. What is the architecture?

The architecture has a Streamlit dashboard, an optional FastAPI backend, and a shared service layer. The service layer handles document ingestion, retrieval, answer generation, citations, and health checks. This design keeps the core logic out of the UI.

## 7. Why did you use a service layer?

I wanted the retrieval and answer logic to be reusable from both FastAPI and Streamlit. Without a service layer, the Streamlit app could become a script with duplicated logic. The service layer makes it easier to test and easier to replace components later.

## 8. How does document ingestion work?

The loader reads Markdown or text files, splits them by Markdown headings, chunks the section text by word count, and attaches metadata such as source document, section, equipment type, and maintenance category.

## 9. How does retrieval work?

The project uses scikit-learn TF-IDF. Each chunk is converted into a sparse vector. When the user asks a question, the question is vectorized with the same vectorizer and cosine similarity ranks the chunks.

## 10. Why TF-IDF instead of embeddings?

TF-IDF is lightweight, explainable, free, and easy to deploy on Streamlit Cloud. For a small portfolio MVP, that tradeoff is reasonable. The downside is that TF-IDF is lexical, so it can miss semantically similar questions if the wording is different.

## 11. What does `LLM_PROVIDER=demo` mean?

It means the app uses local demo answer formatting instead of calling an external model. It does not mean there is a trained local LLM. A clearer name would be `ANSWER_PROVIDER=demo` or `DemoGroundedAnswerer`.

## 12. Does the project use OpenAI?

Not by default. There is an optional OpenAI provider path in `src/llm/providers.py`, but the deployed demo can run without API keys. If `LLM_PROVIDER=openai` and an API key are configured, retrieved context can be sent to an OpenAI chat model.

## 13. What does the answer generator do in demo mode?

It takes the top retrieved chunks, identifies the leading source and section, uses first sentences from the top chunks, extracts action-like sentences using keywords, and returns an answer with confidence and citations.

## 14. How are citations produced?

Citations come from chunk metadata. Each retrieved chunk includes source document, section name, synthetic page/section reference, and retrieval score. The service returns those fields in the response.

## 15. What is the confidence score?

It is a heuristic based on the top cosine similarity score. It is not a calibrated probability. I would explain it as retrieval confidence, not answer correctness.

## 16. How is this deployed?

The deployed version uses Streamlit Cloud in direct mode. Streamlit loads `DocumentCopilotService` directly and rebuilds the local index if needed. This avoids needing a separate FastAPI host.

## 17. Why have FastAPI if Streamlit can run directly?

FastAPI demonstrates a production-style serving boundary and makes the core logic testable through API endpoints. Streamlit direct mode is mainly a practical deployment choice for free hosting.

## 18. What tests did you add?

Tests cover configuration validation, chunking behavior, metadata preservation, retrieval relevance, service responses with citations, and FastAPI health/ask endpoints.

## 19. What are the biggest limitations?

The biggest limitations are the small synthetic document set, TF-IDF retrieval, no PDF parsing, no real LLM by default, no evaluation dataset, and no access control or audit trail. It is a portfolio MVP, not a production maintenance system.

## 20. How would you improve this in production?

I would add real document ingestion for PDFs, dense embeddings, a vector database, stronger citation mapping, a real LLM provider with strict prompting, user feedback, retrieval evaluation, answer faithfulness checks, authentication, audit logging, and monitoring.

## Beginner-Friendly Explanation

This project is like a smart search assistant for maintenance manuals. It does not memorize the manuals by training a model. It indexes the manuals so it can search them, then builds an answer from the most relevant sections.

## Technical Explanation

The system uses a local RAG pipeline. Documents are chunked and indexed with TF-IDF. Queries are vectorized into the same feature space, ranked by cosine similarity, and passed to an answer provider. The default provider is deterministic demo logic. The optional provider can call OpenAI with retrieved context. The response includes citations and maintenance actions so the user can inspect where the answer came from.

## How I Would Explain the Main Tradeoff

I chose a lightweight retrieval approach because the project needed to be deployable and understandable. TF-IDF is not state of the art, but it makes the architecture clear. The project demonstrates the engineering structure of a RAG application without hiding behind a black-box model.

## How I Would Improve This in Production

In production, I would focus first on document quality and evaluation. Better embeddings help, but the system also needs reliable parsing, page-level citations, permission controls, test questions with expected sources, and monitoring for failed or low-confidence queries. I would also rename the demo provider to avoid confusing it with a real LLM.

