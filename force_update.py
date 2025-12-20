import sys
import os
sys.path.append(os.getcwd())

from funciones import actualizacion_horaria, puntaje_nv, leer_registro

target_rut = '18581575-7' # Alain (Clean)

print(f"--- FORCING UPDATE FOR {target_rut} ---")

# 1. Update Ages/Antiquity first
print("1. Running Actualizacion Horaria...")
users = leer_registro('usuarios')
conts = leer_registro('contrato')
actualizacion_horaria('ADMIN', users, conts)

# 2. Run Score Calculation (this updates Bienios, Level, Score)
print("2. Running Puntaje NV...")
puntaje_nv(target_rut)

print("--- UPDATE COMPLETE ---")
