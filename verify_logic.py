def verify_logic():
    # Simulation parameters
    limit_anual = 150
    # Scenario: 
    # 2021: 200 pts (Surplus 50)
    # 2022: 100 pts (Deficit 50) -> Should be covered by 2021
    # 2023: 180 pts (Surplus 30)
    # 2024: 140 pts (Deficit 10) -> Should be covered by 2023
    # 2025: 0 pts   (Deficit 150) -> Partial coverage
    
    dict_puntaje = [
        (2021, 200),
        (2022, 100),
        (2023, 180),
        (2024, 140),
        (2025, 0)
    ]
    
    print("--- SIMULATION ---")
    
    # Logic copied from functions.py (simplified)
    saldos_por_año = {}
    for año, pje in dict_puntaje:
        saldos_por_año[año] = saldos_por_año.get(año, 0) + pje
        
    saldos_agrup = sorted(saldos_por_año.items(), key=lambda x: x[0])
    
    saldos_v2 = []
    for año, total_año in saldos_agrup:
        dif = total_año - limit_anual
        saldos_v2.append((año, dif))

    saldo_acumulado = 0
    lista_final = []
    
    print(f"Initial Diffs: {saldos_v2}")
    
    for año, dif in saldos_v2:
        print(f"Processing {año}: Diff {dif}, Bank Before: {saldo_acumulado}")
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
        print(f"  -> Bank After: {saldo_acumulado}")

    print(f"Final List: {lista_final}")
    
    sum_f = 0
    for año, final_diff in lista_final:
        valid_points = limit_anual + final_diff
        sum_f += valid_points
        print(f"Year {año}: {valid_points} pts")
        
    print(f"Total Annual Points: {sum_f}")
    
verify_logic()
