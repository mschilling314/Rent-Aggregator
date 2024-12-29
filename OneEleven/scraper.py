import requests
from bs4 import BeautifulSoup

from DataClasses.Unit import Unit
from DataClasses.FloorPlan import FloorPlan




if __name__=="__main__":
    response = requests.get(f"https://www.oneelevenchicago.com/floor-plans/?view=grid&sort=unitrent&order=ASC&pagenumber={1}")
    # print(response.text())
    with open("response.txt", "w") as f:
        f.writelines(response.text)