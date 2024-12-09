#!/bin/bash
# wait-for-postgres.sh

# Default PostgreSQL host and port
POSTGRES_HOST=${POSTGRES_HOST:-"postgres"}
POSTGRES_PORT=${POSTGRES_PORT:-"5432"}

# Wait until PostgreSQL is ready
until nc -z -v -w30 $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for PostgreSQL to start..."
  sleep 5
done

echo "PostgreSQL is up!"
