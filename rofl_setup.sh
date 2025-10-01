#!/bin/bash

# Set the secrets
source setenv.sh
if [ -z "$ADMIN_KEY" ]; then
    echo "ADMIN_KEY is not set"
    exit 1
fi
if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "CONTRACT_ADDRESS is not set"
    exit 1
fi
if [ -z "$TICKER" ]; then
    echo "TICKER is not set"
    exit 1
fi

# Build the docker image and push it to the registry
pushd docker
docker build -t brettfalk/rofl-demo-oracle:latest .
docker push brettfalk/rofl-demo-oracle:latest
popd

docker compose build

# ROFL Commands

# https://docs.oasis.io/build/rofl/quickstart/
# https://docs.oasis.io/general/manage-tokens/cli/rofl

# Build the rofl image
docker run --platform linux/amd64 --volume .:/src -it ghcr.io/oasisprotocol/rofl-dev:main oasis rofl build

echo -n "$CONTRACT_ADDRESS" | oasis rofl secret set --force CONTRACT_ADDRESS - 
echo -n "$TICKER" | oasis rofl secret set --force TICKER - 

# Update the rofl image with the secrets
oasis rofl update # This is an on-chain transaction so it requires a signature

oasis rofl deploy # This is an on-chain transaction so it requires a signature

sleep 20

oasis rofl machine show > rofl_machine.txt

# Extract and display the proxy domain
PROXY_DOMAIN=$(oasis rofl machine show | grep -A1 "Proxy:" | grep "Domain:" | awk '{print $2}')
echo "Proxy domain: $PROXY_DOMAIN"

oasis rofl machine logs
