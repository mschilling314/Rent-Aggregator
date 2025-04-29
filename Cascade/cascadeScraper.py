import datetime
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging

from DataClasses.FloorPlan import FloorPlan, create_floor_plan_table
from DataClasses.Unit import Unit, create_unit_table

def grab_webpage(url: str="https://cascadeapartments.com/availability") -> BeautifulSoup:
    try:
        resp = requests.get(url=url)
        if resp.ok:
            return BeautifulSoup(resp.text, "html.parser")
    except:
        logging.ERROR("Failed to get Cascade Apartments website.")
        raise Exception("Website get failed.")
    

def get_floorplans(html: BeautifulSoup) -> list[FloorPlan]:
    rows = html.find("tbody", class_="availability__body").findAll("tr")
    res = []
    for row in rows:
        id = row["data-unit"]
        beds = row["data-br"].split("/")[0].split(" ")[0]
        if beds == "Studio":
            beds = 0
        elif beds == "Convertible":
            beds = 0.5
        else:
            beds = float(beds)
        baths = float(row["data-br"].split("/")[1].split(" ")[1])
        size_str = str(row["data-sf"]).split("–")[0]
        size = int("".join(size_str.split(","))) # only gives sq ft of no-balcony units
        floor_plan = FloorPlan(id=id, common_name=id, beds=beds, baths=baths, sq_ft=size)
        res.append(floor_plan)
    return res


def get_unit(html: BeautifulSoup) -> list[Unit]:
    rows = html.findAll("div", class_="unit-detail")
    res = []
    today = datetime.date.today()
    for row in rows:
        id = row.find("h6").text.strip()
        unit_table = row.findAll("tr")
        for unit in unit_table:
            datum = unit.findAll("td")[0:4]
            unit_number = datum[0].text.strip()[1:]
            # size = datum[1].text.strip()
            price = float("".join(datum[2].text.strip()[1:].split(",")))
            available = datum[3].text.strip()
            res.append(Unit(unit_number=unit_number, floor_plan_id=id, price=price, date_available=available))
    return res


def scrape() -> None:
    soup = grab_webpage()
    floorplans = get_floorplans(soup)
    units = get_unit(soup)

    conn = sqlite3.connect("data/cascade.sqlite")
    cursor = conn.cursor()
    create_floor_plan_table(cursor=cursor)
    create_unit_table(cursor=cursor)

    for floorplan in floorplans:
        floorplan.insert_into_sqlite(cursor)
    for unit in units:
        unit.insert_into_sqlite(cursor)
    
    conn.commit()
    conn.close()



if __name__=="__main__":
    soup = grab_webpage(), 'html.parser'
    print(get_floorplans(soup)[0])
    print(get_unit(soup)[0])
    # scrape()
