def search_model(dataframe):
    """
    Search for one model or a group of related models.
    """

    search_term = input(
        "\nEnter a Lexus model, such as RX350 or NX350h: "
    ).strip()

    matching_sales = dataframe[
        dataframe["model"].str.contains(
            search_term,
            case=False,
            na=False
        )
    ]

    if matching_sales.empty:
        print(
            f"\nNo model found matching: {search_term}"
        )
        return

    model_summary = (
        matching_sales
        .groupby("model")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values(
            "units",
            ascending=False
        )
    )

    model_summary["revenue"] = (
        model_summary["revenue"]
        .round(2)
    )

    model_summary["average_revenue"] = (
        model_summary["average_revenue"]
        .round(2)
    )

    monthly_summary = (
        matching_sales
        .groupby(
            ["month_number", "month"],
            as_index=False
        )
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values("month_number")
    )

    monthly_summary["revenue"] = (
        monthly_summary["revenue"]
        .round(2)
    )

    monthly_summary["average_revenue"] = (
        monthly_summary["average_revenue"]
        .round(2)
    )

    print("\nMODEL SEARCH RESULTS")
    print("=" * 60)
    print(model_summary)

    print("\nPERFORMANCE BY MONTH")
    print("-" * 60)
    print(
        monthly_summary.to_string(
            index=False
        )
    )


def search_salesperson(dataframe):
    """
    Search for a salesperson and display performance.
    """

    search_term = input(
        "\nEnter salesperson name: "
    ).strip()

    matching_sales = dataframe[
        dataframe["salesperson"].str.contains(
            search_term,
            case=False,
            na=False
        )
    ]

    if matching_sales.empty:
        print(
            f"\nNo salesperson found matching: "
            f"{search_term}"
        )
        return

    salesperson_summary = (
        matching_sales
        .groupby("salesperson")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    salesperson_summary["revenue"] = (
        salesperson_summary["revenue"]
        .round(2)
    )

    salesperson_summary["average_revenue"] = (
        salesperson_summary[
            "average_revenue"
        ].round(2)
    )

    monthly_summary = (
        matching_sales
        .groupby(
            ["month_number", "month"],
            as_index=False
        )
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values("month_number")
    )

    monthly_summary["revenue"] = (
        monthly_summary["revenue"]
        .round(2)
    )

    monthly_summary["average_revenue"] = (
        monthly_summary[
            "average_revenue"
        ].round(2)
    )

    print("\nSALESPERSON SEARCH RESULTS")
    print("=" * 60)
    print(salesperson_summary)

    print("\nPERFORMANCE BY MONTH")
    print("-" * 60)
    print(
        monthly_summary.to_string(
            index=False
        )
    )


def filter_by_month(dataframe):
    """
    Filter and summarize sales for one month.
    """

    available_months = (
        dataframe[
            ["month_number", "month"]
        ]
        .drop_duplicates()
        .sort_values("month_number")
    )

    print("\nAVAILABLE MONTHS")
    print("-" * 35)

    for _, row in available_months.iterrows():
        print(
            f"{int(row['month_number'])}. "
            f"{row['month']}"
        )

    month_choice = input(
        "\nEnter the month number: "
    ).strip()

    try:
        month_number = int(
            month_choice
        )
    except ValueError:
        print(
            "\nPlease enter a valid month number."
        )
        return

    filtered_dataframe = dataframe[
        dataframe["month_number"]
        == month_number
    ]

    if filtered_dataframe.empty:
        print(
            "\nNo sales data found for that month."
        )
        return

    month_name = (
        filtered_dataframe["month"]
        .iloc[0]
    )

    total_units = (
        filtered_dataframe["units"]
        .sum()
    )

    total_revenue = (
        filtered_dataframe["revenue"]
        .sum()
    )

    average_revenue = (
        filtered_dataframe["revenue"]
        .mean()
    )

    top_models = (
        filtered_dataframe
        .groupby("model")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values(
            "units",
            ascending=False
        )
        .head(10)
    )

    top_models["revenue"] = (
        top_models["revenue"]
        .round(2)
    )

    top_models["average_revenue"] = (
        top_models["average_revenue"]
        .round(2)
    )

    print("\n" + "=" * 60)
    print(
        f"              "
        f"{month_name.upper()} REPORT"
    )
    print("=" * 60)

    print(
        f"Total units:             "
        f"{total_units:,.0f}"
    )

    print(
        f"Total revenue:           "
        f"${total_revenue:,.2f}"
    )

    print(
        f"Average revenue:         "
        f"${average_revenue:,.2f}"
    )

    print("\nTop models:")
    print("-" * 60)
    print(top_models)


def filter_by_powertrain(dataframe):
    """
    Filter sales by powertrain type.
    """

    powertrain_options = {
        "1": "Gas",
        "2": "Hybrid",
        "3": "Plug-in Hybrid",
        "4": "EV",
    }

    print("\nPOWERTRAIN FILTER")
    print("-" * 35)

    print("1. Gas")
    print("2. Hybrid")
    print("3. Plug-in Hybrid")
    print("4. EV")

    choice = input(
        "\nSelect a powertrain: "
    ).strip()

    selected_powertrain = (
        powertrain_options.get(choice)
    )

    if selected_powertrain is None:
        print(
            "\nInvalid powertrain selection."
        )
        return

    filtered_dataframe = dataframe[
        dataframe["powertrain"]
        == selected_powertrain
    ]

    if filtered_dataframe.empty:
        print(
            f"\nNo {selected_powertrain} "
            f"vehicles found."
        )
        return

    summary = (
        filtered_dataframe
        .groupby("model")
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
            average_revenue=("revenue", "mean")
        )
        .sort_values(
            "units",
            ascending=False
        )
    )

    summary["revenue"] = (
        summary["revenue"]
        .round(2)
    )

    summary["average_revenue"] = (
        summary["average_revenue"]
        .round(2)
    )

    total_units = (
        filtered_dataframe["units"]
        .sum()
    )

    total_revenue = (
        filtered_dataframe["revenue"]
        .sum()
    )

    average_revenue = (
        filtered_dataframe["revenue"]
        .mean()
    )

    print("\n" + "=" * 60)
    print(
        f"          "
        f"{selected_powertrain.upper()} SALES"
    )
    print("=" * 60)

    print(
        f"Total units:             "
        f"{total_units:,.0f}"
    )

    print(
        f"Total revenue:           "
        f"${total_revenue:,.2f}"
    )

    print(
        f"Average revenue:         "
        f"${average_revenue:,.2f}"
    )

    print("\nModel performance:")
    print("-" * 60)
    print(summary)


def filter_sales_data(dataframe):
    """
    Display the sales-filter submenu.
    """

    while True:
        print("\n" + "=" * 50)
        print("             SALES DATA FILTERS")
        print("=" * 50)

        print("1. Filter by month")
        print("2. Filter by powertrain")
        print("3. Filter by model")
        print("4. Filter by salesperson")
        print("0. Return to main menu")

        print("=" * 50)

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice == "1":
            filter_by_month(
                dataframe
            )

        elif choice == "2":
            filter_by_powertrain(
                dataframe
            )

        elif choice == "3":
            search_model(
                dataframe
            )

        elif choice == "4":
            search_salesperson(
                dataframe
            )

        elif choice == "0":
            break

        else:
            print(
                "\nInvalid choice. "
                "Enter a number from 0 to 4."
            )