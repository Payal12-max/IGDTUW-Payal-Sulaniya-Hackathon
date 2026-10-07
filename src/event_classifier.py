"""
Hybrid financial event classifier.

Uses:
1. High-confidence domain-specific rules for explicit event cues.
2. BART zero-shot classification for ambiguous headlines.

Output:
- event_class
- event_confidence
- classification_method
"""

import re

from transformers import pipeline


MODEL_NAME = "facebook/bart-large-mnli"

EVENT_LABELS = [
    "Geopolitical",
    "Macroeconomic",
    "Credit Event",
    "Merger & Acquisition",
    "Product Launch",
    "Regulatory",
    "Earnings / Financial Results",
]

EVENT_RULES = {
    "Merger & Acquisition": [
        r"\bacquisition\b",
        r"\bacquire\b",
        r"\bacquires\b",
        r"\bacquired\b",
        r"\bmerger\b",
        r"\bmerges with\b",
        r"\btakeover\b",
        r"\btake over\b",
        r"\bbuyout\b",
        r"\ball[- ]stock deal\b",
    ],

    "Product Launch": [
        r"\blaunched\b",
        r"\blaunches\b",
        r"\blaunch\b",
        r"\bunveils\b",
        r"\bunveiled\b",
        r"\bintroduces\b",
        r"\bintroduced\b",
        r"\bnew product\b",
        r"\bnew device\b",
    ],

    "Regulatory": [
        r"\bSEC\b",
        r"\bSEBI\b",
        r"\bregulatory\b",
        r"\bregulation\b",
        r"\bregulator\b",
        r"\bcompliance\b",
        r"\bcompliant\b",
        r"\bsanctions? by regulator\b",
        r"\bregulatory pressure\b",
        r"\bregulatory issues\b",
        r"\bban(?:ned)?\b",
    ],

    "Geopolitical": [
        r"\bwar\b",
        r"\bwarfare\b",
        r"\binvasion\b",
        r"\bmilitary\b",
        r"\biran sanctions\b",
        r"\brussia\b",
        r"\bukraine\b",
        r"\biran\b",
        r"\bisrael\b",
        r"\bpalestine\b",
        r"\bgeopolitical\b",
        r"\bsanctions\b",
    ],

    "Macroeconomic": [
        r"\bfed rate\b",
        r"\brate decision\b",
        r"\binterest rates?\b",
        r"\binflation\b",
        r"\bdeflation\b",
        r"\bGDP\b",
        r"\btreasury yields?\b",
        r"\bcentral bank\b",
        r"\bmonetary policy\b",
        r"\beconomic outlook\b",
        r"\bconsumer prices?\b",
    ],

    "Earnings / Financial Results": [
        r"\bearnings call\b",
        r"\bquarterly earnings\b",
        r"\bquarterly results\b",
        r"\bfinancial results\b",
        r"\brevenue outlook\b",
        r"\bprofit\b",
        r"\bnet income\b",
        r"\bearnings report\b",
        r"\bearnings results\b",
    ],

    "Credit Event": [
        r"\bdefault\b",
        r"\bdefaults\b",
        r"\bbankruptcy\b",
        r"\bbankrupt\b",
        r"\bdebt crisis\b",
        r"\bdebt restructuring\b",
        r"\bcredit downgrade\b",
        r"\bdowngraded\b",
    ],
}
def load_event_classifier():
    """Load BART zero-shot classifier once."""
    return pipeline(
        "zero-shot-classification",
        model=MODEL_NAME,
    )


def apply_event_rules(text):
    """
    Check for strong event-specific signals.

    Returns:
        (event_class, confidence) if a rule matches,
        otherwise (None, None).
    """
    text = str(text)
    matches = []

    for event, patterns in EVENT_RULES.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                matches.append(event)
                break

    if not matches:
        return None, None

    if len(matches) == 1:
        return matches[0], 0.95

    priority = [
        "Merger & Acquisition",
        "Product Launch",
        "Regulatory",
        "Credit Event",
        "Geopolitical",
        "Macroeconomic",
        "Earnings / Financial Results",
    ]

    for event in priority:
        if event in matches:
            return event, 0.90

    return matches[0], 0.90


def classify_event(
    text,
    classifier=None,
    min_confidence=0.45,
    min_margin=0.10,
):
    """
    Classify one financial text using explicit rules first,
    followed by BART zero-shot classification.

    Ambiguous or low-scoring fallback predictions are
    returned as Unclassified.
    """

    rule_event, rule_confidence = apply_event_rules(text)

    if rule_event is not None:
        return {
            "event_class": rule_event,
            "event_confidence": rule_confidence,
            "classification_method": "rule",
        }

    if classifier is None:
        classifier = load_event_classifier()

    prediction = classifier(
        str(text),
        EVENT_LABELS,
        multi_label=False,
    )

    labels = prediction["labels"]
    scores = prediction["scores"]

    top_label = labels[0]
    top_score = float(scores[0])

    second_score = (
        float(scores[1])
        if len(scores) > 1
        else 0.0
    )

    margin = top_score - second_score

    if (
        top_score < min_confidence
        or margin < min_margin
    ):
        return {
            "event_class": "Unclassified",
            "event_confidence": top_score,
            "classification_method": "uncertain_zero_shot",
        }

    return {
        "event_class": top_label,
        "event_confidence": top_score,
        "classification_method": "zero_shot",
    }


if __name__ == "__main__":
    classifier = load_event_classifier()

    test_headlines = [
        "Airbnb hits four-year high after lifting revenue outlook",
        "Intel Falls 5% on Proposed $15B Share Sale",
        "Palantir and Salesforce compete in AI software",
        "Archer Aviation to acquire Boeing's Wisk",
        "Google Pixel 11 officially launched in India",
        "SEC announces new regulatory framework for crypto assets",
        "Bitcoin climbs ahead of the Fed rate decision",
        "Company announces major debt default and restructuring",
    ]

    print("\n=== Hybrid Event Classifier Test ===\n")

    for headline in test_headlines:
        result = classify_event(headline, classifier)

        print(f"Headline: {headline}")
        print(f"Event: {result['event_class']}")
        print(f"Confidence: {result['event_confidence']:.3f}")
        print(f"Method: {result['classification_method']}")
        print("-" * 80)