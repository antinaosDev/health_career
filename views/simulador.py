
import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_bd import leer_registro
from indices import nv_tec_AB, nv_tec_CF, horas_cap, aprobacion, indices_niveles
from datetime import datetime

def calcular_puntos_simulados(categoria, nivel_tec, horas, nota):
    # 1. PJE_NV_TEC
    pje_nv = 0
    if categoria in ['A', 'B']:
        pje_nv = nv_tec_AB.get(nivel_tec, 0)
    else:
        pje_nv = nv_tec_CF.get(nivel_tec, 0)
    
    # 2. PJE_HORAS
    pje_horas = 0
    for k, v in horas_cap.items():
        if k[0] <= horas <= k[1]:
            pje_horas = v
            break
            
    # 3. PJE_NOTA
    pje_nota = 0
    for k, v in aprobacion.items():
        if k[0] <= nota <= k[1]:
            pje_nota = v
            break
            
    return round(pje_nv * pje_horas * pje_nota, 2)

def obtener_meta_proximo_nivel(score_actual, categoria):
    # Determine table based on category
    tabla_niveles = indices_niveles.get(('A','B')) if categoria in ['A','B'] else indices_niveles.get(('C','D','E','F'))
    
    # Sort levels by score range start
    # tabla_niveles keys are (min, max). Values are Level (15, 14, etc.)
    sorted_levels = sorted(tabla_niveles.items(), key=lambda x: x[0][0])
    
    current_level = 15
    next_level_data = None
    
    # Find where we are
    for (r_min, r_max), level in sorted_levels:
        if r_min <= score_actual <= r_max:
            current_level = level
        # Check for next level (assuming lower number is higher level, e.g. 15 -> 14)
        # But wait, logic is accumulating points. So higher score = "better" level (numerically lower usually, like Grade 15 to 1)
        
    # Find next level (level - 1)
    target_level = current_level - 1
    if target_level < 1:
        return current_level, None, 0 # Max level reached
        
    # Find requirement for target_level
    for (r_min, r_max), level in sorted_levels:
        if level == target_level:
            points_needed = r_min - score_actual
            return current_level, target_level, points_needed
            
    return current_level, None, 0

