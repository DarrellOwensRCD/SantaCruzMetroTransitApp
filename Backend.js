const express = require('express')
const app = express()

const hostname = '127.0.0.1';
const backedport = 3000;

const {spawn} = require('child_process')
const fs = require('fs');

//https://coderrocketfuel.com/article/handle-get-request-query-string-parameters-in-express-js
//https://expressjs.com/en/guide/routing.html
const ioport = 5000;
const { Server } = require("socket.io");
const io = new Server(ioport, { /* options */ });

app.get('/', (req, resp) => {
    console.log('Incomming request')
    resp.send('<h1></h1>')
})

// Request for route list
app.get('/routes', (req, res) => {
    console.log('Incomming request for list of routes.')
    //Pull all info, send it
    // spawn new child process to call the python script
    const python = spawn('python3', ['Test.py'])
    io.once("connection", (socket) => {
        console.log('Connected.')
        socket.once("Ready", (output) => {
            socket.emit("sendRequest", { line: '71', stop: 'Front & Soquel Ave', direction: 'outbound' })
        });
        // ... 
        socket.once("listResponse", (output) => {
            console.log('GotResponse.')
            res.json(output)
            python.kill()
        });
    }) 
})

app.get('/stop', (req, res) => {
    console.log('Incomming request for list of routes.')
    const req_line = req.query.line
    const req_dir = req.query.direction || "outbound"
    // spawn new child process to call the python script
    const python = spawn('python3', ['Test.py'])
    io.once("connection", (socket) => {
        console.log('Connected.')
        socket.once("Ready", (output) => {
            socket.emit("sendRequest", { line: req_line, stop: 'Front & Soquel Ave', direction: req_dir })
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