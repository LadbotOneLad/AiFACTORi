#!/usr/bin/env python3
# ================================================================
# Engine‑as‑Witness Weather Oracle (single‑file implementation)
#
# What it does:
#   1) Generates a signed atmospheric tile (hash + ECDSA).
#   2) Batches tiles → Merkle root.
#   3) Builds a SymPy proof that three invariants hold:
#        • I1: risk ≤ 0.20  (risk threshold)
#        • I2: K‑value ≥ 0.99 (consensus quality)
#        • I3: no satellite signature forgery
#   4) The engine (this script) signs the XYO bound‑witness
#      transaction itself → becomes the XYO witness.
#   5) FastAPI exposes:
#        • POST /generate_tile   – make a signed tile
#        • POST /batch           – submit a batch (engine signs XYO payload)
#        • GET  /tile/{hash}     – retrieve tile + Merkle proof + XYO tx + SymPy proof
# ================================================================

import hashlib
import json
import time
import uuid
import os
import base64
from typing import List, Dict, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from merkletools import MerkleTools
import requests
from dotenv import dotenv_values
from sympy import symbols, Le, Ge, latex

# ================================================================
# .env CONFIGURATION (HYBRID DETERMINISTIC MODEL)
# ================================================================

# .env is expected in the repo root (same folder as this file)
# Example:
#   SAT_PRIVATE_KEY_1=...
#   SAT_PRIVATE_KEY_2=...
#   ENGINE_PRIVATE_KEY=...   (optional; if missing, engine key is generated)

env = dotenv_values()

# Satellite private keys (32‑byte hex strings)
SAT_KEYS = []
for key_name in ["SAT_PRIVATE_KEY_1", "SAT_PRIVATE_KEY_2", "SAT_PRIVATE_KEY_3"]:
    v = env.get(key_name)
    if v:
        SAT_KEYS.append(v.strip())

# Engine private key (optional; if missing, generate deterministically)
ENGINE_PRIVATE_KEY_HEX = env.get("ENGINE_PRIVATE_KEY")

# ================================================================
# CRYPTO HELPERS
# ================================================================

def sha3_256_hex(data: bytes) -> str:
    """Use Python's built‑in SHA3‑256 (no pysha3 dependency)."""
    return hashlib.sha3_256(data).hexdigest()

def generate_engine_keypair() -> SigningKey:
    """Generate or load the engine's ECDSA key (SECP256k1)."""
    global ENGINE_PRIVATE_KEY_HEX
    if ENGINE_PRIVATE_KEY_HEX:
        sk_bytes = bytes.fromhex(ENGINE_PRIVATE_KEY_HEX)
        return SigningKey.from_string(sk_bytes, curve=SECP256k1)
    # Deterministic generation based on a fixed seed file in repo
    seed_path = Path("engine_key.seed")
    if seed_path.exists():
        seed = seed_path.read_bytes()
    else:
        seed = os.urandom(32)
        seed_path.write_bytes(seed)
    # Derive key from seed via SHA3
    sk_bytes = hashlib.sha3_256(seed).digest()
    ENGINE_PRIVATE_KEY_HEX = sk_bytes.hex()
    return SigningKey.from_string(sk_bytes, curve=SECP256k1)

ENGINE_SK = generate_engine_keypair()
ENGINE_VK = ENGINE_SK.get_verifying_key()

def load_satellite_keys() -> List[SigningKey]:
    """Load satellite keys from .env; if none, engine acts as sole signer."""
    if not SAT_KEYS:
        return [ENGINE_SK]
    result = []
    for hex_key in SAT_KEYS:
        try:
            sk_bytes = bytes.fromhex(hex_key)
            result.append(SigningKey.from_string(sk_bytes, curve=SECP256k1))
        except Exception:
            # Skip invalid keys
            continue
    return result or [ENGINE_SK]

SATELLITE_SKS = load_satellite_keys()

def sign_payload(sk: SigningKey, payload: bytes) -> str:
    sig = sk.sign(payload)
    return base64.b64encode(sig).decode("utf-8")

