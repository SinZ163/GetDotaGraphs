import numpy as np
import matplotlib.pyplot as plt
import simplejson
import re

info = []
with open("node_listener.json") as f:
    jsonres = f.read()
    jsonres = jsonres.replace("\\'", "'")
    info = simplejson.loads(jsonres, strict=False)

matchDict = {}

for match in info:
    if match["mod_id"] not in matchDict:
        matchDict[match["mod_id"]] = {}
    matchJson = simplejson.loads(match["message"], strict=False)
    for player in matchJson["rounds"]["players"]:
        if "hero" in player:
            if player["hero"]["heroID"] in matchDict[match["mod_id"]]:
                matchDict[match["mod_id"]][player["hero"]["heroID"]] = matchDict[match["mod_id"]][player["hero"]["heroID"]] + 1
            else:
                matchDict[match["mod_id"]][player["hero"]["heroID"]] = 1
modList = []
modName = []
colorList = ["r", "g", "b"]
for modID, modInfo in matchDict.iteritems():
    modName.append(modID)
    modList.append(modInfo)
    
n_groups = len(matchDict)
bar_width = 1

opacity = 0.4
error_config = {'ecolor': '0.3'}
i = 0
for mod in modList:
    fig, ax = plt.subplots()
    graphNames = []
    graphValues = []
    for heroID, heroStats in modList[i].iteritems():
        graphNames.append(heroID)
        graphValues.append(heroStats)
        
    index = np.arange(len(graphValues))
    ax.bar(index, graphValues, bar_width,
                     alpha=opacity,
                     color=colorList[i],
                     error_kw=error_config,
                     label=modName[i])
    ax.set_xticks(index)
    ax.set_xticklabels(tuple(graphNames))
    ax.set_xlabel('Hero')
    ax.set_ylabel('Quantity')
    ax.legend()
    plt.show()
    i = i + 1