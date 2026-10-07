import pandas as pd

NEWS_PATH = "data/news.csv"
OUTPUT_PATH = "data/event_validation.csv"


CATEGORIES = {
    "Geopolitical": [
        "Shares flat in Asia before Iran sanctions",
        "AI Trade in Focus as Nvidia Earnings and Iran",
        "U.S. Expands Iran Sanctions",
        "Bitcoin and Ethereum slide as US Iran war",
        "Ousted Ukrainian defense chief lands Palantir",
    ],

    "Macroeconomic": [
        "US Stock Market: Fed uncertainty",
        "Bitcoin hovers near $63K ahead of Fed rate",
        "S&P 500 Falls, Bitcoin Surges as Traders Await",
        "Bitcoin climbs towards $64,000 as cooling inflation",
        "Wall Street Week Ahead: Warsh",
    ],

    "Merger & Acquisition": [
        "Archer Aviation To Acquire Boeing",
        "Tesla (NASDAQ: TSLA) And SpaceX Merger",
        "Archer Aviation Stock Gains 14% On Boeing",
        "Archer Aviation shares jump nearly 10% on deal",
        "MPS board to discuss options against Intesa",
    ],

    "Product Launch": [
        "Google Pixel 11, Pixel 11 Pro and Pro XL launch",
        "Google Officially Unveils Pixel 11 Lineup",
        "Robinhood Launches Crypto Trading in the UK",
        "Apple (NASDAQ: AAPL) Launches Houston Advanced",
        "Google Pixel Watch 5 and upgraded Buds Pro 2",
    ],

    "Regulatory": [
        "Apple Digital Markets Act compliance",
        "SEC's",
        "SEBI's swift ban on JPMorgan",
        "JPMorgan debanked Polymarket over regulatory",
        "Meta Platforms (NASDAQ: META) Stock Price Ticks",
    ],

    "Earnings / Financial Results": [
        "Airbnb hits four-year high after lifting revenue",
        "Airbnb jumps after raising its 2026 revenue",
        "IonQ (NYSE: IONQ) Revenue Surges Fivefold",
        "FinancialContent - Palantir Technologies's Q2",
        "Embraer Flies On Booming Earnings And Backlog",
    ],
}


def find_headline(all_headlines, search_text):
    """Find the first real headline containing the search phrase."""

    matches = [
        headline
        for headline in all_headlines
        if search_text.lower() in headline.lower()
    ]

    if not matches:
        print(f"WARNING: Could not find: {search_text}")
        return None

    return matches[0]


def main():
    news = pd.read_csv(NEWS_PATH)

    all_headlines = (
        news["headline"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    rows = []

    for category, search_terms in CATEGORIES.items():

        for search_text in search_terms:

            headline = find_headline(
                all_headlines,
                search_text
            )

            if headline is not None:

                rows.append(
                    {
                        "headline": headline,
                        "expected_event": category,
                    }
                )

    validation = pd.DataFrame(rows)

    validation.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n=== Event Validation Set ===\n")

    print(validation.to_string(index=False))

    print("\nRows:", len(validation))

    print("\nCategory distribution:")

    print(
        validation["expected_event"]
        .value_counts()
        .to_string()
    )

    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()