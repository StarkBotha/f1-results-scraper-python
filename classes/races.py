from urllib.request import urlopen
from bs4 import BeautifulSoup
from .urlworker import UrlWorker
from .databaseworker import DatabaseWorker


def GetRacesForSeasons(onlyDoFirstSeason, onlyDoFirstRace):
    """ Get all the race venue countries for the season and store them in the Races table in the DB """

    print(">>>Get races for seasons")

    # Set up databaes worker
    databaseWorker = DatabaseWorker()

    # Set up url worker
    urlWorker = UrlWorker()

    # Fetch all the seasons so we can iterate through them
    seasons = databaseWorker.GetSeasons()

    # iterate through each of the retrieved seasons
    for seasonId, seasonYear in seasons:
        # get the formatted season overview url
        seasonUrl = urlWorker.GetSeasonOverviewUrl(str(seasonYear))

        # get the html for the season overview page for the currently iterating season
        seasonHtml = urlopen(seasonUrl)

        # Parse the HTML into beatifulsoup
        seasonSoup = BeautifulSoup(seasonHtml, 'html.parser')

        raceLinks = seasonSoup.findAll("a", {"class": "ArchiveLink"})

        for raceLink in raceLinks:
            urlFrags = raceLink['href'].strip().split('/')

            raceYear = urlFrags[3]
            raceIndex = urlFrags[5]
            raceVenue = urlFrags[6]

            print(raceYear + " - " + raceVenue)

            if databaseWorker.RaceDefinitionExists(seasonId, raceVenue, raceIndex):
                print("Already exists, skipping")
                continue

            print("inserting")
            databaseWorker.InsertRaceDefinition(seasonId, raceVenue, raceIndex)

            if onlyDoFirstRace:
                break
        databaseWorker.CommitChanges()

        if onlyDoFirstSeason:
            break
