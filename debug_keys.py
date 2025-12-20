import sys
import os
sys.path.append(os.getcwd())
from firebase_bd import leer_registro

print("--- CAPACITACIONES KEYS CHECK ---")
caps = leer_registro('capacitaciones')
if caps:
    first_key = list(caps.keys())[0]
    data = caps[first_key]
    print(f"Record Keys: {list(data.keys())}")
    print(f"Record Data: {data}")
else:
    print("No capacitaciones found.")
print("--- END CHECK ---")
