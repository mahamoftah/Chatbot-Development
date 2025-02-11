import os
import uuid
from fastapi import APIRouter, File, Request, UploadFile, HTTPException


files_router  = APIRouter(prefix="/api",tags=['api'])

@files_router.post("/upload-documents", )
async def upload_document(request: Request, files: list[UploadFile] = File(...)):
    """Uploads multiple PDF documents and extracts their text."""
    
    file_urls, error_messages = await request.app.file_uploader.upload_files(files)

    metadata = [{"id": str(uuid.uuid4()), "filename": os.path.basename(file_url)} for file_url in file_urls]

    if not file_urls:
        raise HTTPException(status_code=400, detail="No valid PDF files uploaded. " + " ".join(error_messages))
    
    extracted_texts = await request.app.text_extractor.extract(file_urls)

    documents_with_embeddings = await request.app.rag.text_to_embeddings(extracted_texts, metadata)
    await request.app.rag.embeddings_to_vectordb(documents_with_embeddings)
