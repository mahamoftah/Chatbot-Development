import logging
from typing import List, Optional, Dict, Any


class Rag:
    def __init__(self, text_splitter, embedding_model, vector_db_client):
        self.text_splitter = text_splitter
        self.embedding_model = embedding_model
        self.vector_db_client = vector_db_client


    async def text_to_embeddings(
        self,
        documents: List[str] = [],
        metadatas: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Saves text chunks to the vector database with embeddings.
        """
        if not documents:
            logging.error("No documents provided.")
            return {"status": "error", "message": "No documents provided."}

        if metadatas and len(metadatas) != len(documents):
            logging.error("Mismatch between documents and metadata lengths.")
            return {"status": "error", "message": "Mismatch between documents and metadata lengths."}

        try:
                        
            # Split documents into chunks
            split_documents = self.text_splitter.split_documents(documents, metadatas)
            
            # Add chunk order to metadata
            updated_split_documents = []
            for doc_index, (original_doc, original_metadata) in enumerate(zip(documents, metadatas)):
                chunked_docs = [
                    (chunk_index, doc) for chunk_index, doc in enumerate(split_documents) 
                    if doc.metadata['id'] == original_metadata['id']
                ]
                for chunk_index, chunked_doc in chunked_docs:
                    chunked_doc.metadata['chunk_order'] = chunk_index + 1  
                    updated_split_documents.append(chunked_doc)
            
            # Extract updated page contents and metadata
            page_contents = [doc.page_content for doc in updated_split_documents]
            metadatas = [doc.metadata for doc in updated_split_documents]
            

            embeddings = self.embedding_model.embed_documents(page_contents)

            # Prepare documents for insertion
            documents_with_embeddings = [
                {"text": text, "embedding": embedding, "metadata": metadata}
                for text, embedding, metadata in zip(page_contents, embeddings, metadatas or [{}]*len(page_contents))
            ]
            return documents_with_embeddings
        

        except ValueError as ve:
            logging.error(f"Value error: {ve}")
            return {"status": "error", "message": f"Invalid input: {ve}"}
        except ConnectionError as ce:
            logging.error(f"Database connection error: {ce}")
            return {"status": "error", "message": "Database connection failed."}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "error", "message": "Failed to save text chunks to vector database."}




    async def embeddings_to_vectordb(self, documents_with_embeddings: List[Dict[str, Any]]) -> None:
        try:
            batch_size = 5

            for i in range(0, len(documents_with_embeddings), batch_size):
                batch = documents_with_embeddings[i:i + batch_size]
                try:
                    self.vector_db_client.add_documents(batch)
                except Exception as e:
                    logging.error(f"Error adding batch: {e}")
           
            logging.info("Documents successfully added to the vector database.")

        except ValueError as ve:
            logging.error(f"Value error: {ve}")
            return {"status": "error", "message": f"Invalid input: {ve}"}
        except ConnectionError as ce:
            logging.error(f"Database connection error: {ce}")
            return {"status": "error", "message": "Database connection failed."}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "error", "message": "Failed to save text chunks to vector database."}


    async def query_vectordb(
        self, 
        query: str, 
        k: int = 5
    ) -> Dict[str, Any]:
            """
            Queries the vector database for similar documents.
            """
            if not query:
                logging.error("Query is empty.")
                return {"status": "error", "message": "Query cannot be empty."}
            
            try:
                results = self.vector_db_client.search_similar(query, k)

                documents = [] 
                scores = []
                document_ids = []
                filenames = []

                for result in results:
                    documents.append(result['document'])
                    scores.append(result['score'])
                    document_ids.append(result['metadata']['id'])
                    filenames.append(result['metadata']['filename'])

                return {"status": "success", "documents": documents , "scores":scores, "document_ids":document_ids, "filenames":filenames}

            except ValueError as ve:
                logging.error(f"Value error: {ve}")
                return {"status": "error", "message": f"Invalid input: {ve}"}
            except ConnectionError as ce:
                logging.error(f"Database connection error: {ce}")
                return {"status": "error", "message": "Database connection failed."}
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                return {"status": "error", "message": "Failed to query vector database."}
