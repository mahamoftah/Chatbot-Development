from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Tuple
from src.chat.chat import Chat

chat_router = APIRouter(prefix="/api/chat",tags=['api', 'chat'])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    chat_history: List[Dict[str, str]]



@chat_router.post("/ask", response_model=ChatResponse)
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    """
    Handles user queries and generates AI responses.

    Args:
        chat_request (ChatRequest): User input query.
        chat_service (Chat): Chat instance for processing.

    Returns:
        ChatResponse: AI-generated response with timestamp.
    """
    try:
        print("User Query: ", chat_request.query)
        print("Query Type: ", type(chat_request.query))

        context = request.app.vector_db_client.search_similar(chat_request.query)
        # print("Context: ", context)
        response, timestamp = await request.app.chat_service.generate_chat_response(chat_request.query, context)

        return ChatResponse(response=response, timestamp=timestamp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@chat_router.get("/history", response_model=ChatHistoryResponse)
async def chat_history_endpoint(request: Request):
    """
    Retrieves past chat history.

    Args:
        limit (int): Number of messages to retrieve (default: 10).
        chat_service (Chat): Chat instance for history retrieval.

    Returns:
        ChatHistoryResponse: List of previous chat messages.
    """
    try:
        chat_history = await request.app.chat_service.retrieve_chat_history()
        return ChatHistoryResponse(chat_history=chat_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")
