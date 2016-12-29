FROM node:7-alpine

RUN npm install -g create-react-app

WORKDIR /home/

RUN create-react-app app
