# ENGINE LAYER — OPERATIONAL PIPELINE

Stages:
- INGEST        ? enforce I1 (energy / mass sanity)
- NORMALIZE     ? enforce I1 + I2 (energy + smoothness)
- TILE          ? enforce I2 (spatial regularity)
- HASH          ? structural integrity
- WITNESS       ? cryptographic integrity
- CONSENSUS     ? enforce I3 (coherence / K-value)
- LEDGER        ? store invariant state

VALID(t) holds only when all invariants I1, I2, I3 are within bounds.
