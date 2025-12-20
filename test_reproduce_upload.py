
import pandas as pd
import math

# Mocking the functions from funciones.py relevant to the issue

def limpiar_nans(diccionario):
    cantidad_nans = sum(isinstance(v, float) and math.isnan(v) for v in diccionario.values())
    if cantidad_nans >= 3:
        return None
    return {
        k: None if isinstance(v, float) and math.isnan(v) else v
        for k, v in diccionario.items()
    }

def simulate_carga_masiva(data_rows, headers):
    # Simulate reading excel
    df = pd.DataFrame(data_rows, columns=headers)
    lista_diccionarios = df.to_dict('records')
    
    # Simulate processing
    capacitacion_v = lista_diccionarios # Assume they are detected as training
    
    skipped_count = 0
    inserted_count = 0
    dropped_nan_count = 0
    
    processed_records = []
    
    # Code Logic from funciones.py
    for idv_l in capacitacion_v:
        idv = limpiar_nans(idv_l)
        if not idv:
            dropped_nan_count += 1
            print(f"Dropped by NaN check: {idv_l}")
            continue

        # Extraction Logic used in funciones.py
        nombre = idv.get('NOMBRE_CAPACITACION')
        entidad = idv.get('ENTIDAD')
        
        # If headers are different, these will be None
        
        print(f"Processing: Name='{nombre}', Entity='{entidad}' keys={list(idv.keys())}")
        
        # In actual code, it then checks duplicates and inserts
        # If Name is None, it might still insert a breakage-prone record or fail silently later
        inserted_count += 1
        processed_records.append(idv)
        
    print(f"\nStats:")
    print(f"Total Input: {len(data_rows)}")
    print(f"Inserted: {inserted_count}")
    print(f"Dropped (NaN): {dropped_nan_count}")
    
    return processed_records

# Case 1: Headers as requested in UI
headers_ui = ["RUT", "NOMBRE", "TIPO", "INSTITUCION", "FECHA_INICIO", "FECHA_TERM", "HORAS", "NOTA", "RELEVANTE"]
row_ui = ["1-9", "Python Course", "CURSO", "Udemy", "01/01/2023", "02/01/2023", 20, 7.0, "General"]

# Case 2: Headers expected by code
headers_code = ["RUT", "NOMBRE_CAPACITACION", "ES_POSTGRADO", "ENTIDAD", "AÑO_INICIO", "AÑO_PRESENTACION", "HORAS", "NOTA", "CONTEXTO_PRESS"]
row_code = ["1-9", "Python Course", 0, "Udemy", 2023, 2023, 20, 7.0, "General"]

print("--- TEST 1: UI Headers ---")
simulate_carga_masiva([row_ui], headers_ui)

print("\n--- TEST 2: Code Code Headers ---")
simulate_carga_masiva([row_code], headers_code)
