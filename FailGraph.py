import simplejson
import datetime

import matplotlib
from matplotlib.dates import MONDAY, WeekdayLocator, DayLocator, DateFormatter
from matplotlib.ticker import NullFormatter, FuncFormatter
import matplotlib.pyplot as plt

def to_percent(y, position):
    if matplotlib.rcParams['text.usetex'] == True:
        return str(y) + r'$\%$'
    else:
        return str(y) + '%'

info = []
with open("node_listener.json") as f:
    jsonres = f.read()
    jsonres = jsonres.replace("\\'", "'")
    info = simplejson.loads(jsonres, strict=False)

curMatchID = ""
matchInfo = {}
for message in info:
    matchJson = simplejson.loads(message["message"], strict=False)
    #print(element["match_id"])
    if matchJson["matchID"] == curMatchID:
        #print("###CONTINUED MATCH")
        #this is the continuation of a new match
        matchInfo[message["mod_id"]][curMatchID]["ipList"].append(message["remote_ip"])
    else:
        curMatchID = matchJson["matchID"]

        playerCount = len(matchJson["rounds"]["players"])

        if message["mod_id"] not in matchInfo:
                matchInfo[message["mod_id"]] = {}

        matchInfo[message["mod_id"]][matchJson["matchID"]] = {
            "ipList" : [message["remote_ip"]],
            "numPlayers" : playerCount,
            "date_recorded" : message["date_recorded"]
        }

for mod in matchInfo:
    failInfo = {}
    for matchID in matchInfo[mod]:
        match = matchInfo[mod][matchID]
        date = match["date_recorded"].split(' ')[0]
        if date not in failInfo:
            failInfo[date] = [0,0]
        failInfo[date][1] = failInfo[date][1] + 1
        if len(match["ipList"]) != match["numPlayers"]:
            failInfo[date][0] = failInfo[date][0] + 1

    fig, ax = plt.subplots()
    x = []
    y = []
    for rawDate in failInfo:
        dateList = rawDate.split('-')
        y.append(failInfo[rawDate][0] / float(failInfo[rawDate][1]) * 100)
        x.append(datetime.date(int(dateList[0]), int(dateList[1]), int(dateList[2])))
    ax.plot_date(x, y, '-')
    ax.yaxis.set_major_formatter(FuncFormatter(to_percent))
    ax.xaxis.set_major_locator(WeekdayLocator(MONDAY))
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.xaxis.set_minor_locator(DayLocator())
    ax.xaxis.set_minor_formatter(DateFormatter("%a %d"))
    ax.xaxis.grid(which="minor")

    plt.title(mod)
    plt.show()
