import json
import math
from datetime import datetime, timedelta
from dateutil import parser

with open('./current_loops.txt') as infile:
    data = infile.read()

buses = json.loads(data)

with open('./current_loops.txt','w') as inf:
    json.dump(buses,inf, indent=4)

with open('./StopCoordList.txt') as cdfile:
    coords = cdfile.read()

stops = json.loads(coords)

with open('./StopCoordList.txt','w') as outf:
    json.dump(stops,outf, indent=4)

response = []

for bus in buses:
    if (bus["route"] != "OUT OF SERVICE/SORRY") and (bus["route"] != "LOOP OUT OF SERVICE AT BARN THEATER") and (bus["id"] != "90"):
        closest_stop = "None"
        closest = -1
        eta = 0
        nextBusTime = "error"
        for stop in stops:
            #print("Last Latitude:", lastLatitude,"Last Longitude:", lastLongitude, "Stop Latitude:",stop['latitude'],"Stop Longitude:",stop['longitude'])
            distance = math.dist([bus["lastLatitude"],bus["lastLongitude"]],[stop['latitude'],stop['longitude']])
            prevDist = math.dist([bus["previousLatitude"],bus["previousLongitude"]],[stop['latitude'],stop['longitude']])
            #print("Distance:",distance,"to stop",stop["name"])
            #print("Closest:",closest,"to stop",closest_stop)
            if ((distance < closest) and (distance < prevDist)) or (closest == -1):
                closest = distance
                closest_stop = stop["name"]
                direction = stop["direction"]
                eta = math.ceil(distance / 0.00158264808093)
                nextBusTime = parser.parse(bus["lastPing"]) + timedelta(minutes=eta)
        response.append({"Bus ID":bus["id"], "stopName":closest_stop, "direction":direction, "ETA":eta, "nextBusTime":nextBusTime})

with open('./loopETAs.txt','w') as outfile:
    json.dump(response,outfile,indent=4, sort_keys=True, default=str)