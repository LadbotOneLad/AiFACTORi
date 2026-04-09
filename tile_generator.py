import json
import time
import hashlib
from typing import Dict

from ecdsa import SigningKey, SECP256k1
from dotenv import dotenv_values


# ------------------------------------------------------------
# Load a satellite's private key from .env
# ------------------------------------------------------------
def load_sk(env_name: str) -> SigningKey:
    env = dotenv_values()
    sk_hex = env[env_name]
    return SigningKey.from_string(bytes.fromhex(sk_hex), curve=SECP256k1)


# ------------------------------------------------------------
# Deterministic hash of a tile (pixels + metadata)
# ------------------------------------------------------------
def hash_tile(pixels: bytes, meta: Dict) -> str:
    h_pixels = hashlib.sha256(pixels).digest()
    h_meta = hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).digest()
    return hashlib.sha256(h_pixels + h_meta).hexdigest()


# ------------------------------------------------------------
# Sign the canonical payload: hash || timestamp || nonce
# ------------------------------------------------------------
def sign_tile(tile_hash: str, ts: int, sk: SigningKey) -> str:
    payload = f"{tile_hash}:{ts}:{ts}".encode()
    return sk.sign(payload).hex()


# ------------------------------------------------------------
# Public wrapper – generates a signed tile dict
# ------------------------------------------------------------
def generate_tile(pixels: bytes, meta: Dict, sat_key_env: str) -> Dict:
    ts = int(time.time())
    tile_hash = hash_tile(pixels, meta)
    sk = load_sk(sat_key_env)
    signature = sign_tile(tile_hash, ts, sk)

    return {
        "hash": tile_hash,
        "signature": signature,
        "meta": meta,
        "timestamp": ts,
        "satellite_key_env": sat_key_env,
    }


# ------------------------------------------------------------
# Local test
# ------------------------------------------------------------
if __name__ == "__main__":
    fake_pixels = b"\x00" * 64000
    meta = {
        "satellite": "BOM",
        "band": "VIS",
        "region": "Sydney",
        "bbox": [151.0, -33.5, 151.5, -34.0],
        "timestamp_iso": "2026-04-07T10:32:00Z",
    }
    print(json.dumps(generate_tile(fake_pixels, meta, "SAT_A_SK"), indent=2))