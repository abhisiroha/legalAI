# LegalAI

LegalAI helps companies generate terms of service, GDPR, and custom legal policies using AI.

## Features
- Ingest a company’s existing website and documents
- Generate new policy documents or edit existing ones
- Q&A over legal documents

## Tech Stack
- FastAPI
- LangChain
- Pinecone
- PDF parser
- Google Docs API

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI app:
   ```bash
   uvicorn main:app --reload
   ```
3. Access the API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Endpoints
- `/ingest`: Ingest website and documents
- `/generate-policy`: Generate a new policy
- `/edit-policy`: Edit an existing policy
- `/qa`: Q&A over legal documents
