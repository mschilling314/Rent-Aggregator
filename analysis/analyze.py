import sqlite3
import pandas as pd
import pandasql as ps
import datetime


def get_table_df(connection: sqlite3.Connection, table: str) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame of the given table.
    """
    sql_query = f"SELECT * FROM {table}"
    return pd.read_sql_query(sql = sql_query, con = connection)


def get_average_rent_df_for_floor_plans(floor_plans: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a dataframe that has the average rent for each unit of a floor plan, for each day of data.
    In particular, output has columns date, name, and price.
    """
    query = """
            SELECT units.date_of_update AS date, floor_plans.name, AVG(units.price) as price
            FROM units
            JOIN floor_plans
            ON units.floor_plan_id = floor_plans.floor_plan_id
            GROUP BY units.date_of_update, units.floor_plan_id
            """
    return ps.sqldf(query, locals())


def find_price_drops(units: pd.DataFrame) -> list[str]:
    """
    Returns a list of units whose price has dropped.
    """
    units["date_of_update"] = pd.to_datetime(units["date_of_update"])
    most_recent = units["date_of_update"].max()
    prior_date = most_recent - datetime.timedelta(days=1)

    todays_units = units[units["date_of_update"] == most_recent]
    yesterdays_units = units[units["date_of_update"] == prior_date]

    query = """
            SELECT t.unit_number
            FROM todays_units t
            JOIN yesterdays_units y
            ON t.unit_number = y.unit_number
            WHERE y.price > t.price
            """
    result_df = ps.sqldf(query, locals())
    return list(result_df["unit_number"])

def find_price_increases(units: pd.DataFrame) -> list[str]:
    """
    Returns a list of units whose price has increased.
    """
    units["date_of_update"] = pd.to_datetime(units["date_of_update"])
    most_recent = units["date_of_update"].max()
    prior_date = most_recent - datetime.timedelta(days=1)

    todays_units = units[units["date_of_update"] == most_recent]
    yesterdays_units = units[units["date_of_update"] == prior_date]

    query = """
            SELECT t.unit_number
            FROM todays_units t
            JOIN yesterdays_units y
            ON t.unit_number = y.unit_number
            WHERE y.price < t.price
            """
    result_df = ps.sqldf(query, locals())
    return list(result_df["unit_number"])


def return_new_units(units: pd.DataFrame) -> list[str]:
    """
    Return a list of units that are new to the market.
    """
    units["date_of_update"] = pd.to_datetime(units["date_of_update"])

    most_recent = units["date_of_update"].max()
    yesterday = most_recent - datetime.timedelta(days=1)

    todays_units = units[units["date_of_update"] == most_recent]
    yesterday_units = units[units["date_of_update"] == yesterday]

    new_units = todays_units[~todays_units["unit_number"].isin(yesterday_units["unit_number"])]
    return new_units["unit_number"].to_list()

if __name__ == "__main__":
    db_path = "data/wpe.sqlite"
    conn = sqlite3.connect(db_path)
    units = get_table_df(connection=conn, table="Units")

    print(return_new_units(units))