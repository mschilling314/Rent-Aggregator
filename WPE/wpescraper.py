import requests
from bs4 import BeautifulSoup
import sqlite3
from typing import Callable

from DataClasses.Unit import Unit
from DataClasses.FloorPlan import FloorPlan



def get_paginated_response_text(base_url: str, end_condition: Callable[[str], str], starting_page: int=0) -> str:
    page = starting_page
    response_text = []
    while True:
        url = f"{base_url}{page}"
        try:
            response = requests.get(url=url)
        except:
            print("Invalid response returned.")
            break
        finally:
            if end_condition(response.text):
                break
            response_text.append(response.text)
            page += 1

    return "".join(response_text)


def get_floor_plans() -> list[FloorPlan]:
    # First, need to get response from WPE Website, something like:
    base_url = "https://wolfpointeast.com/floor-plans/?bedroom=&availability=&sqft=&max-price=&pagenumber="
    response_text = get_paginated_response_text(base_url=base_url, end_condition=lambda x: "Your search didn't return any results. Please adjust your options above." in x)
    with open("response.txt", "w") as f:
        f.writelines(response_text)
    
    # now that we have the response text, we need to parse with beautiful soup
    soup = BeautifulSoup(response_text, "html.parser")
    floor_plans = soup.find_all("div", class_="plan-details")
    floor_plan_objects = []
    visited_plan_ids = set()
    for floor_plan in floor_plans:
        floor_plan_id = floor_plan.find("a", class_="plan-img")["href"].split("/")[-2]
        if floor_plan_id in visited_plan_ids:
            continue
        else:
            visited_plan_ids.add(floor_plan_id)
        img_url = floor_plan.find("img")["src"]
        common_name = str(floor_plan.find("span")).split("<")[1].split(">")[1]
        rooms = " ".join(str(floor_plan.find_all("li")[0]).split()[1:-1])
        if rooms.split()[0] == "Studio":
            beds = 0
            baths = 1
        elif rooms.split()[0] == "Convertible":
            beds = 0.5
            baths = 1
        else:
            beds = float(rooms.split()[0])
            baths = float(rooms.split()[-2])
        sq_ft = " ".join(str(floor_plan.find_all("li")[1]).split()[1:-1])
        floor_plan_objects.append(FloorPlan(id=floor_plan_id, common_name=common_name, beds=beds, baths=baths, sq_ft=sq_ft, img_url=img_url))
    return floor_plan_objects


def get_units(floor_plan_id: int) -> list[Unit]:
    base_url = f"https://wolfpointeast.com/floor-plans/{floor_plan_id}?pagenumber="
    response_text = get_paginated_response_text(base_url=base_url, end_condition=lambda x: "class=\"plan-details\"" not in x)
    soup = BeautifulSoup(response_text, "html.parser")
    units = soup.find_all("div", class_="plan-details")
    unit_list = []
    visited_units = set()

    for unit in units:
        # unit, price
        unit_number = unit.find("a", class_="plan-img")["href"].split("/")[-2]
        if unit_number in visited_units:
            continue
        else:
            visited_units.add(unit_number)
        price = -1
        if "$" in unit.text:
            price_index = unit.text.index("$")
            price_str = unit.text[price_index + 1:].split()[0]
            price = float("".join(price_str.split(",")))
        elif "CALL FOR PRICING" in unit.text:
            price = 0
        unit_list.append(Unit(unit_number=unit_number, floor_plan_id=floor_plan_id, price=price))
    
    return unit_list

def create_floor_plan_table(cursor: sqlite3.Cursor) -> None:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FloorPlans (
        floor_plan_id INTEGER PRIMARY KEY,
        name TEXT,
        beds REAL,
        baths REAL,
        sq_ft INTEGER,
        img_url TEXT
    )
    ''')

def create_unit_table(cursor: sqlite3.Cursor) -> None:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Units (
                   unit_number TEXT,
                   floor_plan_id INTEGER,
                   price REAL,
                   date_of_update TEXT,
                   PRIMARY KEY (unit_number, date_of_update),
                   FOREIGN KEY (floor_plan_id) REFERENCES FloorPlans(floor_plan_id)
                   )
                   ''')


def scrape():
    """
    Scrapes the rentwpe.com site, puts results in two tables in SQLite DB for WPE.
    """
    floor_plans = get_floor_plans()
    units = []
    for floor_plan in floor_plans:
        units.extend(get_units(floor_plan_id=floor_plan.get_id()))

    # with open("response.txt", "w") as f:
    #     for unit in units:
    #         f.write(f"{unit}\n")
        
    conn = sqlite3.connect("data/wpe.sqlite")
    cursor = conn.cursor()

    create_unit_table(cursor=cursor)
    create_floor_plan_table(cursor=cursor)

    for floor_plan in floor_plans:
        floor_plan.insert_into_sqlite(cursor=cursor)
    for unit in units:
        unit.insert_into_sqlite(cursor=cursor)
    
    conn.commit()
    conn.close()


if __name__=="__main__":
    scrape()