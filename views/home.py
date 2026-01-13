
import streamlit as st
from firebase_bd import leer_registro
from funciones import porcentaje_postgrado, calculo_años, actualizacion_horaria, puntaje_nv
from indices import indices_niveles
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from collections import defaultdict
from datetime import datetime

def format_clp(value):
    try:
        if isinstance(value, str):
            # Clean string like '$ 500.000' -> 500000
            value = float(value.replace(',', '').replace('$', '').replace('.','').strip())
        return f"${int(value):,}".replace(",", ".")
    except:
        return "$0"

# --- Custom Native Metric Component ---
def custom_metric(label, value, icon, help_text=""):
    with st.container(border=True):
        c1, c2 = st.columns([1, 4])
        with c1:
            st.markdown(f"<div style='font-size: 28px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<p style='color: #666; font-size: 13px; margin:0;'>{label}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #006DB6; font-size: 20px; font-weight: bold; margin:0;' title='{help_text}'>{value}</p>", unsafe_allow_html=True)

def get_cap_status_message(cat_limit_global, planta, arrastre, breakdown_data):
    # Calculate Used Points
    # Used = Planta + Arrastre + Sum(min(Real, AnnualLimit))
    # Note: breakdown_data has 'DIFERENCIA'. 
    # If DIFERENCIA > 0 (Surplus) -> Real > Limit ->Contribution is Limit.
    # If DIFERENCIA <= 0 (Deficit) -> Real <= Limit -> Contribution is Real (Limit + Diff).
    
    annual_contrib = 0
    for row in breakdown_data:
        diff = row.get('DIFERENCIA', 0)
        limit = row.get('LIMITE', 0)
        
        if diff > 0:
            annual_contrib += limit
        else:
            annual_contrib += (limit + diff)
            
    total_used = planta + arrastre + annual_contrib
    remaining = cat_limit_global - total_used
    
    if remaining <= 0:
        return "⚠️ **TOPE ALCANZADO**: Has completado tu cupo de puntaje por capacitación. Solo puedes aumentar tu puntaje mediante Bienios.", total_used, 0
    else:
        return f"✅ **Cupo Disponible**: Te quedan **{remaining:.1f} puntos** para llegar al tope de tu categoría ({cat_limit_global}).", total_used, remaining

