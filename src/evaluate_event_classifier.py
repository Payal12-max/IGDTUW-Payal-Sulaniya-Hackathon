import pandas as pd
from transformers import pipeline


VALIDATION_PATH = "data/event_validation.csv"

LABELS = [
    "Geopolitical",
    "Macroeconomic",
    "Credit Event",
    "Merger & Acquisition",
    "Product Launch",
    "Regulatory",
    "Earnings / Financial Results",
]


def main():

    validation = pd.read_csv(VALIDATION_PATH)

    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
    )

    results = []

    print("\n=== Event Classifier Evaluation ===\n")

    for _, row in validation.iterrows():

        headline = row["headline"]
        expected = row["expected_event"]

        prediction = classifier(
            headline,
            LABELS,
            multi_label=False,
        )

        predicted = prediction["labels"][0]
        confidence = prediction["scores"][0]

        correct = predicted == expected

        results.append(
            {
                "headline": headline,
                "expected_event": expected,
                "predicted_event": predicted,
                "confidence": confidence,
                "correct": correct,
            }
        )

        status = "✓" if correct else "✗"

        print(
            f"{status} "
            f"Expected: {expected:<30} "
            f"Predicted: {predicted:<30} "
            f"Confidence: {confidence:.3f}"
        )

    results_df = pd.DataFrame(results)

    accuracy = results_df["correct"].mean()

    print("\n=== Summary ===")

    print(
        f"Correct: {results_df['correct'].sum()}/{len(results_df)}"
    )

    print(
        f"Accuracy: {accuracy:.2%}"
    )

    print("\nErrors:")

    errors = results_df[~results_df["correct"]]

    if errors.empty:
        print("No errors.")
    else:
        print(
            errors[
                [
                    "headline",
                    "expected_event",
                    "predicted_event",
                    "confidence",
                ]
            ].to_string(index=False)
        )

    results_df.to_csv(
        "data/event_validation_results.csv",
        index=False,
    )

    print(
        "\nSaved: data/event_validation_results.csv"
    )


if __name__ == "__main__":
    main()