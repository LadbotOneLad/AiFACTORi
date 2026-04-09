# ------------------------------------------------------------
# engine_witness.py (hardened)
# A self-contained deterministic engine that:
#   • hashes + signs satellite tiles,
#   • verifies satellite signatures,
#   • batches them into a Merkle tree,
#   • builds a SymPy risk proof,
#   • signs the batch itself as an XYO witness,
#   • serves verification data via FastAPI.
# ------------------------------------------------------------

import hashlib
import json
import time
import uuid
import os
import base64
from typing import List, Dict, Optional, Any, Set
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from merkletools import MerkleTools
import requests
from dotenv import dotenv_values
from sympy import symbols, Le, latex

# ============================================================
# 0️⃣ Configuration + key management
# ============================================================

class EngineConfig:
    def __init__(self) -> None:
        env = dotenv_values()

        required_keys = [
            "SAT_A_SK",
            "SAT_B_SK",
            "SAT_C_SK",
            "XYO_WITNESS_SK",
            "XYO_ENDPOINT",
        ]

        missing = [k for k in required_keys if k not in env or not env[k]]
        if missing:
            raise RuntimeError(f"Missing required .env keys: {', '.join(missing)}")

        self.SAT_KEYS: Dict[str, str] = {
            "SAT_A_SK": env["SAT_A_SK"],
            "SAT_B_SK": env["SAT_B_SK"],
            "SAT_C_SK": env["SAT_C_SK"],
        }

        self.XYO_WITNESS_SK: str = env["XYO_WITNESS_SK"]
        self.XYO_ENDPOINT: str = env["XYO_ENDPOINT"]
        self.XYO_API_KEY: str = os.getenv("XYO_API_KEY", "")

        # Precompute engine verifying key
        sk_bytes = bytes.fromhex(self.XYO_WITNESS_SK)
        vk = SigningKey.from_string(sk_bytes, curve=SECP256k1).get_verifying_key()
        self.XYO_WITNESS_VK: str = vk.to_string().hex()

    def load_sat_sk(self, env_name: str) -> SigningKey:
        if env_name not in self.SAT_KEYS:
            raise ValueError(f"Unknown satellite key env: {env_name}")
        return SigningKey.from_string(bytes.fromhex(self.SAT_KEYS[env_name]), curve=SECP256k1)

    def load_engine_sk(self) -> SigningKey:
        return SigningKey.from_string(bytes.fromhex(self.XYO_WITNESS_SK), curve=SECP256k1)


CONFIG = EngineConfig()

# ============================================================
# 1️⃣ Tile hashing + satellite signing + verification
# ============================================================

def hash_tile(pixels: bytes, meta: Dict[str, Any]) -> str:
    h_pix = hashlib.sha256(pixels).digest()
    h_meta = hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).digest()
    return hashlib.sha256(h_pix + h_meta).hexdigest()


def sign_tile(tile_hash: str, ts: int, sat_sk: SigningKey) -> str:
    payload = f"{tile_hash}:{ts}:{ts}".encode()  # nonce = ts
    return sat_sk.sign(payload).hex()


def verify_tile_signature(tile_hash: str, ts: int, signature_hex: str, sat_env: str) -> bool:
    """
    Verifies that the given signature matches the satellite key and payload.
    """
    try:
        sat_sk = CONFIG.load_sat_sk(sat_env)
        sat_vk: VerifyingKey = sat_sk.get_verifying_key()
        payload = f"{tile_hash}:{ts}:{ts}".encode()
        sat_vk.verify(bytes.fromhex(signature_hex), payload)
        return True
    except (BadSignatureError, ValueError):
        return False


def generate_tile(pixels: bytes, meta: Dict[str, Any], sat_env: str) -> Dict[str, Any]:
    """
    Returns a dict:
    {
        "hash": "...",
        "signature": "...",
        "meta": {...},
        "timestamp": 1234567890,
        "satellite_key_env": "SAT_A_SK"
    }
    """
    ts = int(time.time())
    tile_hash = hash_tile(pixels, meta)
    sat_sk = CONFIG.load_sat_sk(sat_env)
    sig = sign_tile(tile_hash, ts, sat_sk)
    return {
        "hash": tile_hash,
        "signature": sig,
        "meta": meta,
        "timestamp": ts,
        "satellite_key_env": sat_env,
    }

# ============================================================
# 2️⃣ SymPy risk proof (risk ≤ threshold)
# ============================================================

def symbolic_risk_proof(risk_val: float, thresh_val: float) -> Dict[str, Any]:
    risk, thresh = symbols("risk thresh", real=True, positive=True)
    inequality = Le(risk, thresh)  # risk <= thresh
    concrete = inequality.subs({risk: risk_val, thresh: thresh_val})
    holds = bool(concrete)
    latex_expr = latex(inequality) + r"\;\Longrightarrow\;" + latex(concrete)
    return {
        "expression": str(inequality),
        "holds": holds,
        "latex": latex_expr,
    }

# ============================================================
# 3️⃣ Batch building + XYO witness signing
# ============================================================

