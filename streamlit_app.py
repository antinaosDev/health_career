import streamlit as st # Reload Forced 43
import firebase_bd
from views import home, login, contratos, capacitaciones, analisis, simulador, honorarios
import os

st.set_page_config(
    page_title="A2S - Health Career",
    page_icon="icono_app_carr.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global CSS (Institutional Blue #006DB6) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }

    /* Main Background */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Primary Color Accents */
    .stButton>button {
        background-color: #006DB6;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #005a9c;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #004B8D;
        font-weight: 600;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E9ECEF;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 4px;
        color: #6C757D;
        font-weight: 500;
        border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E3F2FD;
        color: #006DB6;
        border-color: #006DB6;
    }

</style>
""", unsafe_allow_html=True)

# Inicializar estado se sesión
if "usuario_rut" not in st.session_state:
    st.session_state["usuario_rut"] = None
if "usuario_rol" not in st.session_state:
    st.session_state["usuario_rol"] = None
if "usuario_nombre" not in st.session_state:
    st.session_state["usuario_nombre"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "home"

def main():
    SIDEBAR_LOGO = "logo_app_carr.png"
    FOOTER_LOGO = "logo_alain.png"
    
    if st.session_state["usuario_rut"]:
        # Sidebar
        with st.sidebar:
            if os.path.exists(SIDEBAR_LOGO):
                st.image(SIDEBAR_LOGO, use_container_width=True)
            else:
                st.title("⚕️")
                
            st.markdown(f"### Hola, {st.session_state['usuario_nombre'].split()[0]}")
            st.caption(f"Rol: {st.session_state['usuario_rol']}")
            st.divider()
            
            # Navigation with emojis
            # Navigation with emojis
            # --- ACCESS CONTROL LOGIC ---
            from firebase_bd import leer_registro
            contratos_all = leer_registro('contrato')
            rut_clean = str(st.session_state['usuario_rut']).replace('.', '').strip().upper()
            
            # Determine flags
            has_honorario = False
            has_career = False # Planta or Plazo Fijo
            
            for c in contratos_all.values():
                if str(c.get('RUT', '')).replace('.', '').strip().upper() == rut_clean:
                    tipo_c = str(c.get('TIPO_CONTRATO', '')).strip().upper()
                    if tipo_c == 'HONORARIO':
                        has_honorario = True
                    elif tipo_c in ['PLANTA', 'PLAZO FIJO']:
                        has_career = True
            
            is_admin = str(st.session_state.get('usuario_rol', '')).strip().upper() in ['ADMIN', 'PROGRAMADOR']
            
            # --- MENU RENDERING ---
            
            # 1. CAREER MODULES (Inicio, Analisis, Simulador, Contratos, Capacitaciones, Gestion Global)
            # Visible if: Admin OR has_career
            if is_admin or has_career:
                if st.sidebar.button("🏠 Inicio", width='stretch', type="secondary" if st.session_state["page"] != "home" else "primary"):
                    st.session_state["page"] = "home"
                    st.rerun()

                if is_admin:
                     if st.sidebar.button("📊 Gestión Global", width='stretch', type="secondary" if st.session_state["page"] != "gestion_global" else "primary"):
                        st.session_state["page"] = "gestion_global"
                        st.rerun()
                
                if st.sidebar.button("📈 Análisis Est.", width='stretch', type="secondary" if st.session_state["page"] != "analisis" else "primary"):
                    st.session_state["page"] = "analisis"
                    st.rerun()

                if st.sidebar.button("🔮 Simulador", width='stretch', type="secondary" if st.session_state["page"] != "simulador" else "primary"):
                    st.session_state["page"] = "simulador"
                    st.rerun()

                if st.sidebar.button("📄 Contratos", width='stretch', type="secondary" if st.session_state["page"] != "contratos" else "primary"):
                    st.session_state["page"] = "contratos"
                    st.rerun()

                if st.sidebar.button("🎓 Capacitaciones", width='stretch', type="secondary" if st.session_state["page"] != "capacitaciones" else "primary"):
                    st.session_state["page"] = "capacitaciones"
                    st.rerun()

            elif not has_career and has_honorario and not is_admin:
                # If Only Honorario and NOT Admin: Force page to 'honorarios' if trying to access others?
                # or just don't show buttons.
                # Ideally, if they login and page is 'home' (default), we redirect them immediately.
                if st.session_state["page"] != "honorarios":
                     st.session_state["page"] = "honorarios"
                     st.rerun()
            
            # 2. HONORARIOS MODULE
            # Visible if: Admin OR has_honorario
            if is_admin or has_honorario:
                if st.sidebar.button("🛡️ Honorarios", width='stretch', type="secondary" if st.session_state["page"] != "honorarios" else "primary"):
                    st.session_state["page"] = "honorarios"
                    st.rerun()
            
            st.divider()
            if st.button("Cerrar Sesión", width='stretch', type="secondary"):
                st.session_state["usuario_rut"] = None
                st.session_state["usuario_rol"] = None
                st.session_state["page"] = "home" # Reset page on logout
                st.rerun()

        # Routing
        if st.session_state["page"] == "home":
            home.app()
        elif st.session_state["page"] == "analisis":
            analisis.app()
        elif st.session_state["page"] == "simulador":
            simulador.app()
        elif st.session_state["page"] == "contratos":
            contratos.app()
        elif st.session_state["page"] == "capacitaciones":
            capacitaciones.app()
        elif st.session_state["page"] == "honorarios":
            honorarios.app()
        elif st.session_state["page"] == "gestion_global":
            from views import dashboard_admin
            dashboard_admin.app()

            
    else:
        login.app()

    # --- FOOTER GLOBAL ---
    st.markdown("---")
    with st.container():
        col1, col2, col3, col4 = st.columns([1,1,4,1])
        with col2:
            # LOGO PIE DE PÁGINA (Alain)
            if os.path.exists(FOOTER_LOGO):
                st.image(FOOTER_LOGO, width=100)
            else:
                st.info("Logo")
                
        with col3:
            st.markdown("""
                <div style='text-align: left; color: #6C757D; font-size: 13px; padding-top: 10px;'>
                    💼 Aplicación desarrollada por <strong>Alain Antinao Sepúlveda</strong> <br>
                    📧 Contacto: <a href="mailto:alain.antinao.s@gmail.com" style="color: #006DB6; text-decoration: none;">alain.antinao.s@gmail.com</a> <br>
                    🌐 Más información en: <a href="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e" target="_blank" style="color: #006DB6; text-decoration: none;">Mi página personal</a>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
