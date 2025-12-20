import sys
import os
sys.path.append(os.getcwd())
from firebase_bd import leer_registro

print("--- DUPLICATE RUT CHECK ---")
users = leer_registro('usuarios')
normalized_map = {}

for uid, u in users.items():
    raw_rut = u.get('RUT', '')
    clean_rut = str(raw_rut).replace('.', '').strip()
    
    if clean_rut in normalized_map:
        print(f"DUPLICATE FOUND! \n  1. ID={normalized_map[clean_rut]['id']} RUT='{normalized_map[clean_rut]['rut']}' \n  2. ID={uid} RUT='{raw_rut}'")
    else:
        normalized_map[clean_rut] = {'id': uid, 'rut': raw_rut}

print("--- END CHECK ---")
