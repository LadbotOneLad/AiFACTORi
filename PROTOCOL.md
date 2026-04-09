# Engine Synchronization Protocol (ESP)

## 1. Purpose
The Engine Synchronization Protocol defines how external networks, nodes, or systems
synchronize with the Engine’s cycle, witness identity, batch structure, and verification logic.

This document is the canonical reference for:
- Cycle governance
- Witness identity
- Batch construction
- Merkle root generation
- Signature verification
- State validation
- Network synchronization rules

The Engine is the reference implementation. All other systems MUST conform to this specification.

---

## 2. Cycle Governance

### 2.1 Cycle File Format
All nodes MUST load a cycle definition file in the following format:

{ "lock_id": "2026-CYCLE-01", "lock_inception": "2026-04-07T00:00:00Z", "lock_expiry": "2026-07-07T00:00:00Z", "witness_key": "SAT_A_SK" }


### 2.2 Cycle Rules
- A cycle defines the valid operational window.
- Nodes MUST reject any batch produced outside the cycle window.
- Nodes MUST verify that the witness key matches the active cycle.

---

## 3. Witness Identity

### 3.1 Witness Key
The witness key defines the identity of the engine for the current cycle.

### 3.2 Requirements
- All signatures MUST be produced using the active witness key.
- Nodes MUST reject signatures from inactive or expired keys.

---

## 4. Batch Construction

### 4.1 Batch Format
A batch consists of:
- A list of tiles (measurements)
- A Merkle tree
- A Merkle root
- A witness signature
- A cycle reference

### 4.2 Merkle Rules
- Tiles MUST be hashed using SHA-256.
- Merkle trees MUST be constructed in sorted order.
- The Merkle root MUST be signed by the witness key.

---

## 5. Verification Logic

### 5.1 Verification Steps
Nodes MUST perform the following checks:

1. Validate cycle window  
2. Validate witness key  
3. Validate Merkle root  
4. Validate signature  
5. Validate batch structure  

### 5.2 Acceptance Criteria
A batch is valid if and only if:
- It is inside the cycle window  
- It uses the correct witness key  
- The Merkle root matches the tile set  
- The signature is valid  
- The batch structure conforms to this spec  

---

## 6. Network Synchronization

### 6.1 Sync Requirements
Any network syncing to the Engine MUST:

- Load the same cycle file  
- Use the same time source (UTC)  
- Implement the same verification logic  
- Accept the Engine as the reference implementation  

### 6.2 Sync Flow
1. Pull cycle file  
2. Pull batch  
3. Verify batch  
4. Accept or reject  
5. Update local state  

---

## 7. Reference Implementation
The Engine repository located at:

`C:\Users\Ai\Desktop\weather`

is the canonical implementation of this protocol.
All other implementations MUST match its behavior.
