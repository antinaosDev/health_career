import sys
import os
sys.path.append(os.getcwd())

from funciones import actualizacion_horaria, puntaje_nv, calculo_años
from firebase_bd import leer_registro

print("--- START DEBUG ---")

# 1. Test calculo_años directly with potential dirty data
dirty_date = " 01/01/2020 "
print(f"Testing dirty date '{dirty_date}': params: strip? No")
res = calculo_años(dirty_date)
print(f"Result for '{dirty_date}': {res}")

clean_date = "01/01/2020"
print(f"Testing clean date '{clean_date}':")
res2 = calculo_años(clean_date)
print(f"Result for '{clean_date}': {res2}")

# 2. Run Actualizacion for a real user to see logs
print("\n--- Running Actualizacion Horaria (Sample) ---")
try:
    # Fetch just one relevant user if possible, or run global but limit output
    usuarios = leer_registro('usuarios')
    contratos = leer_registro('contrato')
    
    # Run for ADMIN to trigger updates
    actualizacion_horaria('ADMIN', usuarios, contratos)
    
except Exception as e:
    print(f"CRITICAL ERROR in Update: {e}")

print("--- END DEBUG ---")
