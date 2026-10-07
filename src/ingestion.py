from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

NEWS_PATH = PROJECT_ROOT / "data" / "news.csv"
SOCIAL_PATH = PROJECT_ROOT / "data" / "social_media.csv"


def load_news(path=NEWS_PATH):
    """Load and normalize financial news data."""

    df = pd.read_csv(path)

    df = df.rename(
        columns={
            "ticker": "entity",
            "published_at": "date",
            "headline": "text",
        }
    )

    df["source_type"] = "news"
    df["company_name"] = df["entity"]
    df["sector"] = None

    columns = [
        "source_type",
        "source",
        "date",
        "entity",
        "company_name",
        "sector",
        "text",
        "url",
    ]

    df = df[columns].copy()

    return clean_text_data(df)


def load_social_media(path=SOCIAL_PATH):
    """Load and normalize social-media data."""

    df = pd.read_csv(path)

    df = df.rename(
        columns={
            "stock_symbol": "entity",
        }
    )

    df["source_type"] = "social_media"

    columns = [
        "source_type",
        "source",
        "date",
        "entity",
        "company_name",
        "sector",
        "text",
    ]

    df = df[columns].copy()

    df["url"] = None

    return clean_text_data(df)


def clean_text_data(df):
    """Apply basic ingestion-level cleaning."""

    df = df.copy()

    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df = df[df["text"] != ""]

    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)

    df = df.dropna(subset=["date"])

    df = df.drop_duplicates(
        subset=["source_type", "date", "entity", "text"]
    )

    df = df.reset_index(drop=True)

    return df


def load_all_data():
    """Load both sources into one unified dataframe."""

    news = load_news()
    social = load_social_media()

    combined = pd.concat(
        [news, social],
        ignore_index=True
    )

    return combined


if __name__ == "__main__":
    news = load_news()
    social = load_social_media()
    combined = load_all_data()

    print("=== RiskPulse Data Ingestion ===")

    print(f"\nNews records: {len(news)}")
    print(f"Social-media records: {len(social)}")
    print(f"Combined records: {len(combined)}")

    print("\nSource distribution:")
    print(combined["source_type"].value_counts())

    print("\nUnified columns:")
    print(combined.columns.tolist())

    print("\nSample records:")
    print(
        combined[
            [
                "source_type",
                "entity",
                "date",
                "text",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )