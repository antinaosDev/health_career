from firebase_bd import *
from datetime import datetime
from indices import *
import pandas as pd
import numpy as np
import math
import streamlit as st
from clases import *

def porcentaje_postgrado(horas_post, rut_ev):
    datos_usr = leer_registro('usuarios')
    for id_u, usr in datos_usr.items():
        if usr.get('RUT') == rut_ev:
            for k, v in asignaciones_posgrados.items():
                if k[0] <= horas_post <= k[1]:
                    actualizar_registro('usuarios', {'ASIG_POSTG': f'{v}%'}, id_u)
                    return f'{v}%'
    return '0%'


def es_contrato_activo(contrato):
    """
    Determina si un contrato está vigente basado en FECHA_TERMINO.
    PLANTA o Indefinido -> Activo.
    Fecha Terminada -> Inactivo.
    """
    if not contrato: return False
    
    tipo = str(contrato.get('TIPO_CONTRATO', '')).strip().upper()
    if tipo == 'PLANTA': return True
    
    fecha_ter = contrato.get('FECHA_TERMINO')
    if not fecha_ter or str(fecha_ter).strip() == '':
        return True # Indefinido assumption
        
    try:
        ft = datetime.strptime(str(fecha_ter).strip(), '%d/%m/%Y')
        now = datetime.now()
        # Compare dates (active if end date is >= today)
        return ft.date() >= now.date()
    except:
        return True # Fail open if bad format? Or safe close?
        # Usually assume active if date format error, but let's be strict if needed.
        # For now, safe assumption: active.
        return True

def dias_restantes_contrato(contrato):
    """
    Retorna int con días restantes.
    None si es indefinido.
    Negativo si venció.
    """
    if not contrato: return None
    fecha_ter = contrato.get('FECHA_TERMINO')
    if not fecha_ter or str(fecha_ter).strip() == '':
        return None
        
    try:
        ft = datetime.strptime(str(fecha_ter).strip(), '%d/%m/%Y')
        now = datetime.now()
        delta = (ft.date() - now.date()).days
        return delta
    except:
        return None

def calculo_años(fecha_inicio, fecha_termino=None):
    from datetime import datetime

    if not isinstance(fecha_inicio, str) or not fecha_inicio.strip():
        return 0

    try:
        f_ini = fecha_inicio.strip()
        # Try multiple formats
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
             try:
                 inicio = datetime.strptime(f_ini, fmt)
                 break
             except ValueError:
                 continue
        else:
             # Raise error if loop completes without break
             raise ValueError(f"Formato desconocido: {f_ini}")

        fin_str = fecha_termino.strip() if fecha_termino and isinstance(fecha_termino, str) else None
        
        fin = datetime.now()
        if fin_str:
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
                 try:
                     fin = datetime.strptime(fin_str, fmt)
                     break
                 except ValueError:
                     continue
            # If fin_str exists but fails all formats, it might default to now or raise. 
            # Original code defaulted to now() if fin_str was falsy, but not if it was malformed.
            # We'll stick to 'now' if malformed or just let the exception flow? 
            # The original 'fin' logic was: fin = datetime.strptime(...) if fin_str else datetime.now()
            # If fin_str was provided but invalid, it crashed. Now we try to handle it.
        
        # Logic Restore: (fin - inicio).days // 365
        return (fin - inicio).days // 365
    except Exception as e:
        msg = f"[ERROR] calculo_años: {e} | inicio: {fecha_inicio} - fin: {fecha_termino}"
        print(msg)
        # st.toast(msg) # Optional: uncomment for UI feedback
        return 0

#Calculo de puntajes 
#Calculo de puntajes 
#Calculo de puntajes 
def puntaje_nv(rut_ev_input, data_cap=None, data_u=None, data_c=None):
    # Normalize input
    rut_ev = str(rut_ev_input).replace('.', '').strip()
    
    # 1. Fetch User & Contract Data FIRST to determine Category/Limit
    datos_u_local = data_u if data_u is not None else leer_registro('usuarios')
    datos_ant = data_c if data_c is not None else leer_registro('contrato')
    
    # Identify user category and Determine Annual Limit
    limit_anual = 150 # Default/Previous Value
    categoria_user = ''
    
    # Locate user in DB
    user_record = None
    user_id = None
    if datos_u_local:
        for idu, usr in datos_u_local.items():
            if str(usr.get('RUT', '')).replace('.', '').strip() == rut_ev:
                user_record = usr
                user_id = idu
                categoria_user = usr.get('CATEGORIA', '')
                break
    
    # Set Limit based on Category (A/B=150, C-F=117)
    if categoria_user in ['A', 'B']:
        limit_anual = 150
    elif categoria_user in ['C', 'D', 'E', 'F']:
        limit_anual = 117
    else:
        limit_anual = 150 # Fallback default
    
    # 2. Process Capacitaciones (Trainings)
    datos = data_cap if data_cap is not None else leer_registro('capacitaciones')
    dict_puntaje = []
    puntaje_planta = []
    
    if datos:
        for idx, cap in datos.items():
            r_cap = str(cap.get('RUT', '')).replace('.', '').strip()
            contexto = cap.get('CONTEXTO_PRESENTACION') or cap.get('CONTEXTO_PRESS')
            
            if r_cap == rut_ev:
                if contexto == 'Ingreso a Planta':
                    pje = cap.get('PJE_POND') or 0
                    puntaje_planta.append(pje)
                else:
                    # Generic Annual Points
                    año = cap.get('AÑO_PRESENTACION')
                    pje = cap.get('PJE_POND') or 0
                    if año: # Valid year
                         dict_puntaje.append((año, pje))

    # 3. Calculate Antiquity (Bienios) - UPDATED LOGIC (Consolidated with Seniority Helper)
    user_contracts_list = []
    tiene_contrato_planta = False
    
    # Valid Dependencies for Bienios/Career Check
    VALID_DEPS = ['CESFAM CHOLCHOL', 'PSR HUENTELAR', 'PSR MALALCHE', 'PSR HUAMAQUI', 'SALUD APS']
    
    if datos_ant:
        for ant in datos_ant.values():
            r_c = str(ant.get('RUT', '')).replace('.', '').strip()
            if r_c == rut_ev:
                user_contracts_list.append(ant)
                tipo = str(ant.get('TIPO_CONTRATO', '')).strip().upper()
                if 'PLANTA' in tipo:
                    tiene_contrato_planta = True

    # Filter contracts for Bienios Calculation
    qualifying_contracts = []
    for c in user_contracts_list:
        dep = str(c.get('DEPENDENCIA', '')).strip().upper()
        # Check if ANY valid dependency substring is in the dependency field
        if any(vd in dep for vd in VALID_DEPS):
            qualifying_contracts.append(c)

    # Use the robust Merge Intervals Helper on FILTERED contracts
    antiguedad_years = calculate_real_seniority(qualifying_contracts)
    bienio = antiguedad_years // 2
    corr_carr = 'SI' if tiene_contrato_planta else 'NO'

    # Update User Record with Bienios
    if user_id:
        actualizar_registro('usuarios', {
            'BIENIOS': bienio,
            'CORR_CARR': corr_carr
        }, user_id)
        if data_u:
             if 'BIENIOS' in datos_u_local[user_id]: datos_u_local[user_id]['BIENIOS'] = bienio


    # 4. Sum "Ingreso a Planta"
    suma_planta = sum(puntaje_planta)

    # 5. Process Annual Points (Group by Year)
    saldos_por_año = {}
    if dict_puntaje:
        years = [x[0] for x in dict_puntaje]
        min_year = min(years)
        max_year = max(years)
        # Ensure we cover up to current year (2025) if logic requires it, or at least max of data
        # User specifically mentioned 2025. Let's use max(max_year, datetime.now().year)
        # But for 'simulador' context usually it's static.
        # Let's assume we fill from min_year to max(current_year, max_year)
        target_max = max(max_year, datetime.now().year)
        
        # Populate dict
        for año, pje in dict_puntaje:
            saldos_por_año[año] = saldos_por_año.get(año, 0) + pje
            
        # Fill gaps with 0
        for y in range(min_year, target_max + 1):
            if y not in saldos_por_año:
                saldos_por_año[y] = 0
    else:
        # No trainings?
        saldos_por_año = {} 

    # Sort years
    saldos_agrup = sorted(saldos_por_año.items(), key=lambda x: x[0])

    # 6. Apply Balance Logic & Capture Trace
    saldo_acumulado = 0
    lista_final = []
    trace_detalle = [] # NEW: Rich trace for UI
    
    for año, total_año in saldos_agrup:
        dif = total_año - limit_anual
        saldo_inicial = saldo_acumulado
        
        saldo_usado = 0
        saldo_generado = 0
        dificit_final = 0
        
        if dif >= 0:
            # Surplus
            saldo_generado = dif
            saldo_acumulado += dif
            # Year Covered
            lista_final.append((año, 0))
            dificit_final = 0
        else:
            # Deficit
            needed = abs(dif)
            if saldo_acumulado >= needed:
                # Pay full
                saldo_usado = needed
                saldo_acumulado -= needed
                lista_final.append((año, 0))
                dificit_final = 0
            else:
                # Pay partial
                saldo_usado = saldo_acumulado
                remaining_deficit = needed - saldo_acumulado
                saldo_acumulado = 0
                lista_final.append((año, -remaining_deficit))
                dificit_final = -remaining_deficit
        
        # Record Trace
        trace_detalle.append({
            'AÑO': año,
            'PUNTOS_REALES': total_año,
            'LIMITE': limit_anual,
            'DIFERENCIA': dificit_final, # 0 means covered
            'SALDO_INICIAL': saldo_inicial,
            'SALDO_USADO': saldo_usado,
            'SALDO_GENERADO': saldo_generado,
            'SALDO_ACUMULADO': saldo_acumulado
        })

    # 7. Final Score Calculation with GLOBAL CAP
    # Global Cap Definition
    limit_capacitacion = 4500 if categoria_user in ['A', 'B'] else 3500

    # Components subject to Cap:
    # 1. Ingreso a Planta (suma_planta)
    # 2. Arrastre (ptje_arrastre) - Assuming Arrastre is historical training score
    # 3. Annual Effective (Suma de valid_points from trace)
    
    # Calculate Annual Effective first
    suma_anual_efectiva = 0
    for row in trace_detalle:
        valid_points = row['LIMITE'] + row['DIFERENCIA'] # This is the amount "paid" by the year + deficit covered
        suma_anual_efectiva += valid_points

    # Retrieve Arrastre
    ptje_arrastre = 0
    if user_record:
        try:
            val_a = user_record.get('PTJE_ARRASTRE', 0)
            ptje_arrastre = float(str(val_a).replace(',', '.')) if val_a else 0
        except:
            ptje_arrastre = 0

    # Total Training Raw
    total_training_raw = suma_planta + suma_anual_efectiva + ptje_arrastre
    
    # Apply Cap
    total_training_capped = min(total_training_raw, limit_capacitacion)
    
    # Calculate Excess to add to Saldo
    excess_training = total_training_raw - total_training_capped
    
    # Update Saldo Acumulado with the excess from the Global Cap
    saldo_acumulado += excess_training
    
    # Final Sum: Capped Training + Bienios
    bienios_val = bienio * 534
    sum_f = total_training_capped + bienios_val

    # 8. Update DB with Final Scores and Salaries
    if user_id and categoria_user:
        cat = categoria_user
        
        # Calculate Level (Nivel)
        nivel_final = 0
        for id2, nv in indices_niveles.items():
            if cat in id2:
                for rng, val in nv.items():
                    if rng[0] <= sum_f <= rng[1]:
                        nivel_final = val
                        break
        
        # Calculate Salary
        sueldo_final = 0
        if nivel_final > 0:
            for nv_ind, cat_s in sueldos_reajustados_2025.items():
                if nv_ind == nivel_final:
                    sueldo_final = cat_s.get(cat, 0)
                    break
        
        # Prepare Detailed Calculation JSON
        import json
        detalle_dump = json.dumps({
            'anios': trace_detalle, # RICH LIST
            'base_planta': suma_planta,
            'valor_bienios': bienios_val,
            'arrastre': ptje_arrastre,
            'limite_anual': limit_anual
        })

        # Update Cached & DB User
        update_data = {
            'PTJE_CARR': round(sum_f, 2),
            'NIVEL': nivel_final,
            'SALDO_PTJE': round(saldo_acumulado, 2),
            'SUELDO_BASE': f"{sueldo_final:,.0f}",
            'DETALLE_CALCULO': detalle_dump
        }
        
        # Check Contract Hours for Proportional Salary
        total_sueldo_real = 0
        has_contracts = False
        
        if datos_ant:
            for idc, elem in datos_ant.items():
                r_elem = str(elem.get('RUT', '')).replace('.', '').strip()
                if r_elem == rut_ev:
                    has_contracts = True
                    horas = elem.get('HORAS', 0)
                    try: 
                        horas = int(horas)
                    except: 
                        horas = 0
                        
                    if horas == 44:
                        s_cont = sueldo_final
                    else:
                        s_cont = (horas * sueldo_final) / 44
                    
                    if not es_contrato_activo(elem):
                         s_cont = 0 # Expired contract contributes 0
                    
                    total_sueldo_real += s_cont
                    actualizar_registro('contrato', {'SUELDO_BASE': f"{s_cont:,.0f}"}, idc)
        
        if has_contracts:
            update_data['SUELDO_BASE'] = f"{total_sueldo_real:,.0f}"
            
        actualizar_registro('usuarios', update_data, user_id)
    
