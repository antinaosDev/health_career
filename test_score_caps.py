
from funciones import puntaje_nv
from clases import Capacitacion
from indices import *
import json

# MOCK DATA
mock_user_A = {
    'user1': {'RUT': '1-9', 'NOMBRE_FUNC': 'Test User A', 'CATEGORIA': 'A', 'BIENIOS': 0, 'PTJE_ARRASTRE': 0}
}
mock_user_E = {
    'user2': {'RUT': '2-7', 'NOMBRE_FUNC': 'Test User E', 'CATEGORIA': 'E', 'BIENIOS': 0, 'PTJE_ARRASTRE': 0}
}

mock_contracts = {
    'c1': {'RUT': '1-9', 'TIPO_CONTRATO': 'Planta', 'ANTIGUEDAD': 0},
    'c2': {'RUT': '2-7', 'TIPO_CONTRATO': 'Planta', 'ANTIGUEDAD': 0}
}


import funciones

# MOCK UPDATE FUNCTION
def mock_actualizar_registro(collection, data, doc_id):
    print(f"       [MOCK UPDATE] {collection} {doc_id} -> {data}")
    if collection == 'usuarios':
        user_key = doc_id
        target = None
        if user_key in mock_user_A: target = mock_user_A[user_key]
        elif user_key in mock_user_E: target = mock_user_E[user_key]
        
        if target:
            target.update(data)

# PATCH
funciones.actualizar_registro = mock_actualizar_registro
funciones.leer_registro = lambda x: {} # prevent real reads

# Helper to run test
def run_test(rut, cat_name, caps_data, limit_expected):
    print(f"\n--- Testing Category {cat_name} (Limit {limit_expected}) ---")
    
    # Reset mocks just in case (optional, but good for isolation)
    # Re-declare mocks inside or reset them? For now, we rely on sequential updates.
    
    # Construct mock caps
    mock_caps = {}
    idx = 0
    for c in caps_data:
        idx += 1
        mock_caps[f'cap{idx}'] = c
    
    # Determine which user dict to use
    users_db = mock_user_A if cat_name == 'A' else mock_user_E
    
    # Run Function
    # We pass the MOCK DBs explicitly
    puntaje_nv(rut, mock_caps, users_db, mock_contracts)
    
    # Check Result
    res_user = users_db.get('user1' if cat_name == 'A' else 'user2')
    final_score = res_user.get('PTJE_CARR')
    saldo = res_user.get('SALDO_PTJE')
    
    print(f"Final Score in DB: {final_score}")
    print(f"Saldo in DB: {saldo}")
    
    # Assertions
    # Note: PTJE_CARR includes bienios (0 here). 
    assert final_score <= limit_expected, f"Score {final_score} exceeded limit {limit_expected}"
    
    # Calculate expected raw
    raw_score = sum(c.get('PJE_POND', 0) for c in caps_data)
    print(f"Raw Score: {raw_score}")
    expected_saldo = max(0, raw_score - limit_expected)
    print(f"Expected Saldo: {expected_saldo}")
    
    assert abs(saldo - expected_saldo) < 0.1, f"Saldo {saldo} != Expected {expected_saldo}"
    print("Test Passed")

def reset_mocks():
    global mock_user_A, mock_user_E
    mock_user_A['user1']['SALDO_PTJE'] = 0
    mock_user_A['user1']['PTJE_CARR'] = 0
    mock_user_E['user2']['SALDO_PTJE'] = 0
    mock_user_E['user2']['PTJE_CARR'] = 0

# TEST CASES

# 1. Category A - Under Limit
reset_mocks()
# Limit 4500. Data: 4000
caps_1 = [
    {'RUT': '1-9', 'CONTEXTO_PRESS': 'Ingreso a Planta', 'PJE_POND': 4000, 'AÑO_PRESENTACION': 2024}
]
# Expect Saldo 0
run_test('1-9', 'A', caps_1, 4500)

# 2. Category A - Over Limit (Single Source)
reset_mocks()
# Limit 4500. Data: 5000 (Planta)
caps_2 = [
    {'RUT': '1-9', 'CONTEXTO_PRESS': 'Ingreso a Planta', 'PJE_POND': 5000, 'AÑO_PRESENTACION': 2024}
]
# Raw 5000 - Limit 4500 = 500 Saldo
run_test('1-9', 'A', caps_2, 4500)

# 3. Category E - Mixed Sources Over Limit
reset_mocks()
# Limit 3500. Planta: 3000. Annual: 1000. 
# Annual Limit Cat E = 117.
# Annual Calc: 1000 - 117 = 883 Saldo (Annual Surplus). Effective Annual = 117.
# Global Calc: Planta(3000) + AnnualEffective(117) = 3117.
# Global Cap (3500). 3117 < 3500. No Global Excess.
# Total Score = 3117. Total Saldo = 883.
# NOTE: Test expectation logic in run_test calculates "Raw - Limit" which is 4000 - 3500 = 500.
# We must override expectation for this complex case or adjust logic.
# Let's verify manually.

print(f"\n--- Testing Category E (Complex) ---")
mock_caps_3 = {
    'c1': {'RUT': '2-7', 'CONTEXTO_PRESS': 'Ingreso a Planta', 'PJE_POND': 3000, 'AÑO_PRESENTACION': 2024},
    'c2': {'RUT': '2-7', 'CONTEXTO_PRESS': 'Cambio de Nivel', 'PJE_POND': 1000, 'AÑO_PRESENTACION': 2024}
}
puntaje_nv('2-7', mock_caps_3, mock_user_E, mock_contracts)
res_e = mock_user_E['user2']
print(f"Final Score: {res_e['PTJE_CARR']}")
print(f"Saldo: {res_e['SALDO_PTJE']}")

# Expectation: Score 3234 (3000 Planta + 117 2024 + 117 2025 paid by saldo), Saldo 766.
# 2024 Surplus = 883. 2025 Deficit = 117. Saldo = 883 - 117 = 766.
assert res_e['PTJE_CARR'] == 3234
assert res_e['SALDO_PTJE'] == 766
print("Test Passed")

# 4. Category A - With Arrastre
# Limit 4500. 
# Arrastre: 4000. 
# Planta: 1000.
# Total Raw: 5000.
# Expect Score 4500. Saldo 500.
reset_mocks()
print(f"\n--- Testing Category A (With Arrastre) ---")
mock_user_A['user1']['PTJE_ARRASTRE'] = 4000
caps_4_list = [
    {'RUT': '1-9', 'CONTEXTO_PRESS': 'Ingreso a Planta', 'PJE_POND': 1000, 'AÑO_PRESENTACION': 2024}
]
mock_caps_4 = {f'cap{i}': c for i, c in enumerate(caps_4_list)}
puntaje_nv('1-9', mock_caps_4, mock_user_A, mock_contracts)
res_a4 = mock_user_A['user1']
print(f"Final Score: {res_a4['PTJE_CARR']}")
print(f"Saldo: {res_a4['SALDO_PTJE']}")
assert res_a4['PTJE_CARR'] == 4500
assert res_a4['SALDO_PTJE'] == 500
print("Test Passed")
