"""
Find real high-impact financial events from the existing dataset.

This script does not create or modify the dataset.
It identifies records that can legitimately trigger
the portfolio stress-testing module.
"""

import pandas as pd

from ingestion import load_all_data
from sentiment import load_sentiment_model, analyze_texts
from event_classifier import load_event_classifier, classify_event
from impact_score import calculate_impact_score


SUPPORTED_STRESS_EVENTS = {
    "Geopolitical",
    "Macroeconomic",
    "Credit Event",
    "Regulatory",
}


def main():

    print("\n=== RiskPulse Demo Event Search ===\n")

    data = load_all_data()

    news = data[data["source_type"] == "news"].copy()

    news = news.drop_duplicates(
        subset=["date", "entity", "text"]
    ).reset_index(drop=True)

    print(f"News records available: {len(news)}")

    sample = news.head(500).copy()

    print(f"Records being analyzed: {len(sample)}")
    print("\nLoading sentiment model...")

    sentiment_model = load_sentiment_model()

    sentiment_results = analyze_texts(
        sample["text"].tolist(),
        sentiment_model,
    )

    sentiment_df = pd.DataFrame(sentiment_results)

    print("Loading event classifier...")

    event_classifier = load_event_classifier()

    event_results = []

    for text in sample["text"]:
        result = classify_event(
            text,
            event_classifier,
        )
        event_results.append(result)

    event_df = pd.DataFrame(event_results)

    # -----------------------------
    # Combine NLP results
    # -----------------------------

    results = pd.concat(
        [
            sample.reset_index(drop=True),
            sentiment_df.reset_index(drop=True),
            event_df.reset_index(drop=True),
        ],
        axis=1,
    )

    results["impact_score"] = results.apply(
        lambda row: calculate_impact_score(
            text=row["text"],
            event_class=row["event_class"],
            sentiment_score=row["sentiment_score"],
        ),
        axis=1,
    )
    candidates = results[
        (results["impact_score"] > 7)
        & (
            results["event_class"].isin(
                SUPPORTED_STRESS_EVENTS
            )
        )
    ].copy()

    candidates = candidates.sort_values(
        by="impact_score",
        ascending=False,
    )

    print("\n=== High-Impact Stress Candidates ===\n")

    if candidates.empty:
        print("No qualifying events found in this sample.")
        print("We can expand the search to more news records.")
        return

    display_columns = [
        "date",
        "entity",
        "text",
        "sentiment_score",
        "event_class",
        "event_confidence",
        "classification_method",
        "impact_score",
    ]

    print(
        candidates[display_columns]
        .head(20)
        .to_string(index=False)
    )

    output_path = "data/demo_event_candidates.csv"

    candidates.to_csv(
        output_path,
        index=False,
    )

    print(f"\nSaved candidates: {output_path}")


if __name__ == "__main__":
    main()