from urllib.request import urlopen
from bs4 import BeautifulSoup
from .urlworker import UrlWorker
from .databaseworker import DatabaseWorker


def GetRaceResults(onlyDoFirstResult, resultTypeId):
    """Iterate through all the race definitions and get qualifying results and store it to database"""

    print(">>> Get Results")
    # set up database worker
    databaseWorker = DatabaseWorker()

    # set up url worker
    urlWorker = UrlWorker()

    # get all the races
    races = databaseWorker.GetRaces()

    # iterate through all the races
    for raceId, seasonId, raceYear, raceVenueIndex, raceVenue in races:

        # get the url for the qualifying session

        resultUrl = urlWorker.GetResultUrl(raceYear, raceVenueIndex, raceVenue, resultTypeId)

        # get the html for the qualifying session
        resultHtml = urlopen(resultUrl)

        # parse the html to soup
        resultSoup = BeautifulSoup(resultHtml, 'html.parser')

        tableRows = resultSoup.findAll("tr")

        for tableRow in tableRows:
            tableHeaderRow = tableRow.find("th")
            if tableHeaderRow is not None:
                continue

            tableColumns = tableRow.findAll("td")
            position = tableColumns[1].text
            # we are not interested in recording losers who did not place.
            if position == "NC" or position == "RT" or position == "DQ" or position == "EX":
                continue
            carNumber = tableColumns[2].text
            driverNameSurnameCombo = tableColumns[3].findAll("span")
            driverName = driverNameSurnameCombo[0].text
            driverSurname = driverNameSurnameCombo[1].text
            car = tableColumns[4].text
            # insert the qualification entry, this will also insert the driver, team and teamcomposition records if they do not exist
            databaseWorker.InsertResult(position, carNumber, driverName, driverSurname, car, seasonId, raceId, resultTypeId)
            databaseWorker.CommitChanges()

        if onlyDoFirstResult:
            break
