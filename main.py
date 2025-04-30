import logging
import os
import sqlite3

from Buildings.Cascade import cascadeScraper

import Buildings.WPE.wpescraper as wpescraper
import analysis.analyze as analyze
from Buildings.OneChicago import scraper as onechicagoScraper 
from Buildings.OneBennett import oneBennettScraper

logging.basicConfig(
    level=logging.INFO,  # Set minimum logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[logging.FileHandler("logs/app.log", mode="a"), logging.StreamHandler()]  # Output to both a file and the console
)

def analyze_for_price_change_or_novelty(db_path: str):
    """
    Write to the database, log significant price changes.
    """
    try:
        conn = sqlite3.connect(db_path)
        units = analyze.get_table_df(conn, "Units")
        price_decreases = analyze.find_price_drops(units)
        if price_decreases:
            units_str = ", ".join(map(str, price_decreases))
            logging.info(f"Price drops detected for the following units: {units_str}")
        price_increases = analyze.find_price_increases(units)
        if price_increases:
            units_str = ", ".join(map(str, price_increases))
            logging.info(f"Price increases detected for these units: {units_str}")
        new_units = analyze.return_new_units(units=units)
        if new_units:
            units_str = ", ".join(map(str, new_units))
            logging.info(f"Units new to the market: {units_str}")
    except Exception as e:
        logging.fatal(f"Analysis failed due to {e}.  Please try again.")



def main():
    """
    Function executed as primary entrypoint into program.
    """
    logging.info("Beginning execution of the app.")

    apartments = [{"name": "Wolf Point East", "scraper": wpescraper, "db_name": "wpe"},
                  {"name": "Cascade", "scraper": cascadeScraper, "db_name": "cascade"},
                  {"name": "OneChicago", "scraper": onechicagoScraper, "db_name": "onechicago"},
                  {"name": "OneBennett", "scraper": oneBennettScraper, "db_name": "onebennett"}]
    
    
    for apartment in apartments:
        logging.info(f"\nScraping website for {apartment['name']}")
        apartment["scraper"].scrape()
        logging.info(f"Writing to database and providing analysis for {apartment['name']}")
        db_path = os.path.join("data", f"{apartment['db_name']}.sqlite")
        analyze_for_price_change_or_novelty(db_path=db_path)
    
    logging.info("Completed execution of the app.")


if __name__=="__main__":
    main()
    
