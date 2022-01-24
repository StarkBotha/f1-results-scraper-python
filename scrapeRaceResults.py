import configparser
from classes.seasons import GetSeasons
from classes.races import GetRacesForSeasons
from classes.raceresults import GetRaceResults

try:
    configuration = configparser.ConfigParser()
    configuration
    configuration.read("config.ini")
    doGetSeasons = configuration.getboolean("running_options","doGetSeasons")
    doGetRaces = configuration.getboolean("running_options","doGetRaces")
    onlyGetFirstSeasonRaces = configuration.getboolean("running_options","onlyGetFirstSeasonRaces")
    onlyDoFirstRace = configuration.getboolean("running_options","onlyDoFirstRace")
    doQuali = configuration.getboolean("running_options","doQuali")
    onlyDofirstQuali = configuration.getboolean("running_options","onlyDofirstQuali")
    doRaceResults = configuration.getboolean("running_options","doRaceResults")    
except:
    #Default values if exception encountered trying to load values from config files
    doGetSeasons = True
    doGetRaces = True
    onlyGetFirstSeasonRaces = True
    onlyDoFirstRace = False
    doQuali = False
    onlyDofirstQuali = False
    doRaceResults = False    

if doGetSeasons:
    GetSeasons()

if doGetRaces:
    GetRacesForSeasons(onlyGetFirstSeasonRaces, onlyDoFirstRace)

if doQuali:
    GetRaceResults(onlyDofirstQuali, 1)

if doRaceResults:
    GetRaceResults(onlyDoFirstRace, 2)
