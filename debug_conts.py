
import sys
import os
# Add parent dir to path to import modules
sys.path.append(os.getcwd())
from firebase_bd import leer_registro

def debug_data():
    print("--- DEBUGGING DATA STRUCTURE ---")
    
    # 1. Read Contracts
    conts = leer_registro('contrato')
    if not conts:
        print("No contracts found.")
        return

    print(f"Total entries in 'contrato': {len(conts)}")
    
    # 2. Inspect keys of first 5 items
    items = list(conts.values())[:5]
    for i, item in enumerate(items):
        print(f"\nItem {i} Keys: {list(item.keys())}")
        if 'DEPENDENCIA' in item:
            print(f"  DEPENDENCIA: {item['DEPENDENCIA']}")
        else:
            print("  MISSING 'DEPENDENCIA' key")
            
if __name__ == "__main__":
    debug_data()
