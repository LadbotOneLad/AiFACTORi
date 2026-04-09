# NASA SYNC SPEC

Supported datasets:
- MERRA-2
- GEOS-5 / GEOS-FP
- GPM
- VIIRS
- MODIS

Tile ID format:
NASA_TILE_{LAT}_{LON}_{TIME}

Hashing:
- data_hash = SHA256(normalized JSON)
- metadata_hash = SHA256(provider + region + times)
- integrity_hash = SHA256(data_hash + metadata_hash)

Consensus rule:
All 14 engines must match ? K = 1.00

Normalization:
- lock cycle
- wobble constants
- hashing order
- tile size