pass
# ... (carga_masiva implementation continues until end of batch processing)

def carga_masiva_finalize(affected_ruts, roles_map):
    # This is pseudo-code representation of the batch block logic, injected into the main function below
    pass




def carga_masiva(ruta_archivo, rut_ev='', categoria=''):
    print(f"📥 RUT evaluador recibido: '{rut_ev}'")

    import pandas as pd
    import numpy as np
    import math
    from datetime import datetime

    p_bar = st.progress(0, text="Iniciando carga masiva...")
    
    xls = pd.ExcelFile(ruta_archivo)
    hojas = xls.sheet_names
    p_bar.progress(10, text=f"Hojas detectadas: {len(hojas)}")
    print(f"📄 Hojas detectadas: {hojas}")
    
    inserted_count = 0
    skipped_count = 0
    print(f"📄 Hojas detectadas: {hojas}")

    def headers(nom_hoja):
        df = xls.parse(nom_hoja)
        return df.columns

    def info_hojas(nom_hoja):
        df = xls.parse(nom_hoja)
        return df

    usuarios = leer_registro('usuarios')
    contratos = leer_registro('contrato')
    capacitaciones = leer_registro('capacitaciones')

    encabezados_lista = []
    data_hojas = []
    for hoja in hojas:
        header = headers(hoja)
        # Normalize headers to ensure matching works
        header = [str(h).strip().upper() for h in header]
        data = info_hojas(hoja).values.tolist()
        encabezados_lista.append(header)
        data_hojas.append(data)

    lista_diccionarios = []

    for idx in range(len(hojas)):
        encabezados_index = encabezados_lista[idx]
        datos_index = data_hojas[idx]

        for fila in datos_index:
            if len(fila) == len(encabezados_index):
                dict_fila = dict(zip(encabezados_index, fila))
                lista_diccionarios.append(dict_fila)
            else:
                # print(f"⚠️ Fila ignorada por longitud en hoja '{hojas[idx]}': {fila}")
                pass

    print(f"📊 Total registros leídos: {len(lista_diccionarios)}")
    
    if rut_ev:
        # Normalize comparison for filtering
        rut_clean = str(rut_ev).replace('.', '').strip()
        lista_diccionarios_v = [
            elem for elem in lista_diccionarios 
            if rut_clean in [str(v).replace('.', '').strip() for v in elem.values()]
        ]
    else:
        lista_diccionarios_v = lista_diccionarios

    print(f"✅ Registros filtrados por RUT ({rut_ev}): {len(lista_diccionarios_v)}")

    for elem in lista_diccionarios_v:
        for k, v in elem.items():
            if isinstance(v, (pd.Timestamp, datetime, np.datetime64)):
                dt_val = pd.to_datetime(v)
                if pd.notna(dt_val):
                    elem[k] = dt_val.strftime('%d/%m/%Y')
                else:
                    elem[k] = ""

    # Dynamic Header Detection Logic
    
    import re

    def clean_text(val):
        """Normalize text: Upper, Remove double spaces, Strip."""
        if val is None: return ""
        s = str(val).upper()
        s = re.sub(r'\s+', ' ', s) # Collapse multiple spaces
        return s.strip()

    idx_user = 0
    idx_cont = 1
    idx_cap = 2
    
    # Try to identify sheets by content
    for i, headers_list in enumerate(encabezados_lista):
        h_set = set(headers_list)
        if 'TIPO_CONTRATO' in h_set or 'CALIDAD_JURIDICA' in h_set:
            idx_cont = i
        elif 'NOMBRE_CAPACITACION' in h_set or 'NOMBRE CURSO' in h_set or 'ENTIDAD' in h_set:
            idx_cap = i
        elif 'CATEGORIA' in h_set or 'SEXO' in h_set or 'TITULO' in h_set:
            idx_user = i
            
    # Safeguard against out-of-bounds if file has fewer sheets
    num_sheets = len(encabezados_lista)
    encabezados_user = encabezados_lista[idx_user] if idx_user < num_sheets else []
    encabezados_contrato = encabezados_lista[idx_cont] if idx_cont < num_sheets else []
    encabezados_capacitacion = encabezados_lista[idx_cap] if idx_cap < num_sheets else []
    
    print(f"🕵️ Detectado: Users=Sheet[{idx_user}], Contracts=Sheet[{idx_cont}], Caps=Sheet[{idx_cap}]")
    print(f"📝 Headers Caps: {encabezados_capacitacion}")

    usuario_v = []
    contrato_v = []
    capacitacion_v = []

    for dic in lista_diccionarios_v:
        claves = set(dic.keys())
        
        # Calculate intersection with detected headers
        match_user = len(claves & set(encabezados_user)) if encabezados_user else 0
        match_contrato = len(claves & set(encabezados_contrato)) if encabezados_contrato else 0
        match_capacitacion = len(claves & set(encabezados_capacitacion)) if encabezados_capacitacion else 0

        # Relaxed classification logic
        if match_user > 0 and match_user >= match_contrato and match_user >= match_capacitacion:
             usuario_v.append(dic)
        elif match_contrato > 0 and match_contrato >= match_user and match_contrato >= match_capacitacion:
             contrato_v.append(dic)
        elif match_capacitacion > 0:
             capacitacion_v.append(dic)
        else:
             pass
    
    print(f"🔢 Clasificación: Users={len(usuario_v)}, Contratos={len(contrato_v)}, Caps={len(capacitacion_v)}")

    def eliminar_duplicados(lista_diccionarios):
        lista_sin_duplicados = list({tuple(sorted(d.items())) for d in lista_diccionarios})
        return [dict(tupla) for tupla in lista_sin_duplicados]

    def limpiar_nans(diccionario):
        # Relaxed Filter: Allow rows with more NaNs (e.g. only essential fields present)
        # Previous limit was >=3, which is too strict for sparse Excel rows.
        cantidad_nans = sum(isinstance(v, float) and math.isnan(v) for v in diccionario.values())
        if cantidad_nans >= 8: # Slightly relaxed further
            return None
        return {
            k: None if isinstance(v, float) and math.isnan(v) else v
            for k, v in diccionario.items()
        }

    usuario_v = eliminar_duplicados(usuario_v)
    contrato_v = eliminar_duplicados(contrato_v)
    capacitacion_v = eliminar_duplicados(capacitacion_v)

    # --- KEY-UPDATE LOGIC IMPLEMENTATION (USER REQUEST) ---
    affected_ruts = set()

    # 1. USERS
    if isinstance(usuarios, dict):
        ruts_existentes = {str(usr.get('RUT', '')).replace('.', '').strip(): (idu, usr) for idu, usr in usuarios.items()}
        
        for i in usuario_v:
            limpio = limpiar_nans(i)
            if not limpio: continue
            
            rut_excel = str(limpio.get('RUT', '')).replace('.', '').strip()
            affected_ruts.add(rut_excel)
            
            if rut_excel in ruts_existentes:
                idu, usr_db = ruts_existentes[rut_excel]
                is_different = False
                for k, v in limpio.items():
                    if k == 'RUT': continue
                    val_excel = clean_text(v)
                    val_db = usr_db.get(k)
                    val_db_norm = clean_text(val_db)
                    
                    if val_excel != val_db_norm:
                        is_different = True
                        break
                
                if is_different:
                    actualizar_registro('usuarios', limpio, idu)
            else:
                ingresar_registro_bd('usuarios', limpio)
    else:
        for i in usuario_v:
            limpio = limpiar_nans(i)
            if limpio: 
                r = str(limpio.get('RUT', '')).replace('.', '').strip()
                affected_ruts.add(r)
                ingresar_registro_bd('usuarios', limpio)

    # 2. CONTRACTS (CONTRATO)
    if isinstance(contratos, dict):
        contracts_map = {}
        for idc, cont in contratos.items():
            key = (
                clean_text(cont.get('RUT', '')).replace('.', ''),
                clean_text(cont.get('TIPO_CONTRATO', '')),
                clean_text(cont.get('CARGO', '')),
                clean_text(cont.get('DEPENDENCIA', '')),
                clean_text(cont.get('FECHA_INICIO', '')),
                clean_text(cont.get('FECHA_TERMINO', '')),
                clean_text(cont.get('HORAS', '')),
                clean_text(cont.get('NOMBRE_INSTITUCION', '')),
                clean_text(cont.get('REEMPLAZO', '')),
                clean_text(cont.get('TIPO_INSTITUCION', ''))
            )
            contracts_map[key] = (idc, cont)

        for i in contrato_v:
            limpio = limpiar_nans(i)
            if not limpio: continue
            
            rut_excel = clean_text(limpio.get('RUT', '')).replace('.', '')
            affected_ruts.add(rut_excel)
            
            tipo = clean_text(limpio.get('TIPO_CONTRATO', ''))
            cargo = clean_text(limpio.get('CARGO', ''))
            dependencia = clean_text(limpio.get('DEPENDENCIA', ''))
            
            # --- VALIDATION START ---
            horas_nuevas = limpio.get('HORAS', 0)
            # Strict Key Construction
            key = (
                rut_excel,
                tipo,
                cargo,
                dependencia,
                clean_text(limpio.get('FECHA_INICIO', '')),
                clean_text(limpio.get('FECHA_TERMINO', '')),
                clean_text(limpio.get('HORAS', '')),
                clean_text(limpio.get('NOMBRE_INSTITUCION', '')),
                clean_text(limpio.get('REEMPLAZO', '')),
                clean_text(limpio.get('TIPO_INSTITUCION', ''))
            )
            id_ignorar = None
            if key in contracts_map:
                id_ignorar, _ = contracts_map[key]
            
            # Validate against current DB state (cached in 'contratos')
            es_valido, total_con_nuevo = validar_tope_horas(rut_excel, horas_nuevas, tipo, id_ignorar, contratos)
            
            if not es_valido:
                print(f"❌ Error (RUT {rut_excel}): Supera tope 44 hrs (Planta + Plazo Fijo). Intento: {total_con_nuevo} hrs. Registro Omitido.")
                continue
            # --- VALIDATION END ---

            if key in contracts_map:
                idc, cont_db = contracts_map[key]
                # CHECK DIFF BEFORE UPDATE
                is_different = False
                for k, v in limpio.items():
                    val_excel = str(v).strip().upper() if isinstance(v, str) else str(v)
                    val_db = cont_db.get(k)
                    val_db_norm = str(val_db).strip().upper() if isinstance(val_db, str) else str(val_db)
                    
                    if val_excel != val_db_norm:
                        is_different = True
                        break
                
                if is_different:
                    actualizar_registro('contrato', limpio, idc)
                    # Update Memory Cache for next loop iteration
                    if idc in contratos:
                        contratos[idc].update(limpio)
            else:
                new_id = ingresar_registro_bd('contrato', limpio)
                # Update Memory Cache for next loop iteration
                # We use a temp key if ID is returned or not, just to be safe for validation
                temp_key = new_id if new_id else f"TEMP_{rut_excel}_{len(contratos)}"
                contratos[temp_key] = limpio
                # Also update map to prevent duplicate inserts if duplicate rows exist
                contracts_map[key] = (temp_key, limpio)

    else:
        # Initial Case (Empty DB)
        contratos = {} # Init cache
        for i in contrato_v:
            limpio = limpiar_nans(i)
            if limpio: 
                r = str(limpio.get('RUT', '')).replace('.', '').strip()
                affected_ruts.add(r)
                
                # Validate
                tipo = str(limpio.get('TIPO_CONTRATO', '')).strip().upper()
                horas_nuevas = limpio.get('HORAS', 0)
                es_valido, total_con_nuevo = validar_tope_horas(r, horas_nuevas, tipo, None, contratos)
                
                if not es_valido:
                     print(f"❌ Error (RUT {r}): Supera tope 44 hrs. Intento: {total_con_nuevo} hrs. Registro Omitido.")
                     continue

                id_new = ingresar_registro_bd('contrato', limpio)
                # Update local cache
                contratos[f"TEMP_{r}_{len(contratos)}"] = limpio


    # 3. CAPACITACIONES
    # Pre-fetch Categories for efficiency
    usuarios_cache = leer_registro('usuarios')
    usuarios_por_rut = {}
    if usuarios_cache:
         usuarios_por_rut = {str(usr.get('RUT', '')).replace('.', '').strip(): usr.get('CATEGORIA') for usr in usuarios_cache.values() if usr.get('RUT')}

    if isinstance(capacitaciones, dict):
        caps_map = {}
        for idc, cap in capacitaciones.items():
            key = (
                clean_text(cap.get('RUT', '')).replace('.', ''),
                clean_text(cap.get('NOMBRE_CAPACITACION', ''))
            )
            caps_map[key] = (idc, cap)

        for idv_l in capacitacion_v:
            try:
                idv = limpiar_nans(idv_l)
                if not idv: continue
    
                rut_excel = clean_text(idv.get('RUT', '')).replace('.', '')
                affected_ruts.add(rut_excel)
                nombre = clean_text(idv.get('NOMBRE_CAPACITACION', ''))
                
                key = (rut_excel, nombre)
                
                category = usuarios_por_rut.get(rut_excel, '')
                
                cap_obj = Capacitacion(
                    rut_excel,
                    category,
                    idv.get('NOMBRE_CAPACITACION'),
                    idv.get('ENTIDAD'),
                    idv.get('HORAS'),
                    idv.get('NIVEL_TECNICO'),
                    idv.get('NOTA'),
                    idv.get('AÑO_INICIO', 0),
                    idv.get('AÑO_PRESENTACION', 0),
                    idv.get('CONTEXTO_PRESENTACION') or idv.get('CONTEXTO_PRESS'),
                    idv.get('ES_POSTGRADO')
                )
                candidate_dict = cap_obj.crear_dict_capacitacion()
    
                if key in caps_map:
                    idc, cap_db = caps_map[key]
                    # CHECK DIFF BEFORE UPDATE
                    is_different = False
                    for k, v in candidate_dict.items():
                        if k in ['PJE_NV_TEC', 'PJE_HORAS', 'PJE_NOTA', 'PJE_POND']: continue
                        
                        val_excel = clean_text(v)
                        val_db = cap_db.get(k)
                        val_db_norm = clean_text(val_db)
                        
                        if val_excel != val_db_norm:
                            is_different = True
                            break
                    
                    if is_different:
                        actualizar_registro('capacitaciones', candidate_dict, idc)
                else:
                    ingresar_registro_bd('capacitaciones', candidate_dict)
            except Exception as e:
                print(f"❌ Error procesando capacitación (RUT {idv_l.get('RUT')}): {e}")

    else:
        for idv_l in capacitacion_v:
            try:
                idv = limpiar_nans(idv_l)
                if not idv: continue
                
                rut_excel = str(idv.get('RUT', '')).replace('.', '').strip()
                affected_ruts.add(rut_excel)
                category = usuarios_por_rut.get(rut_excel, '')
                
                cap = Capacitacion(
                    rut_excel,
                    category,
                    idv.get('NOMBRE_CAPACITACION'),
                    idv.get('ENTIDAD'),
                    idv.get('HORAS'),
                    idv.get('NIVEL_TECNICO'),
                    idv.get('NOTA'),
                    idv.get('AÑO_INICIO', 0),
                    idv.get('AÑO_PRESENTACION', 0),
                    idv.get('CONTEXTO_PRESENTACION') or idv.get('CONTEXTO_PRESS'),
                    idv.get('ES_POSTGRADO')
                )
                ingresar_registro_bd('capacitaciones', cap.crear_dict_capacitacion())
            except Exception as e:
                print(f"❌ Error procesando capacitación (else) (RUT {idv_l.get('RUT')}): {e}")


    # --- BATCH POST-PROCESSING ---
    print(f"Post-processing {len(affected_ruts)} distinct RUTs...")

    # Refetch full datasets ONCE for the batch processing
    latest_users = leer_registro('usuarios')
    latest_contratos = leer_registro('contrato')
    latest_caps = leer_registro('capacitaciones')
    
    # We also need roles map for actualizacion_horaria
    login_data = leer_registro('login')
    roles_map = {}
    if login_data:
        roles_map = {str(l.get('ID', '')).replace('.', '').strip(): l.get('ROL', '') for l in login_data.values()}

    p_bar.progress(90, text=f"Recalculando puntajes para {len(affected_ruts)} funcionarios afectados...")
    
    processed_count = 0
    total_affected = len(affected_ruts)

    for rut in affected_ruts:
        processed_count += 1
        if processed_count % 5 == 0:
             p_bar.progress(90 + int(10 * processed_count / total_affected), text=f"Procesando {processed_count}/{total_affected}...")

        try:
            rol = roles_map.get(rut, '')
            # Update Antiquity/Age with cached data
            actualizacion_horaria(rol, latest_users, latest_contratos, rut)
            
            # Recalculate Score with cached data (Passing ALL caches to avoid refetch)
            puntaje_nv(rut, latest_caps, latest_users, latest_contratos)
            
        except Exception as e:
            print(f"[ERROR] Post-processing RUT {rut}: {e}")

    p_bar.progress(100, text="Carga masiva completada exitosamente.")
    return f"Carga masiva procesada correctamente. Insertados: {inserted_count}, Omitidos (Duplicados): {skipped_count}, Total Leídos: {len(capacitacion_v)}"



