import os
import shutil
from fastapi import UploadFile
from src.config import get_settings


class FileUploader:
    def __init__(self):
        settings = get_settings()
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def upload_files(self, files: list[UploadFile]):
        error_messages = []
        pdf_files = []
        
        for file in files:
            if not file.filename.endswith(".pdf"):
                error_messages.append(f"{file.filename} is not a PDF file")
            else:
                file_path = os.path.join(self.upload_dir, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                pdf_files.append(file_path)
        
        return pdf_files, error_messages