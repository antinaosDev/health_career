
import streamlit as st
import time
import os
from firebase_bd import leer_registro

def app():
    APP_LOGO = "logo_app_carr.png"
    
    st.markdown("""
    <style>
    .stApp > header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Main Card Native
        with st.container(border=True):
            col_logo, col_text = st.columns([1, 2])
            
            with col_logo:
                if os.path.exists(APP_LOGO):
                    st.image(APP_LOGO, use_container_width=True)
            
            with col_text:
                st.markdown("<h3 style='color: #006DB6; margin: 0;'>Portal Funcionarios</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #666; font-size: 14px;'>Sistema de Gestión de Carrera</p>", unsafe_allow_html=True)
            
            st.divider()
            
            with st.form("login_form", border=False):
                usuario = st.text_input("Usuario", placeholder="Ej: usuario.1")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
                
    if submitted:
        if not usuario or not password:
            st.toast("⚠️ Ingrese usuario y contraseña", icon="⚠️")
            return

        with st.spinner("Autenticando..."):
            
            datos_log = leer_registro('login')
            
            user_found = False
            rut_found = None
            user_role = None
            
            for idx, usr in datos_log.items():
                if usr.get('USER') == usuario and usr.get('PASS') == password:
                    user_found = True
                    rut_found = usr.get('ID')
                    user_role = str(usr.get('ROL', '')).strip().upper()
                    break
            
            if user_found:
                st.toast("✅ Bienvenido", icon="👋")
                
                st.session_state["usuario_rut"] = rut_found
                st.session_state["usuario_rol"] = user_role
                
                # Buscar nombre usuario
                reg_usuarios = leer_registro('usuarios')
                nombre = "Usuario"
                for u in reg_usuarios.values():
                    if u.get('RUT') == rut_found:
                        nombre = u.get('NOMBRE_FUNC', 'Usuario')
                        break
                
                st.session_state["usuario_nombre"] = nombre
                
                # --- AUTO-RECALCULATE ON LOGIN ---
                # As requested: Global for Admin/Prog, Single for others.
                from funciones import recalcular_todo, actualizacion_horaria, puntaje_nv
                
                with st.spinner("Sincronizando información..."):
                    try:
                        if user_role in ['ADMIN', 'PROGRAMADOR']:
                            # Global Recalculation (Only once per session)
                            if not st.session_state.get('db_global_update_done', False):
                                recalcular_todo()
                                st.session_state['db_global_update_done'] = True
                                st.toast("🔄 Base de datos recalculada globalmente", icon="✅")
                            else:
                                st.toast("✅ Sesión activa (datos ya actualizados)", icon="ℹ️")
                        else:
                            # Single User Recalculation
                            # We fetch data just for this operation to ensure freshness
                            users_data = leer_registro('usuarios')
                            conts_data = leer_registro('contrato')
                            caps_data = leer_registro('capacitaciones')
                            
                            # Update Antiquity
                            actualizacion_horaria(user_role, users_data, conts_data, rut_found)
                            # Update Score (and generate detailed breakdown)
                            puntaje_nv(rut_found, caps_data, users_data, conts_data)
                            st.toast("🔄 Datos personales actualizados", icon="✅")
                    except Exception as e:
                        print(f"Login Sync Error: {e}")
                # ---------------------------------
                time.sleep(0.5)
                st.rerun()
                
            else:
                st.error("❌ Credenciales incorrectas. Intente nuevamente.")
