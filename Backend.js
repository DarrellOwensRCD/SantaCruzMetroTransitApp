const express = require('express')
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
                socket.emit("sendStopRequest", { line: req_line, direction: req_Dir})
                // ... {lineNum: req_line, lineName: req_Name, lineDir: req_Dir, Stops: stop_list}
                socket.once("listStopResponse", (output) => {
                    console.log('GotResponse.')
                    res.json(output)
                });
        }
    })



    // Request for stop list
    app.get('/stop', (req, res) => {
        console.log('Incomming request for stops.')
        const req_ID = req.query.stopID
        const req_Name = req.query.stopName
        //if req_stop is null send list
        if(Object.keys(req.query).length === 0){
            let rawdata = fs.readFileSync('StopList.json');
            let stoplist = JSON.parse(rawdata);
            res.json(stoplist)
        }
        else{
            console.log('Query requests lines for stop %s, %s.', req_ID, req_Name)
            const line_list = //Call to line
            res.json({stopID: req_ID, stopName: req_Name, Lines: line_list})
        }
        //If not, send stop with lines
    })


    app.get('/linestop', (req, res) => {
        console.log('Incomming request for times.')
        const req_line = req.query.lineNum
        const req_stop = req.query.stopID
        const req_name = req.query.stopName
        const req_dir = req.query.lineDir || "outbound"
        socket.emit("sendRequest", { line: req_line, stop: req_name, direction: req_dir})
        // ...
        socket.once("listResponse", (output) => {
            console.log('GotResponse.')
            const res_ETA = output.ETA[0].split(" ")[4]
            const res_time = output.ETA[0].split(" ")[7]
            res.json({lineNum: req_line, lineDir: req_dir, ETA: res_ETA, nextBusTime: res_time})
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