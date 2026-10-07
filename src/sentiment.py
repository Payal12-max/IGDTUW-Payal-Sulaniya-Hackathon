"""
Financial sentiment analysis using FinBERT.

FinBERT converts financial text into:
- Positive probability
- Neutral probability
- Negative probability
- Continuous sentiment score in [-1, +1]

Sentiment score:
    positive_probability - negative_probability
"""

from pathlib import Path

import pandas as pd
import torch
from transformers import pipeline


MODEL_NAME = "ProsusAI/finbert"

BATCH_SIZE = 16
MAX_LENGTH = 512


def load_sentiment_model():
    """Load FinBERT once and return the inference pipeline."""

    device = 0 if torch.cuda.is_available() else -1

    classifier = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        top_k=None,
        device=device,
        truncation=True,
        max_length=MAX_LENGTH,
    )

    return classifier


def calculate_sentiment_score(results):
    """
    Convert FinBERT probabilities into a continuous score.

    Score = P(positive) - P(negative)

    Range:
        -1 = strongly negative
         0 = neutral
        +1 = strongly positive
    """

    probabilities = {
        item["label"].lower(): item["score"]
        for item in results
    }

    positive = probabilities.get("positive", 0.0)
    negative = probabilities.get("negative", 0.0)

    score = positive - negative

    return max(-1.0, min(1.0, score))


def analyze_texts(texts, classifier=None):
    """
    Analyze a list/Series of financial texts.

    Returns a DataFrame containing:
        sentiment_label
        positive_probability
        neutral_probability
        negative_probability
        sentiment_score
    """

    if classifier is None:
        classifier = load_sentiment_model()

    texts = pd.Series(texts).fillna("").astype(str)

    results = []

    for start in range(0, len(texts), BATCH_SIZE):

        batch = texts.iloc[start:start + BATCH_SIZE].tolist()

        predictions = classifier(batch)

        for prediction in predictions:

            probabilities = {
                item["label"].lower(): item["score"]
                for item in prediction
            }

            positive = probabilities.get("positive", 0.0)
            neutral = probabilities.get("neutral", 0.0)
            negative = probabilities.get("negative", 0.0)

            score = positive - negative

            if score > 0.05:
                label = "positive"
            elif score < -0.05:
                label = "negative"
            else:
                label = "neutral"

            results.append(
                {
                    "sentiment_label": label,
                    "positive_probability": positive,
                    "neutral_probability": neutral,
                    "negative_probability": negative,
                    "sentiment_score": max(-1.0, min(1.0, score)),
                }
            )

    return pd.DataFrame(results)


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[1]

    news_path = project_root / "data" / "news.csv"

    news = pd.read_csv(news_path)

    sample = news["headline"].drop_duplicates().head(5)

    classifier = load_sentiment_model()

    results = analyze_texts(sample, classifier)

    output = pd.concat(
        [
            sample.reset_index(drop=True).rename("text"),
            results,
        ],
        axis=1,
    )

    print("\n=== RiskPulse Financial Sentiment Test ===\n")

    print(output.to_string(index=False))