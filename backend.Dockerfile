FROM python:3.6-alpine3.6

COPY backend/packages.txt /tmp/

RUN apk --no-cache upgrade\
 && PKG="gcc g++ musl-dev linux-headers pcre-dev postgresql-dev yaml-dev jpeg-dev openjpeg-dev zlib-dev tiff-dev freetype-dev lcms2-dev libwebp-dev"\
 && apk add --no-cache gettext postgresql libmagic exiftool yaml jpeg openjpeg zlib tiff freetype lcms2 libwebp ffmpeg $PKG\
 && python -m pip install --no-cache -r /tmp/packages.txt\
 && touch /usr/local/lib/python3.6/site-packages/zope/__init__.py\
 && apk del $PKG

# Touch above is a workaround for https://github.com/zopefoundation/zope.interface/issues/68

ENV PYTHONUNBUFFERED=1\
 PYTHONIOENCODING=utf-8\
 PYTHONDONTWRITEBYTECODE=1\
 PYTHONWARNINGS=all

ENTRYPOINT ["/usr/local/bin/dumb-init", "--verbose", "--single-child"]
