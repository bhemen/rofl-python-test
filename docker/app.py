from rofl import RoflAppdClient
from RoflUtility import RoflUtility
from eth_account import Account
from web3 import Web3
import os
import json

accounts = {}

try:
    rofl = RoflAppdClient()
except Exception as e:
    print(f"Error creating RoflAppdClient: {e}")
    rofl = None

try:
    rofl_utility = RoflUtility()
except Exception as e:
    print(f"Error creating RoflUtility: {e}")
    rofl_utility = None

try:
    if rofl is not None:
        sk, address = rofl.get_keypair()
        accounts['rofl'] = Account.from_key(sk)
    else:
        print("Skipping rofl account creation - RoflAppdClient not available")
except Exception as e:
    print(f"Error getting keypair or creating account: {e}")

try:
    if rofl_utility is not None:
        sk_utility = rofl_utility.fetch_key("copy_trade.key")
        sk_utility = '0x' + sk_utility
        accounts['utility'] = Account.from_key(sk_utility)
    else:
        print("Skipping utility account creation - RoflUtility not available")
except Exception as e:
    print(f"Error fetching utility key or creating account: {e}")

try:
    accounts['new'] = Account.create()
except Exception as e:
    print(f"Error creating new account: {e}")

try:
    accounts['admin'] = Account.from_key(os.getenv("ADMIN_KEY"))
except Exception as e:
    print(f"Error creating admin account: {e}")

oracle_address = os.getenv("CONTRACT_ADDRESS")
if not oracle_address:
    exit(1)

rpc_url = os.getenv("RPC_URL", "http://localhost:8545")

try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        if rpc_url != "http://localhost:8545":
            print(f"Failed to connect to RPC provider at {rpc_url}")
            rpc_url = "http://localhost:8545"
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
            except Exception as e:
                print(f"Error setting up Web3 connection: {e}")
                exit(1)
            if not w3.is_connected():
                print(f"Failed to connect to RPC provider at {rpc_url}")
                exit(1)
        else:
            exit(1)
except Exception as e:
    print(f"Error setting up Web3 connection: {e}")
    exit(1)

try:
    with open("Oracle.abi", "r") as f:
        oracle_abi = json.load(f)
    contract = w3.eth.contract(address=oracle_address, abi=oracle_abi)
except Exception as e:
    print(f"Error loading ABI or creating contract: {e}")
    exit(1)

for i, (name, account) in enumerate(accounts.items()):
    try:
        tx = contract.functions.submitMessage(i).buildTransaction({
            "from": account.address,
            "value": 0,
            "gas": 500000,
            "gasPrice": w3.toWei("1", "gwei"),
            "nonce": w3.eth.getTransactionCount(account.address),
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(f"{name}: {tx_hash.hex()}")
    except Exception as e:
        print(f"Error processing transaction for {name}: {e}")
        continue

try:
    if 'utility' in accounts and rofl_utility is not None:
        tx = contract.functions.submitMessage(501).buildTransaction({
            "from": accounts['utility'].address,
            "value": 0,
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.getTransactionCount(accounts['utility'].address),
        })

        rofl_utility.submit_tx(tx)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        print("Skipping transaction 501 - required components not available")
except Exception as e:
    print(f"Error processing transaction 501: {e}")

try:
    if rofl_utility is not None:
        tx = contract.functions.submitMessage(502).buildTransaction({
            "gasPrice": w3.eth.gas_price,
        })

        rofl_utility.submit_tx(tx)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        print("Skipping transaction 502 - required components not available")
except Exception as e:
    print(f"Error processing transaction 502: {e}")