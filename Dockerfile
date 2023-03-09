FROM node:19

RUN apt update \
    && apt install -y \
	python3 \
    python3-pip

WORKDIR /
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY package*.json ./
RUN npm install

RUN pip install bs4
RUN pip install "python-socketio[client]"

COPY . ./
EXPOSE 8080
RUN chmod +x wrapper.sh
CMD ["./wrapper.sh"]