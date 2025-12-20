import sys
import os
sys.path.append(os.getcwd())
from firebase_bd import leer_registro

rut_target = '18581575-7'
print(f"--- LISTING TRAININGS FOR {rut_target} ---")
caps = leer_registro('capacitaciones')
count = 0
if caps:
    for cid, cap in caps.items():
        r_cap = str(cap.get('RUT', '')).replace('.', '').strip()
        if r_cap == rut_target:
            count += 1
            print(f"#{count}: [{cap.get('AÑO_PRESENTACION')}] {cap.get('NOMBRE_CAPACITACION')} ({cap.get('ENTIDAD')}) - Context: {cap.get('CONTEXTO_PRESENTACION')}")
else:
    print("No capacitaciones found.")
print(f"--- TOTAL FOUND: {count} ---")
