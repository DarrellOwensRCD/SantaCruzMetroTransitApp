const express = require('express')
const cors = require('cors')
const app = express()

const hostname = '0.0.0.0';

const backedport = 8080;
const fs = require('fs');

const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('./swagger.json');

//https://expressjs.com/en/guide/routing.html
//swagger-UI-Express

const ioport = 5000;
const { Server } = require("socket.io");
const io = new Server(ioport, { /* options */ });

app.use(cors());

app.get('/', (req, res) => {
    console.log('Incomming request')
    res.send("OK")
    //Send list of lines here
})

// Request for line list
//http://127.0.0.1:3000/line?lineNum=71&lineName=Front+%26+Soquel+Ave

io.on("connection", (socket) => {
    console.log("Scraper Connected")
    app.get('/line', (req, res) => {
        console.log('Incomming request for list of lines.')
        const req_line = req.query.lineNum
        const req_Name = req.query.lineName
        const req_Dir = req.query.lineDir || "Outbound"
        if(Object.keys(req.query).length === 0){
            console.log('Query empty, sending list of line.')
            let rawdata = fs.readFileSync('LineList.json');
            let linelist = JSON.parse(rawdata);
            res.json(linelist)
        }
        else{
            console.log('Query requests stops for %s, %s %s.', req_line, req_Name, req_Dir)
            if(req_line === "UCSC"){
                 // if received request for loop busses, return list of UCSC stops
                console.log('Got UCSC line returning.')
                res.json({line: "UCSC",
                    stops:["Bay & High (UCSC - Main Entrance)","Coolidge Dr & Hagar Ct  (UCSC - Lower Campus)",
                    "Hagar Dr & Village Rd (UCSC - The Farm)","Hagar Dr (UCSC - East Remote Parking)",
                    "Hagar Dr (UCSC - East Field House)","Hagar Dr (UCSC - Bookstore, Cowell & Stevenson)",
                    "McLaughlin Dr (UCSC - Crown & Merrill College)","McLaughlin Dr (UCSC - College 9 & 10 / Health Ctr)",
                    "McLaughlin Dr (UCSC - Science Hill)","Heller Dr & McLaughlin Dr (UCSC - Kresge College)",
                    "Heller Dr (UCSC - Rachel Carson College & Porter)","Heller Dr (UCSC - Family Student Housing)",
                    "Heller Dr (UCSC - Oakes College)","Empire Grade (UCSC - Arboretum)","High (Tosca Terrace)",
                    "High & Western Dr","High & Bay Dr"]
                })
            }
            else{
                console.log('METRO line received.')
                socket.emit("stopRequest", { line: req_line, direction: req_Dir})
                // ... {lineNum: req_line, lineName: req_Name, lineDir: req_Dir, Stops: stop_list}
                socket.once("listStopResponse", (output) => {
                    console.log('GotResponse.')
                    res.json(output)
                });
        }
    }
})

    app.get('/linestop', (req, res) => {
        console.log('Incomming request for times.')
        const req_line = req.query.lineNum
        const req_stop = req.query.stopID
        const req_name = req.query.stopName
        const req_dir = req.query.lineDir || "outbound"
        if (req_line === "UCSC") {
            socket.emit("loopRequest", { line: req_line, stop: req_name, direction: req_dir })
        }
        else {
            socket.emit("etaRequest", { line: req_line, stop: req_name, direction: req_dir })
        }

        socket.once("listResponse", (output) => {
            console.log('GotResponse.')
            res.json({lineNum: req_line, lineDir: req_dir, ETAs: output.ETA, names:output.names, map_codes:output.map_codes})
        });
    })

})

app.use(
  '/api-docs',
  swaggerUi.serve,
  swaggerUi.setup(swaggerDocument)
);

app.listen(backedport, hostname, () => {
    console.log(`Backend Running at http://${hostname}:${backedport}/`);
    console.log(`Awaiting Scraper connections`);
});
