#!/usr/bin/env python3

import sys
import argparse

# Bech32 implementation
CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'

def bech32_polymod(values):
    """Calculate the Bech32 checksum polynomial."""
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= GEN[i] if ((top >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    """Expand the human readable part."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_verify_checksum(hrp, data):
    """Verify a Bech32 checksum."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

def bech32_create_checksum(hrp, data):
    """Create a Bech32 checksum."""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
    """Encode a Bech32 string."""
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def bech32_decode(bech):
    """Decode a Bech32 string."""
    if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
            (bech.lower() != bech and bech.upper() != bech)):
        return (None, None)
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos > 83 or pos + 7 > len(bech):
        return (None, None)
    if not all(x in CHARSET for x in bech[pos+1:]):
        return (None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos+1:]]
    return (hrp, data[:-6])  # Remove checksum

def convertbits(data, frombits, tobits, pad=True):
    """Convert between bit groups."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def encode_rofl_app_id(rofl_app_id):
    """Encode a ROFL app ID to bytes (hex string)."""
    try:
        # Decode bech32 to get the data
        hrp, data = bech32_decode(rofl_app_id)
        
        if hrp != 'rofl':
            raise ValueError(f'Invalid ROFL app identifier: {rofl_app_id} (must start with "rofl")')
        
        # Convert from 5-bit to 8-bit groups
        decoded_bytes = convertbits(data, 5, 8, False)
        if decoded_bytes is None:
            raise ValueError('Failed to decode bech32 data')
        
        # Convert to hex string with 0x prefix
        hex_string = '0x' + ''.join(f'{b:02x}' for b in decoded_bytes)
        return hex_string
        
    except Exception as e:
        raise ValueError(f'Failed to encode ROFL app ID: {e}')

def decode_rofl_app_id(bytes_input):
    """Decode bytes (hex string) to ROFL app ID."""
    try:
        # Handle hex string input
        if isinstance(bytes_input, str):
            if bytes_input.startswith('0x'):
                hex_string = bytes_input[2:]
            else:
                hex_string = bytes_input
            bytes_data = bytes.fromhex(hex_string)
        else:
            bytes_data = bytes_input
        
        # Convert bytes to 5-bit groups
        data = convertbits(bytes_data, 8, 5, True)
        if data is None:
            raise ValueError('Failed to convert bytes to 5-bit groups')
        
        # Encode to bech32
        rofl_app_id = bech32_encode('rofl', data)
        return rofl_app_id
        
    except Exception as e:
        raise ValueError(f'Failed to decode bytes to ROFL app ID: {e}')

def main():
    parser = argparse.ArgumentParser(description='Encode/decode ROFL app IDs')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encode subcommand
    encode_parser = subparsers.add_parser('encode', help='Encode ROFL app ID to bytes')
    encode_parser.add_argument('rofl_app_id', help='ROFL app ID (starts with "rofl")')
    
    # Decode subcommand
    decode_parser = subparsers.add_parser('decode', help='Decode bytes to ROFL app ID')
    decode_parser.add_argument('bytes', help='Bytes as hex string (with or without 0x prefix)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'encode':
            result = encode_rofl_app_id(args.rofl_app_id)
            print(result)
        elif args.command == 'decode':
            result = decode_rofl_app_id(args.bytes)
            print(result)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
