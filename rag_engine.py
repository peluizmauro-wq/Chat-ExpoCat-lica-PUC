from pathlib import Path
import re
import hashlib

class RAGEngine:
    def __init__(self, docs_dir, persist_dir):
        self.docs_dir = Path(docs_dir)
        self.persist_dir = Path(persist_dir)
        self.backend = None
        self.collection = None
        self._fallback_docs = []
        self._fallback_matrix = None
        self._fallback_vectorizer = None
        self._initialize()

    @staticmethod
    def _chunk(text, max_chars=1100, overlap=180):
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = []
        current = ""
        for p in paragraphs:
            if not current:
                current = p
            elif len(current) + len(p) + 2 <= max_chars:
                current += "\n\n" + p
            else:
                chunks.append(current)
                tail = current[-overlap:] if overlap and len(current) > overlap else current
                current = tail + "\n\n" + p
        if current:
            chunks.append(current)
        return chunks

    def _load_chunks(self):
        items = []
        for path in sorted(self.docs_dir.glob("*.txt")):
            text = path.read_text(encoding="utf-8")
            for i, chunk in enumerate(self._chunk(text)):
                items.append({
                    "id": hashlib.md5(f"{path.name}:{i}:{chunk}".encode("utf-8")).hexdigest(),
                    "text": chunk,
                    "source": path.name,
                    "chunk": i,
                })
        return items

    def _initialize(self):
        items = self._load_chunks()
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self.persist_dir.mkdir(parents=True, exist_ok=True)
            embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.collection = client.get_or_create_collection(
                name="expocatolica_2026",
                embedding_function=embedder,
                metadata={"hnsw:space": "cosine"},
            )
            existing = set(self.collection.get(include=[])["ids"]) if self.collection.count() else set()
            new_items = [x for x in items if x["id"] not in existing]
            if new_items:
                self.collection.add(
                    ids=[x["id"] for x in new_items],
                    documents=[x["text"] for x in new_items],
                    metadatas=[{"source": x["source"], "chunk": x["chunk"]} for x in new_items],
                )
            self.backend = "ChromaDB + SentenceTransformers"
        except Exception:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._fallback_docs = items
            self._fallback_vectorizer = TfidfVectorizer(
                strip_accents="unicode", lowercase=True, ngram_range=(1, 2)
            )
            self._fallback_matrix = self._fallback_vectorizer.fit_transform(
                [x["text"] for x in items]
            )
            self.backend = "TF-IDF local (fallback compatível)"

    def search(self, query, k=4):
        if self.collection is not None:
            result = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )
            out = []
            for doc, meta, dist in zip(
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
            ):
                out.append({
                    "text": doc,
                    "source": meta.get("source", "documento"),
                    "score": round(1 - float(dist), 4),
                })
            return out

        from sklearn.metrics.pairwise import cosine_similarity
        qv = self._fallback_vectorizer.transform([query])
        scores = cosine_similarity(qv, self._fallback_matrix).flatten()
        order = scores.argsort()[::-1][:k]
        return [
            {
                "text": self._fallback_docs[i]["text"],
                "source": self._fallback_docs[i]["source"],
                "score": round(float(scores[i]), 4),
            }
            for i in order
        ]
