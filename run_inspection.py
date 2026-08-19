#!/usr/bin/env python3
"""
Run the inspection script and save output to a file for review.
"""
import subprocess
import sys

# Run the inspection script and capture output
result = subprocess.run([sys.executable, "inspect_samples.py"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Also save to file
with open("inspection_output.txt", "w") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n\nSTDERR:\n")
        f.write(result.stderr)

print("\n\nOutput saved to inspection_output.txt")
