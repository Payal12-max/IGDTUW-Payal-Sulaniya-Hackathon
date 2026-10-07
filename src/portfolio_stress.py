"""
RiskPulse Portfolio Stress Testing Engine.

Applies simplified event-driven shocks to a synthetic
wholesale banking portfolio.

This is a strategic stress-testing prototype, not a
full market-pricing or regulatory capital model.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = PROJECT_ROOT / "data" / "portfolio.csv"


# Simplified scenarios based on the hackathon case statement.
STRESS_SCENARIOS = {
    "Geopolitical": {
        "equity_shock": -0.10,
        "rate_shock": 0.02,
        "credit_shock": 0.05,
    },
    "Macroeconomic": {
        "equity_shock": -0.08,
        "rate_shock": 0.02,
        "credit_shock": 0.03,
    },
    "Credit Event": {
        "equity_shock": -0.10,
        "rate_shock": 0.01,
        "credit_shock": 0.10,
    },
    "Regulatory": {
        "equity_shock": -0.05,
        "rate_shock": 0.01,
        "credit_shock": 0.03,
    },
}


def load_portfolio():
    """Load and validate the synthetic portfolio."""

    portfolio = pd.read_csv(PORTFOLIO_PATH)

    required_columns = [
        "asset_id",
        "asset_type",
        "sector",
        "description",
        "market_value",
        "rate_sensitivity",
        "equity_sensitivity",
        "credit_sensitivity",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in portfolio.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Portfolio is missing required columns: {missing_columns}"
        )

    return portfolio


def get_stress_scenario(event_class):
    """
    Return the predefined stress scenario for an event class.
    """

    return STRESS_SCENARIOS.get(event_class)


def calculate_stressed_value(row, scenario):
    """
    Calculate the stressed value of one portfolio position.

    Simplified approximation:

    Equity effect:
        market_value × equity_sensitivity × equity_shock

    Rate effect:
        market_value × rate_sensitivity × (-rate_shock)

    Credit effect:
        market_value × credit_sensitivity × (-credit_shock)

    The signs reflect the simplified assumption that:
    - falling equity prices reduce value
    - rising rates reduce value
    - worsening credit conditions reduce value
    """

    market_value = row["market_value"]

    equity_effect = (
        market_value
        * row["equity_sensitivity"]
        * scenario["equity_shock"]
    )

    rate_effect = (
        market_value
        * row["rate_sensitivity"]
        * (-scenario["rate_shock"])
    )

    credit_effect = (
        market_value
        * row["credit_sensitivity"]
        * (-scenario["credit_shock"])
    )

    stressed_value = (
        market_value
        + equity_effect
        + rate_effect
        + credit_effect
    )

    return stressed_value


def stress_test_portfolio(portfolio, event_class):
    """
    Apply the appropriate stress scenario to the portfolio.

    Returns position-level and portfolio-level stress results.
    """

    scenario = get_stress_scenario(event_class)

    if scenario is None:
        raise ValueError(
            f"No stress scenario is defined for event class: {event_class}"
        )

    results = portfolio.copy()

    results["stressed_value"] = results.apply(
        lambda row: calculate_stressed_value(row, scenario),
        axis=1,
    )

    results["value_change"] = (
        results["stressed_value"]
        - results["market_value"]
    )

    results["loss"] = (
        -results["value_change"]
    ).clip(lower=0)

    results["loss_percent"] = (
        results["loss"]
        / results["market_value"]
        * 100
    )

    portfolio_before = results["market_value"].sum()
    portfolio_after = results["stressed_value"].sum()

    total_change = portfolio_after - portfolio_before

    summary = {
        "event_class": event_class,
        "portfolio_value_before": portfolio_before,
        "portfolio_value_after": portfolio_after,
        "portfolio_change": total_change,
        "portfolio_loss": max(-total_change, 0),
        "portfolio_loss_percent": (
            max(-total_change, 0)
            / portfolio_before
            * 100
        ),
    }

    return results, summary


def main():
    print("\n=== RiskPulse Portfolio Stress Testing ===\n")

    portfolio = load_portfolio()

    print(f"Portfolio positions: {len(portfolio)}")
    print(
        f"Portfolio value: "
        f"{portfolio['market_value'].sum():,.2f}"
    )

    event_class = "Geopolitical"

    results, summary = stress_test_portfolio(
        portfolio,
        event_class,
    )

    print(f"\nStress scenario: {event_class}")
    print("\nScenario assumptions:")
    print(f"Equity shock: -10%")
    print(f"Interest-rate shock: +2%")
    print(f"Credit shock: +5%")

    print("\n=== Portfolio Stress Result ===")
    print(
        f"Value before: "
        f"{summary['portfolio_value_before']:,.2f}"
    )
    print(
        f"Value after:  "
        f"{summary['portfolio_value_after']:,.2f}"
    )
    print(
        f"Portfolio loss: "
        f"{summary['portfolio_loss']:,.2f}"
    )
    print(
        f"Loss percentage: "
        f"{summary['portfolio_loss_percent']:.2f}%"
    )

    print("\n=== Position-Level Results ===")
    print(
        results[
            [
                "asset_id",
                "asset_type",
                "market_value",
                "stressed_value",
                "loss",
                "loss_percent",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()