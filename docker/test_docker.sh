#!/bin/bash

docker build -t brettfalk/rofl-demo-python:latest .
docker push brettfalk/rofl-demo-python:latest

#source ../setenv.sh
docker run -it --rm -e ADMIN_KEY=$ADMIN_KEY -e RPC_URL=$RPC_URL -e CONTRACT_ADDRESS=$CONTRACT_ADDRESS docker.io/brettfalk/rofl-demo-python:latest 
