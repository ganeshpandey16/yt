import os
import uuid
from typing import List, Dict, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer


class MarkdownVectorStore:
    def __init__(
        self,
        qdrant_url: str,
        qdrant_api_key: str,
        collection_name: str,
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=60,
        )
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                ),
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="doc_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

    def _load_markdown(self, path: str) -> str:
        if not path.endswith(".md"):
            raise ValueError("Only .md files are supported")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return [
            chunk
            for chunk in splitter.split_text(text)
            if len(chunk.strip()) > 20
        ]

    def ingest_markdown(
        self,
        file_path: str,
        doc_id: Optional[str] = None,
        batch_size: int = 50,
    ) -> Dict[str, int]:
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        raw_text = self._load_markdown(file_path)
        chunks = self._chunk_text(raw_text)
        embeddings = self.embedding_model.encode(chunks).tolist()

        stored = 0
        for i in range(0, len(chunks), batch_size):
            points = []
            for text, vector in zip(
                chunks[i : i + batch_size],
                embeddings[i : i + batch_size],
            ):
                points.append(
                    models.PointStruct(
                        id=uuid.uuid4().int >> 64,
                        vector=vector,
                        payload={
                            "text": text,
                            "doc_id": doc_id,
                        },
                    )
                )
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            stored += len(points)

        return {"doc_id": doc_id, "chunks_stored": stored}

    def query(
        self,
        query_text: str,
        doc_id: Optional[str] = None,
        top_k: int = 4,
    ) -> Dict[str, str]:
        query_vector = self.embedding_model.encode([query_text])[0].tolist()

        query_filter = None
        if doc_id:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="doc_id",
                        match=models.MatchValue(value=doc_id),
                    )
                ]
            )

        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
        )

        context = "\n".join(
            hit.payload["text"] for hit in hits
        )

        return {
            "query": query_text,
            "context": context,
            "matches": len(hits),
        }
