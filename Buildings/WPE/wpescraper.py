import requests
from bs4 import BeautifulSoup
import sqlite3
from typing import Callable
import concurrent.futures

from DataClasses.Unit import Unit, create_unit_table
from DataClasses.FloorPlan import FloorPlan, create_floor_plan_table



def get_paginated_response_text(base_url: str, end_condition: Callable[[str], str], starting_page: int=0) -> str:
    """
    Joins paginated response results after calling the given URL, returns the string representation of the webpages.
    """
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
    """
    Gets a list of FloorPlans.
    """
    # First, need to get response from WPE Website, something like:
    base_url = "https://wolfpointeast.com/floor-plans/?bedroom=&availability=&sqft=&max-price=&pagenumber="
    response_text = get_paginated_response_text(base_url=base_url, end_condition=lambda x: "Your search didn't return any results. Please adjust your options above." in x)
    
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
    """
    Gets a list of units given the floor plan ID.
    """
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
        date_available = str(unit.find_all("li")[-1].find("span"))[6:-7]
        
        unit_list.append(Unit(unit_number=unit_number, floor_plan_id=floor_plan_id, price=price, date_available=date_available))
    return unit_list



def scrape():
    """
    Scrapes the rentwpe.com site, puts results in two tables in SQLite DB for WPE.
    """
    floor_plans = get_floor_plans()
   
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start concurrent fetching of units for each floor plan
        future_to_floor_plan = {executor.submit(get_units, floor_plan.get_id()): floor_plan for floor_plan in floor_plans}
        
        units = []
        for future in concurrent.futures.as_completed(future_to_floor_plan):
            floor_plan = future_to_floor_plan[future]
            try:
                units.extend(future.result())  # Add the units for this floor plan to the list
            except Exception as exc:
                print(f"Error fetching units for floor plan {floor_plan.get_id()}: {exc}")
        
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
    