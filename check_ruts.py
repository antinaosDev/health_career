import sys
import os
sys.path.append(os.getcwd())
from firebase_bd import leer_registro

print("--- DB RUT INSPECTION ---")
users = leer_registro('usuarios')
count = 0
for id_u, data in users.items():
    rut = data.get('RUT', 'N/A')
    pje = data.get('PTJE_CARR', 'N/A')
    nivel = data.get('NIVEL', 'N/A')
    bienios = data.get('BIENIOS', 'N/A')
    print(f"ID: {id_u} | RUT: '{rut}' | Niv: {nivel} | Pts: {pje} | Bienios: {bienios}")
    count += 1
    if count > 5: break
print("--- END INSPECTION ---")
