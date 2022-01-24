from .databaseworker import DatabaseWorker


class UrlWorker():
    def __init__(self):
        self.databaseWorker = DatabaseWorker()
        self.mainFormula1Url = self.databaseWorker.GetMainUrl()
        self.seasonOverViewUrlFragment = self.databaseWorker.GetRaceOverviewUrlFragment()
        self.qualifyingResultsFragment = self.databaseWorker.GetQualifyingResultsFragment()
        self.raceResultsFragment = self.databaseWorker.GetRaceResultsFragment()

    def GetSeasonOverviewUrl(self, year):
        # compile the final url, insert year into placeholder
        fullOverviewUrl = (self.mainFormula1Url + self.seasonOverViewUrlFragment).replace("{n}", year)
        return fullOverviewUrl

    def GetResultUrl(self, year, venueIndex, venue, resultTypeId):
        selectedUrl = ""
        if resultTypeId == 1:
            selectedUrl = self.qualifyingResultsFragment
        else:
            selectedUrl = self.raceResultsFragment
        qualificationUrl = (self.mainFormula1Url + selectedUrl).replace("{s}", str(year)).replace("{i}", str(venueIndex)).replace("{v}", venue)
        return qualificationUrl
