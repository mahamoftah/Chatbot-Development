from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache
# Load .env manually
load_dotenv(".env", override=True)

class Settings(BaseSettings):
    UPLOAD_DIR: str
 
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    QDRANT_COLLECTION_NAME: str
    QDRANT_URL: str
    QDRANT_API_KEY: str

    GOOGLE_EMBEDDING_MODEL: str
    GOOGLE_API_KEY: str

    GOOGLE_GENERATIVE_MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float  

    MONGODB_URL: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION: str

    class Config:
        env_file = ".env"
        override = True
        str_strip_whitespace = True
        validate_assignment = True

@lru_cache()
def get_settings():
    return Settings()