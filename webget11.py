import requests
import psycopg2
import re

conn = psycopg2.connect(host="localhost", database="F1Results", user="postgres", password="password")

skipSeasons = True
skipRaces = True

cur = conn.cursor()

cur.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'main\';')

mainQueryUrl = cur.fetchone()[0]
# now we need to fetch the race format url so we can construct the initial request url

cur.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'races-fragment\';')

raceFragmentUrl = cur.fetchone()[0]

fullInitialUrl = mainQueryUrl + raceFragmentUrl
fullInitialUrl = fullInitialUrl.replace("{n}", "2001")

print("fetching url...")
r = requests.get(fullInitialUrl)
content_string = r.content.decode()
print("...done")

# remove linefeed characters
content_string = content_string.replace("\\n", '\n')
content_string = content_string.replace("\\t", '\t')

# remove escape apostrophes
content_string = content_string.replace("\'", "'")
# generate an array of lines that we can work with independently
content_strings = content_string.split("<")
# define the search string
racestrings = ['races.html']
seasons = ['']
for line in content_strings:
    if any(racestring in line for racestring in racestrings):
        seasons.append(line.split("/", 4)[3])
for season in seasons:
    if skipSeasons:
        break
    # add to database if not exist yet
    # print(season)
    if season == '' or season == ' ':
        continue
    # check if the season already exists in the database
    getExistingSeasonQuery = 'SELECT * FROM "Seasons" WHERE "Year"=%s'
    cur.execute(getExistingSeasonQuery, (season,))
    if cur.rowcount > 0:
        # print("Season " + season + " already exists")
        continue
    # if we reach this point of the loop then it means we can go ahead and insert
    # cur.execute('INSERT INTO public."Seasons"("Year") VALUES (' + season + ');')
    cur.execute('INSERT INTO "Seasons"("Year") VALUES (' + season + ');')
conn.commit()  # store seasons to DB

# now that the seasons are in place we can move on to getting the races for each season
# lets retrieve the stored seasons
cur.execute('SELECT * FROM "Seasons"')
# storedSeason = cur.fetchone()
for seasonId, seasonYear in cur.fetchall():
    if skipRaces:
        break
    print("processing season [" + str(seasonId) + "]" + str(seasonYear))
    # now we want to get all the races for this season
    # construct the season race results url
    raceUrl = (mainQueryUrl + raceFragmentUrl).replace("{n}", str(seasonYear))
    # get the html content
    raceResponse = requests.get(raceUrl).content
    decodedRaceResponse = raceResponse.decode().replace("\\n", '\n').replace("\\t", '\t').replace("\'", "'").split("<")
    venues = []
    # venuestrings = ['/races/', '/race-result.html" data-ajax-url="/content/']
    venuestrings = ['/race-result.html" data-ajax-url="/content/']
    # if seasonYear == 2015:
    # break
    for element in decodedRaceResponse:
        if any(venuestring in element for venuestring in venuestrings):
            # with open("raceElements.txt", "a") as raceElementsTextFile:
                # raceElementsTextFile.write(element)
            #    raceElementsTextFile.write("[" + elementChunks[5] + "][" + elementChunks[6] + "]")
            elementChunks = element.split("/", 7)
            # retrieve the race index plus the venue name
            venues.append([elementChunks[5], elementChunks[6]])
            # print("[" + elementChunks[5] + "][" + elementChunks[6] + "]")
            # check in the db if this venue has already been added or not
            existingRacesQuery = 'SELECT * FROM "Races" WHERE "SeasonId"=%s AND "Venue"=%s AND "VenueIndex"=%s;'

            cur.execute(existingRacesQuery, (seasonId, elementChunks[6], elementChunks[5]))
            if (cur.rowcount > 0):
                # race event already exists, move to next one
                # print("already exists, skipping")
                continue
            # race event does not yet exist, so we can insert it
            # print("does not exist, inserting")
            print(elementChunks[6])
            cur.execute('INSERT INTO "Races"("Venue", "SeasonId", "VenueIndex") VALUES (%s, %s, %s);', (elementChunks[6], seasonId, elementChunks[5]))
            conn.commit()  # Save races to DB

# Now we fetch all the races and cycle through each to get the results
# As we scrape the results we will insert teams and drivers if they dont already exist
raceResultQuery = 'SELECT "Seasons"."Year","Races"."VenueIndex","Races"."Venue", format(\'/en/results.html/%s/races/%s/%s/race-result.html\', ("Seasons"."Year"), ("Races"."VenueIndex"), ("Races"."Venue")) as raceUrl FROM "Races" INNER JOIN "Seasons" ON "Races"."SeasonId"="Seasons"."Id"; '
cur.execute(raceResultQuery)
for raceYear, raceVenueIndex, raceVenue, raceUrl in cur.fetchall():
    print("Fetching: [" + str(raceYear) + "] / [" + str(raceVenue) + "]")
    raceResultConstructeUrl = mainQueryUrl + raceUrl
    raceResultResponse = requests.get(raceResultConstructeUrl).content.decode().replace("\\n", '\n').replace("\\t", '\t').replace("\'", "'").split("<")
    entrants = []
    inResultsTable = False
    inResultsTableBody = False
    for resultLine in raceResultResponse:
        # with open("raceElements.txt", "a") as raceElementsTextFile:
            # raceElementsTextFile.write(raceResultResponse)
            # for resultLine in raceResultResponse:
            # raceElementsTextFile.write(resultLine)
        if 'table class="resultsarchive-table' in resultLine:
            inResultsTable = True
        if inResultsTable and '/table' in resultLine:
            inResultsTable = False
        if inResultsTable and 'tbody>' in resultLine and '/tbody>' not in resultLine:
            inResultsTableBody = True
        if inResultsTable and inResultsTableBody and '/tbody>' in resultLine:
            inResultsTableBody = False
    break
