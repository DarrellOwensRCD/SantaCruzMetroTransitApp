# Web Scrapper Testing
# Use the Web Scrapper to Loop Through Each Line and write all the stops w/ respective
# URL codes for each stop into a text file.
# Task #1: Get the default directions for lines
# Task #2: Distinguish between Outbounds & Inbounds
import requests
import re
import csv
import json
from bs4 import BeautifulSoup
import socketio
import sys
import time
import math
from datetime import datetime, timedelta
from dateutil import parser

sio = socketio.Client()
@sio.event
def establish(data):
    print("I'm connected!")


def buscode(string):
    #This gets the bus bound code to generate the map
    count = 0
    new_str = ""
    for i in range(0, len(string)):
        if(count == 1 and string[i] != "-"):
            #covert center values to zero so that Mapbox Recognizes it 74-11-55 -> 75-00-55
            new_str = new_str + '0'
        if(count == 3):
            break
        if(string[i] == "-"):
            count = count + 1
        else:
            if(count != 1):
                new_str = new_str + string[i]
    return new_str

@sio.event
def etaRequest(data):
    routes = {"4": "4347",
          "10": "4354",
          "15": "4356",
          "17": "4368",
          "18": "5337",
          "19": "4378",
          "20": "4371",
          "35": "4367",
          "35E": "5917",
          "40": "4365",
          "41": "4364",
          "42": "4362",
          "55": "4361",
          "66": "4358",
          "68": "4359",
          "69A": "4355",
          "69W": "4360",
          "71": "4353",
          "72": "4352",
          "72W": "4351",
          "74S": "4350",
          "75": "4349",
          "79": "4348",
          "79F": "5915",
          "91X": "4346",
          "WC": "5592"
          }
    direction = {
        "4": "4347",
        "10": "19262",
        "15": "11931",
        "17": "11954",
        "18": "20395",
        "19": "16149",
        "20": "16150",
        "35_O": "11951",  # dir
        "35_I": "11965",  # dir
        "35E_I": "20408",
        "35E_O": "20409",
        "40": "18095",
        "41": "11948",
        "42": "19267",
        "55": "11943",
        "66": "16167",
        "68": "16170",
        "69A": "16172",
        "69W": "16174",
        "71": "16910",
        "72": "16181",
        "72W": "16188",
        "74S": "16190",
        "75": "16191",
        "79": "16195",
        "79F": "20391",
        "91X_I": "16196",  # dir
        "91X_O": "16197",  # dir
        "WC": "18113"
    }

    line_request = data["line"]
    stop_request = data["stop"]
    bound_request = data["direction"]  # this only matters for 3 lines
    # Flag for the situtations of unique bounds, otherwise default bound
    if (line_request == 35):
        if (bound_request == "outbound"):
            dir_URL = direction["35_O"]
        else:
            dir_URL = direction["35_I"]
    elif (line_request == "35E"):
        if (bound_request == "outbound"):
            dir_URL = direction["35E_O"]
        else:
            dir_URL = direction["35E_I"]
    elif (line_request == "91X"):
        if (bound_request == "outbound"):
            dir_URL = direction["91X_O"]
        else:
            dir_URL = direction["91X_I"]
    else:
        dir_URL = direction[line_request]
    # Construct the URL
    URL = "https://cruzmetro.com/simple/routes/" + routes[line_request] + "/direction/" + dir_URL
    # Bus Stop to URL
    file = open("./webstops.txt", "r+")
    content = file.readlines()
    file.close()
    for line in content:
        altline = line.split("|")
        if (stop_request in altline[0]):
            stop_URL = altline[1]
            break
    stop_URL = stop_URL.replace("\n", "")
    # Assemble final URL
    stop_url = "/stops/"+ stop_URL + "/pattern"
    URL = URL + stop_url
    #With the completed URL, call web scrapper
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    job_elements = soup.find_all("ul")
    name_elements = soup.find_all("span")
    eta_times = []
    names = []
    map_codes = []
    #First find the bound names for each bus with a unique terminus
    for name_element in name_elements:
            bound = re.search('[A-Za-z0-9]+-[0-9]+-[0-9]+-([A-Za-z]+( [A-Za-z]+)+)', str(name_element))
            map_code = buscode(str(name_element))
            map_code = map_code.replace("<span>", "")
            map_codes.append(map_code.lower()) #mapbox converts all uppercase to lower
            if bound:
                names.append(bound.group(1))
    #Then the bus arrival ETA
    for job_element in job_elements:
        buses = job_element.find_all("li", class_=None)
        for bus in buses: #note lists of size 0 wont be iterated, of which there are several
            #This is to print out <li> bus arrival stops </li>
            word = (str(bus).replace('<li>', '')).replace('</li>', '')
            time = re.search('arrives in (.+?) minutes at', word)
            if time:
                eta_times.append(time.group(1)) #Appending to JSON list
            else:
                #could be an arrival bus
                if 'arriving' in str(word):
                    eta_times.append('arriving')
            break
        bus_results = {"line": line_request,
                        "ETA": eta_times,
                       "names" : names,
                       "map_codes" : map_codes}
    sio.emit('listResponse', bus_results)

