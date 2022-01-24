from urllib.request import urlopen
from bs4 import BeautifulSoup
from .urlworker import UrlWorker
from .databaseworker import DatabaseWorker


def GetSeasons():
    # Use Url Utility to construct initial Url
    urlWorker = UrlWorker()
    fullInitialUrl = urlWorker.GetSeasonOverviewUrl("2001")

    # Define the database worker
    databaseWorker = DatabaseWorker()

    # Fetch the HTML for the initial page
    print("Fetching initial page")
    seasonsHTML = urlopen(fullInitialUrl)

    # Parse the HTML into beatifulsoup
    seasonsSoup = BeautifulSoup(seasonsHTML, 'html.parser')

    # Find all
    seasonLinks = seasonsSoup.find_all(attrs={"data-name": "year"})
    for seasonLink in seasonLinks:
        seasonVal = seasonLink['data-value'].strip()
        print(seasonVal)

        # Check if the season already exists in the database
        # Only write to DB if it does not exist
        if databaseWorker.SeasonExists(seasonVal):
            print("skipping")
            continue

        # If we reach this point then it means the season does not exist
        # in the DB so we can go ahead and insert it
        databaseWorker.InsertSeason(seasonVal)
    databaseWorker.CommitChanges()
