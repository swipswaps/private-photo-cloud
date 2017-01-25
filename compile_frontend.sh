#!/bin/sh

cd "$(dirname "$0")"

NAME=privatephotocloud_frontend_temp

rm -rf static_collected/public

docker-compose build --pull frontend
docker run --name $NAME privatephotocloud_frontend echo
docker cp $NAME:/home/app/public static_collected/
docker rm -f $NAME
