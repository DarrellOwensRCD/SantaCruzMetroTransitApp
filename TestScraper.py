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

sio = socketio.Client()
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
@sio.event
def establish(data):
    print("I'm connected!")

@sio.event
def sendRequest(data):
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
    exit(0)

sio.connect('http://localhost:5000')
sio.emit('Ready', 'OK')