@sio.event
def stopRequest(data):
    routes = { "4" : "4347",
    "10" : "4354",
    "15" : "4356",
    "17" :"4368",
    "18": "5337",
    "19" :"4378",
    "20" : "4371",
    "35" : "4367",
    "35E" : "5917",
    "40" : "4365",
    "41" :"4364",
    "42" : "4362",
    "55" : "4361",
    "66" : "4358",
    "68" : "4359",
    "69A" : "4355",
    "69W" : "4360",
    "71" : "4353",
    "72" : "4352",
    "72W" : "4351",
    "74S" : "4350",
    "75" : "4349",
    "79" : "4348",
    "79F" : "5915",
    "91X" : "4346",
    "WC" : "5592"
    }
    error_flag = 0
    bus_stops = []
    #Get the user input
    line_request = data["line"]
    user_direction = data["direction"]
    #Construct the URL
    try:
        URL = "https://cruzmetro.com/simple/routes/" + routes[line_request] + "/direction/"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        #UCSC buses are ALWAYS Loopers, avoid this block
        if(line_request != "10" and line_request != "15" and line_request != "18" and line_request != "19" and line_request != "20"):  
            #With the completed URL, call web scrapper
            job_elements = soup.find_all("li")
            error_flag = 2  #ERROR: Wifi must be down or some kind of error if the loop doesnt catch the direction element
            for directions in job_elements:
                if user_direction in str(directions): #find the direction in the list of directions, then construct the URL
                    error_flag = 0
                    #extract bus stops url from str
                    reg = re.search('a href="(.+?)">', str(directions))
                    if reg:
                        url_extension = reg.group(1)
                        stops_url =  "https://cruzmetro.com" + url_extension
                        page = requests.get(stops_url)
                        soup = BeautifulSoup(page.content, "html.parser") #This prints out the stop list
                    else:
                        #Only would happen in the event of an HTML change
                        error_flag = 1
    #if there's an Error of any kind, write an error msg to the JSON file
    except KeyError:
        error_flag = 3
    if error_flag == 0:
        stops_obj = soup.find_all("li", class_="arrow")
        for stop_obj in stops_obj:
            reg = re.search('/pattern">(.+?)</a>',str(stop_obj))
            if reg:
                #append stop name to py list/tuples thing
                bus_stop = reg.group(1).replace('amp;', '')
                bus_stops.append(bus_stop)
        #Done
        bus_stops_list = {"line": line_request,
                            "stops": bus_stops}
    else:
        bus_stops_list = {"line": "0",
                            "stops": bus_stops, 
                            "error": error_flag}
    with open("recent_stop_list.json", "w") as outfile:
        json.dump(bus_stops_list, outfile)
        outfile.close()
    sio.emit('listStopResponse', bus_stops_list)

    
