from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from src.utils import scrape_website, parse_pdf, fetch_google_doc
from src.langchain_pinecone import init_pinecone, add_documents_to_pinecone, query_pinecone
from src.google_auth import get_google_credentials
import tempfile
import shutil
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import os
from tempfile import NamedTemporaryFile
from src.utils import parse_pdf
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

app = FastAPI()

@app.post("/ingest")
def ingest(company_url: str = Form(...), files: Optional[List[UploadFile]] = None):
    """
    Ingest a company's website and uploaded documents.
    """
    # Example: Scrape website
    website_text = scrape_website(company_url)
    # Example: Parse uploaded files (PDFs)
    docs_text = []
    if files:
        for file in files:
            # Save uploaded file to a temporary location and parse it
            

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
            docs_text.append(parse_pdf(tmp_path))
    # Add website_text and docs_text to Pinecone
    # Combine all texts into a list of documents
    all_docs = []
    if website_text and not website_text.startswith("Error"):
        all_docs.append(website_text)
    for doc in docs_text:
        if doc and not doc.startswith("Error"):
            all_docs.append(doc)
    if all_docs:
        # Initialize Pinecone (you may want to move this to app startup in production)
        # Replace with your actual Pinecone API key and environment
        pinecone_api_key = "YOUR_PINECONE_API_KEY"
        pinecone_env = "YOUR_PINECONE_ENVIRONMENT"
        openai_api_key = "YOUR_OPENAI_API_KEY"
        index_name = "company-docs"
        init_pinecone(pinecone_api_key, pinecone_env)
        add_documents_to_pinecone(all_docs, index_name, openai_api_key)
    return {"message": "Ingestion started", "company_url": company_url, "files": [f.filename for f in files] if files else []}

@app.post("/generate-policy")
def generate_policy(company_name: str = Form(...), policy_type: str = Form(...), custom_requirements: Optional[str] = Form(None)):
    """
    Generate a new policy document (e.g., ToS, GDPR, custom).
    """
    # Integrate with LangChain and Pinecone for policy generation

    # Set up Pinecone and OpenAI API keys (replace with your actual keys or load from env)
    pinecone_api_key = "YOUR_PINECONE_API_KEY"
    pinecone_env = "YOUR_PINECONE_ENVIRONMENT"
    openai_api_key = "YOUR_OPENAI_API_KEY"
    index_name = "company-docs"

    # Initialize Pinecone (optional: move to app startup)
    init_pinecone(pinecone_api_key, pinecone_env)

    # Compose the prompt for the LLM
    prompt = (
        f"You are a legal AI assistant. Generate a {policy_type} policy for the company '{company_name}'."
    )
    if custom_requirements:
        prompt += f" The policy must meet these additional requirements: {custom_requirements}"

    # Retrieve relevant company documents from Pinecone using LangChain
    retrieved_docs = query_pinecone(
        query=f"{policy_type} policy for {company_name}",
        index_name=index_name,
        openai_api_key=openai_api_key
    )

    # Combine retrieved docs into context for the LLM
    context = ""
    if retrieved_docs:
        context = "\n\n".join([doc.page_content for doc in retrieved_docs if hasattr(doc, "page_content")])

    # Use OpenAI LLM via LangChain to generate the policy
    

    llm = OpenAI(openai_api_key=openai_api_key, temperature=0.2, max_tokens=2048)

    # Create a prompt template
    template = (
        "Context:\n{context}\n\n"
        "Instructions:\n{prompt}\n\n"
        "Policy:\n"
    )
    prompt_template = PromptTemplate(
        input_variables=["context", "prompt"],
        template=template
    )

    full_prompt = prompt_template.format(context=context, prompt=prompt)
    policy_text = llm(full_prompt)

    return {
        "message": f"Policy generation completed for {company_name} ({policy_type})",
        "policy": policy_text
    }

@app.post("/edit-policy")
def edit_policy(policy_file: UploadFile = File(...), edits: str = Form(...)):
    """
    Edit an existing policy document.
    """
    

    # Save uploaded file to a temporary location
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(policy_file.filename)[-1]) as tmp:
        tmp.write(policy_file.file.read())
        tmp_path = tmp.name

    # Determine file type and extract text
    if policy_file.filename.lower().endswith(".pdf"):
        original_text = parse_pdf(tmp_path)
    else:
        # For simplicity, treat as plain text
        with open(tmp_path, "r", encoding="utf-8") as f:
            original_text = f.read()

    # Clean up temp file
    os.remove(tmp_path)

    # Compose prompt for LLM to apply edits
    prompt_template = PromptTemplate(
        input_variables=["document", "edits"],
        template=(
            "You are a legal AI assistant. Here is the original policy document:\n\n"
            "{document}\n\n"
            "Apply the following edits or changes to the document:\n"
            "{edits}\n\n"
            "Return the revised policy document."
        )
    )
    prompt = prompt_template.format(document=original_text, edits=edits)

    # Call LLM to generate the edited policy
    llm = OpenAI(temperature=0.2, max_tokens=2048)
    edited_policy = llm(prompt)

    return {
        "message": f"Edit completed for {policy_file.filename}",
        "edited_policy": edited_policy
    }

@app.post("/qa")
def qa_over_documents(question: str = Form(...), files: Optional[List[UploadFile]] = None):
    """
    Q&A over uploaded legal documents.
    """
    # If files are provided, parse and ingest them into Pinecone for retrieval
    docs_text = []
    if files:
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
                tmp.write(file.file.read())
                tmp_path = tmp.name
            # Determine file type and extract text
            if file.filename.lower().endswith(".pdf"):
                doc_text = parse_pdf(tmp_path)
            else:
                with open(tmp_path, "r", encoding="utf-8") as f:
                    doc_text = f.read()
            docs_text.append(doc_text)
            os.remove(tmp_path)
    # Add parsed docs to Pinecone if any
    if docs_text:
        pinecone_api_key = "YOUR_PINECONE_API_KEY"
        pinecone_env = "YOUR_PINECONE_ENVIRONMENT"
        openai_api_key = "YOUR_OPENAI_API_KEY"
        index_name = "company-docs"
        init_pinecone(pinecone_api_key, pinecone_env)
        add_documents_to_pinecone(docs_text, index_name, openai_api_key)

    # Query Pinecone for relevant context
    pinecone_api_key = "YOUR_PINECONE_API_KEY"
    pinecone_env = "YOUR_PINECONE_ENVIRONMENT"
    openai_api_key = "YOUR_OPENAI_API_KEY"
    index_name = "company-docs"
    init_pinecone(pinecone_api_key, pinecone_env)
    relevant_docs = query_pinecone(question, index_name, openai_api_key)
    # Concatenate retrieved docs for context
    context = "\n\n".join([doc.page_content if hasattr(doc, "page_content") else str(doc) for doc in relevant_docs])

    # Compose prompt for LLM
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a legal AI assistant. Use the following context from legal documents to answer the user's question.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer as accurately and concisely as possible."
        )
    )
    prompt = prompt_template.format(context=context, question=question)

    # Call LLM to generate the answer
    llm = OpenAI(temperature=0.2, max_tokens=512)
    answer = llm(prompt)

    return {"answer": answer}