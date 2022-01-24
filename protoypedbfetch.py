import psycopg2

conn = psycopg2.connect(host="localhost", database="F1Results",
                        user="postgres", password="password")

cur = conn.cursor()

cur.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'main\';')

mainQueryUrl = cur.fetchone()[0]
# now we need to fetch the race format url so we can construct the initial request url

cur.execute('SELECT "Value" FROM "URLs" WHERE "Name"=\'races-fragment\';')

raceFragmentUrl = cur.fetchone()[0]

fullInitialUrl = mainQueryUrl + raceFragmentUrl
fullInitialUrl = fullInitialUrl.replace("{n}", "2001")
