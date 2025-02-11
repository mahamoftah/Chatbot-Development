import re
from typing import List
from fastapi import HTTPException, status
from langchain_community.document_loaders import PyMuPDFLoader


class TextExtractor:
    def __init__(self):
        pass

    async def extract(self, files_urls: List[str]):
        self.files_urls = files_urls
        
        files_content = []
        for file_url in files_urls:
            content = await self.load_pdf(file_url)
            proccessed_content = await self.process(content)
            files_content.append(proccessed_content)

        return files_content

    async def load_pdf(self, file_url):
        try:
            loader = PyMuPDFLoader(file_url)
            row_data = ""
            for doc in loader.load():
                row_data += doc.page_content + "\n"
            return row_data
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error in processing pdf File: {e}")
    

    async def process(self, row_data):
        processed_data = re.sub(r' +', ' ', row_data)
        processed_data = re.sub(r'\n\s*\n', '\n', processed_data).strip()

        return processed_data