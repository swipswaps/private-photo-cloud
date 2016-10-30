FROM node:7.0.0

RUN npm install -g create-react-app

WORKDIR /home/

RUN create-react-app app
