import json, hashlib, os

# --- LOAD CONFIGS ---
with open('configs/wobble_constants.json') as f:
    WOBBLE = json.load(f)
with open('configs/lock_cycle.json') as f:
    LOCK = json.load(f)
with open('engine_cycle.json') as f:
    ENGINE = json.load(f)

# --- HASHING ONLY (NO TESTS) ---
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

# --- PURE PIPELINE (NO VALIDATION) ---
def INGEST(field):
    return field

def NORMALIZE(field):
    return field

def TILE(field):
    return field

def HASH_STAGE(field):
    return sha256(str(field))

def WITNESS(hash_value):
    return sha256('witness:' + hash_value)

def CONSENSUS(witness_value):
    return witness_value  # no checks, no tests

def LEDGER_WRITE(value):
    with open('logs/ledger.log', 'a') as f:
        f.write(value + '\\n')

# --- PIPELINE ---
def run_engine(field):
    field = INGEST(field)
    field = NORMALIZE(field)
    field = TILE(field)
    h = HASH_STAGE(field)
    w = WITNESS(h)
    c = CONSENSUS(w)
    LEDGER_WRITE(c)
    return c

# --- ENTRYPOINT ---
if __name__ == '__main__':
    sample = {'temp': 22.5, 'humidity': 0.55}
    out = run_engine(sample)
    print('ENGINE OUTPUT:', out)
