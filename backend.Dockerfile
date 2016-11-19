FROM python:3.6.0b3-alpine

RUN apk --no-cache upgrade\
 && PKG="gcc musl-dev"\
 && apk add --no-cache $PKG\
 && python -m pip install pip==9.0.1 setuptools==28.8.0\
 && python -m pip install dumb-init==1.2\
 && apk del $PKG

COPY requirements /tmp/requirements

RUN apk --no-cache upgrade\
 && PKG="gcc musl-dev postgresql-dev jpeg-dev openjpeg-dev zlib-dev tiff-dev freetype-dev lcms2-dev libwebp-dev"\
 && apk add --no-cache postgresql libmagic exiftool jpeg openjpeg zlib tiff freetype lcms2 libwebp ffmpeg $PKG\
# --no-dependencies
 && python -m pip install --no-cache-dir -r /tmp/requirements\
 && apk del $PKG

ENTRYPOINT ["/usr/local/bin/dumb-init", "--verbose", "--single-child"]
