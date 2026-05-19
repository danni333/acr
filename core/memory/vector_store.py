import chromadb
from chromadb.utils import embedding_functions
import os

class SemanticVectorStore:
    """Vector storage for high-level concept retrieval (Semantic Memory)."""
    def __init__(self, path: str = "/home/tob/acr/workspace/vector_db"):
        if not os.path.exists(path):
            os.makedirs(path)
        
        self.client = chromadb.PersistentClient(path=path)
        # Using a simple local embedding function for research-grade independence
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="acr_semantic_memory",
            embedding_function=self.embedding_fn
        )

    async def store_concept(self, concept_id: str, text: str, metadata: dict = None):
        """Stores a semantic concept with its embedding."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[concept_id]
        )

    async def query_concepts(self, query_text: str, n_results: int = 5):
        """Retrieves similar concepts based on text similarity."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