def get_dashboard_data(rut):
    users = leer_registro('usuarios')
    caps = leer_registro('capacitaciones')
    conts = leer_registro('contrato')
    
    user_data = next((u for u in users.values() if u.get('RUT') == rut), None)
    if not user_data: return None

    # Logic
    user_caps = [c for c in caps.values() if c.get('RUT') == rut]
    user_conts = [c for c in conts.values() if c.get('RUT') == rut]

    calificaciones = [c.get('NOTA') for c in user_caps]
    try: prom_calif = round(sum(calificaciones)/len(calificaciones), 1) if calificaciones else 0
    except: prom_calif = 0
    
    horas_cap = [c.get('HORAS') for c in user_caps if c.get('ES_POSTGRADO') == 'SI']
    porcentaje_asig = porcentaje_postgrado(sum(horas_cap), rut)
    
    nivel = user_data.get('NIVEL')
    cat = user_data.get('CATEGORIA')
    pje_g = user_data.get('PTJE_CARR', 0)
    
    # NEW: Read Pre-Calculated Breakdown from DB
    breakdown_data = []
    summary_pts = {}
    cat_limit = 150 if cat in ['A', 'B'] else 117
    
    import json
    if user_data.get('DETALLE_CALCULO'):
        try:
            detail = json.loads(user_data.get('DETALLE_CALCULO'))
            # RICH TRACE MODE (New format)
            raw_anios = detail.get('anios', [])
            
            # Check if it's the new format (dict) or old (list)
            # New format: [{'AÑO':..., 'PUNTOS_REALES':...}]
            # Old format: [[2023, 0], [2024, -20]]
            
            if raw_anios and isinstance(raw_anios[0], dict):
                 breakdown_data = raw_anios
            elif raw_anios and isinstance(raw_anios[0], list):
                 # Fallback for old data until recalculated
                 for year, final_diff in raw_anios:
                     breakdown_data.append({
                         'AÑO': year,
                         'PUNTOS_REALES': 0, # Unknown
                         'LIMITE': detail.get('limite_anual', cat_limit),
                         'DIFERENCIA': final_diff,
                         'SALDO_USADO': 0,
                         'SALDO_GENERADO': 0,
                         'SALDO_ACUMULADO': 0
                     })

            summary_pts = {
                'ARRASTRE_PTS': detail.get('arrastre', 0),
                'BASE_PLANTA': detail.get('base_planta', 0),
                'VALOR_BIENIOS': detail.get('valor_bienios', 0)
            }
            cat_limit = detail.get('limite_anual', cat_limit)
            
        except Exception as e:
            print(f"Error parsing detail: {e}")

    # Fallback to legacy Diff Calc for UI top-right metric
    dif = 0
    for idl, nv in indices_niveles.items():
        if cat in idl:
            for r, val in nv.items():
                if val == nivel:
                   dif = r[1] + 1 - pje_g
                   break

    return {
        "user": user_data,
        "prom_notas": prom_calif,
        "porc_asig": porcentaje_asig,
        "dif_puntos": dif,
        "total_horas_caps": sum(c.get('HORAS', 0) for c in user_caps),
        "total_caps": len(user_caps),
        "caps_raw": user_caps,
        "conts_raw": user_conts,
        "breakdown": breakdown_data,
        "summary": summary_pts, # Pass summary
        "summary": summary_pts, # Pass summary
        "cat_limit_global": 4500 if cat in ['A', 'B'] else 3500,
        "cat_limit": cat_limit
    }

# --- Plotly Theme Colors ---
COLOR_PRIMARY = "#006DB6"
COLOR_SECONDARY = "#42A5F5"
COLOR_ACCENT = "#FF9800"

