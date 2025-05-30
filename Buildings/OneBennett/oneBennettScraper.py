import io
import logging
import os
import sqlite3
import requests
import fitz
from bs4 import BeautifulSoup
import asyncio
import aiohttp

from DataClasses.FloorPlan import FloorPlan, create_floor_plan_table
from DataClasses.Unit import Unit, create_unit_table


def _check_valid_page(soup: BeautifulSoup) -> bool:
    if soup.find("div", class_="contents"):
            if soup.find("div", class_="contents").find("h3"):
                if soup.find("div", class_="contents").find("h3").text == "Sorry, we could not find any results that match your search.":
                     return False
    return True


def _pull_article(soup: BeautifulSoup) -> BeautifulSoup:
     return soup.find("article", attrs={"data-variant": True})



def get_tiles(base_url: str="https://www.relatedrentals.com/search?city=36&property=%5B%5B%3A%3C%3A%5D%5D(2212016)%5B%5B%3A%3E%3A%5D%5D&page="):
    page = 0
    res = []
    while True:
        try:
            resp = requests.get(f"{base_url}{page}")
            if resp.ok:
                soup = BeautifulSoup(resp.text, 'html.parser')
                if _check_valid_page(soup):
                    page += 1
                    res.extend(filter(lambda x: x, map(_pull_article, soup.findAll("div", class_="views-row"))))
                else:
                    break
        except Exception as e:
             logging.error(f"Request to OneBennett failed with {e}")
    return res


def extract_tile_info(article: BeautifulSoup) -> dict:
     rooms = article["data-variant"]
     beds = float(rooms.split(" ")[0][:-2])
     baths = float(rooms.split(" ")[1][:-2])
     price = float(article["data-price"])
     avail = article.find("div", class_="unit-availability-date").find("dd").text
     link = article["about"]
     return {"beds": beds, "baths": baths, "price": price, "avail": avail, "link": link}


async def get_sq_ft(pdf_link: str) -> int:
    sqft = 0
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(pdf_link) as resp:
                if resp.status < 400:
                    content = await resp.read()
                    pdf_file = io.BytesIO(content)
                    doc = fitz.open(stream=pdf_file, filetype="pdf")
                    for page in doc:
                        text = page.get_text()
                        if "FT2" in text:
                            sqft = text.split(" FT2")[0].split("\n")[-1]
                else:
                    logging.error(f"Non-200 status on {pdf_link}")
        except Exception as e:
            logging.error(f"Failed to retrieve floorplan at {pdf_link}, got {e}")
    return sqft


async def get_floorplan_info(link: str):
    res = {}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://www.relatedrentals.com{link}") as resp:
                if resp.status == 200:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    res["unit"] = soup.find("title").text.split("#")[1].split(" ")[0]
                    floorplan_href = soup.find("a", string="DOWNLOAD FLOORPLAN")['href']
                    res["floorplan_link"] = f"https://www.relatedrentals.com{floorplan_href}"
                    res["floorplan_id"] = floorplan_href.split("/")[-1].split(".")[0].split("_")[-1]
                    res["sqft"] = await get_sq_ft(res["floorplan_link"])
                else:
                    logging.error(f"Non-200 status on {link}")
        except Exception as e:
            logging.error(f"Couldn't access {link} on OneBennett, got {e}")
    return res


async def get_info_from_tiles(tiles: BeautifulSoup) -> tuple[list[Unit], list[FloorPlan]]:
    units = []
    floor_plans = []
    for tile in tiles:
        info = extract_tile_info(tile)
        other_info = await get_floorplan_info(info["link"])
        if other_info:
            info = info | other_info
        units.append(Unit(info["unit"], floor_plan_id=int(info["floorplan_id"]), price=info["price"], date_available=info["avail"]))
        floor_plans.append(FloorPlan(id=int(info["floorplan_id"]), common_name=info["floorplan_id"], beds=info["beds"], baths=info["baths"], sq_ft=info["sqft"], img_url=info["floorplan_link"]))
    
    return units, floor_plans


async def scrape():
    tiles = get_tiles()
    units, floorplans = await get_info_from_tiles(tiles)
    
    db_path = os.path.join("data", "onebennett.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_floor_plan_table(cursor)
    create_unit_table(cursor)

    for unit in units:
        unit.insert_into_sqlite(cursor)
    for floorplan in floorplans:
        floorplan.insert_into_sqlite(cursor)
        
    conn.commit()
    conn.close()