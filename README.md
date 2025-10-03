# Testing ROFL Deployment

This repository takes code from the Oasis ROFL demos:

1. [Oasis Demo](https://github.com/oasisprotocol/demo-rofl) deploys an Oracle contract on chain, that listens for price updates from a shell script running inside a ROFL node.  We don't take any code directly from this repository, 
    but it is useful because it is the simplest example of how ROFL should work.  We also use an [oracle contract](oracle/src/Oracle.sol), but we have modified our oracle so that it will accept submissions from ROFL as well as other addresses.
1. [Oasis HyperLiquid Copy Trader](https://github.com/oasisprotocol/template-rofl-hl-copy-trader) provides a [rofl client library](https://github.com/oasisprotocol/template-rofl-hl-copy-trader/blob/master/src/clients/rofl.py) in python that we test (see [rofl.py](docker/rofl.py))
1. [Oasis ROFL Chatbot](https://github.com/oasisprotocol/demo-rofl-chatbot) provides a similar [rofl client library](https://github.com/oasisprotocol/demo-rofl-chatbot/blob/main/oracle/src/RoflUtility.py) in python that we test (see [RoflUtility.py](docker/RoflUtility.py))

The main changes are
1) Use Forge to deploy contracts
2) Add scripts to automate the process of starting a ROFL node

# Usage

## Wallet setup

1. Install oasis CLI with `brew install oasis` (on a Mac)
2. Create a wallet `oasis wallet create <ACCT_NAME>` 
    - If you need to do something else (e.g. import an existing wallet, read the [Oasis CLI Documentation](https://docs.oasis.io/build/tools/cli/wallet#create))
3. Fund your wallet at the [faucet](https://faucet.testnet.oasis.dev/) (Make sure you select the sapphire network)
    - This is the wallet that will be used to deploy the ROFL nodes

## ROFL Initialization

1. Run `oasis rofl init` to initialize the ROFL
2. Run `oasis rofl create --network testnet --account <ACCT_NAME>` 
  - This is important because this will generate the rofl app id

## Install foundry and install sapphire contracts
1. Install foundry `curl -L https://foundry.paradigm.xyz | bash` 
    - Documentation [here](https://getfoundry.sh/introduction/installation/)
2. Run `forge init --force --no-git oracle` to set up the oracle folder as a Foundry project
3. Run `forge soldeer init`
4. Run `forge soldeer install @oasisprotocol-sapphire-contracts~0.2.14` 
    - See [Oasis Foundry docs](https://docs.oasis.io/build/tools/foundry/)

## (Redeploy) ROFL instance

The steps above should only be run once.
The steps below should be run at each update.

1. Run `source setenv.sh` (This will set the `ROFL_APP_ID` environment variable, as well as `ADMIN_KEY` and `CONTRACT_ADDRESS` if available)
1. Run `./deploy.sh`.
    - This will use [rofl_encode.py](rofl_encode.py) to convert the `ROFL_APP_ID` to bytes, and deploy the oracle contract
    - The ROFL app ID is needed as a constructor argument for the oracle, so the oracle must be deployed *after* we have the ROFL app ID
1. Run `./rofl_setup.sh`
    - This will recompile the docker container, push it to dockerhub, update the ROFL manifest on chain and deploy the ROFL node
    - This must be done *after* deploying the contracts, because we pass the contract address as an environment variable to the ROFL node
