from fastapi import FastAPI
from src.chat.chat import Chat
from src.chat.llm import GoogleGenerativeLLM
from src.config import get_settings
from src.database.chat_history import ChatHistory
from src.file_uploading.file_uploader import FileUploader
from src.rag.embedder import GoogleEmbedding
from src.rag.rag import Rag
from src.rag.text_splitter import RecursiveSplitter
from src.rag.vector_db import QdrantDB
from src.routes.document import files_router
from src.routes.chat import chat_router
from src.routes.index import health_router
from src.text_extraction.text_extractor import TextExtractor
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware



settings = get_settings()

app = FastAPI()

app.file_uploader =  FileUploader()
app.text_extractor = TextExtractor()

app.text_splitter = RecursiveSplitter()
app.embedding_model = GoogleEmbedding()
app.vector_db_client = QdrantDB(app.embedding_model)
app.rag = Rag(app.text_splitter, app.embedding_model, app.vector_db_client)

app.mongo_db_conn = AsyncIOMotorClient(settings.MONGODB_URL)
app.mongo_db_client = app.mongo_db_conn[settings.MONGODB_DATABASE]

app.chat_history_model = ChatHistory(app.mongo_db_client)
app.llm = GoogleGenerativeLLM()
app.chat_service = Chat(app.llm, app.chat_history_model)

app.include_router(health_router)
app.include_router(files_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


