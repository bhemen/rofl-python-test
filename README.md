# Testing ROFL Deployment

This repository is basically a copy of the [Oasis Demo](https://github.com/oasisprotocol/demo-rofl)

The main changes are
1) Use Forge to deploy contracts
2) Add scripts to automate the process of starting a ROFL node

# Ordering of events

1. Run `oasis rofl init` to initialize the ROFL
1. Run `oasis rofl create --network testnet --account <ACCT_NAME>`
  * This is important because this will generate the rofl app id
1. Run `forge init --force --no-git oracle` to set up the oracle folder as a Foundry project
1. Run `forge soldeer init`
1. Run `forge soldeer install @oasisprotocol-sapphire-contracts~0.2.14` See [Oasis Foundry docs](https://docs.oasis.io/build/tools/foundry/)

The steps above should only be run once.
The steps below should be run at each update.

1. Run `source setenv.sh`
  * This will set the `ROFL_APP_ID` environment variable.
1. Run `./deploy.sh`
  * This will use [rofl_encode.py](rofl_encode.py) to convert the `ROFL_APP_ID` to bytes, and deploy the oracle contract
  * The ROFL app ID is needed as a constructor argument for the oracle, so the oracle must be deployed *after* we have the ROFL app ID
1. Run `./rofl_setup.sh`
  * This will recompile the docker container, push it to dockerhub, update the ROFL manifest on chain and deploy the ROFL node
  * This must be done *after* deploying the contracts, because we pass the contract address as an environment variable to the ROFL node