def calculate_effective_seniority_data(contracts_list):
    """
    Core logic: Calculates total days of service using Merge Intervals to handle overlaps.
    Returns (years, months, days, total_days_sum).
    """
    from datetime import datetime
    
    intervals = []
    now = datetime.now()
    
    for c in contracts_list:
        try:
            s_str = str(c.get('FECHA_INICIO', '')).strip()
            e_str = str(c.get('FECHA_TERMINO', '')).strip()
            
            if s_str:
                start_date = datetime.strptime(s_str, '%d/%m/%Y')
                
                # Check if it's Planta or Indefinite (no end date)
                ctype = str(c.get('TIPO_CONTRATO', '')).strip().upper()
                
                if 'PLANTA' in ctype or not e_str:
                    end_date = now
                else:
                    end_date = datetime.strptime(e_str, '%d/%m/%Y')
                    if end_date > now:
                        end_date = now
                
                if end_date < start_date: continue # Invalid
                
                intervals.append([start_date, end_date])
        except:
            pass
            
    if not intervals:
        return 0, 0, 0, 0
        
    # Merge Intervals
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    for current in intervals:
        if not merged:
            merged.append(current)
        else:
            prev = merged[-1]
            # If overlap or adjacent
            if current[0] <= prev[1]:
                # Merge
                prev[1] = max(prev[1], current[0]) # Fix: Start depends on sorted order
                prev[1] = max(prev[1], current[1])
            else:
                merged.append(current)
                
    total_days = 0
    for start, end in merged:
        total_days += (end - start).days
        
    # Calculate Y/M/D
    years = total_days // 365
    rem_days = total_days % 365
    months = rem_days // 30
    
    return years, months, rem_days, total_days


