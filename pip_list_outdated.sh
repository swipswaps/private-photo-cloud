#!/bin/sh

cd "$(dirname "$0")"

./exec.sh pip list --outdated --format=columns
