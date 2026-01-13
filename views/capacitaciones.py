
import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_bd import leer_registro, ingresar_registro_bd, eliminar_registro_bd, actualizar_registro
from clases import Capacitacion
from funciones import carga_masiva, puntaje_nv

from datetime import datetime
import time

def app():
    st.markdown("## 🎓 Capacitaciones")
    
    rut_actual = st.session_state["usuario_rut"]
    rol_actual = st.session_state["usuario_rol"]
    
    # Reload data
    datos = leer_registro('capacitaciones')
    
    # Process Data for Charts
    df_chart = pd.DataFrame(datos.values()) if datos else pd.DataFrame()
    if not df_chart.empty and rol_actual not in ['ADMIN', 'PROGRAMADOR']:
        df_chart = df_chart[df_chart['RUT'] == rut_actual]

    # --- METRICS SECTION (Ludic) ---
    st.markdown("### 📊 Resumen de Capacitaciones")
    if not df_chart.empty:
        # Metrics
        total_hrs = df_chart['HORAS'].sum() if 'HORAS' in df_chart.columns else 0
        total_pts = df_chart['PJE_POND'].sum() if 'PJE_POND' in df_chart.columns else 0
        count_caps = len(df_chart)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Registros", count_caps, "Cursos/Dipl.")
        m2.metric("Horas Acumuladas", f"{total_hrs} hrs", "Pedagógicas")
        m3.metric("Puntaje Est.", f"{total_pts:.2f} pts", "Ponderado")
        
        # Charts
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
             with st.container(border=True):
                 st.markdown("**Distribución por Nivel Técnico**")
                 if 'NIVEL_TECNICO' in df_chart.columns:
                     # Fill NaN
                     df_chart['NIVEL_TECNICO'] = df_chart['NIVEL_TECNICO'].fillna('Sin Especificar').replace('', 'Sin Especificar')
                     # Create pie chart
                     fig_nivel = px.pie(df_chart, names='NIVEL_TECNICO', hole=0.4, title="", height=300)
                     st.plotly_chart(fig_nivel, width="stretch")
                 else:
                     st.info("Columna NIVEL_TECNICO no encontrada.")
        with c_chart2:
             with st.container(border=True):
                 st.markdown("**Evolución Anual (Horas)**")
                 if 'AÑO_INICIO' in df_chart.columns:
                     # Filter valid years (assuming > 1900)
                     df_chart['AÑO_INICIO_NUM'] = pd.to_numeric(df_chart['AÑO_INICIO'], errors='coerce').fillna(0)
                     df_y = df_chart[df_chart['AÑO_INICIO_NUM'] > 1900].groupby('AÑO_INICIO')['HORAS'].sum().reset_index()
                     
                     if not df_y.empty:
                         fig_bar = px.bar(df_y, x='AÑO_INICIO', y='HORAS', title="", height=300, color_discrete_sequence=['#006DB6'])
                         fig_bar.update_layout(xaxis_type='category') # Treat years as categories
                         st.plotly_chart(fig_bar, width="stretch")
                     else:
                         st.caption("Sin datos históricos válidos.")
    else:
        st.info("No hay datos suficientes para generar estadísticas.")
    
    st.divider()

    # Permissions Logic
    can_edit = rol_actual in ['ADMIN', 'PROGRAMADOR']
    
    tabs = ["📋 Listado Detallado"]
    if can_edit:
        tabs.extend(["➕ Registro Manual", "📂 Carga Masiva"])
    
    selected_tab = st.components.v1.html(f"""<script>console.log('tabs')</script>""", height=0) # Dummy
    # Using st.tabs dynamic
    tab_objs = st.tabs(tabs)
    
    # --- TAB 1: LISTADO ---
    with tab_objs[0]:
        with st.container(border=True):
            if datos:
                df = pd.DataFrame(datos.values())
                
                # Fetch Users for Name Mapping
                reg_users = leer_registro('usuarios')
                rut_map = {}
                if reg_users:
                     for u in reg_users.values():
                         rut_map[u.get('RUT')] = u.get('NOMBRE_FUNC', 'Desconocido')
                
                df['FUNCIONARIO'] = df['RUT'].map(rut_map).fillna(df['RUT'])

                # Filter by Role
                if not can_edit:
                    df = df[df['RUT'] == rut_actual]
                
                if not df.empty:
                    # Rename cols for display
                    display_cols = ['RUT', 'FUNCIONARIO', 'NOMBRE_CAPACITACION', 'ENTIDAD', 'AÑO_INICIO', 'HORAS', 'NOTA', 'NIVEL_TECNICO', 'PJE_POND']
                    valid_cols = [c for c in display_cols if c in df.columns]
                    
                    # FIX: Force string types for PyArrow compatibility
                    text_cols = ['NOMBRE_CAPACITACION', 'ENTIDAD', 'NIVEL_TECNICO']
                    for c in text_cols:
                        if c in df[valid_cols].columns:
                            df[c] = df[c].astype(str)
                    
                    st.dataframe(
                        df[valid_cols],
                        use_container_width=True,
                        column_config={
                            "RUT": "RUT",
                            "FUNCIONARIO": st.column_config.TextColumn("Funcionario", width="medium"),
                            "NOMBRE_CAPACITACION": st.column_config.TextColumn("Nombre", width="large"),
                            "ENTIDAD": st.column_config.TextColumn("Institución"),
                            "AÑO_INICIO": st.column_config.NumberColumn("Año", format="%d"),
                            "HORAS": st.column_config.NumberColumn("Horas", format="%d hrs"),
                            "NOTA": st.column_config.ProgressColumn("Nota", min_value=1, max_value=7, format="%.1f"),
                            "PJE_POND": st.column_config.NumberColumn("Puntaje", format="%.2f"),
                        },
                        hide_index=True
                    )
                    
                    # Delete Option (Restricted)
                    if can_edit:
                        st.divider()
                        st.markdown("**Gestión de Registros**")
                        exps = df['ID'].tolist() if 'ID' in df.columns else []
                        if exps:
                             c_del1, c_del2 = st.columns([3,1])
                             with c_del1:
                                 id_to_del = st.selectbox("Seleccionar registro para eliminar", exps, format_func=lambda x: f"ID: {x}")
                             with c_del2:
                                 if st.button("🗑️ Eliminar", type="primary"):
                                     eliminar_registro_bd('capacitaciones', id_to_del)
                                     # Recalculate score
                                     puntaje_nv(rut_actual)
                                     st.success("Registro eliminado.")
                                     st.rerun()

                else:
                    st.info("No tienes capacitaciones registradas.")
            else:
                st.info("No hay datos en el sistema.")

    # --- TAB 2 & 3: ADMIN ONLY ---
    if can_edit:
        # --- TAB 2: REGISTRO MANUAL (CRUD) ---
        with tab_objs[1]:
            with st.container(border=True):
                c_mode1, c_mode2 = st.columns([2, 1])
                with c_mode1:
                    st.markdown("### Gestión de Registros")
                with c_mode2:
                    crud_mode = st.radio("Modo", ["Nuevo", "Editar", "Eliminar"], horizontal=True, label_visibility="collapsed")

                # Vars for Form Defaults
                f_rut = rut_actual
                f_nombre = ""
                f_post = False
                f_nv = "Medio"
                f_horas = 20
                f_nota = 7.0
                f_inst = ""
                f_inicio = datetime.now()
                f_year_pres = datetime.now().year
                f_contexto = "Cambio de Nivel"
                f_id = None
                
                # Selection Logic for Edit/Delete
                if crud_mode in ["Editar", "Eliminar"]:
                    # 1. Select User (Admin) or Self (User)
                    target_rut = rut_actual
                    if rol_actual in ['ADMIN', 'PROGRAMADOR']:
                        unique_ruts = list(set([d['RUT'] for d in datos.values()])) if datos else []
                        if unique_ruts:
                            if not 'reg_users' in locals(): reg_users = leer_registro('usuarios')
                            rut_msg = lambda r: f"{r} - {reg_users[r].get('NOMBRE_FUNC','') if reg_users and r in reg_users else ''}"
                            target_rut = st.selectbox("Seleccionar Funcionario", unique_ruts, format_func=rut_msg)
                        else:
                            st.warning("No hay registros para editar.")
                            target_rut = None

                    # 2. Select Training Record
                    if target_rut:
                        user_caps = {k:v for k,v in datos.items() if v.get('RUT') == target_rut}
                        if user_caps:
                            sel_cap_id = st.selectbox(
                                "Seleccionar Capacitación", 
                                options=user_caps.keys(),
                                format_func=lambda k: f"{user_caps[k].get('año_inicio','')} - {user_caps[k].get('NOMBRE_CAPACITACION')} ({user_caps[k].get('HORAS')} hrs)"
                            )
                            
                            # Load Data into Vars
                            rec = user_caps[sel_cap_id]
                            f_id = sel_cap_id
                            f_rut = rec.get('RUT', target_rut)
                            f_nombre = rec.get('NOMBRE_CAPACITACION', '')
                            # f_tipo removed, check ES_POSTGRADO
                            val_post = rec.get('ES_POSTGRADO', 0)
                            f_post = True if str(val_post) == '1' or val_post == 1 else False
                            
                            f_nv = rec.get('NIVEL_TECNICO', 'Medio')
                            f_horas = int(rec.get('HORAS', 0))
                            f_nota = float(rec.get('NOTA', 1.0))
                            f_inst = rec.get('ENTIDAD', '')
                            f_contexto = rec.get('CONTEXTO_PRESS', 'Cambio de Nivel')
                            
                            # Dates
                            try:
                                val_anio = rec.get('AÑO_INICIO', 0)
                                y_start = int(val_anio) if val_anio else datetime.now().year
                            except:
                                y_start = datetime.now().year
                                
                            if y_start < 1900:
                                y_start = datetime.now().year
                            
                            f_inicio = datetime(y_start, 1, 1)
                            
                            f_year_pres = int(rec.get('AÑO_PRESENTACION', datetime.now().year))
                            
                        else:
                            st.info("Este usuario no tiene capacitaciones.")
                            target_rut = None # invalid

                
                # --- FORM ---
                if crud_mode == "Eliminar":
                    if f_id:
                        st.error(f"¿Estás seguro que deseas eliminar: **{f_nombre}**?")
                        if st.button("🚨 Confirmar Eliminación", type="primary"):
                             eliminar_registro_bd('capacitaciones', f_id)
                             puntaje_nv(f_rut)
                             st.success("Registro eliminado.")
                             time.sleep(1.5)
                             st.rerun()
                else:
                    # Create / Edit Form
                    if (crud_mode == "Nuevo") or (crud_mode == "Editar" and f_id):
                        with st.form("form_cap_crud", border=False, clear_on_submit=(crud_mode=="Nuevo")):
                            # We must re-fetch cat for the target rut if Admin changed it
                            cat_user = 'F'
                            if rol_actual in ['ADMIN', 'PROGRAMADOR'] and crud_mode == "Nuevo":
                                # Allow typing RUT for new records
                                f_rut = st.text_input("RUT Funcionario", value=f_rut)
                            else:
                                # Read-only or pre-filled
                                st.text_input("RUT Funcionario", value=f_rut, disabled=True)
                            
                            if not 'reg_users' in locals(): reg_users = leer_registro('usuarios')
                            if reg_users:
                                for u in reg_users.values():
                                    if u.get('RUT') == f_rut:
                                        cat_user = u.get('CATEGORIA', 'F')
                                        break

                            col_a, col_b = st.columns(2)
                            with col_a:
                                nombre = st.text_input("Nombre Capacitación", value=f_nombre)
                                nv_tec = st.selectbox("Nivel Técnico / Pertinencia", ["Bajo", "Medio", "Alto"], index=["Bajo", "Medio", "Alto"].index(f_nv) if f_nv in ["Bajo", "Medio", "Alto"] else 1)
                                is_post = st.checkbox("Es Postgrado", value=f_post, help="Marcar si corresponde a un Diplomado, Postítulo, Magíster o Doctorado.")
                                
                            with col_b:
                                horas = st.number_input("Horas Pedagógicas", min_value=1, value=f_horas)
                                nota = st.number_input("Nota Final", min_value=1.0, max_value=7.0, value=f_nota, step=0.1)
                                inst = st.text_input("Institución (Entidad)", value=f_inst)
                            
                            col_c, col_d = st.columns(2)
                            with col_c:
                                val_y_ini = f_inicio.year if isinstance(f_inicio, datetime) else int(f_inicio)
                                anio_ini_input = st.number_input("Año Inicio", min_value=1980, max_value=2050, value=val_y_ini)
                            with col_d:
                                anio_pres_input = st.number_input("Año Presentación", min_value=1980, max_value=2050, value=f_year_pres)
                            
                            # Context Selector
                            idx_ctx = 0
                            opts_ctx = ["Cambio de Nivel", "Ingreso a Planta"]
                            if f_contexto in opts_ctx: idx_ctx = opts_ctx.index(f_contexto)
                            
                            contexto_sel = st.selectbox(
                                "Contexto de la Capacitación",
                                opts_ctx,
                                index=idx_ctx,
                                help="'Ingreso a Planta' suma puntaje de forma diferenciada. 'Cambio de Nivel' es el estándar."
                            )
                            
                            btn_label = "Guardar Nuevo Registro" if crud_mode == "Nuevo" else "Actualizar Registro"
                            submitted = st.form_submit_button(btn_label, use_container_width=True)
                            
                            if submitted:
                                # Logic for Constructor
                                es_post_val = 1 if is_post else 0
                                tipo_val = "POSTGRADO" if is_post else "CURSO" # Generic infer
                                
                                new_cap = Capacitacion(
                                    rut=f_rut,
                                    cat=cat_user,
                                    nombre_cap=nombre,
                                    entidad=inst,
                                    horas_cap=horas,
                                    nv_tec=nv_tec,
                                    nota=nota,
                                    año_inic=anio_ini_input,
                                    año_pres=anio_pres_input,
                                    cont_press=contexto_sel,
                                    post=es_post_val,
                                    tipo_cap=tipo_val
                                )
                                
                                data_dict = new_cap.crear_dict_capacitacion()
                                
                                if crud_mode == "Nuevo":
                                    ingresar_registro_bd("capacitaciones", data_dict)
                                    st.success("Registro creado exitosamente.")
                                else:
                                    from firebase_bd import actualizar_registro
                                    actualizar_registro("capacitaciones", data_dict, f_id)
                                    st.success("Registro actualizado exitosamente.")
                                
                                puntaje_nv(f_rut)
                                time.sleep(1.5)
                                st.rerun()

        # --- TAB 3: CARGA MASIVA ---
        with tab_objs[2]:
            with st.container(border=True):
                st.markdown("### Importación desde Excel")
                st.info("Sube un archivo .xlsx con las columnas: RUT, AÑO_INICIO, AÑO_PRESENTACION, NOMBRE_CAPACITACION, ENTIDAD, NIVEL_TECNICO, HORAS, NOTA, CONTEXTO_PRESS, ES_POSTGRADO")
                
                uploaded_file = st.file_uploader("Seleccionar archivo", type=["xlsx"])
                
                if uploaded_file:
                    if st.button("Procesar Archivo", type="primary"):
                        with st.spinner("Procesando carga masiva..."):
                            res = carga_masiva(uploaded_file)
                            st.success(res)
                            time.sleep(2)
                            st.rerun()
