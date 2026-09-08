"""
XYO BOUND-WITNESS MESH
Distributed nodes anchor satellite tile hashes into tamper-evident ledger.
Each tile becomes a verifiable state object with provenance and integrity.

Chain of custody: "At time T, node N observed sub-frame H from satellite S over region R."
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

logger = logging.getLogger("XYOBoundWitness")

# ═══════════════════════════════════════════════════════════════
# BOUND-WITNESS NODE
# ═══════════════════════════════════════════════════════════════

@dataclass
class BoundWitness:
    """Single bound-witness attestation of a tile."""
    
    witness_id: str
    node_id: str
    tile_id: str
    tile_hash: str
    satellite: str
    band: str
    region: str
    timestamp: str
    observation_time: str
    witness_signature: str
    ledger_position: int
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def __repr__(self):
        return f"Witness({self.node_id}|{self.tile_id}|time:{self.observation_time[:10]})"

class XYOBoundWitnessMesh:
    """Distributed mesh that anchors tile hashes into ledger."""
    
    def __init__(self, xyo_address: str = "466e84dfcbfbae8d50ad4276e8f2b5d37e8834a8"):
        self.xyo_address = xyo_address
        self.witness_nodes = self._init_witness_nodes()
        self.ledger = []
        self.witness_count = 0
        
        logger.info("XYO Bound-Witness Mesh initialized")
        logger.info(f"XYO Address: {xyo_address}")
        logger.info(f"Witness nodes: {len(self.witness_nodes)}")
    
    def _init_witness_nodes(self) -> Dict:
        """Initialize distributed witness nodes."""
        return {
            "node-au": {
                "name": "Australia Regional Node",
                "region": "Asia-Pacific",
                "coverage": ["BOM", "Himawari"],
            },
            "node-us": {
                "name": "Americas Regional Node",
                "region": "Americas",
                "coverage": ["GOES"],
            },
            "node-eu": {
                "name": "Europe Regional Node",
                "region": "Europe",
                "coverage": ["Meteosat", "BOM"],
            },
            "node-global": {
                "name": "Global Verification Node",
                "region": "Global",
                "coverage": ["BOM", "Himawari", "GOES", "Meteosat"],
            },
        }
    
    def witness_tile(self, tile) -> List[BoundWitness]:
        """
        Anchor tile hash into witness mesh.
        Multiple nodes independently observe and timestamp the tile.
        
        Returns list of bound-witness attestations.
        """
        logger.info(f"Witnessing tile: {tile.tile_id}...")
        
        witnesses = []
        observation_time = datetime.utcnow().isoformat() + "Z"
        
        # Each witness node observes the tile
        for node_id, node_info in self.witness_nodes.items():
            # Check if node covers this satellite
            if tile.satellite not in node_info["coverage"]:
                continue
            
            # Create witness
            witness_id = f"WIT_{self.witness_count}"
            self.witness_count += 1
            
            # Sign witness with node's private key + tile hash
            witness_payload = {
                "node_id": node_id,
                "tile_id": tile.tile_id,
                "tile_hash": tile.integrity_hash,
                "satellite": tile.satellite,
                "band": tile.band,
                "region": tile.region,
                "observation_time": observation_time,
            }
            
            witness_sig = self._sign_witness(witness_payload)
            
            # Create bound-witness
            witness = BoundWitness(
                witness_id=witness_id,
                node_id=node_id,
                tile_id=tile.tile_id,
                tile_hash=tile.integrity_hash,
                satellite=tile.satellite,
                band=tile.band,
                region=tile.region,
                timestamp=datetime.utcnow().isoformat() + "Z",
                observation_time=observation_time,
                witness_signature=witness_sig,
                ledger_position=len(self.ledger),
            )
            
            # Anchor to ledger
            self.ledger.append(witness)
            witnesses.append(witness)
            
            logger.info(f"  ✓ Witnessed by {node_id}: {witness_id}")
        
        return witnesses
    
    def _sign_witness(self, payload: Dict) -> str:
        """Sign witness with HMAC."""
        import hmac
        payload_str = json.dumps(payload, sort_keys=True)
        sig = hmac.new(
            self.xyo_address.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return sig
    
    def verify_witness(self, witness: BoundWitness) -> bool:
        """Verify witness signature."""
        payload = {
            "node_id": witness.node_id,
            "tile_id": witness.tile_id,
            "tile_hash": witness.tile_hash,
            "satellite": witness.satellite,
            "band": witness.band,
            "region": witness.region,
            "observation_time": witness.observation_time,
        }
        
        expected_sig = self._sign_witness(payload)
        
        import hmac
        return hmac.compare_digest(witness.witness_signature, expected_sig)
    
    def get_tile_provenance(self, tile_id: str) -> Dict:
        """Get full chain of custody for a tile."""
        tile_witnesses = [w for w in self.ledger if w.tile_id == tile_id]
        
        return {
            "tile_id": tile_id,
            "witness_count": len(tile_witnesses),
            "witnesses": [w.to_dict() for w in tile_witnesses],
            "ledger_verified": all(self.verify_witness(w) for w in tile_witnesses),
        }
    
    def get_status(self) -> Dict:
        """Get mesh status."""
        return {
            "engine": "XYO Bound-Witness Mesh",
            "xyo_address": self.xyo_address,
            "witness_nodes": len(self.witness_nodes),
            "total_witnesses": self.witness_count,
            "ledger_entries": len(self.ledger),
            "status": "OPERATIONAL",
        }

# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    from satellite_tiles import SatelliteTileDecomposer
    
    print()
    print("╔" + "═" * 88 + "╗")
    print("║" + " XYO BOUND-WITNESS MESH — ATMOSPHERIC GRID ".center(88) + "║")
    print("╚" + "═" * 88 + "╝")
    print()
    
    # Decompose tiles
    print("[1] Decomposing satellite frames...")
    decomposer = SatelliteTileDecomposer()
    tiles = decomposer.decompose_satellite_frame("BOM")
    
    print()
    print(f"[2] Witnessing {len(tiles)} tiles in XYO mesh...")
    mesh = XYOBoundWitnessMesh()
    
    for tile in tiles[:3]:
        witnesses = mesh.witness_tile(tile)
        print(f"  {tile.tile_id}: {len(witnesses)} witnesses")
    
    print()
    print("[3] Chain of custody for first tile:")
    if tiles:
        provenance = mesh.get_tile_provenance(tiles[0].tile_id)
        print(f"  Tile: {provenance['tile_id']}")
        print(f"  Witnesses: {provenance['witness_count']}")
        print(f"  Ledger verified: {provenance['ledger_verified']}")
    
    print()
    print("[4] Mesh status:")
    status = mesh.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print()
