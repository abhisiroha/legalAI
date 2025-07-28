import requests
from bs4 import BeautifulSoup
import pdfplumber

# Website scraping

def scrape_website(url: str) -> str:
    """Scrape text content from a website."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract all visible text from the page
        texts = soup.stripped_strings
        content = "\n".join(texts)
        return content
    except Exception as e:
        return f"Error scraping website: {e}"

# PDF parsing

def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error parsing PDF: {e}"

# Google Docs API integration

def fetch_google_doc(doc_id: str, credentials) -> str:
    """Fetch and extract text from a Google Doc."""
    from googleapiclient.discovery import build

    try:
        service = build('docs', 'v1', credentials=credentials)
        doc = service.documents().get(documentId=doc_id).execute()
        content = doc.get('body', {}).get('content', [])
        text = ""
        for element in content:
            if 'paragraph' in element:
                elements = element['paragraph'].get('elements', [])
                for elem in elements:
                    text_run = elem.get('textRun')
                    if text_run and 'content' in text_run:
                        text += text_run['content']
        return text.strip()
    except Exception as e:
        return f"Error fetching Google Doc: {e}"