def get_next_evaluation_date(contracts_list):
    """
    Determines the next official evaluation date for Bienios/Level changes.
    Rule: 
    - Usage Base: Oldest Planta Contract Start. 
    - If no Planta: Oldest Plazo Fijo/Any Contract Start.
    - Cycle: Every 2 years from Base.
    """
    from datetime import datetime
    
    base_date = None
    
    # 1. Search for Oldest Planta
    plantas = [c for c in contracts_list if 'PLANTA' in str(c.get('TIPO_CONTRATO','')).upper()]
    if plantas:
        # Sort by date
        valid_dates = []
        for p in plantas:
            try: valid_dates.append(datetime.strptime(str(p.get('FECHA_INICIO','')).strip(), '%d/%m/%Y'))
            except: pass
        if valid_dates:
            base_date = min(valid_dates)
            
    # 2. If no Planta, search for Oldest overall (preferring Plazo Fijo implicitly by assuming it's the start)
    if not base_date:
        valid_dates = []
        for c in contracts_list:
             try: valid_dates.append(datetime.strptime(str(c.get('FECHA_INICIO','')).strip(), '%d/%m/%Y'))
             except: pass
        if valid_dates:
            base_date = min(valid_dates)
            
    if not base_date:
        return None, None
        
    # 3. Calculate Next Cycle
    # We want base + 2*N years > Now
    now = datetime.now()
    
    # Calculate years passed
    # We can iterate or calculate
    # If base is 2023, now is 2026. 
    # 2023 -> 2025 -> 2027. Next is 2027.
    
    # Crude approx:
    years_diff = now.year - base_date.year
    # Start checking from a bit before to be safe
    
    # Efficient way:
    # Just add 2 years until > now
    
    # Optimization: jump to near current year
    # (Not strictly necessary for short career spans, loop is fine)
    
    check_date = base_date
    while check_date <= now:
        try:
            check_date = check_date.replace(year=check_date.year + 2)
        except ValueError: # Leap year Feb 29 fix -> Mar 1
            check_date = check_date.replace(year=check_date.year + 2, day=1, month=3)
            
    return base_date, check_date


