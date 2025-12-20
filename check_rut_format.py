import sys
import os
sys.path.append(os.getcwd())
from firebase_bd import leer_registro

print("--- RUT FORMAT CHECK ---")
users = leer_registro('usuarios')
found = False
for uid, u in users.items():
    rut = u.get('RUT', '')
    if '18581575' in rut.replace('.', ''):
        print(f"FOUND MATCH: ID={uid} | RUT='{rut}'")
        found = True

if not found:
    print("NO MATCH FOUND FOR 18581575")
print("--- END CHECK ---")
