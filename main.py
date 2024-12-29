import logging

import WPE.wpescraper as wpescraper

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
    logging.info("Completed execution of the app.")


if __name__=="__main__":
    main()