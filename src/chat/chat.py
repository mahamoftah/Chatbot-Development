import logging
from typing import Any, List, Dict, Tuple, Optional
from datetime import datetime, timezone

class Chat:
    """A Chat manager that interacts with an LLM and stores chat history."""

    def __init__(self, llm, chat_history_manager):
        """
        Initializes the Chat system.

        Args:
            llm (object): A language model instance (e.g., ChatGoogleGenerativeAI).
            chat_history_manager (object): Manages storage and retrieval of chat history.
        """
        self.llm = llm
        self.chat_history_manager = chat_history_manager
        self.logger = logging.getLogger(__name__)


    async def generate_chat_response(self, query: str, context) -> Tuple[str, str]:
        """
        Generates a response from the LLM based on user input and past chat history.

        Args:
            query (str): User's question.

        Returns:
            Tuple[str, str]: The LLM response and timestamp.
        """
        print(f"Query in Chat Class: {query}")

        if not query.strip():
            return "Do you have any specific question?", self._current_timestamp()
        
        context = self._prepare_context(context)
        chat_history = await self.retrieve_chat_history()
        print(f"Chat Histoty: {chat_history}")

        system_prompt = self._construct_prompt(context, chat_history)
        messages = self._format_messages(system_prompt, query)

        try:
            response = self.llm.generate_response(messages)
            if not response.strip():
                response = "I'm sorry, but I couldn't generate a response at this time."
        except Exception as e:
            self.logger.error(f"LLM Error: {e}")
            response = "There was an issue generating a response. Please try again."
        print(f"LLM Response: {response}")

        timestamp = self._current_timestamp()
        await self.chat_history_manager.save_chat_history(query, response, timestamp)
        
        print(f"QA Saved Successfully")
        return response, timestamp


    async def retrieve_chat_history(self, limit: int = 7) -> List[Dict[str, str]]:
        """
        Retrieves past chat history.

        Args:
            limit (int): Number of messages to retrieve.

        Returns:
            List[Dict[str, str]]: Chat history containing questions and answers.
        """
        print(f"Limit: {limit}")
        return await self.chat_history_manager.get_chat_history(limit)
    

    def _prepare_context(self, search_results: list[dict]) -> dict:
        """Prepare and format retrieved document chunks and their scores."""
        try:
            documents = []
            scores = []

            # Extract document texts and scores
            for result in search_results:
                documents.append(result.get("document", ""))
                scores.append(result.get("score", 0.0))

            # Track unique documents while preserving order
            seen = {}
            unique_indices = []
            for i, doc in enumerate(documents):
                if doc not in seen:
                    seen[doc] = i
                    unique_indices.append(i)

            # Filter using unique indices
            unique_documents = [documents[i] for i in unique_indices]
            unique_scores = [scores[i] for i in unique_indices]

            return {
                "documents": [{"content": doc} for doc in unique_documents],
                "scores": unique_scores
            }
        
        except Exception as e:
            self.logger.error(f"Error in preparing context: {str(e)}")
            return {
                "documents": [],
                "scores": []
            }




    def _construct_prompt(self, context, chat_history: List[Dict[str, str]]) -> str:
        """
        Constructs a system prompt using recent chat history.

        Args:
            chat_history (List[Dict[str, str]]): Previous chat messages.

        Returns:
            str: Formatted system prompt.
        """
        prompt = "You are an AI assistant. Provide concise and accurate answers. Keep responses **concise and to the point**.\n\n"

        documents = context.get("documents", [])
        scores = context.get("scores", [])

        if not documents or not scores:
            prompt += "Relevant documents: \nNo relevant documents found.\n" 
        elif max(scores, default=0.0) < 0.1:
            prompt += "Notes on Documents: given context is weakly relevant to the question ,\n" + \
                    "Relevant documents:\n" + "\n".join(f"[{i+1}] {doc['content']}" for i, doc in enumerate(documents)).strip()
        else:
            prompt += "Relevant documents:\n" + "\n".join(f"[{i+1}] {doc['content']}" for i, doc in enumerate(documents)).strip()

        if chat_history:
            prompt += "\nRecent chat history:\n"
            for chat in chat_history:
                prompt += f"- User: {chat['question']}"
                prompt += f"- AI: {chat['answer']}\n\n"
            prompt += "\n"

        return prompt.strip()


    def _format_messages(self, system_prompt: str, query: str) -> List[Dict[str, str]]:
        """
        Formats messages for LLM processing.

        Args:
            system_prompt (str): System-generated context.
            query (str): User query.

        Returns:
            List[Dict[str, str]]: Structured messages.
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

    @staticmethod
    def _current_timestamp():
        """Returns the current timestamp in UTC."""
        return datetime.now(timezone.utc).isoformat()
