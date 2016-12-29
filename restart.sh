#!/bin/sh -e
touch manage.py
exec docker exec -ti privatephotocloud_worker_1 kill -HUP 1
