import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import pandasql as ps

from analysis.analyze import get_table_df, get_average_rent_df_for_floor_plans
from plotting.plot import graph_price_per_day


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