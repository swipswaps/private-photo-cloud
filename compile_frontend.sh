#!/bin/sh

cd "$(dirname "$0")"

rm -rf static/public

docker-compose build --pull frontend
docker-compose run --no-deps frontend echo
docker cp privatephotocloud_frontend_1:/home/public static/
docker-compose rm -f frontend
