import logging
from typing import List, Dict, Any
import uuid
from langchain.embeddings.base import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    Range
)

from src.config import get_settings


class QdrantDB():
    def __init__(self, embedding_function=None):
        """
        Initializes the QdrantDB with a specified collection name and embedding function.
        """
        settings = get_settings()
        
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.embedding_function = embedding_function
        self.embedding_size = settings.CHUNK_SIZE

        # Initialize the Qdrant client with your cloud API key and cluster details
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

        # Initialize the collection
        self._initialize_collection()


    def _initialize_collection(self):
        """
        Initialize the Qdrant collection if it does not exist.
        """
        try:
            # Check if the collection exists
            collections = self.client.get_collections()
            if not any(c.name == self.collection_name for c in collections.collections):
                logging.info(f"Collection '{self.collection_name}' not found. Creating a new one.")

                # Create the collection with appropriate vector parameters
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_size,
                        distance=Distance.COSINE  # Use the Distance enum
                    )
                )
                logging.info(f"Collection '{self.collection_name}' created successfully.")
            else:
                logging.info(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logging.error(f"Error initializing collection: {e}")
            raise ValueError("Failed to initialize vector database interface.")
        


    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents with embeddings to the Qdrant database.
        """
        try:
            points = []
            for doc in documents:
                text = doc["text"]
                embedding = doc["embedding"]
                document_id = doc.get("metadata", {}).get("id")
                chunk_order = doc.get("metadata", {}).get("chunk_order")

                # Generate a unique ID for each point
                point_id = str(uuid.uuid4())

                # Create the point structure
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=
                    {
                        "document_id": document_id,
                        "text": text,
                        "chunk_order": chunk_order
                    }
                )
                points.append(point)

            # Insert points into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logging.info(f"Successfully added {len(documents)} documents to the database.")

        except Exception as e:
            logging.error(f"Error adding documents: {e}")
            raise



    def search_similar(
        self,
        query_text: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform a similarity search and retrieve additional context around the similar chunks,
        interleaving neighbors by chunk_order proximity.

        Parameters:
        - query_text: The text query to search for.
        - top_k: The number of top results to return.
        - company_id: The company ID to filter by (optional).
        - roles: A list of roles to filter by (optional).

        Returns:
        - A list of dictionaries containing the document, score, and metadata.
        """
        try:
            # Step 1: Convert the query text to an embedding
            query_embedding = self.embedding_function.embed_query(query_text)

            # Ensure the embedding is in the correct format (list of floats)
            query_vector = query_embedding

            # Step 3: Perform the similarity search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )

            # Step 4: Extract unique document IDs and chunk orders from the search results
            chunk_requests = [
                {
                    "id": result.payload["document_id"],
                    "chunk_order": result.payload["chunk_order"],
                    "score": float(result.score)
                }
                for result in search_results
            ]

            # Step 5: Interleave neighbors with top-k chunks
            final_results = []
            for chunk in chunk_requests:
                doc_id = chunk["id"]
                chunk_order = chunk["chunk_order"]
                chunk_score = chunk["score"]

                # Fetch neighbors within the range of -5 to +5
                scrolled_chunks = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="document_id",
                                match=MatchValue(value=doc_id)
                            ),
                            FieldCondition(
                                key="chunk_order",
                                range=Range(
                                    gte=max(1, chunk_order - 2),
                                    lte=chunk_order + 2
                                )
                            )
                        ]
                    ),
                    limit=5  # Fetch at most 11 chunks per similar chunk
                )


                # Interleave neighbors by proximity
                neighbors = sorted(
                    scrolled_chunks[0],  # First element contains the chunks
                    # key=lambda x: abs(x.payload["chunk_order"] - chunk_order)
                    key=lambda x: x.payload["chunk_order"]
                )

                # print(f"Neighbors: {neighbors}")


                # Assign the same score to neighbors and include them with the top-k chunk
                for neighbor in neighbors:
                    neighbor.payload["score"] = chunk_score
                    final_results.append({
                        "document": neighbor.payload["text"],
                        "score": neighbor.payload["score"],
                        "metadata": neighbor.payload
                    })

            return final_results

        except Exception as e:
            logging.error(f"Error during similarity search: {e}")
            return []