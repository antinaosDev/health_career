
import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_bd import leer_registro, ingresar_registro_bd, actualizar_registro, borrar_registro
from clases import Contrato
from funciones import actualizacion_horaria, puntaje_nv, validar_tope_horas

from datetime import datetime
import time

from modules.ui import render_header

def app():
    render_header()
    st.markdown("## 📄 Gestión de Contratos")
    
    rut_actual = st.session_state["usuario_rut"]
    rol_actual = st.session_state["usuario_rol"]

    contratos_dict = leer_registro('contrato')
    
    lista_contratos = []
    if rol_actual in ['ADMIN', 'PROGRAMADOR']:
        for k, v in contratos_dict.items():
            v['ID_BD'] = k 
            lista_contratos.append(v)
    else:
        for k, v in contratos_dict.items():
            if v.get('RUT') == rut_actual:
                v['ID_BD'] = k
                lista_contratos.append(v)
                
    df = pd.DataFrame(lista_contratos)
    
    # --- METRICS SECTION (Ludic) ---
    st.markdown("### 📊 Tablero de Contratos")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Contratos", len(df), "Activos")
        hrs_tot = df['HORAS'].astype(float).sum() if 'HORAS' in df.columns else 0
        c2.metric("Hora Totales", f"{hrs_tot} hrs", "Semanales")
        
        # Charts
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            with st.container(border=True):
                st.markdown("**Tipo de Contrato**")
                if 'TIPO_CONTRATO' in df.columns:
                    fig_tipo = px.pie(df, names='TIPO_CONTRATO', hole=0.5, height=250)
                    st.plotly_chart(fig_tipo, width="stretch")
        with c_chart2:
             with st.container(border=True):
                 st.markdown("**Cargos**")
                 if 'CARGO' in df.columns:
                     fig_cargo = px.bar(df['CARGO'].value_counts().reset_index(), x='CARGO', y='count', height=250)
                     st.plotly_chart(fig_cargo, width="stretch")

    else:
        st.info("No hay datos para estadisticas.")

    st.divider()

    # Permissions
    can_edit = rol_actual in ['ADMIN', 'PROGRAMADOR']
    
    tabs = ["📋 Listado General"]
    if can_edit:
        tabs.append("✏️ Editor / Gestión")
        
    tab_objs = st.tabs(tabs)
    
    with tab_objs[0]:
        with st.container(border=True):
            if not df.empty:
                cols = ['RUT', 'TIPO_CONTRATO', 'CARGO', 'HORAS', 'FECHA_INICIO', 'FECHA_TERMINO']
                cols = [c for c in cols if c in df.columns]
                st.dataframe(
                    df[cols], 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "RUT": st.column_config.TextColumn("RUT"),
                        "HORAS": st.column_config.NumberColumn("Horas", format="%d hrs"),
                        "FECHA_INICIO": st.column_config.TextColumn("Inicio"), # Kept as text as it comes dd/mm/yyyy string
                        "FECHA_TERMINO": st.column_config.TextColumn("Término"),
                    }
                )
            else:
                st.info("No hay contratos registrados.")

    if can_edit:
        with tab_objs[1]:
            with st.container(border=True):
                col_act, col_sel = st.columns([1, 2])
            
            with col_act:
                modo = st.radio("Acción", ["Nuevo Contrato", "Editar Existente", "Eliminar"], label_visibility="collapsed")
            
            selected_data = {}
            id_sel = None
            
            with col_sel:
                if modo != "Nuevo Contrato":
                    if df.empty:
                        st.warning("No hay datos")
                    else:
                        opts = df.apply(lambda x: f"{x['RUT']} - {x['CARGO']} ({x.get('FECHA_INICIO', 'S/F')})", axis=1).tolist()
                        sel_text = st.selectbox("Seleccionar", opts)
                        try:
                            idx = opts.index(sel_text)
                            selected_data = df.iloc[idx].to_dict()
                            id_sel = selected_data['ID_BD']
                        except: pass

            st.divider()
            
            # --- ACTION LOGIC ---
            if modo == "Eliminar":
                st.markdown("### 🗑️ Eliminar Contrato")
                if id_sel:
                    st.error(f"¿Estás seguro que deseas eliminar el contrato de **{selected_data.get('RUT','')}** - **{selected_data.get('CARGO','')}**?")
                    st.warning("Esta acción no se puede deshacer.")
                    
                    if st.button("🚨 CONFIRMAR ELIMINACIÓN", type="primary"):
                         borrar_registro('contrato', id_sel)
                         st.success("Contrato eliminado.")
                         time.sleep(1.5)
                         st.rerun()
                else:
                    st.info("Selecciona un contrato en el paso anterior para eliminarlo.")

            else:
                # --- CREATE / EDIT FORM ---
                
                # MOVED OUTSIDE FORM for interactivity
                c_conf1, c_conf2 = st.columns(2)
                idx_tipo = 0
                opts_tipo = ["Plazo Fijo", "Planta", "Honorario"]
                
                curr_tipo = selected_data.get('TIPO_CONTRATO', 'Plazo Fijo')
                if curr_tipo in opts_tipo:
                    idx_tipo = opts_tipo.index(curr_tipo)
                    
                with c_conf1:
                    tipo = st.selectbox("Tipo de Contrato", opts_tipo, index=idx_tipo)
                
                with st.form("form_contrato_pro", border=False):
                    # Parse Dates helper
                    def parse_date(date_str):
                        try:
                            return datetime.strptime(date_str, "%d/%m/%Y")
                        except:
                            return datetime.now()

                    c1, c2 = st.columns(2)
                    def_rut = selected_data.get('RUT', rut_actual if rol_actual not in ['ADMIN', 'PROGRAMADOR'] else '')
                    rut_in = c1.text_input("RUT", value=def_rut, disabled=(rol_actual not in ['ADMIN', 'PROGRAMADOR']))
                    cargo = c2.text_input("Cargo", value=selected_data.get('CARGO', ''))
                    
                    c3, c4 = st.columns(2)
                    # Tipo is now outside.
                    horas = c3.number_input("Horas Semanales", 0, 44, int(selected_data.get('HORAS', 44)))
                    # Spacer or other field
                    opts_dep = ["CESFAM CHOLCHOL", "PSR HUENTELAR", "PSR MALALCHE", "PSR HUAMAQUI", "SALUD APS", "OTRO"]
                    curr_dep = selected_data.get('DEPENDENCIA', 'CESFAM CHOLCHOL')
                    idx_dep = opts_dep.index(curr_dep) if curr_dep in opts_dep else 5 # Default to OTRO if not found, or 0 if preferred. User didn't specify default. Let's default to CESFAM CHOLCHOL (0) if matches, or OTRO? Actually let's assume if it's new it's index 0. If existing and not in list, maybe 'OTRO' or just index 0. I'll stick to a safe default.
                    if curr_dep not in opts_dep and curr_dep:
                         # If current value is weird, maybe show it? No, user wants restricted list.
                         idx_dep = 0 
                    
                    dep = c4.selectbox("Dependencia", opts_dep, index=idx_dep)

                    c5, c6 = st.columns(2)
                    # dep moved to c4
                    reemplazo_val = c5.selectbox("Reemplazo", ["NO", "SI"], index=0 if selected_data.get('REEMPLAZO', 'NO') != "SI" else 1)
                    
                    # DATE LOGIC
                    default_ini = parse_date(selected_data.get('FECHA_INICIO', ''))
                    fe_inicio = c6.date_input("Fecha Inicio", value=default_ini)
                    
                    c7, c8 = st.columns(2)
                    nom_inst = c7.text_input("Nombre Institución", value=selected_data.get('NOMBRE_INSTITUCION', ''))
                    
                    # Termino Logic conditional
                    fe_termino = None
                    if tipo == "Planta":
                        c8.info("ℹ️ Contrato Planta: Sin fecha de término.")
                    else:
                        default_ter = parse_date(selected_data.get('FECHA_TERMINO', ''))
                        fe_termino = c8.date_input("Fecha Término", value=default_ter)

                    
                    # nom_inst moved to c7
                    
                    idx_inst = 0
                    opts_inst = ["Pública", "Privada"]
                    curr_inst = selected_data.get('TIPO_INSTITUCION', 'Pública')
                    if curr_inst in opts_inst:
                        idx_inst = opts_inst.index(curr_inst)
                        
                        
                    tipo_inst = st.selectbox("Tipo Institución", opts_inst, index=idx_inst)

                    btn_text = "Crear Contrato" if modo == "Nuevo Contrato" else "Actualizar Contrato"
                    submitted = st.form_submit_button(btn_text, use_container_width=True)
                    
                    if submitted:
                        # Normalize RUT (Auto-add hyphen if missing, Force Uppercase)
                        rut_clean = str(rut_in).replace(".", "").strip().upper()
                        if "-" not in rut_clean and len(rut_clean) > 1:
                             rut_clean = f"{rut_clean[:-1]}-{rut_clean[-1]}"
                        rut_in = rut_clean

                        # --- HOURS VALIDATION ---
                        id_ignore = id_sel if modo != "Nuevo Contrato" else None
                        es_valido, total_h = validar_tope_horas(rut_in, horas, tipo, id_contrato_ignorar=id_ignore)
                        
                        if not es_valido:
                            st.error(f"⚠️ Error: El tope de horas (Planta + Plazo Fijo) es 44. Total proyectado: {total_h} hrs.")
                            st.stop()
                        # ------------------------

                        # Create Object
                        # Handle Termino Date
                        if fe_termino:
                            dt, mt, yt = fe_termino.day, fe_termino.month, fe_termino.year
                        else:
                            dt, mt, yt = 0, 0, 0

                        nuevo_contrato = Contrato(
                            rut=rut_in,
                            tipo_cont=tipo,
                            horas_cont=horas,
                            dependencia=dep,
                            cargo=cargo,
                            reemplazo=reemplazo_val,
                            inst=tipo_inst,
                            nom_inst=nom_inst,
                            dia_inic=fe_inicio.day, mes_inic=fe_inicio.month, año_inic=fe_inicio.year,
                            dia_ter=dt, mes_ter=mt, año_ter=yt
                        )
                        
                        data_dict = nuevo_contrato.crear_dict_contrato()
                        
                        if modo == "Nuevo Contrato":
                            ingresar_registro_bd("contrato", data_dict)
                            st.success("Contrato creado exitosamente.")
                            time.sleep(1.5)
                        else:
                            if id_sel:
                                actualizar_registro("contrato", data_dict, id_sel)
                                st.success("Contrato actualizado exitosamente.")
                            else:
                                st.error("Error: ID no encontrado para actualizar.")
                        
                        time.sleep(1.5)
                        st.rerun()
