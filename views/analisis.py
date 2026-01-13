
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from firebase_bd import leer_registro
from datetime import datetime
import numpy as np

from modules.ui import render_header

def app():
    render_header()
    st.markdown("## 📈 Análisis Estadístico y Temporal")
    
    rut_actual = st.session_state["usuario_rut"]
    rol = st.session_state["usuario_rol"]

    if rol in ["PROGRAMADOR", "ADMIN"]:
        all_users = leer_registro('usuarios')
        user_opts = {u.get('RUT'): f"{u.get('NOMBRE_FUNC')}" for u in all_users.values()}
        rut_target = st.selectbox("Seleccionar Funcionario", options=list(user_opts.keys()), format_func=lambda x: user_opts[x])
    else:
        rut_target = rut_actual

    # Load Data
    caps = leer_registro('capacitaciones')
    user_caps = [c for c in caps.values() if c.get('RUT') == rut_target]
    
    if not user_caps:
        st.info("Sin datos suficientes para análisis.")
        return

    df = pd.DataFrame(user_caps)
    df['AÑO_PRESENTACION'] = pd.to_numeric(df['AÑO_PRESENTACION'], errors='coerce')
    df = df.dropna(subset=['AÑO_PRESENTACION'])
    df = df.sort_values(by='AÑO_PRESENTACION') # Ensure sorted for line plot

    # --- 1. Tendencia Temporal (Regresión Lineal con Numpy) ---
    st.subheader("1. Tendencia de Adquisición de Puntaje")
    
    # Group by Year
    df_yr = df.groupby('AÑO_PRESENTACION')['PJE_POND'].sum().reset_index()
    df_yr['Acumulado'] = df_yr['PJE_POND'].cumsum()

    col_chart, col_stats = st.columns([3, 1])
    
    with col_chart:
        # Manual Linear Regression to avoid statsmodels dependency
        x = df_yr['AÑO_PRESENTACION']
        y = df_yr['Acumulado']
        
        fig = px.scatter(df_yr, x='AÑO_PRESENTACION', y='Acumulado', title="Crecimiento de Puntaje Acumulado")
        fig.update_traces(marker=dict(size=12, color='#006DB6'), name="Puntaje Real")
        
        avg_pts = 0
        if len(x) > 1:
            try:
                # Calculate trend
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                
                # Add trendline trace
                fig.add_trace(go.Scatter(x=x, y=p(x), mode='lines', name='Tendencia (Regresión)', line=dict(color='red', dash='dash')))
                
                # Slope represents avg points per year roughly in this accumulated view? 
                # Actually slope of accumulated vs time is the rate (pts/year).
                avg_pts = z[0] 
            except Exception as e:
                print(f"Error calculating trend: {e}")
                
        fig.update_layout(template="plotly_white", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, width="stretch")
        
    with col_stats:
        with st.container(border=True):
            st.metric("Velocidad de Crecimiento", f"{avg_pts:.2f} pts/año", help="Promedio de puntos ganados por año según tendencia estadística")
            
            if not df_yr.empty:
                last_yr = df_yr.iloc[-1]['AÑO_PRESENTACION']
                st.metric("Último Año Activo", int(last_yr))

    # --- 2. Predicción (Simulación Simple) ---
    st.subheader("2. Predicción de Ascenso")
    
    usuario = next((u for u in leer_registro('usuarios').values() if u.get('RUT') == rut_target), {})
    current_pts = usuario.get('PTJE_CARR', 0)
    # Mock target (logic dependent on indices.py)
    target_pts = current_pts + 10 # Example gap
    
    if avg_pts > 0:
        years_needed = (target_pts - current_pts) / avg_pts
        future_year = datetime.now().year + years_needed
        st.success(f"📈 A este ritmo ({avg_pts:.1f} pts/año), obtendrías {10} puntos más en **{years_needed:.1f} años** (aprox. {int(future_year)}).")
    else:
        st.warning("No hay suficiente tendencia de crecimiento para predecir.")
    
    # --- 3. Distribución Mensual (Heatmap) ---
    st.subheader("3. Distribución por Categoría")
    
    # Robustness Check: Ensure ENTIDAD exists
    if 'ENTIDAD' not in df.columns:
        df['ENTIDAD'] = 'Desconocido'
    else:
        df['ENTIDAD'] = df['ENTIDAD'].fillna('Desconocido')
    
    if 'NIVEL_TECNICO' in df.columns and 'HORAS' in df.columns:
        fig2 = px.sunburst(df, path=['NIVEL_TECNICO', 'ENTIDAD'], values='HORAS', title="Distribución de Horas por Nivel Técnico")
        st.plotly_chart(fig2, width="stretch")
    else:
        st.info("Falta información de Nivel Técnico para el gráfico de distribución.")
