FROM node:7.2.1-alpine

RUN npm install -g create-react-app

WORKDIR /home/

RUN create-react-app app