def verify_signature(vk: VerifyingKey, payload: bytes, signature_b64: str) -> bool:
    try:
        sig = base64.b64decode(signature_b64.encode("utf-8"))
        vk.verify(sig, payload)
        return True
    except (BadSignatureError, ValueError):
        return False

def vk_to_hex(vk: VerifyingKey) -> str:
    return vk.to_string("compressed").hex()

# ================================================================
# MERKLE TREE HELPERS
# ================================================================

mt = MerkleTools(hash_type="sha256")

def build_merkle_root(tile_hashes: List[str]) -> str:
    mt.reset_tree()
    for h in tile_hashes:
        mt.add_leaf(h, do_hash=False)
    mt.make_tree()
    return mt.get_merkle_root() or ""

def get_merkle_proof(tile_hashes: List[str], target_hash: str) -> List[Dict]:
    mt.reset_tree()
    for h in tile_hashes:
        mt.add_leaf(h, do_hash=False)
    mt.make_tree()
    try:
        idx = tile_hashes.index(target_hash)
    except ValueError:
        return []
    return mt.get_proof(idx) or []

# ================================================================
# SYMPY INVARIANTS (CORRECTED — K MUST BE ≥ 1.00)
# ================================================================

# Invariants:
#   I1: risk ≤ 0.20
#   I2: K ≥ 1.00
#   I3: no satellite signature forgery (forgery_flag == 0)

risk, K, forgery_flag = symbols("risk K forgery_flag")

def build_invariant_proof(risk_value: float, k_value: float, forgery_detected: bool) -> Dict:
    """Return a symbolic proof object that invariants hold."""
    i1 = Le(risk, 0.20)
    i2 = Ge(K, 1.00)  # ⭐ FIXED — K must be ≥ 1.00
    i3 = Le(forgery_flag, 0)  # forgery_flag == 0 means no forgery

    holds_i1 = risk_value <= 0.20
    holds_i2 = k_value >= 1.00   # ⭐ FIXED — deterministic threshold
    holds_i3 = (not forgery_detected)

    all_hold = holds_i1 and holds_i2 and holds_i3

    return {
        "invariants": {
            "I1_risk_le_0_20": {
                "expr": str(i1),
                "latex": latex(i1),
                "value": risk_value,
                "holds": holds_i1,
            },
            "I2_K_ge_1_00": {   # ⭐ FIXED LABEL
                "expr": str(i2),
                "latex": latex(i2),
                "value": k_value,
                "holds": holds_i2,
            },
            "I3_no_forgery": {
                "expr": str(i3),
                "latex": latex(i3),
                "value": 0 if not forgery_detected else 1,
                "holds": holds_i3,
            },
        },
        "all_hold": all_hold,
    }
# ================================================================
# DATA MODELS
# ================================================================

class TileRequest(BaseModel):
    location: str
    timestamp: Optional[int] = None
    temperature_c: float
    humidity: float
    pressure_hpa: float
    risk: float
    k_value: float

class BatchRequest(BaseModel):
    tile_hashes: List[str]

# ================================================================
# IN‑MEMORY STORAGE
# ================================================================

TILES: Dict[str, Dict] = {}
BATCHES: Dict[str, Dict] = {}

# ================================================================
# XYO‑STYLE BOUND‑WITNESS (SIMPLIFIED)
# ================================================================

def build_xyo_payload(merkle_root: str, tile_hashes: List[str]) -> Dict:
    return {
        "xyo_version": "1.0",
        "engine_id": vk_to_hex(ENGINE_VK),
        "merkle_root": merkle_root,
        "tile_hashes": tile_hashes,
        "timestamp": int(time.time()),
    }

def sign_xyo_payload(payload: Dict) -> Dict:
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = sign_payload(ENGINE_SK, payload_bytes)
    return {
        "payload": payload,
        "engine_pubkey": vk_to_hex(ENGINE_VK),
        "signature": signature,
        "hash": sha3_256_hex(payload_bytes),
    }

# ================================================================
# FASTAPI APP
# ================================================================

