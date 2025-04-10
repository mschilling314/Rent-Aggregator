import logging
import sqlite3

import WPE.wpescraper as wpescraper
import analysis.analyze as analyze

logging.basicConfig(
    level=logging.INFO,  # Set minimum logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[logging.FileHandler("logs/app.log", mode="a"), logging.StreamHandler()]  # Output to both a file and the console
)


def main():
    """
    Function executed as primary entrypoint into program.
    """
    logging.info("Beginning execution of the app.")
    wpescraper.scrape()

    try:
        db_path = "data/wpe.sqlite"
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
    logging.info("Completed execution of the app.")


if __name__=="__main__":
    main()
    