def plot_horas_por_anio(caps_list):
    data = defaultdict(int)
    for c in caps_list:
        anio = c.get('AÑO_PRESENTACION')
        if anio: data[anio] += c.get('HORAS', 0)
    if not data: return None
    labels, values = list(data.keys()), list(data.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
    fig.update_traces(marker=dict(colors=px.colors.sequential.Blues_r))
    fig.update_layout(title="Horas por Año", template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
    return fig

def plot_contratos_tipo(conts_list):
    data = defaultdict(int)
    for c in conts_list:
        tipo = c.get('TIPO_CONTRATO', 'Desconocido')
        data[tipo] += 1
    if not data: return None
    fig = px.pie(names=list(data.keys()), values=list(data.values()), title="Tipos de Contrato", hole=0.4)
    fig.update_traces(marker=dict(colors=px.colors.qualitative.Prism))
    fig.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
    return fig

def plot_horas_nivel(caps_list):
    data = defaultdict(int)
    for c in caps_list:
        nv = c.get('NIVEL_TECNICO', 'Sin Clasificar')
        data[nv] += c.get('HORAS', 0)
    if not data: return None
    df = pd.DataFrame(list(data.items()), columns=['Nivel', 'Horas'])
    fig = px.bar(df, x='Nivel', y='Horas', title="Horas por Nivel Técnico", color='Horas', color_continuous_scale='Blues')
    fig.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
    return fig

def plot_horas_bienio(caps_list):
    data = defaultdict(int)
    for c in caps_list:
        try:
            anio = int(c.get('AÑO_PRESENTACION'))
            bienio_start = (anio // 2) * 2
            bienio_label = f"{bienio_start}-{bienio_start+1}"
            data[bienio_label] += c.get('HORAS', 0)
        except: pass
    if not data: return None
    df = pd.DataFrame(list(data.items()), columns=['Bienio', 'Horas']).sort_values('Bienio')
    fig = px.line(df, x='Bienio', y='Horas', title="Progresión por Bienios", markers=True)
    fig.update_traces(line_color=COLOR_ACCENT)
    fig.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
    return fig

def app():
    st.markdown("## 📊 Dashboard Integral del Funcionario")
    
    # --- Guía de Orientación ---
    with st.expander("ℹ️ GUÍA DE ORIENTACIÓN: ¿Cómo leer este tablero?"):
        st.markdown("""
        **Bienvenido a su portal de carrera funcionaria.** Aquí encontrará toda la información relevante de su trayectoria.
        
        1.  **Indicadores Clave**: En la parte superior verá su Nivel, Puntaje y lo que le falta para subir.
        2.  **Análisis de Contratos**: Revise cuántos contratos tiene vigentes y su distribución horaria.
        3.  **Capacitaciones**: Gráficos detallados sobre sus cursos, agrupados por nivel técnico y períodos (bienios).
        4.  **Historial**: Tabla detallada al final con todas sus actividades registradas.
        """)

    rut_actual = st.session_state["usuario_rut"]
    rol = st.session_state["usuario_rol"]

    if rol in ["PROGRAMADOR", "ADMIN"]:
        users = leer_registro('usuarios')
        conts = leer_registro('contrato')
        # Filter: Exclude users who ONLY have Honorario contracts.
        # Logic: effective_users are those with at least one 'Planta' or 'Plazo Fijo' (or just NOT 'Honorario' exclusively).
        valid_ruts = set()
        for c in conts.values():
            if str(c.get('TIPO_CONTRATO', '')).strip().upper() != 'HONORARIO':
                valid_ruts.add(str(c.get('RUT', '')).replace('.', '').strip())
        
        # Create options only for valid ruts
        user_opts = {
            u.get('RUT'): f"{u.get('NOMBRE_FUNC')} ({u.get('RUT')})" 
            for u in users.values() 
            if str(u.get('RUT', '')).replace('.', '').strip() in valid_ruts
        }
        
        rut_target = st.selectbox("Seleccionar Funcionario", options=list(user_opts.keys()), format_func=lambda x: user_opts[x])
    else:
        rut_target = rut_actual

    data = get_dashboard_data(rut_target)
    if not data:
        st.error(f"No se encontraron datos para el RUT: {rut_target}")
        return

    # --- PENDING LEVEL NOTIFICATION ---

    # --- PENDING LEVEL NOTIFICATION ---
    pending_lvl = data['user'].get('NIVEL_PENDIENTE')
    if pending_lvl:
        st.warning(f"⚠️ **ESTADO DE CARRERA:** Usted ha alcanzado los requisitos para ascender al **Nivel {pending_lvl}**. Este cambio se encuentra **Pendiente de Aprobación** por parte de Administración. Sus datos actuales (Nivel {data['user'].get('NIVEL')}) se mantendrán vigentes hasta la autorización.")

    # --- SCORE EXPLANATION & BREAKDOWN (NEW) ---
    # --- CAP STATUS CALCULATION (Moved out for visibility/scope) ---
    cap_global = data.get('cat_limit_global', 3500)
    # breakdown_data already loaded in data['breakdown']
    summ = data.get('summary', {})
    arrastre_val = summ.get('ARRASTRE_PTS', 0)
    planta_val = summ.get('BASE_PLANTA', 0)
    
    msg_status, used_pts, rem_pts = get_cap_status_message(cap_global, planta_val, arrastre_val, data.get('breakdown', []))

    # --- SCORE EXPLANATION & BREAKDOWN ---
    with st.expander("📐 Explicación Detallada del Cálculo de Puntaje", expanded=True):
        st.info(f"**Tu Categoría es {data['user'].get('CATEGORIA')}, por lo tanto tu límite anual es de {data.get('cat_limit', 0)} puntos.**")
        
        c_exp1, c_exp2 = st.columns([1, 1])
        with c_exp1:
            st.markdown("""
            **¿Cómo funciona tu saldo?**
            - Si en un año haces **más puntos** que tu límite, el excedente se guarda en tu **Saldo**.
            - Si en un año haces **menos puntos**, el sistema usa tu Saldo acumulado para completar la meta.
            """)
        with c_exp2:
             st.markdown("""
            **Componentes del Puntaje Total:**
            1. **Puntaje Base**: Bienios.
            2. **Puntaje Sujeto a Tope Global**: Ingreso a Planta + Cambio de Nivel + Arrastre.
            3. **Tope Global**: 4.500 (A/B) o 3.500 (C-F).
            """)
            
        st.markdown("##### 📅 Desglose Anual de Puntos y Saldo")
        st.caption("Esta tabla muestra cómo se han asignado tus puntos año a año, respetando el límite anual y usando tu saldo histórico.")
        
        breakdown = data.get('breakdown', [])
        if breakdown:
            df_bd = pd.DataFrame(breakdown)
            df_bd = df_bd[['AÑO', 'PUNTOS_REALES', 'LIMITE', 'DIFERENCIA', 'SALDO_USADO', 'SALDO_GENERADO', 'SALDO_ACUMULADO']]
            df_bd.columns = ['Año', 'Pts. Cursos', 'Tope Anual', 'Déficit/Exceso', 'Saldo Usado', 'Saldo Generado', 'Saldo Final']
            st.dataframe(df_bd, use_container_width=True, hide_index=True)
        else:
            st.info("No se registran movimientos anuales de capacitación (ingresos o défitics) para el desglose.")

        # --- ARRASTRE & BASE DISPLAY ---
        planta = planta_val
        bienios_val = summ.get('VALOR_BIENIOS', 0)
        
        st.markdown("---")
        st.markdown("**Resumen de Componentes Base:**")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Ingreso a Planta", f"{planta:,.1f}")
        col_s2.metric("Arrastre (Histórico)", f"{arrastre_val:,.1f}")
        col_s3.metric("Bienios (Antigüedad)", f"{bienios_val:,.1f}")
        
        if arrastre_val > 0:
            st.caption(f"✅ Tu puntaje incluye **{arrastre_val} puntos** históricos (Arrastre) que se suman a tu base de cálculo.")
    
    # --- GLOBAL CAP STATUS DISPLAY (Now visible outside expander) ---
    st.markdown("### 🚦 Estado del Tope Global")
    if rem_pts <= 0:
         st.warning(msg_status)
    else:
         st.success(msg_status)
    
    # Progress Bar
    progress = min(1.0, max(0.0, used_pts / cap_global))
    st.progress(progress, text=f"Progreso Tope: {used_pts:.1f} / {cap_global} Used")

    data = get_dashboard_data(rut_target)
    if not data: 
        st.warning("No se encontraron datos.")
        return
    ud = data['user']

    # --- Metrics Row ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: custom_metric("Nivel Carrera", str(ud.get('NIVEL')), "🏆", "Nivel actual en la carrera funcionaria")
    with c2: custom_metric("Puntaje Total", f"{ud.get('PTJE_CARR', 0):.2f}", "⭐", "Puntaje acumulado histórico")
    with c3: custom_metric("Meta Próx. Nivel", f"{data['dif_puntos']:.2f}", "🎯", "Puntos faltantes para el siguiente nivel")
    with c4: custom_metric("Saldo Actual", f"{ud.get('SALDO_PTJE', 0):.2f}", "💰", "Puntaje disponible para uso")

    # --- Bio ---
    c_left, c_right = st.columns([1, 2])
    with c_left:
        with st.container(border=True):
            st.markdown("### 👤 Perfil")
            st.markdown(f"**{ud.get('NOMBRE_FUNC')}**")
            st.caption(f"RUT: {ud.get('RUT')}")
            
            # --- MANUAL RECALCULATE BUTTON REMOVED (Replaced by Auto-Correction) ---
            # if st.button("🔄 Actualizar Datos", type="primary", help="Recalcular puntajes y bienios ahora"):
            #    ...
            
            st.divider()
            # Calc Next Bienio
            fecha_prox_bienio = "Desconocida"
            dias_para_bienio = ""
            
            # Find earliest start date
            fechas = []
            for c in data['conts_raw']:
                try: 
                    fechas.append(datetime.strptime(c.get('FECHA_INICIO'), "%d/%m/%Y"))
                except: pass
            
            if fechas:
                earliest = min(fechas)
                
                # Calculate Bienios using OFFICAL LOGIC (Just for display prediction)
                antiguedad_real = calculo_años(earliest.strftime("%d/%m/%Y"))
                bienios_calc = antiguedad_real // 2
                
                # Next bienio milestone in years
                next_milestone_years = (bienios_calc + 1) * 2
                
                # Add years to earliest date
                try:
                    target_date = earliest.replace(year=earliest.year + next_milestone_years)
                except ValueError: 
                    target_date = earliest.replace(year=earliest.year + next_milestone_years, day=1, month=3)
                
                fecha_prox_bienio = target_date.strftime("%d/%m/%Y")
                now = datetime.now()
                days_left = (target_date - now).days
                
                if days_left < 0:
                     dias_para_bienio = f"(Alcanzado hace {-days_left} días)"
                else:
                     dias_para_bienio = f"(faltan {days_left} días)"
                    


            from funciones import calculate_detailed_seniority
            y_det, m_det, d_det = calculate_detailed_seniority(data['conts_raw'])
            
            st.markdown(f"**Categoría:** {ud.get('CATEGORIA')} | **Bienios:** {ud.get('BIENIOS')}")
            st.markdown(f"**Antigüedad Total:** {y_det} años, {m_det} meses")
            st.markdown(f"📅 **Próximo Bienio:** {fecha_prox_bienio} <span style='color: #666; font-size: 0.85em;'>{dias_para_bienio}</span>", unsafe_allow_html=True)
            
            st.markdown(f"**Edad:** {ud.get('EDAD')} años")
            
            # Sueldo Base + APS Calculation
            sueldo_base_val = 0
            raw_sb = ud.get('SUELDO_BASE', '0')
            try:
                # Clean format points/commas
                clean_sb = str(raw_sb).replace('.', '').replace(',', '').replace('$', '').strip()
                sueldo_base_val = float(clean_sb)
            except:
                pass
            
            sueldo_aps = sueldo_base_val * 2
            st.markdown(f"**Sueldo Base + APS:** {format_clp(sueldo_aps)}")
            st.caption(f"(Base: {format_clp(sueldo_base_val)})")
            st.info(f"Promedio Notas: {data['prom_notas']}")

            st.markdown("---")
            # PDF Generation
            try:
                from modules.pdf_gen import create_pdf
                import os
                
                # Prepare Extra Info for PDF
                extra_info = {
                    "prox_bienio": f"{fecha_prox_bienio} {dias_para_bienio}",
                    "meta_puntos": data.get('dif_puntos', 0),
                    "cap_status_msg": msg_status, # Pass status
                    "cap_used": used_pts,
                    "cap_global": cap_global,
                    "antiguedad_real": {'y': y_det, 'm': m_det}
                }
                
                # Check Logo
                logo_path = os.path.abspath("logo_app_carr.png")
                logo_company_path = os.path.abspath("logo_alain.png") 
                
                if st.button("📄 Generar Reporte PDF"):
                    with st.spinner("Actualizando datos y generando documento..."):
                         # --- 0. FORCE DATA UPDATE (User Request) ---
                         try:
                             # We use the specific user's RUT (rut_target)
                             # Fetches fresh data for update
                             ud_db = leer_registro('usuarios')
                             ct_db = leer_registro('contrato')
                             cp_db = leer_registro('capacitaciones')
                             
                             # Single User Update
                             # This updates DB and local dicts in-place
                             actualizacion_horaria(st.session_state["usuario_rol"], ud_db, ct_db, rut_target)
                             puntaje_nv(rut_target, cp_db, ud_db, ct_db)
                             
                             # RE-FETCH FOR DISPLAY/PDF
                             # We need to refresh the 'data' and 'ud' variables used below
                             data = get_dashboard_data(rut_target)
                             ud = data['user']
                             
                         except Exception as e:
                             print(f"Error updating before PDF: {e}")
                             st.error("No se pudieron actualizar los datos recientes, generando con datos actuales...")

                         # --- 1. GENERATE CHARTS FOR PDF ---
                         chart_paths = {}
                         temp_files = []
                         try:
                             # Re-generate figures for export (or access if scope allowed, but safer to re-call plot funcs)
                             # We use the functions defined above: plot_horas_nivel, etc.
                             # Note: We must use NEW 'data' from re-fetch
                             
                             charts_map = {
                                 'nivel': plot_horas_nivel(data['caps_raw']),
                                 'bienio': plot_horas_bienio(data['caps_raw']),
                                 'year': plot_horas_por_anio(data['caps_raw']),
                                 'contrato': plot_contratos_tipo(data['conts_raw'])
                             }
                             
                             for key, fig in charts_map.items():
                                 if fig:
                                     fname = f"temp_home_{key}.png"
                                     # Update layout for print
                                     fig.update_layout(width=500, height=350, title_font_size=16)
                                     try:
                                         fig.write_image(fname, scale=2) # Requires kaleido
                                         chart_paths[key] = os.path.abspath(fname)
                                         temp_files.append(fname)
                                     except Exception as e:
                                         print(f"Chart gen error {key}: {e}")
                                         
                         except Exception as e:
                             st.warning(f"No se pudieron generar gráficos para el PDF: {e}")

                         # --- 2. GENERATE PDF ---
                         # Now passing contracts (data['conts_raw']) and extra_info AND chart_paths
                         pdf_bytes = create_pdf(
                             ud, 
                             data['caps_raw'], 
                             data['conts_raw'], 
                             extra_info, 
                             logo_path, 
                             logo_company_path,
                             chart_paths,
                             breakdown_data=data.get('breakdown'),
                             summary_dict=data.get('summary')
                         )
                         
                         # --- 3. CLEANUP ---
                         for f in temp_files:
                             if os.path.exists(f): os.remove(f)
                         
                         st.download_button(
                             label="⬇️ Descargar PDF",
                             data=pdf_bytes,
                             file_name=f"Reporte_Carrera_{ud.get('RUT')}.pdf",
                             mime="application/pdf",
                             key="pdf_download_btn"
                         )

            except ImportError:
                 st.warning("Librería 'fpdf' no instalada. No se puede generar PDF.")
            except Exception as e:
                 st.error(f"Error al generar PDF: {e}")

    # --- Contract Analysis ---
    with c_right:
        with st.container(border=True):
            st.markdown("### 📄 Análisis de Contratos")
            cc1, cc2 = st.columns(2)
            total_horas_cont = sum(int(c.get('HORAS',0)) for c in data['conts_raw'])
            with cc1:
                st.metric("Total Horas Contratadas", f"{total_horas_cont} hrs")
                st.metric("Cantidad Contratos", len(data['conts_raw']))
                
                st.markdown("---")
                st.caption("Detalle de Vigencia")
                for c in data['conts_raw']:
                    inicio = c.get('FECHA_INICIO', 'S/I')
                    termino = c.get('FECHA_TERMINO')
                    tipo = c.get('TIPO_CONTRATO', 'Otro')
                    
                    st.markdown(f"**• {tipo}**")
                    st.markdown(f"📅 Inicio: `{inicio}`")
                    
                    if termino and tipo != 'Planta':
                        try:
                            # Parse dates (assuming dd/mm/yyyy from firebase)
                            f_term = datetime.strptime(termino, "%d/%m/%Y").date()
                            f_now = datetime.now().date()
                            dias = (f_term - f_now).days
                            
                            color = "#e53935" if dias < 30 else "#fb8c00" if dias < 90 else "#43a047"
                            
                            if dias < 0:
                                label_dias = f"Vencido hace {abs(dias)} días"
                                st.markdown(f"⏳ Termina: `{termino}`")
                                st.markdown(f"<span style='color:{color}; font-weight:bold; background: #ffebee; padding: 2px 5px; border-radius: 4px;'>⚠️ {label_dias}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"⏳ Termina: `{termino}`")
                                st.markdown(f"<span style='color:{color}; font-weight:bold; background: #e8f5e9; padding: 2px 5px; border-radius: 4px;'>✅ Quedan {dias} días</span>", unsafe_allow_html=True)
                        except:
                            st.markdown(f"⏳ Termina: `{termino}`")
                    
                    st.markdown("<br>", unsafe_allow_html=True)

            with cc2:
                fig_cont = plot_contratos_tipo(data['conts_raw'])
                if fig_cont: st.plotly_chart(fig_cont, width="stretch")
                else: st.info("Sin contratos registrados")

    # --- Training Deep Dive ---
    st.markdown("### 🎓 Análisis Profundo de Capacitaciones")
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        with st.container(border=True):
            st.markdown("**Por Nivel Técnico**")
            fig_nv = plot_horas_nivel(data['caps_raw'])
            if fig_nv: st.plotly_chart(fig_nv, width="stretch")
            else: st.caption("Sin datos")
            
    with col_t2:
        with st.container(border=True):
            st.markdown("**Por Bienios**")
            fig_bi = plot_horas_bienio(data['caps_raw'])
            if fig_bi: st.plotly_chart(fig_bi, width="stretch")
            else: st.caption("Sin datos")

    with col_t3:
        with st.container(border=True):
            st.markdown("**Por Año**")
            fig_yr = plot_horas_por_anio(data['caps_raw'])
            if fig_yr: st.plotly_chart(fig_yr, width="stretch")
            else: st.caption("Sin datos")

    # --- Detailed Table ---
    st.markdown("### 🧾 Historial Detallado")
    if data['caps_raw']:
        df = pd.DataFrame(data['caps_raw'])
        
        # FIX: Force string types for PyArrow compatibility
        text_cols = ['NOMBRE_CAPACITACION', 'ENTIDAD', 'AÑO_PRESENTACION', 'NIVEL_TECNICO']
        for c in text_cols:
            if c in df.columns:
                df[c] = df[c].astype(str)

        cols = ['NOMBRE_CAPACITACION', 'ENTIDAD', 'AÑO_PRESENTACION', 'CONTEXTO_PRESS', 'HORAS', 'NOTA', 'PJE_POND', 'NIVEL_TECNICO']
        cols = [c for c in cols if c in df.columns]
        
        st.dataframe(
            df[cols],
            hide_index=True,
            use_container_width=True,
            column_config={
                "NOMBRE_CAPACITACION": st.column_config.TextColumn("Capacitación", width="large"),
                "ENTIDAD": st.column_config.TextColumn("Entidad"),
                "NOTA": st.column_config.ProgressColumn("Nota", min_value=1, max_value=7, format="%.1f"),
                "PJE_POND": st.column_config.NumberColumn("Puntaje", format="%.2f"),
                "HORAS": st.column_config.NumberColumn("Horas", format="%d h"),
                "AÑO_PRESENTACION": st.column_config.TextColumn("Año"),
                "CONTEXTO_PRESS": st.column_config.TextColumn("Contexto"),
                "NIVEL_TECNICO": st.column_config.TextColumn("Nivel"),
            },
        )

