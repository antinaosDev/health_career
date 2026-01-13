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
    
    # Container for the header with custom styling
    st.markdown("""
        <style>
        .header-container {
            background-color: #f0f2f6; 
            padding: 1.5rem; 
            border-radius: 10px; 
            border-left: 6px solid #006DB6;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header-title {
            color: #0F2942;
            font-size: 24px;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
        }
        .header-subtitle {
            color: #006DB6;
            font-size: 18px;
            font-weight: 500;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        # Using columns to create the card layout
        c1, c2 = st.columns([0.85, 0.15])
        
        with c1:
            st.markdown(f"""
            <div class="header-container">
                <div class="header-title">DEPARTAMENTO DE SALUD</div>
                <div class="header-subtitle">CESFAM CHOLCHOL</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            if os.path.exists(image_path):
                # Display image vertically centered relative to text if possible, 
                # but standard st.image works best for compatibility.
                st.image(image_path, width=110)
            else:
                st.empty()
