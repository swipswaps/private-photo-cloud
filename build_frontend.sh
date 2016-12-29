#!/bin/sh
docker-compose -f frontend.docker-compose.yaml pull
exec docker-compose -f frontend.docker-compose.yaml build --pull
