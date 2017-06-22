FROM node:8-alpine

RUN npm install -g salita

WORKDIR /home/app/

COPY frontend/package.json /home/app/

RUN PKG="build-base autoconf automake libtool nasm libpng-dev"\
 && apk add --no-cache libpng curl $PKG\
 && npm install\
 && apk del $PKG

COPY frontend /home/app/

ENV NODE_ENV=production

RUN ./node_modules/.bin/webpack  --display-optimization-bailout

EXPOSE 80
