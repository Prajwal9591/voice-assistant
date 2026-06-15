import os
import json
import numpy as np
import logging

logger = logging.getLogger("Jarvis.RAGSystem")

# Try to import SentenceTransformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("Sentence-Transformers not available. Falling back to high-fidelity pure Python token RAG.")

class RAGSystem:
    """
    Implements a local semantic Vector RAG retrieval system.
    Saves text indices in memory_store/ and semantic embeddings in vector_store/.
    """
    def __init__(self):
        self.text_store_path = r"c:\Users\Prajwal HY\Voice_assistant\memory_store\memories.json"
        self.vector_store_path = r"c:\Users\Prajwal HY\Voice_assistant\vector_store\memories.npy"
        
        # Ensure directories exist
        os.makedirs(r"c:\Users\Prajwal HY\Voice_assistant\memory_store", exist_ok=True)
        os.makedirs(r"c:\Users\Prajwal HY\Voice_assistant\vector_store", exist_ok=True)
        
        self.memories = []
        self.embeddings = None
        self.model = None
        
        # Load existing database
        self.load_database()
        
        # Load embedding model if sentence-transformers is installed
        if HAS_TRANSFORMERS:
            try:
                # Use a small, high-performance local transformer
                logger.info("Initializing SentenceTransformer Model (all-MiniLM-L6-v2)...")
                # Set huggingface offline flag if needed or let it download once
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("SentenceTransformer loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model offline: {e}. Falling back to lexical retrieval.")
                self.model = None

    def load_database(self):
        """Loads text metadata from memory_store and semantic vectors from vector_store."""
        try:
            if os.path.exists(self.text_store_path):
                with open(self.text_store_path, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
                logger.info(f"Loaded {len(self.memories)} documents from local memory store.")
                
            if os.path.exists(self.vector_store_path):
                self.embeddings = np.load(self.vector_store_path, allow_pickle=True)
                logger.info(f"Loaded vector store array with shape: {self.embeddings.shape}")
        except Exception as e:
            logger.error(f"Error loading RAG databases: {e}")

    def save_database(self):
        """Saves current text records and vector embeddings to disk."""
        try:
            with open(self.text_store_path, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
                
            if self.embeddings is not None:
                np.save(self.vector_store_path, self.embeddings)
            logger.debug("RAG databases successfully persisted to disk.")
        except Exception as e:
            logger.error(f"Error saving RAG databases: {e}")

    def add_memory(self, text: str, category: str = "fact"):
        """
        Adds a new record, computes its semantic embedding,
        and saves both the text metadata and vectors.
        """
        text_clean = text.strip()
        if not text_clean:
            return
            
        # Avoid duplicate documents
        if any(m["text"].lower() == text_clean.lower() for m in self.memories):
            return
            
        logger.info(f"Adding memory record to local RAG: [{category}] '{text_clean}'")
        self.memories.append({
            "text": text_clean,
            "category": category
        })
        
        # Calculate and update embeddings
        if self.model is not None:
            try:
                new_vector = self.model.encode([text_clean])[0]
                if self.embeddings is None:
                    self.embeddings = np.array([new_vector])
                else:
                    self.embeddings = np.vstack([self.embeddings, new_vector])
            except Exception as e:
                logger.error(f"Failed to calculate transformer embedding: {e}")
        
        self.save_database()

    def retrieve(self, query: str, top_n: int = 3) -> list:
        """
        Queries the vector store using Cosine Similarity.
        If offline or transformer is unavailable, falls back to dynamic lexical TF-IDF.
        """
        if not self.memories or not query:
            return []
            
        # 1. SEMANTIC VECTOR RETRIEVAL (SENTENCE EMBEDDINGS)
        if self.model is not None and self.embeddings is not None:
            try:
                query_vector = self.model.encode([query])[0]
                
                # Compute Cosine Similarities
                dot_products = np.dot(self.embeddings, query_vector)
                norm_embeddings = np.linalg.norm(self.embeddings, axis=1)
                norm_query = np.linalg.norm(query_vector)
                
                # Protect against zero division
                scores = np.zeros(len(self.memories))
                mask = (norm_embeddings > 0) & (norm_query > 0)
                scores[mask] = dot_products[mask] / (norm_embeddings[mask] * norm_query)
                
                # Sort by scores
                top_indices = np.argsort(scores)[::-1][:top_n]
                retrieved = []
                for idx in top_indices:
                    if scores[idx] > 0.15: # confidence threshold
                        retrieved.append(self.memories[idx]["text"])
                        
                logger.info(f"Transformer RAG retrieved {len(retrieved)} memories for query '{query}': {retrieved}")
                if retrieved:
                    return retrieved
            except Exception as e:
                logger.error(f"Transformer cosine similarity check failed: {e}. Falling back to lexical retrieval.")
                
        # 2. LEXICAL TF-IDF FALLBACK (DYNAMIC LEXICAL VECTOR ENGINE)
        query_words = set(query.lower().split())
        scored_memories = []
        
        for m in self.memories:
            text = m["text"]
            text_words = text.lower().split()
            overlap = len(query_words.intersection(text_words))
            if overlap > 0:
                # Basic overlap ratio score
                score = overlap / (np.sqrt(len(query_words)) * np.sqrt(len(text_words)))
                scored_memories.append((text, score))
                
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        retrieved = [item[0] for item in scored_memories[:top_n]]
        
        logger.info(f"Lexical RAG retrieved {len(retrieved)} memories for query '{query}': {retrieved}")
        return retrieved
