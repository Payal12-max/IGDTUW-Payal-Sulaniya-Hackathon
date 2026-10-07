"""
Financial event impact scoring.

Produces a transparent severity score from 1 to 10 using:
- event type
- sentiment
- high-severity language

This is a rule-based prototype score, not a trained prediction model.
"""

import re


EVENT_BASE_SCORES = {
    "Geopolitical": 7.0,
    "Macroeconomic": 6.0,
    "Credit Event": 8.0,
    "Merger & Acquisition": 5.0,
    "Product Launch": 3.0,
    "Regulatory": 6.0,
    "Earnings / Financial Results": 5.0,
    "Unclassified": 0.0,
}


SEVERE_TERMS = {
    "default": 2.0,
    "bankruptcy": 2.0,
    "bankrupt": 2.0,
    "collapse": 2.0,
    "crisis": 1.5,
    "war": 1.5,
    "invasion": 1.5,
    "sanctions": 1.0,
    "downgrade": 1.0,
    "downgraded": 1.0,
    "lawsuit": 0.5,
    "ban": 0.5,
    "fraud": 1.5,
    "losses": 0.5,
}


def calculate_impact_score(
    text,
    event_class,
    sentiment_score,
):
    """
    Calculate an impact score between 1 and 10.

    Unclassified events receive 0.0 because their event type
    is too uncertain to support a reliable stress signal.

    Parameters
    ----------
    text : str
        Original financial text/headline.

    event_class : str
        Classified event type.

    sentiment_score : float
        Financial sentiment score in [-1, +1].

    Returns
    -------
    float
        Impact score between 1 and 10, or 0.0 for Unclassified.
    """

    # Do not generate a stress signal from an uncertain event class.
    if event_class == "Unclassified":
        return 0.0

    text = str(text).lower()

    score = EVENT_BASE_SCORES.get(
        event_class,
        5.0,
    )

    # Sentiment adjustment
    if sentiment_score < -0.75:
        score += 1.5
    elif sentiment_score < -0.50:
        score += 1.0
    elif sentiment_score < -0.25:
        score += 0.5
    elif sentiment_score > 0.75:
        score += 0.5

    # Severe-language adjustment
    for term, weight in SEVERE_TERMS.items():
        if re.search(
            rf"\b{re.escape(term)}\b",
            text,
            flags=re.IGNORECASE,
        ):
            score += weight

    # Keep classified-event scores within 1-10.
    score = max(1.0, min(10.0, score))

    return round(score, 2)


if __name__ == "__main__":

    test_cases = [
        {
            "text": "Company announces major debt default and restructuring",
            "event_class": "Credit Event",
            "sentiment_score": -0.95,
        },
        {
            "text": "AI Trade in Focus as Nvidia Earnings and Iran Sanctions Keep Markets on Edge",
            "event_class": "Geopolitical",
            "sentiment_score": -0.60,
        },
        {
            "text": "Bitcoin climbs ahead of the Fed rate decision",
            "event_class": "Macroeconomic",
            "sentiment_score": 0.20,
        },
        {
            "text": "Google Pixel 11 officially launched in India",
            "event_class": "Product Launch",
            "sentiment_score": 0.80,
        },
        {
            "text": "Airbnb hits four-year high after lifting revenue outlook",
            "event_class": "Earnings / Financial Results",
            "sentiment_score": 0.90,
        },
        {
            "text": "Intel Falls 5% on Proposed $15B Share Sale",
            "event_class": "Unclassified",
            "sentiment_score": -0.10,
        },
    ]

    print("\n=== Impact Score Test ===\n")

    for case in test_cases:
        score = calculate_impact_score(
            text=case["text"],
            event_class=case["event_class"],
            sentiment_score=case["sentiment_score"],
        )

        print(f"Text: {case['text']}")
        print(f"Event: {case['event_class']}")
        print(f"Sentiment: {case['sentiment_score']:+.2f}")
        print(f"Impact Score: {score:.2f}/10")
        print("-" * 80)