from firebase_bd import leer_registro, actualizar_registro
from indices import indices_niveles, sueldos_reajustados_2025

def debug_puntaje_nv(rut_ev_input):
    # Normalize input
    rut_ev = str(rut_ev_input).replace('.', '').strip()
    
    # 1. Fetch User & Contract Data
    datos_u_local = leer_registro('usuarios')
    datos_ant = leer_registro('contrato')
    
    # Identify user category and Determine Annual Limit
    limit_anual = 150 
    categoria_user = ''
    
    user_id = None
    if datos_u_local:
        for idu, usr in datos_u_local.items():
            if str(usr.get('RUT', '')).replace('.', '').strip() == rut_ev:
                user_record = usr
                user_id = idu
                categoria_user = usr.get('CATEGORIA', '')
                break
    
    if categoria_user in ['A', 'B']:
        limit_anual = 150
    elif categoria_user in ['C', 'D', 'E', 'F']:
        limit_anual = 117
    else:
        limit_anual = 150

    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"--- DEBUGGING RUT: {rut_ev_input} ---\n")
        f.write(f"Categoria: {categoria_user}, Limite: {limit_anual}\n")
        
        # 2. Process Capacitaciones (Trainings)
        datos = leer_registro('capacitaciones')
        dict_puntaje = []
        puntaje_planta = []
        
        if datos:
            f.write(f"--- DUMPING ALL TRAININGS FOR {rut_ev} ---\n")
            for idx, cap in datos.items():
                r_cap = str(cap.get('RUT', '')).replace('.', '').strip()
                if r_cap == rut_ev:
                    # Dump minimal info to identify
                    nombre = cap.get('NOMBRE_CAPACITACION')
                    año = cap.get('AÑO_PRESENTACION')
                    contexto = cap.get('CONTEXTO_PRESENTACION') or cap.get('CONTEXTO_PRESS')
                    pje = cap.get('PJE_POND')
                    f.write(f"Found: {nombre} | Year: {año} | Ctx: {contexto} | Pts: {pje}\n")
                    
                    if contexto == 'Ingreso a Planta':
                        puntaje_planta.append((nombre, pje))
                    else:
                        if año: 
                             dict_puntaje.append((año, pje))
        f.write("--- END DUMP ---\n")

        f.write(f"Puntajes Planta ({len(puntaje_planta)}): {puntaje_planta}\n")
        suma_planta = sum([p[1] for p in puntaje_planta])
        f.write(f"Suma Planta: {suma_planta}\n")

        # 3. Calculate Antiquity (Bienios)
        mayor_antiguedad = 0
        tiene_contrato_planta = False

        if datos_ant:
            for ant in datos_ant.values():
                r_ant = str(ant.get('RUT', '')).replace('.', '').strip()
                if r_ant == rut_ev and ant.get('TIPO_CONTRATO') in ['Planta', 'Plazo Fijo']:
                    antiguedad = ant.get('ANTIGUEDAD')
                    if antiguedad is not None:
                        try:
                            antiguedad = int(antiguedad)
                            if antiguedad > mayor_antiguedad:
                                mayor_antiguedad = antiguedad
                        except ValueError:
                            pass

                    if ant.get('TIPO_CONTRATO') == 'Planta':
                        tiene_contrato_planta = True

        bienio = mayor_antiguedad // 2
        f.write(f"Antiguedad: {mayor_antiguedad}, Bienios: {bienio}\n")

        import datetime
        # 4. Process Annual Points (Group by Year)
        saldos_por_año = {}
        if dict_puntaje:
            years = [x[0] for x in dict_puntaje]
            min_year = min(years)
            max_year = max(years)
            target_max = max(max_year, datetime.datetime.now().year)
            
            for año, pje in dict_puntaje:
                saldos_por_año[año] = saldos_por_año.get(año, 0) + pje
            
            # Fill gaps
            for y in range(min_year, target_max + 1):
                if y not in saldos_por_año:
                    saldos_por_año[y] = 0
        else:
            saldos_por_año = {}
            
        saldos_agrup = sorted(saldos_por_año.items(), key=lambda x: str(x[0])) # Safe sort
        f.write(f"Saldos por Año (Raw): {saldos_agrup}\n")

        # Calculate Raw Difference vs Limit
        saldos_v2 = []
        for año, total_año in saldos_agrup:
            dif = total_año - limit_anual
            saldos_v2.append((año, dif))

        f.write(f"Diffs vs Limit ({limit_anual}): {saldos_v2}\n")

        # 5. Apply Balance Logic
        saldo_acumulado = 0
        lista_final = []
        
        for año, dif in saldos_v2:
            if dif >= 0:
                saldo_acumulado += dif
                lista_final.append((año, 0))
            else:
                needed = abs(dif)
                if saldo_acumulado >= needed:
                    saldo_acumulado -= needed
                    lista_final.append((año, 0)) 
                else:
                    remaining_deficit = needed - saldo_acumulado
                    saldo_acumulado = 0
                    lista_final.append((año, -remaining_deficit))
                    
        f.write(f"Lista Final (Diff Ajustada): {lista_final}\n")
        f.write(f"Saldo Final: {saldo_acumulado}\n")

        # 6. Final Score Calculation
        bienios_val = bienio * 534
        f.write(f"Valor Bienios: {bienios_val}\n")
        
        sum_f = bienios_val + suma_planta
        f.write(f"Base (Bienios+Planta): {sum_f}\n")
        
        for año, final_diff in lista_final:
            valid_points = limit_anual + final_diff
            f.write(f"Año {año}: {valid_points} pts (Limit {limit_anual} + Diff {final_diff})\n")
            sum_f += valid_points

        f.write(f"--- TOTAL FINAL: {sum_f} ---\n")

if __name__ == "__main__":
    debug_puntaje_nv('18581575-7')
