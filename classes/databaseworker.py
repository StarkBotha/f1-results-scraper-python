import psycopg2
import configparser


class DatabaseWorker():
    def __init__(self):
        #load database connection properties from configuration file
        try:
            configuration = configparser.ConfigParser()
            configuration
            configuration.read("config.ini")
            
            self.host = configuration.get("database","host")
            self.database = configuration.get("database","database")
            self.user = configuration.get("database","user")
            self.password = configuration.get("database","password")
        except:
            #default values in event of exception whilst reading values from config
            self.host = "localhost"
            self.database = "F1Results"
            self.user = "postgres"
            self.password = "password"
        
        self.connection = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        self.cursor = self.connection.cursor()

    def CommitChanges(self):
        self.connection.commit()

    # URLS
    def GetMainUrl(self):
        self.cursor.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'main\';')
        mainFormula1Url = self.cursor.fetchone()[0]
        return mainFormula1Url

    def GetRaceOverviewUrlFragment(self):
        self.cursor.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'races-fragment\';')
        overviewUrlFragment = self.cursor.fetchone()[0]
        return overviewUrlFragment

    def GetQualifyingResultsFragment(self):
        self.cursor.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'qualifying-results-fragment\';')
        qualifyingUrlFragment = self.cursor.fetchone()[0]
        return qualifyingUrlFragment

    def GetRaceResultsFragment(self):
        self.cursor.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'result-fragment\';')
        raceResultUrlFragment = self.cursor.fetchone()[0]
        return raceResultUrlFragment

    # SEASON
    def SeasonExists(self, year):
        self.cursor.execute('SELECT * FROM "Seasons" WHERE "Year"=%s;', (year,))
        if self.cursor.rowcount > 0:
            return True
        return False

    def InsertSeason(self, year):
        self.cursor.execute('INSERT INTO "Seasons"("Year") VALUES (%s);', (year,))

    def GetSeasons(self):
        self.cursor.execute('SELECT * FROM "Seasons";')
        return self.cursor.fetchall()

    # RACE DEFINITIONS
    def RaceDefinitionExists(self, seasonId, venue, raceIndex):
        self.cursor.execute('SELECT * FROM "Races" WHERE "SeasonId"=%s AND "Venue"=%s AND "VenueIndex"=%s;', (seasonId, venue, raceIndex))
        if (self.cursor.rowcount > 0):
            return True
        return False

    def InsertRaceDefinition(self, seasonId, venue, raceIndex):
        self.cursor.execute('INSERT INTO "Races"("Venue", "SeasonId", "VenueIndex") VALUES (%s, %s, %s);', (venue, seasonId, raceIndex))

    def GetRaces(self):
        self.cursor.execute('SELECT "Races"."Id", "Seasons"."Id", "Seasons"."Year", "Races"."VenueIndex", "Races"."Venue" FROM "Races" INNER JOIN "Seasons" ON "Races"."SeasonId"="Seasons"."Id";')
        return self.cursor.fetchall()

    def InsertDriver(self, driverName, driverSurname):
        # see if driver exists
        self.cursor.execute('SELECT * FROM "Drivers" WHERE "Name"=%s AND "Surname"=%s;', (driverName, driverSurname))
        if self.cursor.rowcount == 0:
            print("inserting driver [" + driverName + " " + driverSurname + "]")
            self.cursor.execute('INSERT INTO "Drivers"("Name", "Surname") VALUES (%s, %s);', (driverName, driverSurname))

    def GetDriver(self, driverName, driverSurname):
        self.cursor.execute('SELECT * FROM "Drivers" WHERE "Name"=%s AND "Surname"=%s;', (driverName, driverSurname))
        return self.cursor.fetchone()

    def InsertTeam(self, teamName):
        self.cursor.execute('SELECT * FROM "Teams" WHERE "Name"=%s;', (teamName,))
        if self.cursor.rowcount == 0:
            print("inserting team [" + teamName + "]")
            self.cursor.execute('INSERT INTO "Teams"("Name") VALUES (%s);', (teamName,))

    def GetTeam(self, teamName):
        self.cursor.execute('SELECT * FROM "Teams" WHERE "Name"=%s;', (teamName,))
        return self.cursor.fetchone()

    def InsertTeamComposition(self, driverId, teamId, raceNumber, seasonId):
        self.cursor.execute('SELECT * FROM "TeamComposition" WHERE "DriverId"=%s AND "TeamId"=%s AND "SeasonId"=%s;', (driverId, teamId, seasonId))
        if self.cursor.rowcount == 0:
            print("inserting TeamComp [" + str(driverId) + "] [" + str(teamId) + "] [" + raceNumber + "] [" + str(seasonId) + "] ")
            self.cursor.execute('INSERT INTO "TeamComposition"("DriverId", "TeamId", "RaceNumber", "SeasonId") VALUES (%s, %s, %s, %s);', (driverId, teamId, raceNumber, seasonId))

    def GetTeamComposition(self, driverId, teamId, seasonId):
        self.cursor.execute('SELECT * FROM "TeamComposition" WHERE "DriverId"=%s AND "TeamId"=%s AND "SeasonId"=%s;', (driverId, teamId, seasonId))
        return self.cursor.fetchone()

    def InsertResult(self, position, carNumber, driverName, driverSurname, car, seasonId, raceId, resultTypeId):
        typestring = ""
        if resultTypeId == 1:
            typestring = "Qualification result"
        else:
            typestring = "Race Result"
        # insert driver
        self.InsertDriver(driverName, driverSurname)
        insertedDriver = self.GetDriver(driverName, driverSurname)
        # insert team
        self.InsertTeam(car)
        insertedTeam = self.GetTeam(car)
        # insert team composition
        self.InsertTeamComposition(insertedDriver[0], insertedTeam[0], carNumber, seasonId)
        insertedTeamComposition = self.GetTeamComposition(insertedDriver[0], insertedTeam[0], seasonId)

        self.cursor.execute('SELECT * FROM "Results" WHERE "RaceId"=%s AND "TeamCompositionId"=%s AND "ResultTypeId"=%s', (raceId, insertedTeamComposition[0], resultTypeId))
        if self.cursor.rowcount == 0:
            print("inserting " + typestring + " [" + str(raceId) + "][" + str(insertedTeamComposition[0]) + "]")
            self.cursor.execute('INSERT INTO "Results"("RaceId", "TeamCompositionId", "Position", "ResultTypeId") VALUES (%s, %s, %s, %s);', (raceId, insertedTeamComposition[0], position, resultTypeId))
