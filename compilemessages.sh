#!/bin/sh -e

cd "$(dirname "$0")"

# TODO: Make a single translation file

for dir in $(find "$(pwd)" -name locale -type d); do
    cd "${dir}/../"
    PYTHONWARNINGS=ignore ../manage.py compilemessages "$@"
done
