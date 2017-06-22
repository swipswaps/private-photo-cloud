FROM node:8-alpine

RUN yarn global add salita

RUN mkdir -p /home/app

WORKDIR /home/app/

RUN PKG="build-base autoconf automake libtool nasm libpng-dev"\
 && apk add --no-cache libpng curl $PKG\
 && yarn add gifsicle@3.0.4 mozjpeg@4.1.1 optipng-bin@4.0.0 pngquant-bin@3.1.1\
 && apk del $PKG

COPY frontend/package.json /home/app/

RUN yarn install

COPY frontend /home/app/

ENV NODE_ENV=production

RUN ./node_modules/.bin/webpack --display-optimization-bailout

EXPOSE 80
