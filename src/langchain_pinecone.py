import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LangChainPinecone

# Pinecone and LangChain setup

def init_pinecone(api_key: str, environment: str):
    pinecone.init(api_key=api_key, environment=environment)


def add_documents_to_pinecone(docs: list, index_name: str, openai_api_key: str):
    """Embed and add documents to Pinecone."""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = LangChainPinecone.from_texts(docs, embeddings, index_name=index_name)
    vectorstore.index.upsert(items=vectorstore.docstore._dict.items())
    return None


def query_pinecone(query: str, index_name: str, openai_api_key: str):
    """Query Pinecone for relevant documents."""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = LangChainPinecone(index_name=index_name, embedding=embeddings)
    results = vectorstore.similarity_search(query)
    return results