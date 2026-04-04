"""
Quick tuning sweep: Test DECAY_FACTOR values to find breathing pattern.
"""

import subprocess
import sys

decay_values = [0.80, 0.85, 0.90, 0.92, 0.95]

print("\n" + "="*110)
print("E14 DECAY FACTOR TUNING SWEEP")
print("="*110)
print()

for decay in decay_values:
    # Read test file
    with open("test_e14_offset_decay.py", "r") as f:
        content = f.read()
    
    # Replace DECAY_FACTOR
    new_content = content.replace(
        'DECAY_FACTOR = 0.88',
        f'DECAY_FACTOR = {decay}'
    )
    
    # Write temp file
    with open("_temp_test.py", "w") as f:
        f.write(new_content)
    
    print(f"Testing DECAY_FACTOR = {decay}...")
    sys.stdout.flush()
    
    # Run test (suppress most output)
    result = subprocess.run([sys.executable, "_temp_test.py"], 
                          capture_output=True, text=True, timeout=180)
    
    # Extract key results
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if 'Convergence ratio:' in line:
            print(f"  {line.strip()}")
        elif 'Contiguous windows:' in line:
            print(f"  {line.strip()}")
        elif 'Average K:' in line:
            print(f"  {line.strip()}")
    
    print()

print("="*110)
print("Summary: Higher DECAY_FACTOR = slower offset shrink = fewer, longer windows")
print("="*110)
