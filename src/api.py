from pathlib import Path
import sys

import pandas as pd
from fastapi import FastAPI, HTTPException

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_PATH = PROJECT_ROOT / "data" / "integrated_risk_results.csv"

app = FastAPI(
    title="RiskPulse API",
    description="AI/NLP financial risk engine for event-driven portfolio stress testing.",
    version="1.0.0",
)

def load_results():
    if not RESULTS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Integrated risk results not found. Run the integrated pipeline first.",
        )

    df = pd.read_csv(RESULTS_PATH)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Integrated risk results file is empty.",
        )

    return df

def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "RiskPulse API",
        "results_available": RESULTS_PATH.exists(),
    }

@app.get("/risk/latest")
def latest_risk():

    df = load_results()

    row = df.iloc[0]

    result = {
        "source_type": clean_value(row.get("source_type")),
        "source": clean_value(row.get("source")),
        "date": clean_value(row.get("date")),
        "entity": clean_value(row.get("entity")),
        "text": clean_value(row.get("text")),

        "sentiment": {
            "label": clean_value(row.get("sentiment_label")),
            "score": clean_value(row.get("sentiment_score")),
        },

        "event": {
            "class": clean_value(row.get("event_class")),
            "confidence": clean_value(row.get("event_confidence")),
            "classification_method": clean_value(
                row.get("classification_method")
            ),
        },

        "impact_score": clean_value(row.get("impact_score")),
        "risk_level": (
            "Critical"
            if float(row.get("impact_score", 0)) >= 9
            else "High"
            if float(row.get("impact_score", 0)) >= 7
            else "Moderate"
            if float(row.get("impact_score", 0)) >= 4
            else "Low"
        ),

        "stress_trigger": clean_value(row.get("stress_trigger")),
    }

    return result

@app.get("/portfolio/stress")
def portfolio_stress():

    df = load_results()

    row = df.iloc[0]

    stress_trigger = str(
        row.get("stress_trigger", "")
    ).strip().lower() in ("true", "1", "yes")

    if not stress_trigger:
        return {
            "stress_trigger": False,
            "message": "No portfolio stress scenario was triggered.",
        }

    event_class = str(
        row.get("event_class", "Unclassified")
    )

    try:
        from src.portfolio_stress import (
            load_portfolio,
            stress_test_portfolio,
            get_stress_scenario,
        )

        portfolio = load_portfolio()

        positions, summary = stress_test_portfolio(
            portfolio,
            event_class,
        )

        scenario = get_stress_scenario(event_class)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio stress calculation failed: {exc}",
        )

    position_records = []

    for _, position in positions.iterrows():
        position_records.append(
            {
                "asset_id": clean_value(position.get("asset_id")),
                "asset_type": clean_value(position.get("asset_type")),
                "sector": clean_value(position.get("sector")),
                "market_value": clean_value(position.get("market_value")),
                "stressed_value": clean_value(position.get("stressed_value")),
                "value_change": clean_value(position.get("value_change")),
                "loss": clean_value(position.get("loss")),
                "loss_percent": clean_value(position.get("loss_percent")),
            }
        )

    return {
        "stress_trigger": True,
        "event_class": event_class,

        "portfolio": {
            "value_before": clean_value(
                summary["portfolio_value_before"]
            ),
            "value_after": clean_value(
                summary["portfolio_value_after"]
            ),
            "loss": clean_value(
                summary["portfolio_loss"]
            ),
            "loss_percent": clean_value(
                summary["portfolio_loss_percent"]
            ),
        },

        "scenario": {
            "equity_shock": clean_value(
                scenario["equity_shock"]
            ),
            "rate_shock": clean_value(
                scenario["rate_shock"]
            ),
            "credit_shock": clean_value(
                scenario["credit_shock"]
            ),
        },

        "positions": position_records,
    }