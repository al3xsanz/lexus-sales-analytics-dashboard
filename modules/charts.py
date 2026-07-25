from pathlib import Path

import matplotlib.pyplot as plt


CHARTS_FOLDER = Path("charts")


def create_charts(
    dataframe,
    monthly_sales,
    model_sales,
    salesperson_sales,
    weekday_sales
):
    """
    Generate all charts for the dealership analysis.
    """

    CHARTS_FOLDER.mkdir(exist_ok=True)

    # -------------------------------------------------
    # Monthly Units Sold
    # -------------------------------------------------

    plt.figure(figsize=(10, 6))

    plt.bar(
        monthly_sales["month"],
        monthly_sales["units"]
    )

    plt.title(
        "Monthly Units Sold",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Month")
    plt.ylabel("Units Sold")

    plt.grid(
        axis="y",
        alpha=0.30
    )

    for index, value in enumerate(
        monthly_sales["units"]
    ):
        plt.text(
            index,
            value + 1,
            f"{value:.0f}",
            ha="center"
        )

    plt.tight_layout()

    plt.savefig(
        CHARTS_FOLDER /
        "monthly_units_sold.png",
        dpi=300
    )

    plt.close()

    # -------------------------------------------------
    # Monthly Revenue Trend
    # -------------------------------------------------

    plt.figure(figsize=(10, 6))

    plt.plot(
        monthly_sales["month"],
        monthly_sales["revenue"],
        marker="o",
        linewidth=2
    )

    plt.title(
        "Monthly Revenue",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")

    plt.grid(alpha=0.30)

    plt.tight_layout()

    plt.savefig(
        CHARTS_FOLDER /
        "monthly_revenue.png",
        dpi=300
    )

    plt.close()

    # -------------------------------------------------
    # Top Models
    # -------------------------------------------------

    top_models = (
        model_sales
        .sort_values(
            "units",
            ascending=True
        )
        .tail(10)
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        top_models.index,
        top_models["units"]
    )

    plt.title(
        "Top 10 Models by Units",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Units")

    plt.grid(
        axis="x",
        alpha=0.30
    )

    plt.tight_layout()

    plt.savefig(
        CHARTS_FOLDER /
        "top_models.png",
        dpi=300
    )

    plt.close()

    # -------------------------------------------------
    # Salesperson Leaderboard
    # -------------------------------------------------

    top_salespeople = (
        salesperson_sales
        .sort_values(
            "revenue",
            ascending=True
        )
        .tail(10)
    )

    plt.figure(figsize=(11, 7))

    plt.barh(
        top_salespeople.index,
        top_salespeople["revenue"]
    )

    plt.title(
        "Top Salespeople by Revenue",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Revenue ($)")

    plt.grid(
        axis="x",
        alpha=0.30
    )

    plt.tight_layout()

    plt.savefig(
        CHARTS_FOLDER /
        "top_salespeople.png",
        dpi=300
    )

    plt.close()

    # -------------------------------------------------
    # Revenue by Weekday
    # -------------------------------------------------

    weekday_ranked = (
        weekday_sales
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    plt.figure(figsize=(10, 6))

    plt.bar(
        weekday_ranked.index,
        weekday_ranked["revenue"]
    )

    plt.title(
        "Revenue by Weekday",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Weekday")
    plt.ylabel("Revenue ($)")

    plt.xticks(rotation=30)

    plt.grid(
        axis="y",
        alpha=0.30
    )

    plt.tight_layout()

    plt.savefig(
        CHARTS_FOLDER /
        "weekday_revenue.png",
        dpi=300
    )

    plt.close()

    # -------------------------------------------------
    # Powertrain Mix
    # -------------------------------------------------

    if "powertrain" in dataframe.columns:

        powertrain = (
            dataframe
            .groupby("powertrain")["units"]
            .sum()
        )

        plt.figure(figsize=(8, 8))

        plt.pie(
            powertrain,
            labels=powertrain.index,
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title(
            "Powertrain Mix",
            fontsize=16,
            fontweight="bold"
        )

        plt.tight_layout()

        plt.savefig(
            CHARTS_FOLDER /
            "powertrain_mix.png",
            dpi=300
        )

        plt.close()

    # -------------------------------------------------
    # Revenue Growth
    # -------------------------------------------------

    if (
        "revenue_growth_pct"
        in monthly_sales.columns
    ):

        growth = (
            monthly_sales
            .dropna(
                subset=[
                    "revenue_growth_pct"
                ]
            )
        )

        plt.figure(figsize=(10, 6))

        plt.bar(
            growth["month"],
            growth[
                "revenue_growth_pct"
            ]
        )

        plt.axhline(
            y=0,
            linewidth=1
        )

        plt.title(
            "Revenue Growth (%)",
            fontsize=16,
            fontweight="bold"
        )

        plt.xlabel("Month")
        plt.ylabel("Growth (%)")

        plt.grid(
            axis="y",
            alpha=0.30
        )

        plt.tight_layout()

        plt.savefig(
            CHARTS_FOLDER /
            "revenue_growth.png",
            dpi=300
        )

        plt.close()

    print("\nCharts generated successfully.")
    print(
        f"Saved inside: "
        f"{CHARTS_FOLDER}"
    )