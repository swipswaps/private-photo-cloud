#!/bin/sh
exec docker exec -ti privatephotocloud_backend_1 ./manage.py "$@"
