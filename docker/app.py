from rofl import RoflAppdClient
from RoflUtility import RoflUtility
from eth_account import Account
from web3 import Web3
import os
import json
import time
import logging
import sys


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/app.log')
    ]
)

logger = logging.getLogger(__name__)

accounts = {}
time.sleep(60)

try:
    rofl = RoflAppdClient()
except Exception as e:
    logger.error(f"Error creating RoflAppdClient: {e}")
    rofl = None

try:
    rofl_utility = RoflUtility()
except Exception as e:
    logger.error(f"Error creating RoflUtility: {e}")
    rofl_utility = None

try:
    if rofl is not None:
        sk, address = rofl.get_keypair("rofl_main.key")
        accounts['rofl'] = Account.from_key(sk)
    else:
        logger.info("Skipping rofl account creation - RoflAppdClient not available")
except Exception as e:
    logger.error(f"Error getting keypair or creating account: {e}")

try:
    if rofl_utility is not None:
        sk_utility = rofl_utility.fetch_key("copy_trade.key")
        sk_utility = '0x' + sk_utility
        accounts['utility'] = Account.from_key(sk_utility)
    else:
        logger.info("Skipping utility account creation - RoflUtility not available")
except Exception as e:
    logger.error(f"Error fetching utility key or creating account: {e}")

try:
    accounts['new'] = Account.create()
    logger.info(f"New account created: {accounts['new'].address}")
except Exception as e:
    logger.error(f"Error creating new account: {e}")

try:
    admin_key = os.getenv("ADMIN_KEY")
    if admin_key:
        accounts['admin'] = Account.from_key(admin_key)
        logger.info(f"Admin account found: {accounts['admin'].address}")
    else:
        logger.info("Skipping admin account creation - ADMIN_KEY environment variable not set")
except Exception as e:
    logger.error(f"Error creating admin account: {e}")

oracle_address = os.getenv("CONTRACT_ADDRESS")
logger.info(f"CONTRACT_ADDRESS from env: {oracle_address}")
if not oracle_address:
    logger.error("ERROR: CONTRACT_ADDRESS environment variable is not set!")
    exit(1)

rpc_url = os.getenv("RPC_URL", "http://localhost:8545")
logger.info(f"RPC_URL: {rpc_url}")

try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    logger.info(f"Attempting Web3 connection to: {rpc_url}")
    if not w3.is_connected():
        logger.error(f"Failed to connect to Web3 provider at {rpc_url}")
        if rpc_url != "http://localhost:8545":
            logger.error(f"Failed to connect to RPC provider at {rpc_url}")
            rpc_url = "http://localhost:8545"
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
            except Exception as e:
                logger.error(f"Error setting up Web3 connection: {e}")
                exit(1)
            if not w3.is_connected():
                logger.error(f"Failed to connect to RPC provider at {rpc_url}")
                exit(1)
        else:
            exit(1)
    logger.info("Web3 connection successful!")
except Exception as e:
    logger.error(f"Error setting up Web3 connection: {e}")
    exit(1)

try:
    logger.info("Loading oracle.abi file...")
    with open("oracle.abi", "r") as f:
        oracle_abi = json.load(f)
    logger.info(f"Creating contract with address: {oracle_address}")
    contract = w3.eth.contract(address=oracle_address, abi=oracle_abi)
    logger.info("Contract created successfully!")
except Exception as e:
    logger.error(f"Error loading ABI or creating contract: {e}")
    exit(1)

for i, (name, account) in enumerate(accounts.items()):
    logger.info(f"Submitting transaction for {name} from {account.address} to {contract.address}")
    try:
        tx = contract.functions.submitMessage(i).build_transaction({
            "from": account.address,
            "value": 0,
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address),
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f"{name}: {tx_hash.hex()}")
    except Exception as e:
        logger.error(f"Error processing transaction for {name}: {e}")
        continue
        
try:
    if 'utility' in accounts and rofl_utility is not None:
        tx = contract.functions.submitMessage(501).build_transaction({
            "from": accounts['utility'].address,
            "value": 0,
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(accounts['utility'].address),
        })

        signed_tx_data = rofl_utility.submit_tx(tx)
        logger.info(f"utility_tx_501: Transaction submitted via utility")
    else:
        logger.info("Skipping transaction 501 - required components not available")
except Exception as e:
    logger.error(f"Error processing transaction 501: {e}")
    
try:
    if rofl_utility is not None:
        tx = contract.functions.submitMessage(502).build_transaction({
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx_data = rofl_utility.submit_tx(tx)
        logger.info(f"utility_tx_502: Transaction submitted via utility")
    else:
        logger.info("Skipping transaction 502 - required components not available")
except Exception as e:
<<<<<<< HEAD
    print(f"Error processing transaction 502: {e}")
=======
    logger.error(f"Error processing transaction 502: {e}")
>>>>>>> c3e251460cc4a070a9c03c14c5c4221791d59dba
