FROM python:3.6-alpine

RUN apk --no-cache upgrade\
 && PKG="gcc musl-dev"\
 && apk add --no-cache $PKG\
 && python -m pip install pip==9.0.1 setuptools==33.1.1\
 && python -m pip install dumb-init==1.2\
 && apk del $PKG

COPY requirements /tmp/requirements

RUN apk --no-cache upgrade\
 && PKG="gcc musl-dev postgresql-dev jpeg-dev openjpeg-dev zlib-dev tiff-dev freetype-dev lcms2-dev libwebp-dev"\
 && apk add --no-cache gettext postgresql libmagic exiftool jpeg openjpeg zlib tiff freetype lcms2 libwebp ffmpeg $PKG\
 && python -m pip install --no-cache-dir -r /tmp/requirements\
 && apk del $PKG

# Workaround for https://github.com/zopefoundation/zope.interface/issues/68
RUN touch /usr/local/lib/python3.6/site-packages/zope/__init__.py

ENTRYPOINT ["/usr/local/bin/dumb-init", "--verbose", "--single-child"]
