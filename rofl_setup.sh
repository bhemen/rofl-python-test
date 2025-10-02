#!/bin/bash

if [ ! -f "oracle/foundry.toml" ]; then
    echo "oracle/foundry.toml not found"
    echo "Would you like to create it? (y/n)"
    read -n 1 -s CREATE_FOUNDRY_TOML
    if [ "$CREATE_FOUNDRY_TOML" = "y" ]; then
        forge init --force --no-git oracle
        pushd oracle
        rm -f test/Counter.t.sol
        rm -f src/Counter.sol
        rm -f script/Counter.s.sol
        forge soldeer init
        forge soldeer install @oasisprotocol-sapphire-contracts~0.2.14
        popd
    fi
fi

if [ ! -f "deployed_contract.env" ]; then
    echo "deployed_contract.env not found"
    echo "Would you like to deploy the contract? (y/n)"
    read -n 1 -s DEPLOY_CONTRACT
    if [ "$DEPLOY_CONTRACT" = "y" ]; then
        ./deploy.sh
    fi
    if [ ! -s "deployed_contract.env" ]; then
        echo "Deployment failed"
        exit 1
    fi
fi

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
if [ -z "$RPC_URL" ]; then
    echo "RPC_URL is not set"
    exit 1
fi

# Build the docker image and push it to the registry
pushd docker
docker build -t brettfalk/rofl-demo-python:latest .
docker push brettfalk/rofl-demo-python:latest
popd

docker compose build

# ROFL Commands

# https://docs.oasis.io/build/rofl/quickstart/
# https://docs.oasis.io/general/manage-tokens/cli/rofl

# Build the rofl image
docker run --platform linux/amd64 --volume .:/src -it ghcr.io/oasisprotocol/rofl-dev:main oasis rofl build

echo -n "$CONTRACT_ADDRESS" | oasis rofl secret set --force CONTRACT_ADDRESS - 
echo -n "$ADMIN_KEY" | oasis rofl secret set --force ADMIN_KEY - 
echo -n "$RPC_URL" | oasis rofl secret set --force RPC_URL - 


# Update the rofl image with the secrets
oasis rofl update # This is an on-chain transaction so it requires a signature

oasis rofl deploy # This is an on-chain transaction so it requires a signature

sleep 20

oasis rofl machine show > rofl_machine.txt

# Extract and display the proxy domain
PROXY_DOMAIN=$(oasis rofl machine show | grep -A1 "Proxy:" | grep "Domain:" | awk '{print $2}')
echo "Proxy domain: $PROXY_DOMAIN"

oasis rofl machine logs
