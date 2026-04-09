import hashlib
import json
import time
from typing import List, Dict

from ecdsa import SigningKey, SECP256k1
from dotenv import dotenv_values


# ------------------------------------------------------------
# Load XYO private key from .env
# ------------------------------------------------------------
def load_xyo_key() -> SigningKey:
    env = dotenv_values()
    sk_hex = env["XYO_SK"]
    return SigningKey.from_string(bytes.fromhex(sk_hex), curve=SECP256k1)


# ------------------------------------------------------------
# Build a Merkle tree from tile hashes
# ------------------------------------------------------------
def merkle_tree(hashes: List[str]) -> List[List[str]]:
    layers = [hashes]

    while len(layers[-1]) > 1:
        layer = layers[-1]
        next_layer = []

        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            combined = hashlib.sha256((left + right).encode()).hexdigest()
            next_layer.append(combined)

        layers.append(next_layer)

    return layers


# ------------------------------------------------------------
# Build Merkle proof for a specific tile
# ------------------------------------------------------------
def build_proof(layers: List[List[str]], index: int) -> List[Dict]:
    proof = []

    for layer in layers[:-1]:
        layer_len = len(layer)
        is_right = index % 2
        pair_index = index - 1 if is_right else index + 1

        if pair_index < layer_len:
            proof.append({
                "position": "left" if is_right else "right",
                "hash": layer[pair_index]
            })

        index //= 2

    return proof


# ------------------------------------------------------------
# Batch tiles and sign the Merkle root
# ------------------------------------------------------------
def batch_tiles(tiles: List[Dict]) -> Dict:
    if not tiles:
        raise ValueError("No tiles provided")

    tile_hashes = [t["hash"] for t in tiles]
    layers = merkle_tree(tile_hashes)
    merkle_root = layers[-1][0]

    ts = int(time.time())
    sk = load_xyo_key()

    payload = f"{merkle_root}:{ts}".encode()
    signature = sk.sign(payload).hex()

    batch_id = hashlib.sha256(payload).hexdigest()

    proofs = {
        h: build_proof(layers, i)
        for i, h in enumerate(tile_hashes)
    }

    return {
        "batch_id": batch_id,
        "tiles": tiles,
        "tile_proofs": proofs,
        "merkle_root": merkle_root,
        "timestamp": ts,
        "xyo_tx": {
            "root": merkle_root,
            "timestamp": ts,
            "signature": signature,
        },
    }