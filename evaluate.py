
import time
from pathlib import Path

import pandas as pd

from app.assistant import BankAssistant


TEST_PATH = Path("data/test-questions.csv")
GROUND_TRUTH_PATH = Path("evaluation/ground-truth.csv")
OUTPUT_PATH = Path("evaluation/final-results.csv")

FALLBACK = "I don't know, let me connect you to a person"


def main():
    test_data = pd.read_csv(
        TEST_PATH,
        dtype={"id": str}
    )

    ground_truth = pd.read_csv(
        GROUND_TRUTH_PATH,
        dtype=str
    )

    test_data["id"] = test_data["id"].str.strip()

    ground_truth["test_id"] = (
        ground_truth["test_id"].str.strip()
    )

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
        raise ValueError(
            "Some test questions have no ground-truth label."
        )

    if len(data) != 40:
        raise ValueError(
            f"Expected 40 test questions, found {len(data)}."
        )

    print(f"Total test questions: {len(data)}")

    assistant = BankAssistant()

    rows = []

    for _, item in data.iterrows():

        test_id = item["id"]
        question = str(item["question"]).strip()
        expected = item["expected_faq_id"]

        # Measure complete assistant response time.
        start_time = time.perf_counter()

        try:
            result = assistant.ask(question)

            latency = time.perf_counter() - start_time

        except Exception as error:
            latency = time.perf_counter() - start_time

            result = {
                "answer": "",
                "faq_id": None,
                "status": "error",
                "error": str(error)
            }

        answer = str(result.get("answer", "")).strip()

        returned_faq_id = result.get("faq_id")

        if returned_faq_id is not None:
            returned_faq_id = str(returned_faq_id)

        status = str(result.get("status", "error")).lower()

        is_unsupported = expected == "NO_ANSWER"

        # Correct answer means the assistant selected
        # the expected FAQ and returned a grounded answer.
        correct_answer = (
            not is_unsupported
            and status == "answered"
            and returned_faq_id == expected
            and bool(answer)
        )

       
        correct_fallback = (
            is_unsupported
            and status == "fallback"
            and bool(answer)
        )

        correct = correct_answer or correct_fallback

        if is_unsupported:
            outcome = (
                "CORRECT_FALLBACK"
                if correct_fallback
                else "INCORRECT_UNSUPPORTED_RESPONSE"
            )

        else:
            outcome = (
                "CORRECT_ANSWER"
                if correct_answer
                else "INCORRECT_ANSWER"
            )

        rows.append({
            "test_id": test_id,
            "question": question,
            "expected_faq_id": expected,
            "returned_faq_id": returned_faq_id,
            "answer": answer,
            "status": status,
            "correct_answer": correct_answer,
            "correct_fallback": correct_fallback,
            "correct": correct,
            "outcome": outcome,
            "latency_seconds": round(latency, 4),
            "error": result.get("error", "")
        })

        print(
            f"[{test_id:>2}] "
            f"Expected={expected:<10} "
            f"Returned={str(returned_faq_id):<10} "
            f"Outcome={outcome:<32} "
            f"Time={latency:.3f}s"
        )

    report = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    answerable = report[
        report["expected_faq_id"] != "NO_ANSWER"
    ]

    unsupported = report[
        report["expected_faq_id"] == "NO_ANSWER"
    ]

    total_correct_answers = int(
        answerable["correct_answer"].sum()
    )

    total_correct_fallbacks = int(
        unsupported["correct_fallback"].sum()
    )

    total_correct = int(report["correct"].sum())

    average_latency = report["latency_seconds"].mean()

    total_time = report["latency_seconds"].sum()

    print("\n" + "=" * 65)
    print("FINAL LOCAL ASSISTANT EVALUATION")
    print("=" * 65)

    print(f"Total questions: {len(report)}")

    print(
        f"Answerable questions: {len(answerable)}"
    )

    print(
        f"Correct answers: "
        f"{total_correct_answers}/{len(answerable)}"
    )

    print(
        f"Unsupported questions: {len(unsupported)}"
    )

    print(
        f"Correct fallback responses: "
        f"{total_correct_fallbacks}/{len(unsupported)}"
    )

    print(
        f"Incorrect responses: "
        f"{len(report) - total_correct}"
    )

    print(
        f"Overall correct: "
        f"{total_correct}/{len(report)} "
        f"({total_correct / len(report):.2%})"
    )

    print(
        f"Average response time: {average_latency:.3f}s"
    )

    print(
        f"Total evaluation time: {total_time:.3f}s"
    )

    print(
        f"Maximum response time: "
        f"{report['latency_seconds'].max():.3f}s"
    )

    print(
        f"Minimum response time: "
        f"{report['latency_seconds'].min():.3f}s"
    )

    print(f"\nDetailed results: {OUTPUT_PATH}")

    print("=" * 65)


if __name__ == "__main__":
    main()
