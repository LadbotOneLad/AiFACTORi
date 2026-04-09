import time
import base64
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tile_generator import generate_tile
from batcher import batch_tiles


app = FastAPI(title="Weather‑Oracle Tile Verification Service")


# ------------------------------------------------------------
# In‑memory storage
# ------------------------------------------------------------
BATCH_STORAGE: Dict[str, Dict] = {}


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------
class TileMeta(BaseModel):
    satellite: str
    band: str
    region: str
    bbox: List[float]
    timestamp_iso: str


class TileRequest(BaseModel):
    pixels: str
    meta: TileMeta


class VerifyResponse(BaseModel):
    hash: str
    signature: str
    meta: TileMeta
    timestamp: int
    merkle_proof: List[Dict]
    xyo_tx: Dict


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def decode_pixels(b64: str) -> bytes:
    return base64.b64decode(b64)


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------
@app.post("/generate_tile")
def api_generate(req: TileRequest):
    pixels = decode_pixels(req.pixels)
    meta = req.meta.dict()
    return generate_tile(pixels, meta, "SAT_A_SK")


@app.post("/batch")
def api_batch(tiles: List[Dict]):
    try:
        batch_res = batch_tiles(tiles)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    BATCH_STORAGE[batch_res["batch_id"]] = batch_res
    return {"batch_id": batch_res["batch_id"], "xyo_tx": batch_res["xyo_tx"]}


@app.get("/tile/{tile_hash}", response_model=VerifyResponse)
def get_tile(tile_hash: str):
    for batch in BATCH_STORAGE.values():
        for tile in batch["tiles"]:
            if tile["hash"] == tile_hash:
                return VerifyResponse(
                    hash=tile["hash"],
                    signature=tile["signature"],
                    meta=tile["meta"],
                    timestamp=tile["timestamp"],
                    merkle_proof=batch["tile_proofs"][tile_hash],
                    xyo_tx=batch["xyo_tx"],
                )
    raise HTTPException(status_code=404, detail="Tile not found")


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.time()}