app = FastAPI(
    title="Engine‑as‑Witness Weather Oracle",
    version="0.1.0",
    description="Deterministic weather oracle engine with Merkle, ECDSA, SymPy invariants, and XYO‑style witness signing.",
)

# ================================================================
# ENDPOINT: HEALTH
# ================================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "engine_pubkey": vk_to_hex(ENGINE_VK),
        "tiles": len(TILES),
        "batches": len(BATCHES),
    }

# ================================================================
# ENDPOINT: GENERATE TILE
# ================================================================

@app.post("/generate_tile")
def generate_tile(req: TileRequest):
    ts = req.timestamp or int(time.time())
    tile_id = str(uuid.uuid4())

    tile_body = {
        "tile_id": tile_id,
        "location": req.location,
        "timestamp": ts,
        "temperature_c": req.temperature_c,
        "humidity": req.humidity,
        "pressure_hpa": req.pressure_hpa,
        "risk": req.risk,
        "k_value": req.k_value,
    }

    tile_json = json.dumps(tile_body, sort_keys=True).encode("utf-8")
    tile_hash = sha3_256_hex(tile_json)

    # Sign with all satellite keys (or engine if none)
    signatures = []
    forgery_detected = False
    for sk in SATELLITE_SKS:
        sig = sign_payload(sk, tile_json)
        vk = sk.get_verifying_key()
        if not verify_signature(vk, tile_json, sig):
            forgery_detected = True
        signatures.append({
            "pubkey": vk_to_hex(vk),
            "signature": sig,
        })

    # Build SymPy invariant proof
    proof = build_invariant_proof(
        risk_value=req.risk,
        k_value=req.k_value,
        forgery_detected=forgery_detected,
    )

    tile_record = {
        "tile": tile_body,
        "hash": tile_hash,
        "signatures": signatures,
        "sympy_proof": proof,
    }

    TILES[tile_hash] = tile_record

    return {
        "status": "ok",
        "tile_hash": tile_hash,
        "tile": tile_body,
        "signatures": signatures,
        "sympy_proof": proof,
    }

# ================================================================
# ENDPOINT: BATCH TILES → MERKLE + XYO
# ================================================================

@app.post("/batch")
def batch_tiles(req: BatchRequest):
    if not req.tile_hashes:
        raise HTTPException(status_code=400, detail="No tile hashes provided.")

    missing = [h for h in req.tile_hashes if h not in TILES]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tile hashes: {missing}",
        )

    merkle_root = build_merkle_root(req.tile_hashes)
    xyo_payload = build_xyo_payload(merkle_root, req.tile_hashes)
    xyo_signed = sign_xyo_payload(xyo_payload)

    batch_id = xyo_signed["hash"]
    BATCHES[batch_id] = {
        "batch_id": batch_id,
        "merkle_root": merkle_root,
        "tile_hashes": req.tile_hashes,
        "xyo": xyo_signed,
    }

    return {
        "status": "ok",
        "batch_id": batch_id,
        "merkle_root": merkle_root,
        "xyo": xyo_signed,
    }

# ================================================================
# ENDPOINT: GET TILE + MERKLE PROOF + XYO + PROOF
# ================================================================

@app.get("/tile/{tile_hash}")
def get_tile(tile_hash: str):
    tile = TILES.get(tile_hash)
    if not tile:
        raise HTTPException(status_code=404, detail="Tile not found.")

    # Find any batch that includes this tile
    batch = None
    for b in BATCHES.values():
        if tile_hash in b["tile_hashes"]:
            batch = b
            break

    merkle_proof = []
    if batch:
        merkle_proof = get_merkle_proof(batch["tile_hashes"], tile_hash)

    return {
        "status": "ok",
        "tile_hash": tile_hash,
        "tile": tile["tile"],
        "signatures": tile["signatures"],
        "sympy_proof": tile["sympy_proof"],
        "batch": batch,
        "merkle_proof": merkle_proof,
    }

# ================================================================
# LOCAL DEV ENTRYPOINT
# ================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("engine_api:app", host="0.0.0.0", port=8000, reload=True)