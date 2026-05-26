# Project Overview

## One-Sentence Explanation

AI Engineering Document Copilot is a deployed Streamlit and FastAPI RAG-style application that searches engineering maintenance documents and returns grounded answers with citations and practical maintenance actions.

## Problem Solved

Maintenance teams often need to find specific procedures, alarms, restart criteria, and troubleshooting steps inside long manuals. In real operations, this can be slow and error-prone, especially when documents are spread across folders, PDFs, site standards, and equipment manuals.

This project demonstrates a focused version of that problem:

- A user asks a maintenance question.
- The system searches a small document set.
- It returns relevant manual sections, citations, confidence, and action-oriented guidance.

The current project uses synthetic demo manuals for compressors, pumps, and conveyors. It is not connected to real manufacturer documents or live plant systems.

## Target Users

- Maintenance engineers who need fast access to procedures and troubleshooting guidance.
- Reliability engineers who work with equipment history, symptoms, and maintenance standards.
- Operations supervisors who need explainable guidance during equipment events.
- AI/ML engineers evaluating how to structure a small RAG application with a service layer, API, UI, and tests.

## Business and Operational Value

The value is not that the system replaces engineering judgement. The value is that it reduces the time needed to find relevant documentation and makes the answer traceable.

Operationally, a system like this could help with:

- Faster lookup of alarm response steps.
- More consistent use of maintenance standards.
- Better handover between operators, technicians, and engineers.
- Clearer auditability because answers include source documents and sections.
- A safer workflow than a generic chatbot because answers are grounded in retrieved context.

## What I Should Understand for Interviews

- This is a RAG-style application, not a trained model.
- The system builds a searchable local index over documents.
- The default answer generator is demo-level Python logic, not a real LLM.
- The optional OpenAI path exists, but the deployed demo can run without API keys.
- The important engineering work is the architecture: document ingestion, retrieval, service boundary, API, UI, deployment mode, and tests.

## Demo-Level vs Production-Level

Demo-level:

- Uses synthetic Markdown manuals.
- Uses TF-IDF retrieval instead of dense embeddings.
- Uses rule-based answer formatting by default.
- Does not parse PDFs, tables, diagrams, or scanned documents.
- Does not evaluate answer quality with a benchmark set.

Production-style:

- Has a clear service layer in `DocumentCopilotService`.
- Supports local API mode and Streamlit direct mode.
- Uses stable API schemas with Pydantic.
- Persists a retrieval index.
- Has tests for configuration, chunking, retrieval, service responses, and API endpoints.
- Documents environment variables and deployment workflow.

