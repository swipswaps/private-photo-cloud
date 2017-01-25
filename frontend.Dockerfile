FROM node:7-alpine

WORKDIR /home/app/

RUN PKG="build-base autoconf automake libtool nasm libpng-dev"\
 && apk add --no-cache libpng curl $PKG\
 && npm install gifsicle mozjpeg optipng-bin pngquant-bin\
 && apk del $PKG

COPY frontend/package.json /home/app/

RUN npm install

COPY frontend /home/app/

RUN NODE_ENV=production ./node_modules/.bin/webpack

EXPOSE 80