@sio.event
def loopRequest(indata):
    time.sleep(3) #wait for curl to finish
    with open('./current_loops.txt') as infile:
        data = infile.read()

    buses = json.loads(data)

    with open('./current_loops.txt','w') as inf:
        json.dump(buses,inf, indent=4)

    stops = [
    {
        "name": "Bay & High (UCSC - Main Entrance)",
        "latitude": 36.977704,
        "longitude": -122.053602,
        "direction": "counterclockwise"
    },
    {
        "name": "Coolidge Dr & Hagar Ct (UCSC - Lower Campus)",
        "latitude": 36.981409,
        "longitude": -122.051967,
        "direction": "counterclockwise"
    },
    {
        "name": "Coolidge Dr & Hagar Ct (UCSC - Lower Campus)",
        "latitude": 36.981523,
        "longitude": -122.052074,
        "direction": "clockwise"
    },
    {
        "name": "Hagar Dr & Village Rd (UCSC - The Farm)",
        "latitude": 36.9859,
        "longitude": -122.053572,
        "direction": "counterclockwise"
    },
    {
        "name": "Hagar Dr & Village Rd (UCSC - The Farm)",
        "latitude": 36.985565,
        "longitude": -122.053507,
        "direction": "clockwise"
    },
    {
        "name": "Hagar Dr (UCSC - East Remote Parking)",
        "latitude": 36.991307,
        "longitude": -122.054713,
        "direction": "counterclockwise"
    },
    {
        "name": "Hagar Dr (UCSC - East Remote Parking)",
        "latitude": 36.991307,
        "longitude": -122.054713,
        "direction": "clockwise"
    },
    {
        "name": "Hagar Dr (UCSC - East Field House)",
        "latitude": 36.994266,
        "longitude": -122.055578,
        "direction": "counterclockwise"
    },
    {
        "name": "Hagar Dr (UCSC - Bookstore, Cowell & Stevenson)",
        "latitude": 36.996664,
        "longitude": -122.055388,
        "direction": "clockwise"
    },
    {
        "name": "Hagar Dr (UCSC - Bookstore, Cowell & Stevenson)",
        "latitude": 36.997499,
        "longitude": -122.055084,
        "direction": "counterclockwise"
    },
    {
        "name": "McLaughlin Dr (UCSC - Crown & Merrill College)",
        "latitude": 36.998969,
        "longitude": -122.055202,
        "direction": "counterclockwise"
    },
    {
        "name": "McLaughlin Dr (UCSC - College 9 & 10 / Health Ctr)",
        "latitude": 36.999877,
        "longitude": -122.058458,
        "direction": "counterclockwise"
    },
    {
        "name": "McLaughlin Dr (UCSC - College 9 & 10 / Health Ctr)",
        "latitude": 36.999798,
        "longitude": -122.05831,
        "direction": "clockwise"
    },
    {
        "name": "McLaughlin Dr (UCSC - Science Hill)",
        "latitude": 36.999903,
        "longitude": -122.062318,
        "direction": "counterclockwise"
    },
    {
        "name": "McLaughlin Dr (UCSC - Science Hill)",
        "latitude": 36.99989,
        "longitude": -122.062139,
        "direction": "clockwise"
    },
    {
        "name": "Heller Dr & McLaughlin Dr (UCSC - Kresge College)",
        "latitude": 36.999305,
        "longitude": -122.064501,
        "direction": "counterclockwise"
    },
    {
        "name": "Heller Dr & McLaughlin Dr (UCSC - Kresge College)",
        "latitude": 36.999333,
        "longitude": -122.064323,
        "direction": "clockwise"
    },
    {
        "name": "Heller Dr (UCSC - Kerr Hall)",
        "latitude": 36.996712,
        "longitude": -122.063616,
        "direction": "clockwise"
    },
    {
        "name": "Heller Dr (UCSC - Rachel Carson College & Porter)",
        "latitude": 36.992945,
        "longitude": -122.06527,
        "direction": "counterclockwise"
    },
    {
        "name": "Heller Dr (UCSC - Rachel Carson College & Porter)",
        "latitude": 36.992857,
        "longitude": -122.064712,
        "direction": "clockwise"
    },
    {
        "name": "Heller Dr (UCSC - Family Student Housing)",
        "latitude": 36.991804,
        "longitude": -122.066755,
        "direction": "clockwise"
    },
    {
        "name": "Heller Dr (UCSC - Oakes College)",
        "latitude": 36.990604,
        "longitude": -122.066152,
        "direction": "clockwise"
    },
    {
        "name": "Heller Dr (UCSC - Oakes College)",
        "latitude": 36.989903,
        "longitude": -122.06719,
        "direction": "counterclockwise"
    },
    {
        "name": "Empire Grade & Arboretum Access Trail",
        "latitude": 36.983683,
        "longitude": -122.064902,
        "direction": "counterclockwise"
    },
    {
        "name": "Empire Grade (UCSC - Arboretum)",
        "latitude": 36.98272,
        "longitude": -122.062665,
        "direction": "counterclockwise"
    },
    {
        "name": "High (Tosca Terrace)",
        "latitude": 36.979919,
        "longitude": -122.059291,
        "direction": "counterclockwise"
    },
    {
        "name": "High & Western Dr",
        "latitude": 36.978639,
        "longitude": -122.057775,
        "direction": "counterclockwise"
    },
    {
        "name": "High & Western Dr",
        "latitude": 36.978782,
        "longitude": -122.057751,
        "direction": "clockwise"
    },
    {
        "name": "High & Bay Dr",
        "latitude": 36.977314,
        "longitude": -122.054247,
        "direction": "clockwise"
    }
]

    name = []
    eta = []
    dire = []
    map_codes = []

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
            name.append(closest_stop)
            eta.append(eta)
            dire.append(direction)
            map_codes.append("loop")
   
    sio.emit('loopResponse', {"ETA":eta,"names":name,"Direction":dire, "map_codes":map_codes})
    
isConnected = False
while not isConnected:
    try:
        sio.connect('http://localhost:5000')
        isConnected = True
    except:
        print("Waiting to connect...")
        time.sleep(1)

