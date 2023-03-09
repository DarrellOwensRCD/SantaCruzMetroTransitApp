#!/bin/bash
# Start the first process
npm start &
# Start the second process
python3 Scraper.py &
# Wait for any process to exit
wait -n
# Exit with status of process that exited first
exit $?