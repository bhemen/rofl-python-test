#https://raw.githubusercontent.com/oasisprotocol/demo-rofl-chatbot/d3b6d1ea8ae1707aed775d56bd1f24706214fda1/oracle/src/RoflUtility.py
import httpx
import json
import typing
import cbor2
from web3.types import TxParams


class RoflUtility:
    ROFL_SOCKET_PATH = "/run/rofl-appd.sock"

    def __init__(self, url: str = ''):
        self.url = url

    def _appd_post(self, path: str, payload: typing.Any) -> typing.Any:
        transport = None
        if self.url and not self.url.startswith('http'):
            transport = httpx.HTTPTransport(uds=self.url)
            print(f"Using HTTP socket: {self.url}")
        elif not self.url:
            transport = httpx.HTTPTransport(uds=self.ROFL_SOCKET_PATH)
            print(f"Using unix domain socket: {self.ROFL_SOCKET_PATH}")

        client = httpx.Client(transport=transport)

        url = self.url if self.url and self.url.startswith('http') else "http://localhost"
        print(f"  Posting {json.dumps(payload)} to {url+path}")
        response = client.post(url + path, json=payload, timeout=None)
        response.raise_for_status()
        return response.json()

    def fetch_key(self, id: str) -> str:
        payload = {
            "key_id": id,
            "kind": "secp256k1"
        }

        path = '/rofl/v1/keys/generate'

        response = self._appd_post(path, payload)
        return response["key"]

    def submit_tx(self, tx: TxParams) -> dict:
        payload = {
            "tx": {
                "kind": "eth",
                "data": {
                    "gas_limit": tx["gas"],
                    "to": tx["to"].removeprefix("0x"),
                    "value": tx["value"],
                    "data": tx["data"].removeprefix("0x"),
                },
            },
            "encrypt": False,
        }

        path = '/rofl/v1/tx/sign-submit'

        response = self._appd_post(path, payload)
        
        # Check if the response contains CBOR data to deserialize
        if "data" in response and response["data"]:
            return deserialize_response(response)
        else:
            # Return the raw response if no CBOR data (e.g., for error cases)
            return response

def deserialize_response(response: dict) -> dict:
    """
    Deserialize a CBOR-encoded hex string response from the ROFL API.
    
    Args:
        response (dict): The response dictionary containing a 'data' field with CBOR-encoded hex string
        
    Returns:
        dict: The deserialized CBOR data as a Python dictionary
        
    Example:
        # Successful call result
        response = {"data": "a1626f6b40"}
        result = deserialize_response(response)
        # Returns: {"ok": ""}
        
        # Failed call result  
        response = {"data": "a1646661696ca364636f646508666d6f64756c656365766d676d6573736167657272657665727465643a20614a416f4c773d3d"}
        result = deserialize_response(response)
        # Returns: {"fail": {"code": 8, "module": "evm", "message": "reverted: aJAoLw=="}}
    """
    if "data" not in response:
        raise ValueError("Response must contain a 'data' field")
    
    response_hex = response["data"]
    
    # Convert hex string to bytes
    try:
        cbor_bytes = bytes.fromhex(response_hex)
    except ValueError as e:
        raise ValueError(f"Invalid hex string in response data: {e}")
    
    # Deserialize CBOR data
    try:
        deserialized_data = cbor2.loads(cbor_bytes)
        return deserialized_data
    except Exception as e:
        raise ValueError(f"Failed to deserialize CBOR data: {e}")