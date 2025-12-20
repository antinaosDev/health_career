
from firebase_bd import leer_registro
import json

def debug_rut(rut_target):
    print(f"--- DEBUGGING CONTRACTS FOR RUT: {rut_target} ---")
    data = leer_registro('contrato')
    
    count = 0
    for k, v in data.items():
        # Normalize RUTs for comparison
        r_bd = str(v.get('RUT', '')).strip().upper()
        r_target = str(rut_target).strip().upper()
        
        if r_bd == r_target:
            count += 1
            print(f"\n[MATCH #{count}] ID: {k}")
            print(json.dumps(v, indent=4, ensure_ascii=False))

    if count == 0:
        print("No matches found.")
    else:
        print(f"\nTotal records found: {count}")

if __name__ == "__main__":
    debug_rut("18581575-7")
