import streamlit as st
import pandas as pd
from firebase_bd import leer_registro, actualizar_registro
from funciones import puntaje_nv

def app():
    st.title("🚀 Gestión de Ascensos y Niveles")
    st.markdown("---")

    # Security Check
    if st.session_state.get("usuario_rol") not in ["ADMIN", "PROGRAMADOR"]:
        st.error("Acceso denegado. Se requieren permisos de Administrador.")
        return

    # Fetch Data
    usuarios = leer_registro('usuarios')
    if not usuarios:
        st.warning("No se pudieron cargar los usuarios.")
        return

    # Filter Pending Approvals
    pendientes = []
    for id_u, data in usuarios.items():
        if data.get('NIVEL_PENDIENTE'):
            pendientes.append({
                'ID_DB': id_u,
                'RUT': data.get('RUT'),
                'NOMBRE': data.get('NOMBRE_FUNC'),
                'NIVEL_ACTUAL': data.get('NIVEL'),
                'NIVEL_NUEVO': data.get('NIVEL_PENDIENTE'),
                'PUNTAJE': data.get('PTJE_CARR')
            })

    if not pendientes:
        st.success("✅ No hay ascensos pendientes de aprobación.")
        return

        with st.expander(f"{badge} | 👤 {p['NOMBRE']}", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            
            with c1:
                st.markdown(f"### {arrow}")
                st.caption(f"RUT: {p['RUT']} | Puntaje: {p['PUNTAJE']}")
                if badge == "🔴 DESCENSO":
                    st.warning("⚠️ Atención: Este cambio rebaja el nivel del funcionario.")
            
            with c2:
                # Flexible Level Selector
                # If 12 -> 8, options: 8, 9, 10, 11
                # If 8 -> 12 (Demotion), options: 12 (or allow 8,9,10,11?)
                # User scenario: "ej nivel 12 a nivel 8 ... aprobar un nivel intermedio ej el nivel 10"
                # Logic: Range between min and max of (act, new)
                
                v_min = min(n_act, n_new)
                v_max = max(n_act, n_new)
                
                # Exclude current? No, maybe they want to affirm current (Reject implicit)
                # But to approve a change, it should be different.
                # Range from New to Act-1 (for promotion)
                
                options = []
                if n_new < n_act: # Promotion
                     options = list(range(n_new, n_act)) # 8, 9, 10, 11
                elif n_new > n_act: # Demotion
                     options = list(range(n_act + 1, n_new + 1)) # 13, 14
                
                if not options: options = [n_new]
                
                # Default to n_new
                target_lvl = st.selectbox("Nivel a Aprobar", options, index=0, key=f"sel_{p['RUT']}")
                
            with c3:
                # Approve Button
                if st.button("✅ Aprobar", key=f"btn_ap_{p['RUT']}"):
                    try:
                        # 1. Update Level in DB with SELECTED level
                        actualizar_registro('usuarios', {
                            'NIVEL': target_lvl, 
                            'NIVEL_PENDIENTE': None
                        }, p['ID_DB'])
                        
                        # 2. Trigger Calc
                        puntaje_nv(p['RUT'])
                        
                        st.success(f"Ascenso a Nivel {target_lvl} aprobado.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error al aprobar: {e}")
