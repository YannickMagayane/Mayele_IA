"""
Vector Database Engine for ChromaDB and Gemini Embedding 2 Integration.

This module manages local vector store persistence using ChromaDB and generates
1536-dimensional semantic embeddings via Google Gemini Embedding 2 (with a fallback
vector generator for offline/unconfigured environments).

:Example:

>>> from analyzer.vector_engine import VectorEngine
>>> engine = VectorEngine()
>>> engine.add_document("Offre d'emploi ingénieur Glencore KCC Kolwezi", {"source": "ONEM"}, "doc_1")
>>> results = engine.query_similarity("Recrutement minier Kolwezi")
>>> print(len(results))
1
"""

import os
import logging
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    import google.genai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class VectorEngine:
    """
    Interface for ChromaDB vector store and Gemini Embedding 2 vectorization.

    :param collection_name: Name of ChromaDB collection (default: 'rdc_knowledge').
    :type collection_name: str
    """

    EMBEDDING_DIMENSION = 1536

    def __init__(self, collection_name: str = "rdc_knowledge"):
        """
        Initialize VectorEngine with ChromaDB persistent storage path.

        :param collection_name: Collection identifier.
        :type collection_name: str
        :returns: None
        :rtype: None

        :Example:

        >>> engine = VectorEngine("rdc_test")
        """
        self.collection_name = collection_name
        self.persist_dir = str(getattr(settings, "CHROMA_DB_DIR", "./chroma_db_store"))
        os.makedirs(self.persist_dir, exist_ok=True)

        if HAS_CHROMADB:
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.client = None
            self.collection = None
            logger.warning("ChromaDB is not installed. Vector storage will run in in-memory fallback mode.")

        # In-memory storage fallback if ChromaDB is missing
        self._fallback_docs = []

    def generate_embedding(self, text: str) -> list:
        """
        Generate 1536-dimensional embedding using gemini-embedding-2 or fallback vector.

        :param text: Text string to vectorize.
        :type text: str
        :returns: 1536-element float list embedding.
        :rtype: list

        :Example:

        >>> engine = VectorEngine()
        >>> vector = engine.generate_embedding("Code Minier RDC 2026")
        >>> len(vector)
        1536
        """
        api_key = getattr(settings, "GEMINI_API_KEY_PRO", "")
        if HAS_GENAI and api_key and api_key != "your_gemini_api_key_pro_here":
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=text
                )
                if hasattr(response, "embedding") and response.embedding:
                    return response.embedding.values
            except Exception as exc:
                logger.error(f"Error calling Gemini Embedding 2 API: {exc}. Using fallback vector.")

        # Deterministic fallback embedding generation based on text hash
        seed = abs(hash(text)) % (2**32)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.EMBEDDING_DIMENSION)
        norm_vec = vec / np.linalg.norm(vec)
        return norm_vec.tolist()

    def add_document(self, content: str, metadata: dict, doc_id: str) -> bool:
        """
        Ingest a document chunk into ChromaDB collection.

        :param content: Document text content.
        :type content: str
        :param metadata: Document metadata dictionary (source, url, date, etc.).
        :type metadata: dict
        :param doc_id: Unique document identifier.
        :type doc_id: str
        :returns: True if successful, False otherwise.
        :rtype: bool

        :Example:

        >>> engine = VectorEngine()
        >>> engine.add_document("Glencore KCC recrute à Kolwezi", {"territory": "Kolwezi"}, "id_101")
        True
        """
        embedding = self.generate_embedding(content)
        if self.collection:
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        else:
            self._fallback_docs.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata,
                "embedding": embedding
            })
            return True

    def query_similarity(self, query_text: str, n_results: int = 5) -> list:
        """
        Perform cosine similarity vector search over ingested knowledge documents.

        :param query_text: Natural language user query.
        :type query_text: str
        :param n_results: Number of nearest matches to return.
        :type n_results: int
        :returns: List of dict objects containing content, metadata, and distance.
        :rtype: list

        :Example:

        >>> engine = VectorEngine()
        >>> results = engine.query_similarity("recrutement Kolwezi", n_results=3)
        """
        query_vec = self.generate_embedding(query_text)
        results = []

        if self.collection and self.collection.count() > 0:
            res = self.collection.query(
                query_embeddings=[query_vec],
                n_results=min(n_results, self.collection.count())
            )
            if res and res.get("documents"):
                docs = res["documents"][0]
                metas = res["metadatas"][0] if res.get("metadatas") else [{}] * len(docs)
                ids = res["ids"][0] if res.get("ids") else [""] * len(docs)
                distances = res["distances"][0] if res.get("distances") else [0.0] * len(docs)

                for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                    results.append({
                        "id": doc_id,
                        "content": doc,
                        "metadata": meta,
                        "distance": dist,
                        "similarity_score": round(1.0 - (dist if dist < 1.0 else 0.5), 3)
                    })
            return results

        # Fallback linear search over stored fallback docs
        if self._fallback_docs:
            q_arr = np.array(query_vec)
            scores = []
            for item in self._fallback_docs:
                d_arr = np.array(item["embedding"])
                sim = float(np.dot(q_arr, d_arr))
                scores.append((sim, item))
            scores.sort(key=lambda x: x[0], reverse=True)
            for sim, item in scores[:n_results]:
                results.append({
                    "id": item["id"],
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "similarity_score": round(sim, 3)
                })

        return results

    similarity_search = query_similarity
