#!/bin/sh -e
./manage.sh migrate storage zero
find . -path '*/migrations/0*' -delete
./manage.sh makemigrations
./manage.sh migrate
