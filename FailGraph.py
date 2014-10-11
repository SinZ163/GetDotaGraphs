import simplejson
import datetime
from collections import OrderedDict

import matplotlib
from matplotlib.dates import MONDAY, WeekdayLocator, DayLocator, DateFormatter
from matplotlib.ticker import NullFormatter, FuncFormatter
import matplotlib.pyplot as plt

import numpy

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
                matchInfo[message["mod_id"]] = OrderedDict()

        matchInfo[message["mod_id"]][matchJson["matchID"]] = {
            "ipList" : [message["remote_ip"]],
            "numPlayers" : playerCount,
            "date_recorded" : message["date_recorded"]
        }
fig, ax = plt.subplots(4, sharex=True)
ax[0].set_title("Fail Percentage")
ax[1].set_title("Raw fails")
ax[2].set_title("Raw games")
ax[3].set_title("Average players")

ax[0].yaxis.set_major_formatter(FuncFormatter(to_percent))
ax[0].xaxis.set_major_locator(WeekdayLocator(MONDAY))
ax[0].xaxis.set_major_formatter(NullFormatter())
ax[0].xaxis.set_minor_locator(DayLocator())
ax[0].xaxis.set_minor_formatter(DateFormatter("%a %d"))
ax[0].xaxis.grid(which="minor")
ax[1].xaxis.grid(which="minor")
ax[2].xaxis.grid(which="minor")
ax[3].xaxis.grid(which="minor")
#ax[1].set_yscale('log')
#ax[2].set_yscale('log')

for mod in matchInfo:
    print("===== " + mod + " =====")
    failInfo = OrderedDict()
    countInfo = OrderedDict()
    for matchID in matchInfo[mod]:
        match = matchInfo[mod][matchID]
        date = match["date_recorded"].split(' ')[0]
        if date not in failInfo:
            failInfo[date] = [0,0]
            countInfo[date] = [match["numPlayers"]]
        else:
            countInfo[date].append(match["numPlayers"])
        failInfo[date][1] = failInfo[date][1] + 1
        if len(match["ipList"]) != match["numPlayers"]:
            failInfo[date][0] = failInfo[date][0] + 1

    x = []
    y = []
    y2 = []
    y3 = []
    countY = []
    print(failInfo)
    for rawDate in failInfo:
        countY.append(sum(countInfo[rawDate]) / float(len(countInfo[rawDate])))
        dateList = rawDate.split('-')
        y.append(failInfo[rawDate][0] / float(failInfo[rawDate][1]) * 100)
        y2.append(failInfo[rawDate][0])
        y3.append(failInfo[rawDate][1])
        x.append(datetime.date(int(dateList[0]), int(dateList[1]), int(dateList[2])))
    ax[0].plot_date(x, y, '-', label=mod + " (" +  str(len(matchInfo[mod])) + " Games)")
    ax[1].plot_date(x, y2, '-', label=mod + " (" +  str(len(matchInfo[mod])) + " Games)")
    ax[2].plot_date(x, y3, '-', label=mod + " (" +  str(len(matchInfo[mod])) + " Games)")
    ax[3].plot_date(x, countY, '-', label=mod + " (" +  str(len(matchInfo[mod])) + " Games)")

    print("r = " + str(numpy.corrcoef(y, countY)[0, 1]))
    print("r^2 = " + str(numpy.corrcoef(y, countY)[0, 1]**2))
    #plt.title(mod)
plt.legend(bbox_to_anchor=(1, 1),
           bbox_transform=plt.gcf().transFigure)
plt.show()
