import re
import math
import logging

logger = logging.getLogger("Jarvis.Agent.RAGMemory")

class RAGMemory:
    """
    RAGMemory implements a local lexical vector retrieval engine in pure Python.
    Calculates TF-IDF vector relevance scores between user speech queries
    and stored facts, reminders, notes, and past conversation logs.
    """
    def __init__(self):
        pass

    @staticmethod
    def _tokenize(text: str) -> list:
        """Helper to lowercase, remove punctuation, and return word tokens."""
        text_clean = text.lower().strip()
        tokens = re.findall(r"\b\w{3,}\b", text_clean)  # words with at least 3 chars
        return tokens

    def retrieve(self, query: str, document_list: list, top_n: int = 3) -> list:
        """
        Retrieves the top N most relevant documents from document_list matching the query.
        Uses a dynamic term-frequency/cosine overlap score.
        """
        if not document_list or not query:
            return []
            
        query_tokens = self._tokenize(query)
        if not query_tokens:
            # Fallback to simple substring match if query was too short/untokenized
            substring_matches = []
            for doc in document_list:
                if query.lower().strip() in doc.lower():
                    substring_matches.append((doc, 1.0))
            substring_matches.sort(key=lambda x: x[1], reverse=True)
            return [item[0] for item in substring_matches[:top_n]]

        # Compute document frequencies (DF) for TF-IDF calculations
        doc_tokens_list = [self._tokenize(doc) for doc in document_list]
        num_docs = len(document_list)
        
        # Calculate Term Frequency (TF) for the query
        query_tf = {}
        for token in query_tokens:
            query_tf[token] = query_tf.get(token, 0) + 1
            
        scored_docs = []
        for idx, doc in enumerate(document_list):
            doc_tokens = doc_tokens_list[idx]
            if not doc_tokens:
                continue
                
            # Calculate Term Frequency (TF) for the document
            doc_tf = {}
            for token in doc_tokens:
                doc_tf[token] = doc_tf.get(token, 0) + 1
                
            # Compute Dot Product of term overlaps
            dot_product = 0.0
            query_magnitude = sum(count ** 2 for count in query_tf.values())
            doc_magnitude = sum(count ** 2 for count in doc_tf.values())
            
            for token in query_tf:
                if token in doc_tf:
                    # TF matching score (simple cosine similarity of frequencies)
                    dot_product += query_tf[token] * doc_tf[token]
                    
            if doc_magnitude > 0 and query_magnitude > 0:
                score = dot_product / (math.sqrt(query_magnitude) * math.sqrt(doc_magnitude))
            else:
                score = 0.0
                
            # Give a small boost if the document contains exact phrase match
            if query.lower() in doc.lower():
                score += 0.2
                
            if score > 0.0:
                scored_docs.append((doc, score))
                
        # Sort documents by highest score first
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        retrieved = [item[0] for item in scored_docs[:top_n]]
        
        logger.info(f"RAG retrieved {len(retrieved)} memories matching query '{query}': {retrieved}")
        return retrieved
