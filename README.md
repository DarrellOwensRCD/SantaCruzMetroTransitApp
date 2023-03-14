# Transit-APP Backend
The backend is written in Node js with Express.
It's run in a docker contianer on google cloud

Intermediate Routes
---
/line<br/>
Line is a request that can act in one of two ways:<br/>
Case 1: If no arguments are provided in the query, the response is a list of all bus lines, with UCSC busses listed first.<br/>
Case 2: If arguments are provided, a list of stops that the selected line services is sent as a response.<br/>
<br/>
After Case 2, all information is collected and the client can proceed to the final route.

Final Routes
---
/linestop<br/>
A linestop request is the final request in the chain, It provides the estimated time of arival and a time stamp.<br/>
All previouse feilds (Line number, Stop name, and direction) are required to make this request.<br/>

Loop Bus Calculation
---
The location of loop busses (longitude and latitude) is recieved by the Slugloop API. However the calculation of time to the selected bus stop needs to be calculated.<br/>
This calculation is preformed by the python script and the response is identical to that of the Santa Cruz metro web scraper.<br/>

Communication
---
The Node js backened invokes a runnin python script whenever it receives a valid request. This python script runs along side Node to provide web
scraping services and calculate the loop bus location and ETA.

To remedy complications with cross language communication, the Socket.IO library allows for communication between them.
Whenever a Route with a query is processed, the information in the query is sent as a JSON to the python script, using Socket.IO events.
After the information is processed, the python script sends the result back as a JSON, which the Backend parses and returns relevant information to the frontend.

The Socket.IO server/client runs on port 5000 in the docker file.

![alt text](https://github.com/jongbinny98/Transit-APP/blob/main/docs/Backend%20Graphic.png)
