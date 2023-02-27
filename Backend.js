const express = require('express')
const app = express()

const hostname = '127.0.0.1';
const backedport = 3000;

const {spawn} = require('child_process')
const fs = require('fs');

//https://expressjs.com/en/guide/routing.html
//swagger-UI-Express

const ioport = 5000;
const { Server } = require("socket.io");
const io = new Server(ioport, { /* options */ });

app.get('/', (req, resp) => {
    console.log('Incomming request')
    //Send list of lines here
})

// Request for line list
app.get('/line', (req, res) => {
    console.log('Incomming request for list of lines.')
    const req_line = req.query.lineNum
    if(Object.keys(req.query).length === 0){
        //if req_line is null send list
    }
    else{
        console.log(req_line)
    }
    //If not, send line with stops
})

// Request for stop list
app.get('/stop', (req, res) => {
    console.log('Incomming request for list of routes.')
    const req_stop = req.query.stopNum 
    if(Object.keys(req.query).length === 0){
        console.log('Empty.')
    }
    //if req_stop is null send list
    //If not, send stop with lines
})

app.get('/linestop', (req, res) => {
    console.log('Incomming request for list of routes.')
    const req_line = req.query.lineNum
    const req_stop = req.query.stopID
    const req_dir = req.query.direction || "outbound"
    // spawn new child process to call the python script
    const python = spawn('python3', ['Testscraper.py'])
    io.once("connection", (socket) => {
        console.log('Connected.')
        socket.once("Ready", (output) => {
            socket.emit("sendRequest", { line: req_line, stop: req_stop, direction: req_dir })
        });
        // ... 
        socket.once("listResponse", (output) => {
            console.log('GotResponse.')
            res.json(output)
            python.kill()
        });
    })
})

app.listen(backedport, hostname, () => {
    console.log(`Backend Running at http://${hostname}:${backedport}/`);
});