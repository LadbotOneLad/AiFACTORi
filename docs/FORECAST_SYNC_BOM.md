# BOM NATIONAL FORECAST SYNC SPEC

Tile ID format:
BOM_FORECAST_{REGION}_{FORECAST_TIME}

Hashing:
- data_hash = SHA256(normalized JSON)
- metadata_hash = SHA256(provider + region + times)
- integrity_hash = SHA256(data_hash + metadata_hash)

Consensus:
K < 1.00 ? DEGRADED
K = 1.00 ? VERIFIED

Requirements:
- obey lock cycle
- obey wobble constants
- enforce structural invariants (I1, I2, I3).
