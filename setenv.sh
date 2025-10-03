#!/bin/bash

DOCKER_FQDN="docker.io/brettfalk/rofl-demo-python:latest"

ADMIN_KEY=$(python3 -c "
import json
with open('sapphire_accounts.json', 'r') as f:
    accounts = json.load(f)
for account in accounts:
    if account['label'] == 'admin':
        print(account['secret_key'])
        break
")

export ADMIN_KEY

if [ -f 'rofl.yaml' ]; then
    ROFL_APP_ID=$(grep -A 20 "deployments:" rofl.yaml | grep -A 10 "default:" | grep "app_id:" | awk '{print $2}')
    export ROFL_APP_ID
    echo "ROFL_APP_ID set to $ROFL_APP_ID"
    else
    echo "rofl.yaml not found"
    echo "Run:"
    echo "oasis rofl init"
    echo "oasis rofl create --network testnet --account <ACCT_NAME>"
fi

#echo "ADMIN_KEY set to $ADMIN_KEY"
if [ -z "$ADMIN_KEY" ]; then
    echo "ADMIN_KEY is not set"
    exit 1
else
    echo "ADMIN_KEY set"
fi

RPC_URL="https://testnet.sapphire.oasis.io"

export RPC_URL

if [ -f "deployed_contract.env" ]; then
    source deployed_contract.env
    if [ -z "$CONTRACT_ADDRESS" ]; then
        echo "CONTRACT_ADDRESS is not set"
        exit 1
    else
        echo "CONTRACT_ADDRESS set to $CONTRACT_ADDRESS"
    fi
else
    echo "deployed_contract.env not found"
    echo "Run:"
    echo "./deploy.sh"
fi
