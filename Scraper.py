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
sio = socketio.Client()
@sio.event
def establish(data):
    print("I'm connected!")

@sio.event
def sendRequest(data):
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
    stop_url = "/stops/" + stop_URL + "/pattern"
    URL = URL + stop_url
    print(URL)
    # With the completed URL, call web scrapper
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    job_elements = soup.find_all("ul")
    eta_times = []

    for job_element in job_elements:
        buses = job_element.find_all("li", class_=None)
        for bus in buses:  # note lists of size 0 wont be iterated, of which there are several
            # This is to print out <li> bus arrival stops </li>
            word = (str(bus).replace('<li>', '')).replace('</li>', '')
            eta_times.append(word)  # Appending to JSON list
        bus_results = {"line": line_request,
                       "ETA": eta_times}
    sio.emit('listResponse', bus_results)

@sio.event
def sendStopRequest(data):
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

sio.connect('http://localhost:5000')
