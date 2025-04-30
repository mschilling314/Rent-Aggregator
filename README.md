# Rent Aggregator
## Summary
The purpose of this repository is to collect data from various buildings I'm interested in within the loop, so I can identify whether I'm getting a good deal or not.

## Structure
The main entrypoint is, perhaps fittingly, `main.py`.  This file will be run daily at midnight UTC to update the databases.  As part of the log file (`logs/app.log`), I also record units new to the market, as well as units whose prices have increased/decreased.  I may use this as the groundwork for alerting in the future, should I hook this up to a cloud provider with the capability to send email (or build my own SMTP server).


### RelevantDirectories
DataClasses has two classes, Unit and FloorPlan, each of which are useful containers for the data I obtain from scraping.  I encapsulated them as a data class so that the code for writing to the databases is uniform and only present once, allowing for easier extension.  

Buildings has modules for each building I'm interested in, with specific functions based on the structure of that building's website.

The `data` directory is where the databases live at the moment, they're simple SQLite databases I change when the main script runs, in the GitHub Actions version of this I do in fact commit these changes to the repository.  Perhaps in the future if the data grows to be too much, I'll migrate this to an actual database, as of writing this I'm under the GitHub limits by a factor of 1,000 so that will be a problem if I'm still collecting data in about a year (given that adding buildings will decrease the time until I hit that limit).

## Process to add a Building
1. Create new module in Buildings, where the Python file has a scrape function that takes no arguments, scrapes the website, and writes to the proper database
2. Create SQLite file in `data/`
3. Test flow, make sure data ends up in SQLite file
4. Add configuration to `apartments` dictionary in `main.py`
5. Add `git add {database_name}` to `.github/workflows/daily_run.yaml`
6. Open PR, ensure checks pass before merging

## To-Do
[ ] Add remaining buildings of interest
[ ] Refactor for better concurrency/asynchronous calls with asyncio module
[ ] Migrate data to different database for longevity
[ ] Add documentation on how to set up