#!/bin/sh -e
docker-compose pull
exec docker-compose build --pull
