import datetime
import os
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging

from DataClasses.FloorPlan import FloorPlan, create_floor_plan_table
from DataClasses.Unit import Unit, create_unit_table


def _generate_floorplan_id(id: str) -> int:
    res = 0
    for c in id:
        ascii = ord(c)
        if 48 <= ascii <= 57:
            res = res * 10 + int(c)
        elif 65 <= ascii <= 90:
            res = res * 10 + ascii - 65
        elif 97 <= ascii <= 122:
            res = res * 10 + ascii - 97
        else:
            res = res * 10 + 0
    return res


def grab_webpage(url: str="https://liveonechicago.com/floor-plans"):
    try:
        resp = requests.get(url)
        if resp.ok:
            return BeautifulSoup(resp.text, 'html.parser')
    except:
        logging.ERROR("Failed to get OneChicago Website.")
    
def get_floorplans(html: BeautifulSoup) -> list[FloorPlan]:
    rows = html.find("tbody", class_="unit-list__table-body").findAll("tr", class_="unit-list__row")
    res = []
    for row in rows:
        floorplan_id_str = row.find("td", class_="unit-list__col--unit").text.strip()
        floorplan_id_encoded = _generate_floorplan_id(floorplan_id_str)
        rooms = row.find("td", class_="unit-list__col--rooms").text.strip()
        baths = float(rooms.split("/")[1].strip().split("\xa0")[0])
        beds = rooms.split("/")[0].strip()
        if beds == "Studio":
            beds = 0.0
        elif beds == "Junior 1 Bed":
            beds = 0.5
        else:
            beds = float(beds.split(" ")[0])
        size = int("".join(row.find("td", class_="unit-list__col--sf").text.strip().split(" ")[0].split(",")))
        img = row.find("td", class_="unit-list__col--links").find("a").href
        
        res.append(FloorPlan(id = floorplan_id_encoded, common_name=floorplan_id_str, beds=beds, baths=baths, sq_ft=size, img_url=img))
    return res


def _parse_unit(floorplan: int, unit_page: BeautifulSoup) -> Unit:
    rows = unit_page.find("tbody", class_="unit-availability__table-body").findAll("tr")
    for row in rows:
        data = row.findAll("td")
        unit = data[0].text
        price = float("".join(data[1].text[1:].split(",")))
        avail = data[2].text.strip()
    return Unit(unit_number=unit, floor_plan_id=floorplan, price=price, date_available=avail)


def get_units(floorplans: list[FloorPlan]) -> list[Unit]:
    res = []
    for floorplan in floorplans:
        url = f"https://liveonechicago.com/floor-plans?view=availability&id={floorplan.name}"
        try:
            resp = requests.get(url)
            if resp.ok:
                soup = BeautifulSoup(resp.text, "html.parser")
                res.append(_parse_unit(floorplan.floor_plan_id, soup))
        except:
            logging.ERROR(f"Broken web request for floorplan {floorplan.name}")
    return res


def scrape() -> None:
    soup = grab_webpage()
    floorplans = get_floorplans(soup)
    units = get_units(floorplans)

    db_path = os.path.join("data", "onechicago.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_floor_plan_table(cursor)
    create_unit_table(cursor)

    for floorplan in floorplans:
        floorplan.insert_into_sqlite(cursor)
    for unit in units:
        unit.insert_into_sqlite(cursor)
    
    conn.commit()
    conn.close()