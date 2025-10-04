#!/bin/bash

source setenv.sh

RPC_URL="https://testnet.sapphire.oasis.io"
CHAIN_ID=23295

if [ -z "$ROFL_APP_ID" ]; then
    echo "ROFL_APP_ID is not set"
    exit 1
fi

# Convert ROFL app ID from bech32 to bytes
# Check if the prefix is "rofl"
if [[ ! "$ROFL_APP_ID" =~ ^rofl1 ]]; then
    echo "Error: Malformed ROFL app identifier: $ROFL_APP_ID"
    echo "Expected format: rofl1..."
    exit 1
fi

# Decode bech32 to hex bytes using rofl_encode.py
RAW_APP_ID=$(python3 rofl_encode.py encode "$ROFL_APP_ID" 2>&1)

if [ $? -ne 0 ]; then
    echo "Failed to convert ROFL app ID to bytes"
    echo "$RAW_APP_ID"
    exit 1
fi

echo "ROFL App ID: $ROFL_APP_ID"
echo "Raw App ID (bytes): $RAW_APP_ID"

pushd oracle
# Deploy the contract and capture output
OUTPUT=$(forge create src/Oracle.sol:Oracle \
    --broadcast \
    --rpc-url $RPC_URL \
    --private-key $ADMIN_KEY \
    --chain-id $CHAIN_ID \
    --verify \
    --verifier sourcify \
    --constructor-args $RAW_APP_ID 2>&1)
popd

# Extract the deployed contract address
CONTRACT_ADDRESS=$(echo "$OUTPUT" | grep -oE "Deployed to: 0x[a-fA-F0-9]{40}" | cut -d' ' -f3)

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "Failed to deploy contract or extract address"
    echo "Output: $OUTPUT"
    exit 1
fi

echo "Contract deployed successfully!"
echo "Contract address: $CONTRACT_ADDRESS"

# Save the contract address to a file for future reference
echo "export CONTRACT_ADDRESS=$CONTRACT_ADDRESS" > deployed_contract.env
echo "Contract address saved to deployed_contract.env"

# Extract the ABI from Oracle.json and save to docker folder
echo "Extracting ABI from Oracle contract..."
jq '.abi' oracle/out/Oracle.sol/Oracle.json > docker/oracle.abi
echo "Oracle ABI saved to docker/oracle.abi"

# https://docs.oasis.io/build/tools/verification#verification-with-foundry
pushd oracle
forge verify-contract $CONTRACT_ADDRESS --chain-id $CHAIN_ID src/Oracle.sol:Oracle --verifier sourcify
popd
