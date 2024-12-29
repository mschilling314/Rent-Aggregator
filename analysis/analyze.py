import sqlite3
import pandas as pd
import pandasql as ps


def get_table_df(connection: sqlite3.Connection, table: str) -> pd.DataFrame:
    sql_query = f"SELECT * FROM {table}"
    return pd.read_sql_query(sql = sql_query, con = connection)


def get_average_rent_df_for_floor_plans(floor_plans: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    query = """
            SELECT units.date_of_update AS date, floor_plans.name, AVG(units.price) as price
            FROM units
            JOIN floor_plans
            ON units.floor_plan_id = floor_plans.floor_plan_id
            GROUP BY units.date_of_update, units.floor_plan_id
            """
    return ps.sqldf(query, locals())