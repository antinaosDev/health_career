import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from firebase_bd import leer_registro
from indices import indices_niveles, sueldos_reajustados_2025
from datetime import datetime
import time

def format_clp(value):
    try:
        return f"${int(value):,}".replace(",", ".")
    except:
        return "$0"

def format_score(value):
    try:
        # Chilean format: 1.234,56
        return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

def get_salary_for_level(category, level):
    try:
        lvl_data = sueldos_reajustados_2025.get(level)
        if lvl_data:
            return lvl_data.get(category, 0)
    except:
        return 0
    return 0

def calculate_level_from_points(category, points):
    final_lvl = 15 
    for cats, levels_map in indices_niveles.items():
        if category in cats:
            for r, lvl in levels_map.items():
                if r[0] <= points <= r[1]:
                    final_lvl = lvl
                    break
    return final_lvl

def get_days_to_bienio(rut, current_bienios, df_conts):
    user_conts = df_conts[df_conts['RUT'] == rut]
    if user_conts.empty: return None
    
    dates = []
    for _, c in user_conts.iterrows():
        try: dates.append(datetime.strptime(c.get('FECHA_INICIO'), "%d/%m/%Y"))
        except: pass
        
    if not dates: return None
    earliest = min(dates)
    
    next_years = (int(current_bienios) + 1) * 2
    try:
        target = earliest.replace(year=earliest.year + next_years)
    except ValueError:
        target = earliest.replace(year=earliest.year + next_years, day=1, month=3)
        
    return (target.date() - datetime.now().date()).days

