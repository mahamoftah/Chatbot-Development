from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import get_settings

class GoogleEmbedding:
    def __init__(self):
        settings = get_settings()

        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=settings.GOOGLE_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            
        )
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self.embedding_model.embed_documents(documents)

    def embed_query(self, query: str):
        return self.embedding_model.embed_query(query)