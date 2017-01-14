#!/bin/sh

if [ -t 0 ] ; then
    PARAMS="-ti"
else
    PARAMS="-i"
fi

exec docker exec $PARAMS privatephotocloud_backend_1 ./manage.py "$@"
