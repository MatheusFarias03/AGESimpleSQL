#!/bin/bash

# Set the Apache AGE container running.
docker pull apache/age
docker run \
    --name myPostgresDb  \
    -p 5455:5432 \
    -e POSTGRES_USER=postgresUser \
    -e POSTGRES_PASSWORD=postgresPW \
    -e POSTGRES_DB=postgresDB \
    -d \
    apache/age
sleep 3

# Execute the Python test script.
python3 -m tests.test

docker stop myPostgresDb

docker rm myPostgresDb
