import pandas as pd
from sentence_transformers import SentenceTransformer

from app.config import (
    FAQ_PATH,
    EMBEDDING_MODEL,
    TOP_K,
    SIMILARITY_THRESHOLD,
)


class FAQRetriever:

    def __init__(self):
        if not FAQ_PATH.exists():
            raise FileNotFoundError(
                f"FAQ file not found: {FAQ_PATH}"
            )

        self.faq = pd.read_csv(FAQ_PATH)

        required_columns = {
            "id",
            "topic",
            "question",
            "answer",
        }

        missing = required_columns - set(self.faq.columns)

        if missing:
            raise ValueError(
                f"Missing FAQ columns: {missing}"
            )

        if self.faq.empty:
            raise ValueError("FAQ dataset is empty.")

        self.faq = self.faq.fillna("")

        print("Loading multilingual embedding model...")

        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.documents = [
            f"Topic: {row['topic']}. "
            f"Question: {row['question']}"
            for _, row in self.faq.iterrows()
        ]

        print("Creating FAQ embeddings...")

        self.faq_embeddings = self.model.encode(
            self.documents,
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        print(f"FAQ Retriever ready: {len(self.faq)} FAQs loaded.")

    def search(self, query, top_k=TOP_K):

        if not isinstance(query, str) or not query.strip():
            return []

        query_embedding = self.model.encode(
            query.strip(),
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        similarities = (
            self.faq_embeddings @ query_embedding
        )

        top_k = min(top_k, len(self.faq))

        scores, indices = similarities.topk(top_k)

        results = []

        for score, index in zip(
            scores.tolist(),
            indices.tolist()
        ):
            row = self.faq.iloc[index]

            similarity = float(score)

            results.append({
                "id": int(row["id"]),
                "topic": str(row["topic"]),
                "question": str(row["question"]),
                "answer": str(row["answer"]),
                "similarity": round(similarity, 4),
                "is_relevant": (
                    similarity >= SIMILARITY_THRESHOLD
                ),
            })

        return results