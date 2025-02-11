import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from pymongo import DESCENDING
from typing import List, Dict, Any
from src.config import get_settings


class ChatHistory:
    """A simple chat history storage class using MongoDB."""

    def __init__(self, db_client: AsyncIOMotorClient):
        """Initialize the chat history storage."""
        settings = get_settings()

        self.db = db_client
        self.chat_collection = self.db[settings.MONGODB_COLLECTION]
        self.logger = logging.getLogger(__name__)

    async def save_chat_history(self, question: str, answer: str, timestamp) -> bool:
        """Save a chat question and answer to the database."""
        chat_entry = {"question": question, "answer": answer, "timestamp": timestamp}

        try:
            await self.chat_collection.insert_one(chat_entry)
            return True
        except PyMongoError as e:
            self.logger.error(f"Error saving chat: {e}")
            return False

    async def get_chat_history(self, limit: int = 7) -> List[Dict[str, Any]]:
        """Retrieve the latest chat history (question and answer only)."""
        try:
            print("Before Chat History Retrival")
            cursor = self.chat_collection.find({}).sort("timestamp", DESCENDING).limit(limit)
            print("After Chat History Retrival")
            return await cursor.to_list(length=limit)
        except PyMongoError as e:
            self.logger.error(f"Error retrieving chat history: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving chat history: {e}")
            return []            