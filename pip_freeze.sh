#!/bin/sh

# Usage: ./pip_freeze.sh > backend/packages.txt

docker-compose exec backend sh -c "PYTHONWARNINGS= pip freeze"
