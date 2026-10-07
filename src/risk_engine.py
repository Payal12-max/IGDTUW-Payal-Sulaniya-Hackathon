"""
RiskPulse Unified AI/NLP Risk Engine.

Combines:
1. Financial sentiment analysis using FinBERT
2. Hybrid event classification
3. Rule-based impact scoring

Produces structured, machine-readable financial risk signals.
"""

from pathlib import Path

import pandas as pd

from ingestion import load_all_data
from sentiment import load_sentiment_model, analyze_texts
from event_classifier import load_event_classifier, classify_event
from impact_score import calculate_impact_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_sample_data(n_news=3, n_social=3):
    """
    Load a small development sample using the unified ingestion pipeline.

    Using ingestion.py ensures that:
    - news and social data use the same schema
    - dates and text are normalized
    - empty records are removed
    - exact duplicate observations are removed
    """

    data = load_all_data()

    news = (
        data[data["source_type"] == "news"]
        .head(n_news)
        .copy()
    )

    social = (
        data[data["source_type"] == "social_media"]
        .head(n_social)
        .copy()
    )

    sample = pd.concat(
        [news, social],
        ignore_index=True,
    )

    return sample

def assign_risk_level(impact_score):
    """
    Convert the numerical impact score into a human-readable
    risk category.
    """

    if impact_score >= 9:
        return "Critical"

    if impact_score >= 7:
        return "High"

    if impact_score >= 4:
        return "Moderate"

    return "Low" 


def analyze_records(
    data,
    sentiment_classifier,
    event_classifier,
):
    """
    Run the complete NLP risk pipeline on a DataFrame.

    Pipeline:
        Text
          ↓
        FinBERT Sentiment
          ↓
        Hybrid Event Classification
          ↓
        Impact Score
          ↓
        Stress Trigger

    Returns
    -------
    pandas.DataFrame
        Original records plus structured risk signals.
    """

    data = data.copy().reset_index(drop=True)

    sentiment_results = analyze_texts(
        data["text"],
        classifier=sentiment_classifier,
    )

    data = pd.concat(
        [
            data,
            sentiment_results.reset_index(drop=True),
        ],
        axis=1,
    )

    event_results = []

    for text in data["text"]:

        result = classify_event(
            text,
            classifier=event_classifier,
        )

        event_results.append(result)

    event_df = pd.DataFrame(event_results)

    data = pd.concat(
        [
            data,
            event_df.reset_index(drop=True),
        ],
        axis=1,
    )

    data["impact_score"] = data.apply(
        lambda row: calculate_impact_score(
            text=row["text"],
            event_class=row["event_class"],
            sentiment_score=row["sentiment_score"],
        ),
        axis=1,
    )
    data["risk_level"] = data["impact_score"].apply(
        assign_risk_level
    )

    data["stress_trigger"] = (
        data["impact_score"] > 7
    )

    return data


def main():

    print("\n=== RiskPulse Unified AI/NLP Risk Engine ===\n")

    data = load_sample_data(
        n_news=3,
        n_social=3,
    )

    print(f"Records to analyze: {len(data)}")

    print("\nSource distribution:")

    print(
        data["source_type"]
        .value_counts()
        .to_string()
    )

    print("\nLoading sentiment model...")

    sentiment_classifier = load_sentiment_model()

    print("Loading event classifier...")

    event_classifier = load_event_classifier()

    results = analyze_records(
        data=data,
        sentiment_classifier=sentiment_classifier,
        event_classifier=event_classifier,
    )

    output_columns = [
        "source_type",
        "source",
        "date",
        "entity",
        "text",
        "sentiment_label",
        "sentiment_score",
        "event_class",
        "event_confidence",
        "classification_method",
        "impact_score",
        "risk_level",
        "stress_trigger",
    ]

    print("\n=== Risk Signals ===\n")

    print(
        results[output_columns].to_string(
            index=False
        )
    )

    output_path = (
        PROJECT_ROOT
        / "data"
        / "risk_engine_sample.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved sample output: {output_path}"
    )


if __name__ == "__main__":
    main()