def calculate_real_seniority(contracts_list):
    y, m, d, total = calculate_effective_seniority_data(contracts_list)
    return y

def calculate_detailed_seniority(contracts_list):
    y, m, d, total = calculate_effective_seniority_data(contracts_list)
    return y, m, d


def actualizacion_horaria(rol, reg, conts, rut_red=''):
    """
    Updates Age (Usuarios) and Antiquity (Contratos).
    Calculates Seniority per PERSON (Summing contracts), not per contract.
    """
    # 1. Update Age (Users) - Keeps original logic
    if reg:
        # Filter if rut_red provided
        target_ids = []
        if rut_red:
             target_ids = [k for k,v in reg.items() if str(v.get('RUT','')).replace('.', '').strip() == rut_red]
        else:
             target_ids = reg.keys()

        for idx in target_ids:
             v = reg[idx]
             inicio = v.get('FECHA_NAC', '')
             edad = calculo_años(inicio)
             if v.get('EDAD') != edad:
                 actualizar_registro('usuarios', {'EDAD': edad}, idx)
                 v['EDAD'] = edad

    # 2. Update Seniority (Contracts) - New Logic
    if conts:
        # Group contracts by RUT
        rut_to_conts = {}
        for idc, vc in conts.items():
            r = str(vc.get('RUT', '')).replace('.', '').strip()
            if not r: continue
            if r not in rut_to_conts: rut_to_conts[r] = []
            rut_to_conts[r].append((idc, vc))
        
        # Determine targets
        target_ruts = [rut_red] if rut_red else rut_to_conts.keys()
        
        for r in target_ruts:
            if r not in rut_to_conts: continue
            
            user_contracts = [x[1] for x in rut_to_conts[r]]
            ids = [x[0] for x in rut_to_conts[r]]
            
            # Calculate Global Seniority for this person
            ant_real = calculate_real_seniority(user_contracts)
            
            # Apply to ALL contracts for this person
            for idc, vc in zip(ids, user_contracts):
                 if vc.get('ANTIGUEDAD') != ant_real:
                     actualizar_registro('contrato', {'ANTIGUEDAD': ant_real}, idc)
                     vc['ANTIGUEDAD'] = ant_real



