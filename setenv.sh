#!/bin/bash

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

source deployed_contract.env

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "CONTRACT_ADDRESS is not set"
    exit 1
else
    echo "CONTRACT_ADDRESS set to $CONTRACT_ADDRESS"
fi


ROFL_APP_ID=$(grep -A 20 "deployments:" rofl.yaml | grep -A 10 "default:" | grep "app_id:" | awk '{print $2}')

export ROFL_APP_ID

#echo "ADMIN_KEY set to $ADMIN_KEY"
if [ -z "$ADMIN_KEY" ]; then
    echo "ADMIN_KEY is not set"
    exit 1
else
    echo "ADMIN_KEY set"
fi
echo "ROFL_APP_ID set to $ROFL_APP_ID"

RPC_URL="https://testnet.sapphire.oasis.io"

export RPC_URL