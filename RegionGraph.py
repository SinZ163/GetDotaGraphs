from pylab import *
import simplejson
import re
import csv
import iptools

def ipToList(ip):
    return ip.split(".")
info = []
with open("node_listener.json") as f:
    jsonres = f.read()
    jsonres = jsonres.replace("\\'", "'")
    info = simplejson.loads(jsonres, strict=False)

ipDict = {}

ipCount = 0
for match in info:
    ipCount = ipCount + 1
    if match["mod_id"] not in ipDict:
        ipDict[match["mod_id"]] = []
    ipDict[match["mod_id"]].append(match["remote_ip"])

geoDB = []
with open("GeoIPCountryWhois.csv", "rb") as f:
    geoIPDB = csv.reader(f)
    for row in geoIPDB:
        geoDB.append(row)
geoCache = {} #its too slow without caching results
with open("GeoCache.json", "rb") as f:
    jsonres = f.read()
    geoCache = simplejson.loads(jsonres, strict=False)

for mod in ipDict:
    print("MOD: "+mod)
    regionList = {}
    i = 0
    for ip in ipDict[mod]:
        i = i + 1
        #print("IP: " + ip)
        ipInt = iptools.ipv4.ip2long(ip)
        #print("IPLong: " +str(ipInt))
        #ip = 192.168.0.5
        if ipInt in geoCache:
            print("USING CACHE FOR "+ip)
            if geoCache[ipInt] in regionList:
                regionList[geoCache[ipInt]] = regionList[geoCache[ipInt]] + 1
            else:
                regionList[geoCache[ipInt]] = 1
        else:
            for row in geoDB:
                #print(str(row[2]) + " < "+ str(ipInt) + " < " + str(row[3]))
                if ipInt >= int(row[2]):
                    #print("a")
                    if ipInt <= int(row[3]):
                        geoCache[ipInt] = row[5]
                        print("COUNTRY: "+row[5])
                        if row[5] in regionList:
                            regionList[row[5]] = regionList[row[5]] + 1
                        else:
                            regionList[row[5]] = 1
                    #else:
                    #    print(str(ipInt) + " > " + str(row[3]))
                #else:
                #    print(str(ipInt) + " < " + str(row[2]))
    # make a square figure and axes
    with open("GeoCache.json", "w") as f:
        jsonres = simplejson.dumps(geoCache)
        f.write(jsonres)

    figure(1)
    ax = axes()

    # The slices will be ordered and plotted counter-clockwise.
    labels = []
    fracs = []
    print("============================")
    for region in regionList:
        print(region + (22-len(region))*' ' +  " | " + str((float(regionList[region]) / i)*100.0))
        labels.append(region)
        fracs.append((float(regionList[region]) / i)*100.0)
    print("============================")

    pie(fracs, labels=labels)

    title(mod, bbox={'facecolor':'0.8', 'pad':5})
    #legend(loc="center left")
    show()
