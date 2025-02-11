from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Optional
from langchain.schema import Document
from src.config import get_settings

class RecursiveSplitter:
    def __init__(self):
        settings = get_settings()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def split_documents(self, documents: List[str], metadatas: Optional[List[dict]] = None) -> List[Document]:
        return self.text_splitter.create_documents(documents, metadatas)