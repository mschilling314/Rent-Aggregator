import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import pandasql as ps

from analysis.analyze import get_table_df, get_average_rent_df_for_floor_plans


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

    plt.show()

def print_price_per_day_for_floor_plan(df: pd.DataFrame, floor_plan_name: str) -> None:
    print(df[df["name"] == floor_plan_name])


if __name__=="__main__":
    db_path = "data/wpe.sqlite"
    conn = sqlite3.connect(db_path)
    floor_plans = get_table_df(conn, "FloorPlans")
    units = get_table_df(conn, "Units")
    
    average_rent_by_floor_plan = get_average_rent_df_for_floor_plans(floor_plans=floor_plans, units=units)

    print_price_per_day_for_floor_plan(average_rent_by_floor_plan, "A+D-2")
    graph_price_per_day(average_rent_by_floor_plan, yaxis="Average Price", floor_plan_name="A+D-2")