def app():
    st.markdown("## 📊 Panel de Gestión Global")
    st.markdown("Visión general del estado de la dotación y costos.")
    st.divider()

    # --- PROGRAMMER SECTION: USER MANAGEMENT ---
    if st.session_state.get("usuario_rol") == "PROGRAMADOR":
        with st.expander("👤 Gestión de Usuarios - Login (Solo Programador)", expanded=False):
            st.info("Administración de usuarios de acceso (Tabla 'login').")
            
            tab_create, tab_manage = st.tabs(["🆕 Crear Usuario", "📝 Editar / Eliminar"])
            
            # --- TAB 1: CREATE ---
            with tab_create:
                with st.form("frm_add_user_login"):
                    c_u1, c_u2 = st.columns(2)
                    with c_u1:
                        new_rut = st.text_input("RUT (ID)", help="Ej: 12345678-9")
                        new_user = st.text_input("Nombre de Usuario (USER)", help="Ej: jperez")
                    with c_u2:
                        new_pass = st.text_input("Contraseña (PASS)", type="password")
                        new_rol = st.selectbox("Rol (ROL)", ["USUARIO", "ADMIN", "PROGRAMADOR"])
                    
                    submitted_user = st.form_submit_button("💾 Crear Usuario")
                    
                    if submitted_user:
                        if new_rut and new_user and new_pass:
                            from firebase_bd import ingresar_registro_bd
                            data_login = {
                                "ID": new_rut,
                                "USER": new_user,
                                "PASS": new_pass,
                                "ROL": new_rol
                            }
                            try:
                                ingresar_registro_bd("login", data_login)
                                st.success(f"✅ Usuario '{new_user}' creado correctamente.")
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al crear usuario: {e}")
                        else:
                            st.warning("⚠️ Todos los campos son obligatorios.")

            # --- TAB 2: EDIT / DELETE ---
            with tab_manage:
                from firebase_bd import actualizar_registro, borrar_registro
                
                # Fetch fresh data
                login_data = leer_registro("login")
                
                if not login_data:
                    st.warning("No hay usuarios registrados en la tabla 'login'.")
                else:
                    # Handle Firebase List/Dict weirdness
                    # If keys are mostly integers, it might be a list.
                    # Best to normalize to dict {key: val}
                    if isinstance(login_data, list):
                        # Convert list to dict with index as key
                        login_dict = {str(i): v for i, v in enumerate(login_data) if v is not None}
                    else:
                        login_dict = login_data

                    # Create options list: "USER (ID) [Key]"
                    # We store key in a lookup or Tuple
                    user_opts = []
                    for k, v in login_dict.items():
                        if isinstance(v, dict):
                            label = f"{v.get('USER', 'N/A')} ({v.get('ID', 'N/A')})"
                            user_opts.append((k, label))
                    
                    if not user_opts:
                        st.info("No se encontraron registros válidos para editar.")
                    else:
                        selected_opt = st.selectbox("Seleccionar Usuario", user_opts, format_func=lambda x: x[1])
                        
                        if selected_opt:
                            sel_key = selected_opt[0]
                            sel_data = login_dict[sel_key]
                            
                            st.markdown("---")
                            st.write(f"**Editando:** {sel_data.get('USER')} (Key: `{sel_key}`)")
                            
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                edit_id = st.text_input("ID / RUT", value=sel_data.get("ID", ""), key=f"id_{sel_key}")
                                edit_user = st.text_input("Usuario", value=sel_data.get("USER", ""), key=f"u_{sel_key}")
                            with col_e2:
                                edit_pass = st.text_input("Contraseña", value=sel_data.get("PASS", ""), key=f"p_{sel_key}")
                                
                                curr_rol = sel_data.get("ROL", "USUARIO")
                                roles = ["USUARIO", "ADMIN", "PROGRAMADOR"]
                                try: idx_r = roles.index(curr_rol)
                                except: idx_r = 0
                                edit_rol = st.selectbox("Rol", roles, index=idx_r, key=f"r_{sel_key}")
                            
                            c_btn1, c_btn2 = st.columns([1,1])
                            
                            with c_btn1:
                                if st.button("💾 Actualizar Datos", type="primary", key=f"btn_upd_{sel_key}"):
                                    new_data = {
                                        "ID": edit_id,
                                        "USER": edit_user,
                                        "PASS": edit_pass,
                                        "ROL": edit_rol
                                    }
                                    try:
                                        actualizar_registro("login", new_data, sel_key)
                                        st.success("✅ Datos actualizados correctamente.")
                                        time.sleep(1.5)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al actualizar: {e}")
                                        
                            with c_btn2:
                                if st.button("🗑️ Eliminar Usuario", type="secondary", key=f"btn_del_{sel_key}"):
                                    try:
                                        borrar_registro("login", sel_key)
                                        st.warning(f"Usuario {edit_user} eliminado.")
                                        time.sleep(1.5)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al eliminar: {e}")


    # --- MAINTENANCE SECTION ---
    from funciones import recalcular_todo, es_contrato_activo

    with st.expander("🛠️ Acciones de Mantenimiento (Admin)", expanded=False):
        st.info("Utilice esta función para forzar el recálculo de antigüedad y puntajes de TODA la dotación. Útil tras cambios en reglas de negocio.")
        
        c_btn, c_stat = st.columns([1, 3])
        with c_btn:
            if st.button("🔄 Forzar Recálculo Global", type="secondary", help="Esto puede tardar unos minutos."):
                status_box = st.empty()
                prog_bar = st.progress(0, text="Iniciando...")
                
                def progress_adapter(pct, text):
                    prog_bar.progress(pct, text=text)

                result = recalcular_todo(progress_adapter)
                
                prog_bar.progress(100, text="Completado")
                status_box.success(result)
    
    st.divider()

    with st.spinner("Consolidando información global..."):
        users_raw = leer_registro('usuarios')
        conts_raw = leer_registro('contrato')
        
    if not users_raw:
        st.error("No hay datos de usuarios disponibles.")
        return

    df_users = pd.DataFrame(users_raw.values())
    df_conts = pd.DataFrame(conts_raw.values())

    # Clean numeric fields
    df_users['SUELDO_BASE'] = pd.to_numeric(df_users['SUELDO_BASE'].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce').fillna(0)
    df_users['BIENIOS'] = pd.to_numeric(df_users['BIENIOS'], errors='coerce').fillna(0)
    df_conts['HORAS'] = pd.to_numeric(df_conts['HORAS'], errors='coerce').fillna(0)

    # --- INJECT HONORARIOS ESTIMATED INCOME INTO DF_USERS ---
    # Goal: Add estimated Honorario salary to SUELDO_BASE so charts reflect it.
    honorarios_income_map = {}
    
    # Pre-fetch user categories (redundant with later map but cleanly separated logic)
    user_cats_lookup = {u.get('RUT'): u.get('CATEGORIA') for u in users_raw.values()}

    total_honorarios_est = 0
    count_honorarios_ok = 0
    count_honorarios_err = 0

    for c in conts_raw.values():
        if str(c.get('TIPO_CONTRATO', '')).strip().upper() == 'HONORARIO':
            try:
                rut_c = c.get('RUT')
                cat = user_cats_lookup.get(rut_c)
                horas = int(c.get('HORAS', 0))
                
                if cat in ['A', 'B', 'C', 'D', 'E', 'F'] and horas > 0:
                    if es_contrato_activo(c): # Check expiration
                        base_n15 = sueldos_reajustados_2025.get(15, {}).get(cat, 0)
                        if base_n15 > 0:
                            est_base = (base_n15 / 44) * horas
                            # Metric: Needs full amount (Base + APS)
                            total_honorarios_est += (est_base * 2)
                            
                            # Dataframe Injection: Needs only BASE (charts apply *2 themselves)
                            honorarios_income_map[rut_c] = honorarios_income_map.get(rut_c, 0) + est_base
                            
                            count_honorarios_ok += 1
                        else:
                            count_honorarios_err += 1
                    # If expired, we ignore
                else:
                    count_honorarios_err += 1
            except:
                count_honorarios_err += 1

    # Apply to dataframe
    # We iterate and update the value in the dataframe
    for idx, row in df_users.iterrows():
        rut = row.get('RUT')
        if rut in honorarios_income_map:
            extra_income = honorarios_income_map[rut]
            # Add to existing Base (which might be 0 or have Planta income)
            # Note: If they have both Planta and Honorario (rare but possible), this sums them.
            df_users.at[idx, 'SUELDO_BASE'] = row['SUELDO_BASE'] + extra_income

    # 3. GLOBAL KPIs
    total_base = df_users['SUELDO_BASE'].sum()
    total_aps = total_base # Regla APS = Sueldo Base
    total_gasto = total_base + total_aps
    
    # Calculate Dotación from Unique RUTs in Contracts (to include everyone)
    unique_ruts_conts = set()
    for c in conts_raw.values():
        if es_contrato_activo(c): # Only active contracts count for Dotacion
            r = str(c.get('RUT', '')).replace('.', '').strip().upper()
            if r: unique_ruts_conts.add(r)
    
    total_dotacion = len(unique_ruts_conts)
    total_contratos = len(df_conts)
    # Average salary is based on Planta/PF users found in df_users (which drives total_gasto)
    avg_sueldo = total_gasto / total_dotacion if total_dotacion > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        with st.container(border=True):
            st.metric("Gasto Mensual Total", format_clp(total_gasto), delta="Planta + PF + Honorario")
    with k2:
        with st.container(border=True):
             total_processed = count_honorarios_ok + count_honorarios_err
             st.metric("Gasto Est. Honorarios", format_clp(total_honorarios_est), delta=f"{count_honorarios_ok} de {total_processed} Honorarios clasificados")
             st.caption("ℹ️ Cálculo estimativo (Base Nivel 15)")
    with k3:
        with st.container(border=True):
            st.metric("Dotación Total", f"{total_dotacion}", delta="Planta + PF + Honorario")
    with k4:
        with st.container(border=True):
             if count_honorarios_err > 0:
                 st.metric("Cttos Honorarios Sin Monto", f"{count_honorarios_err}", delta_color="inverse", delta="Requiere Revisión")
             else:
                 st.metric("Total Contratos", f"{total_contratos}")


    # 4. CHARTS - DOTACIÓN & CONTRATOS
    st.markdown("### 📈 Dotación y Contratos")
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("**Distribución por Categoría (Cantidad)**")
            if 'CATEGORIA' in df_users.columns:
                cat_counts = df_users['CATEGORIA'].value_counts().reset_index()
                cat_counts.columns = ['Categoría', 'Cantidad']
                fig_cat = px.bar(cat_counts, x='Categoría', y='Cantidad', text='Cantidad', color='Categoría', color_discrete_sequence=px.colors.qualitative.Prism)
                st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("**Tipos de Contrato**")
            if 'TIPO_CONTRATO' in df_conts.columns:
                tipo_counts = df_conts['TIPO_CONTRATO'].value_counts().reset_index()
                tipo_counts.columns = ['Tipo', 'Cantidad']
                fig_tipo = px.pie(tipo_counts, names='Tipo', values='Cantidad',  hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_tipo, use_container_width=True)

    # 4.2 FINANCIAL BURDEN (NEW)
    st.markdown("### 💰 Análisis de Carga Presupuestaria")
    st.caption("Ranking de impacto financiero (Sueldo Base + APS) por grupo.")
    
    # Cost per Category
    df_cat_cost = df_users.groupby('CATEGORIA')['SUELDO_BASE'].sum().reset_index()
    df_cat_cost['Costo Total'] = df_cat_cost['SUELDO_BASE'] * 2 # Add APS
    df_cat_cost = df_cat_cost.sort_values('Costo Total', ascending=False)
    
    # Cost per Profession
    df_prof_cost = df_users.groupby('PROFESION')['SUELDO_BASE'].sum().reset_index()
    df_prof_cost['Costo Total'] = df_prof_cost['SUELDO_BASE'] * 2 # Add APS
    df_prof_cost = df_prof_cost.sort_values('Costo Total', ascending=True).tail(10) # Top 10 descending for H-bar
    
    fc1, fc2 = st.columns(2)
    
    with fc1:
         with st.container(border=True):
            st.markdown("**Costo Global por Categoría**")
            fig_cc = px.bar(
                df_cat_cost, 
                x='CATEGORIA', 
                y='Costo Total', 
                text_auto='.2s',
                title="Suma de Sueldos (Base+APS)",
                color='Costo Total',
                color_continuous_scale='Reds'
            )
            fig_cc.update_layout(showlegend=False)
            st.plotly_chart(fig_cc, use_container_width=True)
            
    with fc2:
         with st.container(border=True):
            st.markdown("**Top Profesiones - Mayor Gasto**")
            fig_cp = px.bar(
                df_prof_cost, 
                x='Costo Total', 
                y='PROFESION', 
                orientation='h',
                text_auto='.2s',
                title="Top 10 Profesiones (Costo Total)",
                color='Costo Total',
                color_continuous_scale='Greens'
            )
            fig_cp.update_layout(showlegend=False)
            st.plotly_chart(fig_cp, use_container_width=True)

    # 4.2.1 UNIT COST ANALYSIS (NEW)
    # "Impacto Unitario": Average Cost per Profession AND Category
    
    # 4.2.1 UNIT COST ANALYSIS (NEW)
    # "Impacto Unitario": Average Cost per Profession AND Category
    
    # 1. Profession Avg
    df_prof_avg = df_users.groupby('PROFESION')['SUELDO_BASE'].mean().reset_index()
    df_prof_avg['Costo Promedio'] = df_prof_avg['SUELDO_BASE'] * 2 # APS
    df_prof_avg = df_prof_avg.sort_values('Costo Promedio', ascending=True).tail(10)

    # 2. Category Avg
    df_cat_avg = df_users.groupby('CATEGORIA')['SUELDO_BASE'].mean().reset_index()
    df_cat_avg['Costo Promedio'] = df_cat_avg['SUELDO_BASE'] * 2 # APS
    df_cat_avg = df_cat_avg.sort_values('Costo Promedio', ascending=True)
    
    uc1, uc2 = st.columns(2)
    
    with uc1:
        with st.container(border=True):
            st.markdown("**Costo Promedio: Profesiones**")
            fig_avg_p = px.bar(
                df_prof_avg, 
                x='Costo Promedio', 
                y='PROFESION', 
                orientation='h',
                text_auto='.2s',
                title="Promedio Unitario (Ranking)",
                color='Costo Promedio',
                color_continuous_scale='OrRd'
            )
            fig_avg_p.update_layout(showlegend=False)
            st.plotly_chart(fig_avg_p, use_container_width=True)
            
    with uc2:
         with st.container(border=True):
             st.markdown("**Costo Promedio: Categorías**")
             fig_avg_c = px.bar(
                df_cat_avg, 
                x='Costo Promedio', 
                y='CATEGORIA', 
                orientation='h',
                text_auto='.2s',
                title="Promedio Unitario por Categoría",
                color='Costo Promedio',
                color_continuous_scale='OrRd'
             )
             fig_avg_c.update_layout(showlegend=False)
             st.plotly_chart(fig_avg_c, use_container_width=True)

    # 4.3 OTHER STATS (Levels)
    with st.container(border=True):
        st.markdown("**Distribución por Nivel Carrera Funcionaria**")
        if 'NIVEL' in df_users.columns:
            lvl_counts = df_users['NIVEL'].value_counts().reset_index()
            lvl_counts.columns = ['Nivel', 'Funcionarios']
            lvl_counts = lvl_counts.sort_values('Nivel')
            fig_lvl = px.bar(lvl_counts, x='Nivel', y='Funcionarios', text='Funcionarios', color_discrete_sequence=['#006DB6'])
            st.plotly_chart(fig_lvl, use_container_width=True)

    # 4.5 ANALISIS PREDICTIVO AVANZADO
    st.markdown("### 🚀 Análisis Predictivo de Ascensos")
    
    immediate_upgrades = []
    upcoming_upgrades = []
    
    immediate_cost = 0
    upcoming_cost = 0
    
    # Iterate users for prediction
    for idx, row in df_users.iterrows():
        rut = row.get('RUT')
        nome = row.get('NOMBRE_FUNC')
        cat = row.get('CATEGORIA')
        try: curr_lvl = int(row.get('NIVEL', 15))
        except: curr_lvl = 15
        try: curr_pts = float(row.get('PTJE_CARR', 0))
        except: curr_pts = 0
        try: curr_salary = float(row.get('SUELDO_BASE', 0))
        except: curr_salary = 0
        try: bienios = int(row.get('BIENIOS', 0))
        except: bienios = 0
        
        days_left = get_days_to_bienio(rut, bienios, df_conts)
        
        # --- LOGIC ENHANCEMENT ---
        
        # 1. REAL-TIME LEVEL CHECK (Score Integrity)
        # Calculate what level they SHOULD be based on points
        calc_lvl = calculate_level_from_points(cat, curr_pts)
        
        is_immediate = False
        
        if calc_lvl < curr_lvl:
            # IMMEDIATE UPGRADE START
            new_base = get_salary_for_level(cat, calc_lvl)
            new_aps = new_base
            new_total = new_base + new_aps
            
            old_aps = curr_salary
            old_total = curr_salary + old_aps
            
            diff_real = max(0, new_total - old_total)
            
            immediate_upgrades.append({
                "Funcionario": nome,
                "RUT": rut,
                "Cat": cat,
                "Pts Actual": curr_pts,
                "Nivel Actual": curr_lvl,
                "Nivel Nuevo": calc_lvl,
                "Causa": f"Puntaje (Corresponde Nivel {calc_lvl})",
                "Impacto Mensual": diff_real
            })
            immediate_cost += diff_real
            is_immediate = True
            
        # 2. BIENNIUM CHECK (Time Based)
        # Only check if not already flagged by score
        if not is_immediate and days_left is not None:
             if -355 <= days_left <= 0:
                # Overdue Biennium -> Simulate +534 pts
                 sim_pts = curr_pts + 534
                 lvl_by_bienio = calculate_level_from_points(cat, sim_pts)
                 
                 if lvl_by_bienio < curr_lvl:
                    new_base = get_salary_for_level(cat, lvl_by_bienio)
                    new_aps = new_base
                    new_total = new_base + new_aps
                    old_aps = curr_salary
                    old_total = curr_salary + old_aps
                    diff_real = max(0, new_total - old_total)
                    
                    immediate_upgrades.append({
                        "Funcionario": nome,
                        "RUT": rut,
                        "Cat": cat,
                        "Pts Actual": curr_pts,
                        "Nivel Actual": curr_lvl,
                        "Nivel Nuevo": lvl_by_bienio,
                        "Causa": f"Bienio Cumplido (Hace {abs(days_left)} días)",
                        "Impacto Mensual": diff_real
                    })
                    immediate_cost += diff_real
                    is_immediate = True

        # 3. UPCOMING / NEAR MISS (Prediction)
        if not is_immediate:
             # A. Score Prediction (Near Miss)
             # Find points needed for next level
             next_lvl = curr_lvl - 1
             if next_lvl >= 1:
                 # Hack: find range for next level
                 range_found = None
                 if cat in ['A', 'B']: table = indices_niveles.get(('A','B'))
                 else: table = indices_niveles.get(('C','D','E','F'))
                 
                 for r, l in table.items():
                     if l == next_lvl:
                         range_found = r[0] # Min points
                         break
                 
                 if range_found:
                     dist = range_found - curr_pts
                     if 0 < dist <= 50: # Within 50 points
                         upcoming_upgrades.append({
                            "Funcionario": nome,
                            "RUT": rut,
                            "Cat": cat,
                            "Pts Actual": curr_pts,
                            "Nivel Actual": curr_lvl,
                            "Nivel Proy.": next_lvl,
                            "Días Restantes": 0, # N/A
                            "Detalle": f"Faltan {dist:.1f} pts",
                            "Impacto Mensual": 0 # Unknown
                         })

             # B. Time Prediction (<= 60 days)
             if days_left is not None and 0 < days_left <= 60:
                 sim_pts_upc = curr_pts + 534
                 lvl_upc = calculate_level_from_points(cat, sim_pts_upc)
                 
                 if lvl_upc < curr_lvl:
                     new_base = get_salary_for_level(cat, lvl_upc)
                     new_aps = new_base
                     diff_real = max(0, (new_base + new_aps) - (curr_salary * 2))
                     
                     upcoming_upgrades.append({
                        "Funcionario": nome,
                        "RUT": rut,
                        "Cat": cat,
                        "Pts Actual": curr_pts,
                        "Nivel Actual": curr_lvl,
                        "Nivel Proy.": lvl_upc,
                        "Días Restantes": days_left,
                        "Detalle": f"Bienio en {days_left} días",
                        "Impacto Mensual": diff_real
                     })
                     upcoming_cost += diff_real

    # --- UI DISPLAY ---
    
    # SECTION 1: IMMEDIATE
    st.markdown("#### ⚠️ Ascensos Inmediatos / Pendientes")
    st.caption("Funcionarios que, por puntaje actual o bienio ya cumplido, deberían estar en un nivel superior.")
    
    c_im1, c_im2 = st.columns(2)
    c_im1.metric("Funcionarios", len(immediate_upgrades), delta="Requieren Acción")
    c_im2.metric("Impacto Costo Mensual", format_clp(immediate_cost), delta="Sueldos Base")
    
    if immediate_upgrades:
        with st.expander("Ver Nómina Inmediata", expanded=False):
            st.dataframe(
                pd.DataFrame(immediate_upgrades), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Funcionario": st.column_config.TextColumn("Funcionario", width="medium"),
                    "Impacto Mensual": st.column_config.NumberColumn("Impacto ($)", format="$%d"),
                    "Pts Actual": st.column_config.NumberColumn("Pts Actual", format="%.2f"),
                    "RUT": st.column_config.TextColumn("RUT"),
                }
            )
    else:
        st.success("✅ Todo al día. No hay ascensos pendientes.")
        
    st.divider()
    
    # SECTION 2: UPCOMING
    st.markdown("#### 📅 Próximos Ascensos (60 días)")
    st.caption("Proyección a corto plazo para anticipar presupuesto.")
    
    c_up1, c_up2 = st.columns(2)
    c_up1.metric("Proyección Funcionarios", len(upcoming_upgrades), delta="En < 60 días")
    c_up2.metric("Proyección Costo", format_clp(upcoming_cost))
    
    if upcoming_upgrades:
        with st.expander("Ver Nómina Proyección", expanded=True):
            st.dataframe(
                pd.DataFrame(upcoming_upgrades).sort_values('Días Restantes'), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Funcionario": st.column_config.TextColumn("Funcionario", width="medium"),
                    "Impacto Mensual": st.column_config.NumberColumn("Impacto ($)", format="$%d"),
                    "Pts Actual": st.column_config.NumberColumn("Pts Actual", format="%.2f"),
                    "Detalle": st.column_config.TextColumn("Motivo"),
                }
            )
    else:
        st.info("No se proyectan cambios de nivel en los próximos 2 meses.")

    # 5. DATA TABLE
    with st.expander("📂 Ver Nómina Completa de Funcionarios"):
        display_cols = ['RUT', 'NOMBRE_FUNC', 'PROFESION', 'CATEGORIA', 'NIVEL', 'BIENIOS', 'SUELDO_BASE']
        # Filter cols that actually exist
        valid_cols = [c for c in display_cols if c in df_users.columns]
        
        st.dataframe(
            df_users[valid_cols],
            column_config={
                "RUT": st.column_config.TextColumn("RUT"),
                "NOMBRE_FUNC": st.column_config.TextColumn("Nombre", width="medium"),
                "SUELDO_BASE": st.column_config.NumberColumn("Sueldo Base", format="$%d"),
                "BIENIOS": st.column_config.NumberColumn("Bienios"),
            },
            use_container_width=True,
            hide_index=True
        )

    st.divider()
    
    # 6. EXPORTAR INFORME GLOBAL
    # Requires: pip install -U kaleido
    import os
    
    if st.button("📄 Exportar Informe Completo (PDF)", type="primary"):
        with st.spinner("Generando reporte global... Esto puede tomar unos segundos..."):
            try:
                # 1. Prepare KPIs
                kpis = {
                    "gasto": format_clp(total_gasto),
                    "dotacion": total_dotacion,
                    "contratos": total_contratos,
                    "promedio": format_clp(avg_sueldo)
                }
                
                # 2. Save Charts to Images (Temp)
                # We need to define the figures outside the columns to access them here, 
                # OR re-generate them. Re-generating is cleaner than refactoring the whole file scope.
                # Actually, defined figures in previous scopes (fig_cat, fig_tipo, etc) are valid ONLY if they executed.
                # However, Python scope in Streamlit is function-level, so if they ran, they exist.
                
                chart_paths = {}
                charts_to_save = {
                    'cat_counts': locals().get('fig_cat'),
                    'tipo_counts': locals().get('fig_tipo'),
                    'cat_cost': locals().get('fig_cc'),
                    'prof_cost': locals().get('fig_cp'),
                    'prof_avg': locals().get('fig_avg_p'),
                    'cat_avg': locals().get('fig_avg_c')
                }
                
                temp_files = []
                
                # Prepare fallback data dict
                fallback_data = {
                    'cat_counts': locals().get('cat_counts'),
                    'tipo_counts': locals().get('tipo_counts'),
                    'cat_cost': locals().get('df_cat_cost'),
                    'prof_cost': locals().get('df_prof_cost'),
                    'prof_avg': locals().get('df_prof_avg'),
                    'cat_avg': locals().get('df_cat_avg')
                }

                temp_files = []
                kaleido_failed = False
                
                # Attempt Plotly Generation
                for key, fig in charts_to_save.items():
                    if fig:
                        fname = f"temp_{key}.png"
                        try:
                            fig.write_image(fname, scale=2)
                            chart_paths[key] = os.path.abspath(fname)
                            temp_files.append(fname)
                        except Exception as e:
                            kaleido_failed = True
                            print(f"Kaleido failed for {key}: {e}")
                
                # If ANY chart failed, use Fallback for ALL to maintain consistent style, 
                # or just for missing ones? Better to use fallback for all or missing. 
                # Let's simple check: if kaleido_failed, run batch fallback.
                
                if kaleido_failed:
                    st.toast("⚠️ Usando motor gráfico alternativo (Matplotlib)...", icon="🎨")
                    from modules.chart_utils import generate_fallback_charts_batch
                    try:
                        fb_paths = generate_fallback_charts_batch(fallback_data)
                        chart_paths.update(fb_paths) # Merge/Overwrite
                        for p in fb_paths.values():
                            if os.path.basename(p) not in temp_files:
                                temp_files.append(os.path.basename(p))
                    except Exception as e:
                        st.error(f"Error en gráficos alternativos: {e}")

                # 3. Prepare Upgrade Data
                upgrades_data = {
                    "immediate": immediate_upgrades,
                    "upcoming": upcoming_upgrades
                }
                
                # 4. Logos
                logo_path = os.path.abspath("logo_app_carr.png")
                logo_c_path = os.path.abspath("logo_alain.png")
                
                # 5. Generate PDF
                from modules.pdf_admin import create_global_pdf
                pdf_bytes = create_global_pdf(kpis, chart_paths, upgrades_data, logo_path, logo_c_path)
                
                # 6. Clean Temp
                for f in temp_files:
                    if os.path.exists(f):
                        try: os.remove(f)
                        except: pass
                
                # 7. Download
                st.download_button(
                    label="⬇️ Descargar Reporte Global",
                    data=pdf_bytes,
                    file_name=f"Reporte_Gestion_Global_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error crítico al generar reporte: {e}")

