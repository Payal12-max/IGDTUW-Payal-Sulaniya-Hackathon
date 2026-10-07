"""
Integrated RiskPulse pipeline.

Flow:
Financial News / Social Data
        ↓
Sentiment Analysis
        ↓
Event Classification
        ↓
Impact Scoring
        ↓
Stress Trigger
        ↓
Portfolio Stress Testing
"""

import pandas as pd

from ingestion import load_all_data
from sentiment import load_sentiment_model, analyze_texts
from event_classifier import load_event_classifier, classify_event
from impact_score import calculate_impact_score
from portfolio_stress import load_portfolio, stress_test_portfolio


SUPPORTED_STRESS_EVENTS = {
    "Geopolitical",
    "Macroeconomic",
    "Credit Event",
    "Regulatory",
}


# Real event selected from the existing financial-news dataset.
DEMO_EVENT_TEXT = (
    "Pentagon Urges Boeing (NYSE: BA), Lockheed (NYSE: LMT) "
    "And RTX (NYSE: RTX) To Fast-Track Weapons Output "
    "Amid Iran War Strain"
)

DEMO_EVENT_DATE = "2026-08-10 18:45:00+00:00"
DEMO_EVENT_ENTITY = "BA"


def load_demo_event(data):
    """
    Select the real demo event from the existing dataset.

    The event is identified using fields already present in the
    downloaded dataset. No headline or model output is fabricated.
    """

    matches = data[
        (data["source_type"] == "news")
        & (data["entity"] == DEMO_EVENT_ENTITY)
        & (data["date"].astype(str) == DEMO_EVENT_DATE)
        & (data["text"] == DEMO_EVENT_TEXT)
    ].copy()

    if matches.empty:
        raise ValueError(
            "Demo event was not found in the existing dataset."
        )

    return matches.iloc[[0]].reset_index(drop=True)


def analyze_event(data, sentiment_model, event_classifier):
    """
    Run sentiment, event classification, and impact scoring.
    """

    sentiment_results = analyze_texts(
        data["text"].tolist(),
        sentiment_model,
    )

    sentiment_df = pd.DataFrame(sentiment_results)

    event_results = []

    for text in data["text"]:
        result = classify_event(
            text,
            event_classifier,
        )
        event_results.append(result)

    event_df = pd.DataFrame(event_results)

    results = pd.concat(
        [
            data.reset_index(drop=True),
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

    results["stress_trigger"] = (
        results["impact_score"] > 7
    )

    return results


def main():

    print("\n=== RiskPulse Integrated Risk Pipeline ===\n")

    # ---------------------------------
    # Load source data
    # ---------------------------------

    data = load_all_data()

    print(f"Total unified records available: {len(data)}")

    # ---------------------------------
    # Select real demo event
    # ---------------------------------

    demo_event = load_demo_event(data)

    print("\n=== Selected Demo Event ===\n")
    print(demo_event[["date", "entity", "text"]].to_string(index=False))

    # ---------------------------------
    # Load NLP models
    # ---------------------------------

    print("\nLoading NLP models...")

    sentiment_model = load_sentiment_model()
    event_classifier = load_event_classifier()

    # ---------------------------------
    # NLP risk analysis
    # ---------------------------------

    results = analyze_event(
        demo_event,
        sentiment_model,
        event_classifier,
    )

    print("\n=== NLP Risk Signal ===\n")

    display_columns = [
        "source_type",
        "entity",
        "text",
        "sentiment_score",
        "event_class",
        "event_confidence",
        "classification_method",
        "impact_score",
        "stress_trigger",
    ]

    print(
        results[display_columns].to_string(index=False)
    )

    # ---------------------------------
    # Portfolio stress testing
    # ---------------------------------

    triggered_events = results[
        (results["stress_trigger"])
        & (
            results["event_class"].isin(
                SUPPORTED_STRESS_EVENTS
            )
        )
    ]

    if triggered_events.empty:
        print(
            "\nNo high-impact event triggered a "
            "supported portfolio stress scenario."
        )
        return

    portfolio = load_portfolio()

    print("\n=== Portfolio Stress Results ===\n")

    for _, event in triggered_events.iterrows():

        event_class = event["event_class"]

        stress_result = stress_test_portfolio(
            portfolio,
            event_class,
        )
        positions, summary = stress_result

        print(f"Event: {event_class}")
        print(f"Impact Score: {event['impact_score']:.2f}/10")
        print("Stress Trigger: TRUE")

        print(
            f"\nPortfolio Value Before: "
            f"{summary['portfolio_value_before']:,.2f}"
        )

        print(
            f"Portfolio Value After:  "
            f"{summary['portfolio_value_after']:,.2f}"
        )

        print(
            f"Portfolio Loss:          "
            f"{summary['portfolio_loss']:,.2f}"
        )

        print(
            f"Portfolio Loss %:        "
            f"{summary['portfolio_loss_percent']:.2f}%"
        )

        print("\nStress Scenario:")
        print(
            "  Equity shock: -10%"
        )
        print(
            "  Rate shock:   +2%"
        )
        print(
            "  Credit shock: +5%"
        )

        print("\nPosition-level impact:")
        print(
            positions.to_string(index=False)
        )

    # ---------------------------------
    # Save integrated result
    # ---------------------------------

    output_path = "data/integrated_risk_results.csv"

    results.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved integrated result: {output_path}"
    )


if __name__ == "__main__":
    main()