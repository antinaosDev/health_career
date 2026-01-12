
import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_bd import leer_registro
from indices import sueldos_reajustados_2025
from funciones import actualizacion_horaria, es_contrato_activo, dias_restantes_contrato
from modules.pdf_honorarios import create_pdf_honorarios
import os

def format_clp(value):
    try:
        return f"${int(value):,}".replace(",", ".")
    except:
        return "$0"

def app():
    st.markdown("## 🛡️ Gestión de Honorarios")
    
    rut_actual = st.session_state["usuario_rut"]
    rol_actual = st.session_state["usuario_rol"]

    users = leer_registro('usuarios')
    contratos = leer_registro('contrato')

    # --- FILTERING LOGIC ---
    # Goal: Get users who have AT LEAST ONE 'Honorario' contract.
    # Note: A user might have mixed contracts? 
    # User Request: "Usuarios con contrato Honorario... módulo exclusivo...".
    # User also said: "Usuarios con tipo de contrato Honorario... no deben mostrarse en el listado Seleccionar Funcionario".
    # This implies a separation.
    
    honorarios_ruts = set()
    for c in contratos.values():
        if str(c.get('TIPO_CONTRATO', '')).strip().upper() == 'HONORARIO':
             honorarios_ruts.add(str(c.get('RUT', '')).replace('.', '').strip())
    
    # If ADMIN/PROGRAMADOR, can see/select any Honorario user.
    if rol_actual in ['ADMIN', 'PROGRAMADOR']:
        # Filter users list to only those in honorarios_ruts
        valid_users = {r: u for r, u in users.items() if str(u.get('RUT', '')).replace('.', '').strip() in honorarios_ruts}
        
        if not valid_users:
            st.info("No hay funcionarios a honorarios registrados.")
            return

        user_opts = {u.get('RUT'): f"{u.get('NOMBRE_FUNC')} ({u.get('RUT')})" for u in valid_users.values() if u.get('RUT')}
        rut_target = st.selectbox("Seleccionar Funcionario (Honorario)", options=list(user_opts.keys()), format_func=lambda x: user_opts[x])
    
    else:
        # If Standard User, check if they are in the honorarios list.
        my_rut = str(rut_actual).replace('.', '').strip()
        if my_rut in honorarios_ruts:
            rut_target = rut_actual # Self-view
        else:
            st.error("🚫 Acceso Denegado: No tienes un contrato vigente como Honorario.")
            return

    # --- DISPLAY DATA FOR TARGET ---
    user_data = next((u for u in users.values() if u.get('RUT') == rut_target), None)
    if not user_data:
        st.error("Datos de usuario no encontrados.")
        return

    st.divider()
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"### 👤 {user_data.get('NOMBRE_FUNC')}")
        st.markdown(f"**RUT:** {user_data.get('RUT')}")
        cat = user_data.get('CATEGORIA', 'Sin Categoría')
        st.markdown(f"**Categoría:** {cat}")
        st.markdown(f"**Profesión:** {user_data.get('PROFESION', '--')}")
    
    with c2:
        st.info("ℹ️ **Nota**: Este módulo es exclusivo para funcionarios a Honorarios. El cálculo de sueldo es **estimativo** basado en un estándar (Nivel 15) y no refleja carrera funcionaria.")

    # --- CONTRACTS & ESTIMATION ---
    st.subheader("📋 Contratos y Estimación de Sueldo")
    
    user_conts = [c for c in contratos.values() if str(c.get('RUT', '')).replace('.', '').strip() == str(rut_target).replace('.', '').strip()]
    honorario_conts = [c for c in user_conts if str(c.get('TIPO_CONTRATO', '')).strip().upper() == 'HONORARIO']
    
    if not honorario_conts:
        st.warning("Este usuario no tiene contratos Honorario activos (o fueron eliminados).")
        return

    total_estimado_global = 0
    df_data = []

    for c in honorario_conts:
        horas = 0
        try: horas = int(c.get('HORAS', 0))
        except: pass
        
        # ESTIMATION LOGIC
        # Base: Level 15 of user Category.
        # Formula: (Base / 44) * Horas -> Base is for 44 hrs usually?
        # Assuming table `sueldos_reajustados_2025` is for 44 hours.
        # So: (Sueldo_N15_Cat / 44) * Horas_Contrato
        
        monto_str = "Monto no determinable"
        monto_val = 0
        determinable = False
        
        if cat in ['A', 'B', 'C', 'D', 'E', 'F'] and horas > 0:
            if es_contrato_activo(c):
                base_n15 = sueldos_reajustados_2025.get(15, {}).get(cat, 0)
                if base_n15 > 0:
                    estimado_base = (base_n15 / 44) * horas
                    estimado_total = estimado_base * 2 # Base + APS (Base*2)
                    
                    monto_val = int(estimado_total)
                    monto_str = format_clp(monto_val) + " (Base+APS)"
                    determinable = True
                    
                    total_estimado_global += monto_val
                else:
                    monto_str = "Error en base"
            else:
                 monto_str = "$0 (Vencido)"
        elif horas == 0:
            monto_str = "Sin horas definidas"
        else:
            monto_str = "Categoría inválida"
            
        # Status Label
        dias_left = dias_restantes_contrato(c)
        status_label = "Vigente"
        if dias_left is not None:
            if dias_left < 0: status_label = f"🔴 Vencido hace {abs(dias_left)} días"
            else: status_label = f"🟢 Quedan {dias_left} días"
            
        df_data.append({
            "Inst.": c.get('NOMBRE_INSTITUCION', '--'),
            "Cargo": c.get('CARGO', '--'),
            "Estado": status_label,
            "Horas": horas,
            "Inicio": c.get('FECHA_INICIO', '--'),
            "Término": c.get('FECHA_TERMINO', '--'),
            "Sueldo Est.": monto_str
        })
    
    st.dataframe(pd.DataFrame(df_data), width='stretch', hide_index=True)
    
    st.markdown(f"### 💰 Total Estimado Mensual (Base + APS): **{format_clp(total_estimado_global)}**")
    st.caption("*Cálculo: Sueldo Base Nivel 15 (proporcional a horas) + Asignación APS (100% Base)*")
    
    st.divider()

    # --- PDF REPORT GENERATION ---
    logo_path = os.path.abspath("logo_app_carr.png")
    logo_company_path = os.path.abspath("logo_alain.png")

    if st.button("📄 Generar Reporte PDF", key="btn_pdf_honorario"):
        with st.spinner("Actualizando datos y generando documento..."):
            try:
                # 1. Force Update (Logic from home.py but simplified for Honorarios context if needed)
                # We reuse actualizacion_horaria to ensure consistency in what 'user_data' holds vs Contracts
                ud_db = leer_registro('usuarios')
                ct_db = leer_registro('contrato')
                
                # Update logic (updates DB and local objects)
                actualizacion_horaria(st.session_state["usuario_rol"], ud_db, ct_db, rut_target)
                
                # 2. Re-fetch refreshed data
                # We need fresh user object and contracts
                # Re-read contracts for target
                users_fresh = leer_registro('usuarios')
                conts_fresh = leer_registro('contrato')
                
                user_data_fresh = next((u for u in users_fresh.values() if u.get('RUT') == rut_target), {})
                
                user_conts_fresh = [c for c in conts_fresh.values() if str(c.get('RUT', '')).replace('.', '').strip() == str(rut_target).replace('.', '').strip()]
                honorario_conts_fresh = [c for c in user_conts_fresh if str(c.get('TIPO_CONTRATO', '')).strip().upper() == 'HONORARIO']
                
                # 3. Recalculate salary for PDF (to pass explicitly)
                salary_data = {'total_base_aps': total_estimado_global} # We already calc'd it above, but assuming stable. 
                # Ideally we recalculate with fresh data, but cost is minimal to trust above if no data change.
                # Actually, fresh data is better. Recalc quickly:
                
                pdf_total = 0
                cat_f = user_data_fresh.get('CATEGORIA')
                for c in honorario_conts_fresh:
                    try:
                        h = int(c.get('HORAS', 0))
                        if cat_f in ['A', 'B', 'C', 'D', 'E', 'F'] and h > 0:
                            if es_contrato_activo(c):
                                b_n15 = sueldos_reajustados_2025.get(15, {}).get(cat_f, 0)
                                if b_n15 > 0:
                                    pdf_total += ((b_n15 / 44) * h) * 2
                    except: pass
                
                salary_data['total_base_aps'] = pdf_total

                # 4. Generate PDF
                pdf_bytes = create_pdf_honorarios(
                    user_data=user_data_fresh, 
                    honorario_conts=honorario_conts_fresh, 
                    estimated_salary_data=salary_data, 
                    logo_path=logo_path,
                    logo_company_path=logo_company_path
                )
                
                # 5. Download Button
                st.download_button(
                    label="💾 Descargar Ficha Honorario",
                    data=pdf_bytes,
                    file_name=f"Ficha_Honorario_{rut_target}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Reporte generado exitosamente.")
                
            except Exception as e:
                st.error(f"Error generando reporte: {e}")
    
