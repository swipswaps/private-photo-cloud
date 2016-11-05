#!/bin/sh
docker exec -ti privatephotocloud_backend_1 ./manage.py shell -c 'from storage.models import *; Media.objects.all().delete()'
rm -rf media/*
