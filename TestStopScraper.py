#Web Scrapper Testing
#Sending: Line Number & Direction
#Produces New URL to Stops
#Returns List of Stops
#Error flags: 3 nonexistent bus line, 2 nonexistent direction, 1 can't find HTML data
import requests
import re
import csv
import json
from bs4 import BeautifulSoup
import socketio
sio = socketio.Client()

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

@sio.event
def sendStopRequest(data):
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
    exit(0)

sio.connect('http://localhost:5000')
sio.emit('Ready', 'OK')