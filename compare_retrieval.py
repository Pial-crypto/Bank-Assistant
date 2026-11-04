
import pandas as pd
import torch

from pathlib import Path
from app.retriever import FAQRetriever
from app.language import normalize_query
from app.config import SIMILARITY_THRESHOLD


TEST_PATH = Path("data/test-questions.csv")
GROUND_TRUTH_PATH = Path("evaluation/ground-truth.csv")

OUTPUT_PATH = Path("evaluation/retrieval-comparison.csv")
THRESHOLD_REPORT_PATH = Path("evaluation/threshold-analysis.csv")
MARGIN_THRESHOLDS = [
    0.00,
    0.02,
    0.04,
    0.06,
    0.08,
    0.10,
]
THRESHOLDS_TO_TEST = [
    0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75
]

STRATEGIES = ["original", "normalized", "combined"]


def rank_faqs(retriever, scores):
    document_scores = scores.tolist()

    faq_scores = [float("-inf")] * len(retriever.faq)

    for faq_index, score in zip(
        retriever.document_faq_indices,
        document_scores
    ):
        faq_scores[faq_index] = max(
            faq_scores[faq_index],
            float(score)
        )

    ranked_indices = sorted(
        range(len(retriever.faq)),
        key=lambda i: faq_scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indices:
        faq = retriever.faq.iloc[index]

        results.append({
            "id": str(int(faq["id"])),
            "topic": str(faq["topic"]),
            "question": str(faq["question"]),
            "score": float(faq_scores[index])
        })

    return results


def main():
    test_data = pd.read_csv(TEST_PATH, dtype={"id": str})

    ground_truth = pd.read_csv(
        GROUND_TRUTH_PATH,
        dtype=str
    )

    test_data["id"] = test_data["id"].str.strip()
    ground_truth["test_id"] = ground_truth["test_id"].str.strip()
    ground_truth["expected_faq_id"] = (
        ground_truth["expected_faq_id"].str.strip()
    )

    data = test_data.merge(
        ground_truth,
        left_on="id",
        right_on="test_id",
        how="left",
        validate="one_to_one"
    )

    if data["expected_faq_id"].isna().any():
        raise ValueError("Some test questions have missing ground truth.")

    print(f"Total questions: {len(data)}")
    print(f"Current configured threshold: {SIMILARITY_THRESHOLD}")
    print(f"Thresholds to evaluate: {THRESHOLDS_TO_TEST}")

    retriever = FAQRetriever()

    all_rows = []

    for _, item in data.iterrows():
        test_id = item["id"]
        question = str(item["question"]).strip()
        expected = item["expected_faq_id"]

        print("\n" + "=" * 100)
        print(f"TEST ID: {test_id}")
        print(f"QUESTION: {question}")
        print(f"EXPECTED FAQ: {expected}")

        normalized = normalize_query(question)

        if not isinstance(normalized, str) or not normalized.strip():
            normalized = question

        normalized = normalized.strip()

        print(f"NORMALIZED: {normalized}")

        original_embedding = retriever.model.encode(
            question,
            convert_to_tensor=True,
            normalize_embeddings=True
        )

        normalized_embedding = retriever.model.encode(
            normalized,
            convert_to_tensor=True,
            normalize_embeddings=True
        )

        original_scores = (
            retriever.document_embeddings @ original_embedding
        )

        normalized_scores = (
            retriever.document_embeddings @ normalized_embedding
        )

        combined_scores = torch.maximum(
            original_scores,
            normalized_scores
        )

        score_sets = {
            "original": original_scores,
            "normalized": normalized_scores,
            "combined": combined_scores
        }

        for strategy in STRATEGIES:
            results = rank_faqs(
                retriever,
                score_sets[strategy]
            )

            top1 = results[0]
            top2 = results[1]
            top3 = results[2]

            margin = top1["score"] - top2["score"]

            expected_result = next(
                (
                    (rank, result)
                    for rank, result in enumerate(results, start=1)
                    if result["id"] == expected
                ),
                None
            )

            expected_rank = (
                expected_result[0]
                if expected_result else None
            )

            expected_score = (
                round(expected_result[1]["score"], 4)
                if expected_result else None
            )

            is_no_answer = expected == "NO_ANSWER"

            accepted = top1["score"] >= SIMILARITY_THRESHOLD

            top1_correct = (
                not is_no_answer and top1["id"] == expected
            )

            top3_correct = (
                not is_no_answer
                and expected in [r["id"] for r in results[:3]]
            )

            false_accept = is_no_answer and accepted

            print(f"\n--- {strategy.upper()} ---")

            for rank, result in enumerate(results[:3], start=1):
                print(
                    f"Rank {rank}: FAQ {result['id']} | "
                    f"Score {result['score']:.4f} | "
                    f"{result['topic']} | "
                    f"{result['question']}"
                )

            print(f"Top-1 / Top-2 margin: {margin:.4f}")
            print(
                f"Expected rank: {expected_rank} | "
                f"Expected score: {expected_score}"
            )
            print(
                f"Accepted: {accepted} | "
                f"Top1 correct: {top1_correct} | "
                f"Top3 correct: {top3_correct} | "
                f"False accept: {false_accept}"
            )

            all_rows.append({
                "test_id": test_id,
                "question": question,
                "normalized_query": normalized,
                "expected_faq_id": expected,
                "strategy": strategy,

                "top1_faq_id": top1["id"],
                "top1_score": round(top1["score"], 4),

                "top2_faq_id": top2["id"],
                "top2_score": round(top2["score"], 4),

                "top3_faq_id": top3["id"],
                "top3_score": round(top3["score"], 4),

                "score_margin": round(margin, 4),

                "top3_faq_ids": ", ".join(
                    r["id"] for r in results[:3]
                ),

                "expected_rank": expected_rank,
                "expected_score": expected_score,

                "accepted": accepted,
                "top1_correct": top1_correct,
                "top3_correct": top3_correct,
                "false_accept": false_accept
            })

    report = pd.DataFrame(all_rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

        # ---------------------------------------------
    # Threshold and margin gate analysis
    # ---------------------------------------------

    gate_rows = []

    combined = report[
        report["strategy"] == "combined"
    ].copy()

    answerable = combined[
        combined["expected_faq_id"] != "NO_ANSWER"
    ]

    unsupported = combined[
        combined["expected_faq_id"] == "NO_ANSWER"
    ]

    for threshold in THRESHOLDS_TO_TEST:

        for margin_threshold in MARGIN_THRESHOLDS:

            answerable_accepted = (
                (answerable["top1_score"] >= threshold)
                &
                (answerable["score_margin"] >= margin_threshold)
            )

            unsupported_accepted = (
                (unsupported["top1_score"] >= threshold)
                &
                (unsupported["score_margin"] >= margin_threshold)
            )

            gate_rows.append({
                "similarity_threshold": threshold,
                "margin_threshold": margin_threshold,

                "answerable_total": len(answerable),

                "answerable_accepted": int(
                    answerable_accepted.sum()
                ),

                "answerable_rejected": int(
                    (~answerable_accepted).sum()
                ),

                "accepted_top1_correct": int(
                    (
                        answerable_accepted
                        &
                        answerable["top1_correct"]
                    ).sum()
                ),

                "accepted_top1_wrong": int(
                    (
                        answerable_accepted
                        &
                        (~answerable["top1_correct"])
                    ).sum()
                ),

                "unsupported_total": len(unsupported),

                "unsupported_false_accepts": int(
                    unsupported_accepted.sum()
                ),

                "unsupported_correctly_rejected": int(
                    (~unsupported_accepted).sum()
                ),
            })

    gate_report = pd.DataFrame(gate_rows)

    gate_report.to_csv(
        THRESHOLD_REPORT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCOMBINED STRATEGY: SIMILARITY + MARGIN GATE")
    print(gate_report.to_string(index=False))

    # ---------------------------------------------
    # Final strategy comparison
    # ---------------------------------------------

    print("\n\n" + "=" * 100)
    print("FINAL STRATEGY COMPARISON")
    print("=" * 100)

    for strategy in STRATEGIES:
        subset = report[
            report["strategy"] == strategy
        ]

        valid = subset[
            subset["expected_faq_id"] != "NO_ANSWER"
        ]

        invalid = subset[
            subset["expected_faq_id"] == "NO_ANSWER"
        ]

        print(f"\n{strategy.upper()}")

        print(
            f"Top-1 accuracy: "
            f"{valid['top1_correct'].mean():.2%}"
        )

        print(
            f"Top-3 accuracy: "
            f"{valid['top3_correct'].mean():.2%}"
        )

        print(
            f"False accepts at configured threshold "
            f"({SIMILARITY_THRESHOLD}): "
            f"{int(invalid['false_accept'].sum())}/"
            f"{len(invalid)}"
        )

    print("\n\n" + "=" * 100)
    print("COMBINED STRATEGY: THRESHOLD ANALYSIS")
    print("=" * 100)

    # print(threshold_report.to_string(index=False))
    print(gate_report.to_string(index=False))
    print("\nDetailed retrieval report:", OUTPUT_PATH)
    print("Threshold analysis report:", THRESHOLD_REPORT_PATH)


if __name__ == "__main__":
    main()
