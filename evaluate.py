
import pandas as pd
from pathlib import Path

from app.retriever import FAQRetriever


TEST_PATH = Path("data/test-questions.csv")
OUTPUT_PATH = Path("evaluation/retrieval-results.csv")


def main():
    if not TEST_PATH.exists():
        raise FileNotFoundError(f"Test file not found: {TEST_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    test_data = pd.read_csv(TEST_PATH)

    required_columns = {"id", "question"}
    missing = required_columns - set(test_data.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if test_data.empty:
        raise ValueError("Test dataset is empty.")

    print(f"\nTotal test questions: {len(test_data)}")

    retriever = FAQRetriever()

    evaluation_results = []

    for _, test_row in test_data.iterrows():
        question_id = test_row["id"]
        question = str(test_row["question"])

        results = retriever.search(question, top_k=3)

        if not results:
            print(f"\n[{question_id}] {question}")
            print("No retrieval results.")
            continue

        top_result = results[0]
        second_score = (
            results[1]["similarity"] if len(results) > 1 else 0
        )

        print("\n" + "=" * 70)
        print(f"QUESTION ID: {question_id}")
        print(f"QUESTION: {question}")

        print("\nTOP 3 RETRIEVED FAQs:")

        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"FAQ ID: {result['id']}")
            print(f"Topic: {result['topic']}")
            print(f"Question: {result['question']}")
            print(f"Similarity: {result['similarity']}")
            print(f"Relevant (current threshold): {result['is_relevant']}")

        evaluation_results.append({
            "test_id": question_id,
            "customer_question": question,
            "top_faq_id": top_result["id"],
            "top_faq_topic": top_result["topic"],
            "top_faq_question": top_result["question"],
            "top_similarity": top_result["similarity"],
            "second_similarity": second_score,
            "score_gap": round(
                top_result["similarity"] - second_score, 4
            ),
            "current_threshold_match": top_result["is_relevant"],
            "manual_expected_faq_id": "",
            "manual_correct": ""
        })

    report = pd.DataFrame(evaluation_results)
    report.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETED")
    print(f"Questions processed: {len(evaluation_results)}")
    print(f"Results saved to: {OUTPUT_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
