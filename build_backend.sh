#!/bin/sh -e
docker-compose -f backend.docker-compose.yaml pull
exec docker-compose -f backend.docker-compose.yaml build --pull
