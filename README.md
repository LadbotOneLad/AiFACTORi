# E14 ORACLE — WEATHER ENGINE

This folder contains the E14 Oracle weather architecture:
- docs/    ? specs, invariants, sync contracts
- configs/ ? lock cycle, wobble constants, engine cycle
- math/    ? symbolic invariants
- logs/    ? runtime traces

Engine flow:
INGEST ? NORMALIZE ? TILE ? HASH ? WITNESS ? CONSENSUS ? LEDGER
