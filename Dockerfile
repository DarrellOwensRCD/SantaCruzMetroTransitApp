FROM node:19

RUN apt update \
    && apt install -y \
	python3 \
    python3-pip

WORKDIR /

COPY package*.json .
RUN npm install

RUN pip install bs4
RUN pip install "python-socketio[client]"

COPY Backend.js Backend.js
COPY Scraper.py Scraper.py
COPY wrapper.sh wrapper.sh
COPY swagger.json swagger.json
COPY webstops.txt webstops.txt
EXPOSE 8080
CMD ./wrapper.sh