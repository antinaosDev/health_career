import streamlit as st
import os

def render_header():
    """
    Renders a unified header with the establishment name and logo.
    """
    # Image path
    image_path = "CESFAM_CHOLCHOL.jpg"
    
    # Check if image exists
    if not os.path.exists(image_path):
        # Try finding it in root if we are in a submodule
        image_path = os.path.join(os.getcwd(), "CESFAM_CHOLCHOL.jpg")
    
    # Container for the header
    with st.container():
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            st.markdown("""
            <div style="display: flex; align-items: center; height: 100%;">
                <h3 style="margin: 0; color: #006DB6; font-weight: bold;">Establecimiento: DEPARTAMENTO DE SALUD / CESFAM CHOLCHOL</h3>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            if os.path.exists(image_path):
                st.image(image_path, width=100)
            else:
                st.empty()
        
        st.divider()
