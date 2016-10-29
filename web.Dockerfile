FROM python:3.6.0b2-alpine

RUN apk --no-cache upgrade\
 && PKG="gcc musl-dev"\
 && apk add --no-cache $PKG\
 && python -m pip install dumb-init==1.2\
 && apk del $PKG

COPY requirements /tmp/requirements

RUN apk --no-cache upgrade\
 && PKG="gcc musl-dev jpeg-dev openjpeg-dev zlib-dev tiff-dev freetype-dev lcms2-dev libwebp-dev"\
 && apk add --no-cache $PKG\
 && python -m pip install -r /tmp/requirements\
 && apk del $PKG

ENTRYPOINT ["/usr/local/bin/dumb-init", "--verbose", "--single-child"]
