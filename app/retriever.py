
import re
import pandas as pd
import torch

from sentence_transformers import SentenceTransformer

from app.config import (
    FAQ_PATH,
    EMBEDDING_MODEL,
    TOP_K,
    SIMILARITY_THRESHOLD,
)

from app.language import normalize_query


class FAQRetriever:

    def __init__(self):

        if not FAQ_PATH.exists():
            raise FileNotFoundError(
                f"FAQ file not found: {FAQ_PATH}"
            )

        self.faq = pd.read_csv(FAQ_PATH).fillna("")

        required_columns = {
            "id",
            "topic",
            "question",
            "answer",
            "search_aliases",
            "answerable_aliases",
            "unanswerable_aliases",
        }

        missing = required_columns - set(self.faq.columns)

        if missing:
            raise ValueError(
                f"Missing FAQ columns: {missing}"
            )

        if self.faq.empty:
            raise ValueError("FAQ dataset is empty.")

        print("Loading multilingual embedding model...")

        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.document_texts = []
        self.document_faq_indices = []

        for faq_index, row in self.faq.iterrows():

            topic = str(row["topic"]).strip()
            question = str(row["question"]).strip()

            # Original FAQ question.
            main_text = (
                f"Topic: {topic}. "
                f"Question: {question}"
            )

            self.document_texts.append(main_text)
            self.document_faq_indices.append(faq_index)

            # Only search_aliases are used for retrieval.
            # answerable_aliases and unanswerable_aliases
            # are reserved for evaluation.
            aliases = str(row["search_aliases"]).strip()

            if aliases:

                alias_list = [
    item.strip()
    for item in re.split(r"[;\n]+", aliases)
    if item.strip()
]

                for alias in alias_list:

                    alias_text = (
                        f"Topic: {topic}. "
                        f"Question: {alias}"
                    )

                    self.document_texts.append(alias_text)
                    self.document_faq_indices.append(faq_index)

        print(
            f"Creating embeddings for "
            f"{len(self.document_texts)} FAQ representations..."
        )

        self.document_embeddings = self.model.encode(
            self.document_texts,
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        print(
            f"FAQ Retriever ready: "
            f"{len(self.faq)} FAQs loaded."
        )

    def search(self, query, top_k=TOP_K):

        if not isinstance(query, str) or not query.strip():
            return []

        original_query = query.strip()

        normalized_query = normalize_query(original_query)

        if not isinstance(normalized_query, str):
            normalized_query = original_query

        if not normalized_query.strip():
            normalized_query = original_query

        # Encode the original query.
        original_embedding = self.model.encode(
            original_query,
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        original_scores = (
            self.document_embeddings @ original_embedding
        )

        # Encode the normalized query when it differs.
        # This helps retain matches from both the original
        # language and the normalized/translated version.
        if normalized_query.strip() != original_query:

            normalized_embedding = self.model.encode(
                normalized_query.strip(),
                convert_to_tensor=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            normalized_scores = (
                self.document_embeddings @ normalized_embedding
            )

            document_scores = torch.maximum(
                original_scores,
                normalized_scores
            )

        else:
            document_scores = original_scores

        document_scores = document_scores.tolist()

        # Keep the maximum score among each FAQ's
        # main question and its individual search aliases.
        faq_scores = [float("-inf")] * len(self.faq)

        for faq_index, score in zip(
            self.document_faq_indices,
            document_scores
        ):

            faq_scores[faq_index] = max(
                faq_scores[faq_index],
                float(score)
            )

        ranked_indices = sorted(
            range(len(self.faq)),
            key=lambda index: faq_scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices[:min(top_k, len(self.faq))]:

            row = self.faq.iloc[index]
            similarity = faq_scores[index]

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

        print(results,"Carefully checking the results")

        return results