def app():
    st.markdown("## 🔮 Simulador de Carrera Profesional")
    st.markdown("Proyecta tu evolución funcionaria considerando **Plan Anual** y **Bienios** (Asignación de Antigüedad).")
    
    rut_actual = st.session_state.get("usuario_rut")
    if not rut_actual:
        st.error("No se ha identificado el usuario.")
        return

    # --- 1. Load Data ---
    users = leer_registro('usuarios')
    usuario = next((u for u in users.values() if u.get('RUT') == rut_actual), {})
    
    contratos = leer_registro('contrato')
    antiguedad_actual = 0
    # Find max antiquity from valid contracts
    for c in contratos.values():
         if c.get('RUT') == rut_actual and c.get('TIPO_CONTRATO') in ['Planta', 'Plazo Fijo']:
             try:
                 ant = int(c.get('ANTIGUEDAD', 0))
                 if ant > antiguedad_actual: antiguedad_actual = ant
             except: pass
             
    if not usuario:
        st.error("Usuario no encontrado en base de datos.")
        return

    # Base Stats
    current_score = float(usuario.get('PTJE_CARR', 0))
    saldo_actual = float(usuario.get('SALDO_PTJE', 0))
    categoria = usuario.get('CATEGORIA', 'E') 
    
    # Determine Annual Limit
    limit_anual = 150 if categoria in ['A', 'B'] else 117
    
    # Identify Current Level
    nivel_actual, prox_nivel, ptos_para_nivel = obtener_meta_proximo_nivel(current_score, categoria)
    
    # --- 2. Interface Layout ---
    
    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nivel Actual", nivel_actual)
    c2.metric("Puntaje Carrera", f"{current_score:,.2f}")
    c3.metric("Antigüedad (Años)", antiguedad_actual)
    c4.metric("Saldo Acumulado", f"{saldo_actual:,.2f}", help="Puntaje de sobra disponible para cubrir déficits.")
    
    st.divider()
    
    col_config, col_results = st.columns([1, 2])
    
    with col_config:
        with st.container(border=True):
            st.subheader("⚙️ Parámetros de Simulación")
            
            sim_years = st.slider("Años a proyectar", 1, 10, 5)
            st.divider()
            
            # Inputs
            s_horas = st.slider("Horas Cap. Promedio / Año", 0, 120, 40, step=10)
            s_nota = st.slider("Nota Promedio Esperada", 4.0, 7.0, 6.5, step=0.1)
            s_nivel_tec = st.selectbox("Nivel Técnico Promedio", ["Alto", "Medio", "Bajo"], index=1) 
            
            # Calculation of 'Annual Power'
            pts_anuales_brutos = calcular_puntos_simulados(categoria, s_nivel_tec, s_horas, s_nota)
            diff_anual = pts_anuales_brutos - limit_anual
            
            st.markdown(f"**Puntos Generados/Año**: `{pts_anuales_brutos}`")
            if diff_anual >= 0:
                st.success(f"✅ Superávit Anual: +{diff_anual:.2f} (Va a Saldo)")
            else:
                st.warning(f"⚠️ Déficit Anual: {diff_anual:.2f} (Se paga con Saldo)")

    with col_results:
        st.subheader("📊 Proyección de Resultados")
        
        # Simulation Loop
        projection_data = []
        running_score = current_score
        running_saldo = saldo_actual
        running_antiguedad = antiguedad_actual
        
        current_year_sim = datetime.now().year
        
        # --- INITIALIZE TRAINING SPLIT for Simulation ---
        # limits
        limit_global = 4500 if categoria in ['A', 'B'] else 3500
        
        # We need to know current "Training Score" vs "Bienios Score"
        # Current logic in funciones.py: sum_f = total_training_capped + bienios_val
        # So we can reverse engineer or fetch detail?
        # For simplicity in simulation:
        # User PTJE_CARR is valid.
        # Bienios score = (BIENIOS * 534)
        # Training Score = PTJE_CARR - Bienios Score
        
        bienios_count_initial = int(usuario.get('BIENIOS', 0))
        bienios_score_initial = bienios_count_initial * 534
        
        # running_training_score is the component subject to Cap
        running_training_score = current_score - bienios_score_initial
        
        # Safety: If data is inconsistent (e.g. manual edits), ensure non-negative
        if running_training_score < 0: running_training_score = 0
        
        # Apply immediate cap check for start state (in case logic changed since last save)
        if running_training_score > limit_global:
            diff = running_training_score - limit_global
            running_training_score = limit_global
            running_saldo += diff # Add existing excess to available balance for sim?
            # Note: This aligns simulator with new logic immediately.
        
        # Add year 0
        projection_data.append({
            "Año": current_year_sim,
            "Puntaje Total": running_score,
            "Nivel Estimado": nivel_actual,
            "Fuente": "Actual",
            "Saldo Disp.": running_saldo
        })
        
        for i in range(1, sim_years + 1):
            year = current_year_sim + i
            running_antiguedad += 1
            
            # 1. Base Annual Points (Capped at Limit)
            puntos_ganados_anio = 0
            
            if pts_anuales_brutos >= limit_anual:
                # Surplus
                puntos_ganados_anio = limit_anual
                surplus = pts_anuales_brutos - limit_anual
                running_saldo += surplus
                desc = "Tope Anual"
            else:
                # Deficit
                deficit = limit_anual - pts_anuales_brutos
                if running_saldo >= deficit:
                    # Pay full
                    running_saldo -= deficit
                    puntos_ganados_anio = limit_anual
                    desc = "Tope (c/Saldo)"
                else:
                    # Partial
                    puntos_ganados_anio = pts_anuales_brutos + running_saldo
                    running_saldo = 0
                    desc = "Parcial"
            
            # 2. Biennium Points (Every even year of antiquity)
            puntos_bienio = 0
            if running_antiguedad > 0 and running_antiguedad % 2 == 0:
                puntos_bienio = 534
                desc += " + Bienio"
            
            total_gain = puntos_ganados_anio # Tentative gain before global cap
            
            # --- GLOBAL CAP LOGIC ---
            # Increase training score
            potential_training_score = running_training_score + total_gain
            
            # Check against Global Cap (limit_global)
            if potential_training_score > limit_global:
                # Cap it
                allowed_training = limit_global
                excess = potential_training_score - limit_global
                
                # Update Running Training Score to Max
                running_training_score = allowed_training
                
                # Excess goes to Saldo
                running_saldo += excess
                
                desc += " (Tope Global)"
            else:
                running_training_score = potential_training_score
                
            # Final Score = Capped Training + Bienios
            # We must recalculate bienios contribution to total score.
            # running_score was: Training + Bienios
            # Now running_score = running_training_score + (running_antiguedad // 2 * 534)
            
            bienios_total_sim = (running_antiguedad // 2) * 534
            running_score = running_training_score + bienios_total_sim
            
            # Identify Level
            lvl_sim, _, _ = obtener_meta_proximo_nivel(running_score, categoria)
            
            projection_data.append({
                "Año": year,
                "Puntaje Total": round(running_score, 2),
                "Nivel Estimado": lvl_sim,
                "Fuente": desc,
                "Saldo Disp.": round(running_saldo, 2),
                "Score Cap Limit": round(running_training_score, 2) # Debug/Info
            })
            
        df_sim = pd.DataFrame(projection_data)
        
        # Chart
        fig = px.line(df_sim, x="Año", y="Puntaje Total", markers=True, 
                      title="Trayectoria Proyectada (Incluye Bienios)", text="Nivel Estimado")
        fig.update_traces(textposition="bottom right")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(df_sim.style.format({"Puntaje Total": "{:,.2f}", "Saldo Disp.": "{:,.2f}"}), use_container_width=True)

    # --- 3. Gap Analysis / Recommendations ---
    st.divider()
    st.markdown("### 🎯 Análisis de Metas")
    
    if prox_nivel:
        c_gap1, c_gap2 = st.columns([2, 1])
        with c_gap1:
            st.info(f"Para llegar al **Nivel {prox_nivel}**, necesitas **{ptos_para_nivel:,.2f}** puntos adicionales.")
            
            # Estimate Avg Growth (Total Gain / Years)
            final_points = projection_data[-1]["Puntaje Total"]
            total_growth = final_points - current_score
            avg_growth = total_growth / sim_years if sim_years > 0 else 0
            
            if avg_growth > 0:
                years_needed = ptos_para_nivel / avg_growth
                st.write(f"Con tu plan actual (crecimiento aprox **{avg_growth:.1f} pts/año**), llegarás en **{years_needed:.1f} años**.")
                
                # Breakdown Explanation
                avg_bienios = 267.0 # 534 / 2
                avg_cap = avg_growth - avg_bienios
                st.caption(f"Desglose estimativo:")
                st.caption(f"• Capacitación (Topada): ~{avg_cap:.0f} pts/año")
                st.caption(f"• Bienios (Promedio): 267 pts/año")
            else:
                st.error("No estás creciendo en puntaje.") # Should not happen with bienios usually
                
        with c_gap2:
            st.caption("Consejo:")
            if pts_anuales_brutos < limit_anual and saldo_actual < 100:
                 st.warning("⚠️ Tu plan anual no cubre el límite y tienes poco saldo. Aumenta tus horas o nota.")
            elif pts_anuales_brutos >= limit_anual:
                 st.success("✅ Tu plan maximiza el puntaje anual.")
            else:
                 st.info("ℹ️ Estás usando saldo para cubrir el año.")
    else:
        st.success("¡Nivel Máximo Alcanzado!")
