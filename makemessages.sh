#!/bin/sh -e

cd "$(dirname "$0")"

for dir in $(find "$(pwd)" -name locale -type d); do
    cd "${dir}/../"
    PYTHONWARNINGS=ignore ../manage.py makemessages --all --no-wrap "$@"
done
