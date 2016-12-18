#!/bin/sh
touch manage.py
docker exec -ti privatephotocloud_worker_1 kill -HUP 1