def batch_and_witness(signed_tiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not signed_tiles:
        raise ValueError("No tiles provided for batching.")

    # 3.1 Verify we have at least 2 distinct satellite signatures
    distinct_sats: Set[str] = {t.get("satellite_key_env", "") for t in signed_tiles}
    distinct_sats.discard("")
    if len(distinct_sats) < 2:
        raise ValueError("Need signatures from ≥2 distinct satellites.")

    # 3.1b Verify each tile signature
    for t in signed_tiles:
        tile_hash = t.get("hash")
        sig = t.get("signature")
        ts = t.get("timestamp")
        sat_env = t.get("satellite_key_env")
        if not all([tile_hash, sig, ts, sat_env]):
            raise ValueError("Tile missing required fields for verification.")
        if not verify_tile_signature(tile_hash, ts, sig, sat_env):
            raise ValueError(f"Invalid satellite signature for tile {tile_hash}.")

    # 3.2 Build Merkle tree
    mt = MerkleTools(hash_type="sha256")
    mt.add_leaf([t["hash"] for t in signed_tiles], True)
    mt.make_tree()
    merkle_root = mt.get_merkle_root()
    if merkle_root is None:
        raise ValueError("Failed to compute Merkle root.")

    # 3.3 Compute a dummy risk value for the whole batch
    dummy_risk = sum(float(t.get("risk_estimate", 0.0)) for t in signed_tiles) / max(len(signed_tiles), 1)
    RISK_THRESHOLD = 0.20
    sym_proof = symbolic_risk_proof(dummy_risk, RISK_THRESHOLD)

    # 3.4 Build the XYO bound-witness payload
    batch_id = str(uuid.uuid4())
    payload: Dict[str, Any] = {
        "batch_id": batch_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "merkle_root": merkle_root,
        "leaf_count": len(signed_tiles),
        "signer_set": sorted(list(distinct_sats)),
        "sympy_proof": sym_proof,
        "engine_public_key": CONFIG.XYO_WITNESS_VK,
        "risk_aggregate": {
            "dummy_risk": dummy_risk,
            "threshold": RISK_THRESHOLD,
        },
    }

    # 3.5 Engine signs the payload (engine = XYO witness)
    engine_sk = CONFIG.load_engine_sk()
    payload_canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    engine_sig = engine_sk.sign(payload_canonical).hex()
    payload["engine_signature"] = engine_sig

    # 3.6 Submit to XYO
    headers = {
        "Authorization": f"Bearer {CONFIG.XYO_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(CONFIG.XYO_ENDPOINT, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        xyo_tx = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to submit to XYO: {e}")

    # 3.7 Build per-tile Merkle proofs
    tile_proofs: Dict[str, Any] = {}
    for idx, tile in enumerate(signed_tiles):
        proof = mt.get_proof(idx)
        tile_proofs[tile["hash"]] = proof

    # 3.8 Return everything needed for the API
    return {
        "batch_id": batch_id,
        "xyo_tx": xyo_tx,
        "merkle_root": merkle_root,
        "tile_proofs": tile_proofs,
        "tiles": signed_tiles,
        "sympy_proof": sym_proof,
    }

# ============================================================
# 4️⃣ FastAPI service (verification layer)
# ============================================================

app = FastAPI(title="Engine-as-Witness Weather Oracle")

# In-memory store for demo purposes
BATCH_STORE: Dict[str, Dict[str, Any]] = {}


class TileMeta(BaseModel):
    satellite: str = Field(..., description="Satellite identifier")
    band: str
    region: str
    bbox: List[float] = Field(..., min_items=4, max_items=4)
    timestamp_iso: str


class TileRequest(BaseModel):
    pixels: str  # base64-encoded pixel bytes
    meta: TileMeta


class SympyProof(BaseModel):
    expression: str
    holds: bool
    latex: str


class VerifyResponse(BaseModel):
    hash: str
    signature: str
    meta: Dict[str, Any]
    timestamp: int
    merkle_proof: List[Dict[str, Any]]
    xyo_tx: Dict[str, Any]
    sympy_proof: Optional[SympyProof] = None


def decode_pixels(b64: str) -> bytes:
    try:
        return base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 pixel data")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "engine_public_key": CONFIG.XYO_WITNESS_VK,
    }


@app.post("/generate_tile")
def api_generate(req: TileRequest) -> Dict[str, Any]:
    pixels = decode_pixels(req.pixels)
    tile = generate_tile(pixels, req.meta.dict(), "SAT_A_SK")
    return tile


@app.post("/batch")
def api_batch(tiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    The client posts a JSON array where each element is the dict
    returned by `/generate_tile`. The engine validates signatures,
    builds a Merkle root, creates a SymPy proof, signs the payload
    as the XYO witness, and posts it to the XYO network.
    """
    try:
        batch_res = batch_and_witness(tiles)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

    BATCH_STORE[batch_res["batch_id"]] = batch_res
    return {
        "batch_id": batch_res["batch_id"],
        "xyo_tx": batch_res["xyo_tx"],
        "merkle_root": batch_res["merkle_root"],
    }


@app.get("/tile/{tile_hash}", response_model=VerifyResponse)
def get_tile(tile_hash: str) -> VerifyResponse:
    for batch in BATCH_STORE.values():
        for tile in batch["tiles"]:
            if tile["hash"] == tile_hash:
                return VerifyResponse(
                    hash=tile["hash"],
                    signature=tile["signature"],
                    meta=tile["meta"],
                    timestamp=tile["timestamp"],
                    merkle_proof=batch["tile_proofs"][tile_hash],
                    xyo_tx=batch["xyo_tx"],
                    sympy_proof=batch.get("sympy_proof"),
                )
    raise HTTPException(status_code=404, detail="Tile not found")