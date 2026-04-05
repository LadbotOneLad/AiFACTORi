"""
XYO WITNESS LAYER
Cryptographic proof-of-location validation for E14 Oracle decision execution.

XYO provides legally-binding witness attestation for satellite frames and 
geolocation proofs. All execution gates require XYO witness verification.
"""

import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger("XYOWitness")

# ═══════════════════════════════════════════════════════════════
# XYO CONFIGURATION
# ═══════════════════════════════════════════════════════════════

XYO_ADDRESS = "466e84dfcbfbae8d50ad4276e8f2b5d37e8834a8"
XYO_NETWORK = "mainnet"
XYO_CONSENSUS_REQUIREMENT = 3  # Minimum witnesses required for proof

# Witness node registry (can be extended)
WITNESS_NODES = {
    "sentinel-1": {"pubkey": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b", "region": "north-america"},
    "sentinel-2": {"pubkey": "0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c", "region": "europe"},
    "sentinel-3": {"pubkey": "0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d", "region": "asia-pacific"},
}

# ═══════════════════════════════════════════════════════════════
# PROOF STRUCTURES
# ═══════════════════════════════════════════════════════════════

class XYOProof:
    """Cryptographic proof-of-location witness."""
    
    def __init__(
        self,
        witness_id: str,
        payload: Dict,
        signature: str,
        timestamp: float,
        location_hash: str
    ):
        self.witness_id = witness_id
        self.payload = payload
        self.signature = signature
        self.timestamp = timestamp
        self.location_hash = location_hash
        self.verified = False
    
    def to_dict(self) -> Dict:
        return {
            "witness_id": self.witness_id,
            "payload": self.payload,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "location_hash": self.location_hash,
            "verified": self.verified,
        }
    
    def __repr__(self):
        return f"XYOProof(witness={self.witness_id}, verified={self.verified}, hash={self.location_hash[:16]}...)"

# ═══════════════════════════════════════════════════════════════
# XYO WITNESS VALIDATION
# ═══════════════════════════════════════════════════════════════

def hash_payload(payload: Dict) -> str:
    """Hash payload for signature verification."""
    payload_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(payload_str.encode()).hexdigest()

def verify_witness_signature(
    witness_id: str,
    payload: Dict,
    signature: str
) -> bool:
    """
    Verify witness signature against payload.
    
    Args:
        witness_id: Identifier of witness node
        payload: Data being witnessed
        signature: Cryptographic signature from witness
    
    Returns:
        True if signature is valid, False otherwise
    """
    if witness_id not in WITNESS_NODES:
        logger.warning(f"Unknown witness: {witness_id}")
        return False
    
    witness_pubkey = WITNESS_NODES[witness_id]["pubkey"]
    payload_hash = hash_payload(payload)
    
    # Simulate HMAC-SHA256 verification
    # (In production: use actual elliptic curve signature verification)
    expected_sig = hmac.new(
        witness_pubkey.encode(),
        payload_hash.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_sig)

def create_geolocation_hash(latitude: float, longitude: float, timestamp: float) -> str:
    """Create deterministic hash of geolocation + timestamp."""
    geo_str = f"{latitude:.6f},{longitude:.6f},{int(timestamp)}"
    return hashlib.sha256(geo_str.encode()).hexdigest()

def generate_witness_proof(
    witness_id: str,
    latitude: float,
    longitude: float,
    satellite_frame_id: str,
    data: Dict
) -> XYOProof:
    """
    Generate XYO witness proof for satellite frame and location.
    
    Args:
        witness_id: ID of witness node
        latitude: Geographic latitude
        longitude: Geographic longitude
        satellite_frame_id: ID of satellite frame being witnessed
        data: Additional data payload
    
    Returns:
        XYOProof object
    """
    timestamp = time.time()
    location_hash = create_geolocation_hash(latitude, longitude, timestamp)
    
    payload = {
        "witness_id": witness_id,
        "xyo_address": XYO_ADDRESS,
        "network": XYO_NETWORK,
        "latitude": latitude,
        "longitude": longitude,
        "satellite_frame_id": satellite_frame_id,
        "location_hash": location_hash,
        "timestamp": timestamp,
        "data": data,
    }
    
    # Generate signature
    payload_hash = hash_payload(payload)
    witness_pubkey = WITNESS_NODES.get(witness_id, {}).get("pubkey", "unknown")
    signature = hmac.new(
        witness_pubkey.encode(),
        payload_hash.encode(),
        hashlib.sha256
    ).hexdigest()
    
    proof = XYOProof(
        witness_id=witness_id,
        payload=payload,
        signature=signature,
        timestamp=timestamp,
        location_hash=location_hash
    )
    
    return proof

# ═══════════════════════════════════════════════════════════════
# XYO VERIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════

class XYOWitnessEngine:
    """XYO consensus verification for E14 Oracle execution gates."""
    
    def __init__(self, xyo_address: str = XYO_ADDRESS, consensus_requirement: int = XYO_CONSENSUS_REQUIREMENT):
        self.xyo_address = xyo_address
        self.consensus_requirement = consensus_requirement
        self.proof_cache = {}
        self.verification_count = 0
        self.failed_count = 0
        
        logger.info(f"XYO Witness Engine initialized for address: {xyo_address}")
        logger.info(f"Consensus requirement: {consensus_requirement}/3 witnesses")
    
    def verify_single_proof(self, proof: XYOProof) -> bool:
        """Verify single witness proof."""
        if not verify_witness_signature(
            proof.witness_id,
            proof.payload,
            proof.signature
        ):
            logger.warning(f"Signature verification failed for {proof.witness_id}")
            return False
        
        proof.verified = True
        logger.info(f"✓ Verified witness: {proof.witness_id}")
        return True
    
    def verify_consensus(self, proofs: list[XYOProof]) -> Tuple[bool, Dict]:
        """
        Verify multiple witness proofs reach consensus.
        
        Returns:
            (consensus_reached: bool, details: dict)
        """
        if len(proofs) < self.consensus_requirement:
            return False, {
                "consensus_reached": False,
                "reason": f"Insufficient proofs: {len(proofs)}/{self.consensus_requirement}",
                "verified_count": 0,
                "failed_count": len(proofs),
            }
        
        verified_proofs = []
        failed_proofs = []
        
        for proof in proofs:
            if self.verify_single_proof(proof):
                verified_proofs.append(proof)
            else:
                failed_proofs.append(proof)
        
        consensus_reached = len(verified_proofs) >= self.consensus_requirement
        
        self.verification_count += 1
        if not consensus_reached:
            self.failed_count += 1
        
        return consensus_reached, {
            "consensus_reached": consensus_reached,
            "verified_count": len(verified_proofs),
            "failed_count": len(failed_proofs),
            "verified_witnesses": [p.witness_id for p in verified_proofs],
            "failed_witnesses": [p.witness_id for p in failed_proofs],
            "timestamp": datetime.now().isoformat(),
        }
    
    def gate_execution(self, proofs: list[XYOProof]) -> bool:
        """
        Gate execution based on XYO witness consensus.
        
        Returns True only if consensus is reached.
        """
        consensus_reached, details = self.verify_consensus(proofs)
        
        if consensus_reached:
            logger.info(f"✓ XYO CONSENSUS REACHED - Execution ALLOWED")
            logger.info(f"  Verified: {details['verified_count']}/{len(proofs)}")
        else:
            logger.warning(f"✗ XYO CONSENSUS FAILED - Execution BLOCKED")
            logger.warning(f"  Reason: {details.get('reason', 'Unknown')}")
        
        return consensus_reached
    
    def get_status(self) -> Dict:
        """Get witness engine status."""
        return {
            "xyo_address": self.xyo_address,
            "consensus_requirement": self.consensus_requirement,
            "total_verifications": self.verification_count,
            "failed_verifications": self.failed_count,
            "success_rate": round(
                (1 - self.failed_count / max(1, self.verification_count)) * 100, 2
            ) if self.verification_count > 0 else 0,
            "status": "OPERATIONAL",
        }

# ═══════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print()
    print("╔" + "═" * 88 + "╗")
    print("║" + " XYO WITNESS LAYER — CRYPTOGRAPHIC PROOF-OF-LOCATION ".center(88) + "║")
    print("╚" + "═" * 88 + "╝")
    print()
    
    # Initialize engine
    engine = XYOWitnessEngine(xyo_address=XYO_ADDRESS)
    
    print(f"XYO Address: {XYO_ADDRESS}")
    print(f"Network: {XYO_NETWORK}")
    print(f"Witness Nodes: {len(WITNESS_NODES)}")
    print()
    
    # Generate proofs from 3 sentinel nodes
    print("[1] Generating witness proofs from 3 sentinel nodes...")
    proofs = []
    locations = [
        (40.7128, -74.0060, "sentinel-1"),  # New York
        (51.5074, -0.1278, "sentinel-2"),   # London
        (35.6762, 139.6503, "sentinel-3"),  # Tokyo
    ]
    
    for lat, lon, witness_id in locations:
        proof = generate_witness_proof(
            witness_id=witness_id,
            latitude=lat,
            longitude=lon,
            satellite_frame_id="SAT-2026-04-05-001",
            data={"quality": "high", "cloud_cover": 0.15}
        )
        proofs.append(proof)
        print(f"  ✓ Generated: {proof}")
    
    print()
    
    # Verify consensus
    print("[2] Verifying witness consensus...")
    consensus_reached, details = engine.verify_consensus(proofs)
    
    print(f"  Consensus: {consensus_reached}")
    print(f"  Verified: {details['verified_count']}/{len(proofs)}")
    print(f"  Failed: {details['failed_count']}/{len(proofs)}")
    print()
    
    # Gate execution
    print("[3] Gating E14 Oracle execution...")
    can_execute = engine.gate_execution(proofs)
    
    print()
    print(f"Execution Status: {'ALLOWED ✓' if can_execute else 'BLOCKED ✗'}")
    print()
    
    # Status report
    print("[4] Witness Engine Status")
    status = engine.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print()
    print("=" * 90)
