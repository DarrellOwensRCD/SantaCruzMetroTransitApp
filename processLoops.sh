curl -X 'GET' \
  'https://slugloop.azurewebsites.net/buses' \
  -H 'accept: application/json' > current_loops.txt

python3 LoopProcessor.py