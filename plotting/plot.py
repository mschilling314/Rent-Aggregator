import pandas as pd
import matplotlib.pyplot as plt

def graph_price_per_day(df: pd.DataFrame, floor_plan_name: str="A21", xaxis: str="Date", yaxis: str="Price", title: str="Price per Day") -> None:
    """
    Graphs the price given on a daily basis.

    Inputs:
    ------
    df: A Pandas DataFrame that MUST have "date" and "price" columns.
    """
    df_to_plot = df[df["name"] == floor_plan_name]
    plt.plot(df_to_plot["date"], df_to_plot["price"])

    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    plt.xticks(rotation=90)

    plt.show()