def validar_tope_horas(rut, nuevas_horas, tipo_contrato, id_contrato_ignorar=None, data_contratos=None):
    """
    Valida que la suma de horas Planta + Plazo Fijo no supere 44.
    Retorna (True, total) si es válido, (False, total) si excede.
    """
    if "HONORARIO" in str(tipo_contrato).upper():
        return True, 0

    if data_contratos is None:
        data_contratos = leer_registro('contrato')
    
    rut_clean = str(rut).replace('.', '').strip().upper()
    total_horas = 0
    
    for k, v in data_contratos.items():
        if id_contrato_ignorar and k == id_contrato_ignorar:
            continue
        
        r_c = str(v.get('RUT', '')).replace('.', '').strip().upper()
        if r_c == rut_clean:
            t_c = v.get('TIPO_CONTRATO', '')
            if str(t_c).upper() in ['PLANTA', 'PLAZO FIJO']:
                try:
                    h = int(v.get('HORAS', 0))
                    total_horas += h
                except:
                    pass
    
    try:
        nuevas_horas = int(nuevas_horas)
    except:
        nuevas_horas = 0

    total_proyectado = total_horas + nuevas_horas
    
    if total_proyectado > 44:
        return False, total_proyectado
    return True, total_proyectado

# RECALCULATION FUNCTION
def recalcular_todo(progress_callback=None):
    """
    Recalcula antigüedad y puntajes para TODOS los funcionarios.
    Optimizado para descarga única de datos (Batch).
    """
    try:
        if progress_callback: progress_callback(0, "Iniciando descarga de datos...")
        
        # 1. Fetch All Data
        latest_users = leer_registro('usuarios')
        latest_contratos = leer_registro('contrato')
        latest_caps = leer_registro('capacitaciones')
        login_data = leer_registro('login')
        
        if not latest_users:
            return "No hay usuarios en la base de datos."
            
        roles_map = {}
        if login_data:
            roles_map = {str(l.get('ID', '')).replace('.', '').strip(): l.get('ROL', '') for l in login_data.values()}

        # 2. Iterate All Users
        all_ruts = set()
        for u in latest_users.values():
            if u.get('RUT'):
                all_ruts.add(str(u.get('RUT')).replace('.', '').strip())
                
        total = len(all_ruts)
        processed = 0
        
        # print(f"Recalculando {total} funcionarios...")
        
        for rut in all_ruts:
            processed += 1
            if progress_callback and processed % 5 == 0:
                pct = int((processed / total) * 100)
                progress_callback(pct, f"Procesando {processed}/{total} (RUT {rut})...")
                
            try:
                rol = roles_map.get(rut, '')
                # Update Antiquity
                actualizacion_horaria(rol, latest_users, latest_contratos, rut)
                
                # Recalculate Score
                puntaje_nv(rut, latest_caps, latest_users, latest_contratos)
                
            except Exception as e:
                print(f"[ERROR] Recalculando RUT {rut}: {e}")

        if progress_callback: progress_callback(100, "Finalizado!")
        return f"Proceso completado. {total} funcionarios actualizados."
        
    except Exception as e:
        return f"Error crítico: {e}"
