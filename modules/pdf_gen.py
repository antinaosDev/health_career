from fpdf import FPDF
import datetime
import os

class CareerReport(FPDF):
    def __init__(self, logo_path=None, logo_company_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.logo_company_path = logo_company_path
        
    def header(self):
        # Logo App (Left)
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, 30)

        # Logo Company (Right)
        if self.logo_company_path and os.path.exists(self.logo_company_path):
            self.image(self.logo_company_path, 170, 8, 30)
            
        # Title
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Ficha Resumen - Carrera Funcionaria', 0, 1, 'C')
        
        # Date
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generado el: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        
        self.ln(10)
        self.line(10, 35, 200, 35)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        
        # 3 column layout
        self.cell(65, 10, 'Sistema de Gestión de Carrera Funcionaria', 0, 0, 'L')
        self.cell(60, 10, 'Desarrollado por Alain Antinao Sepúlveda', 0, 0, 'C')
        self.cell(65, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'R')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'{label}', 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, self.sanitize_text(text))
        self.ln()

    @staticmethod
    def sanitize_text(text):
        if not isinstance(text, str): return str(text)
        # Replacements for characters not supported by Latin-1
        replacements = {
            '\u2013': '-',  # En-dash
            '\u2014': '-',  # Em-dash
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u2022': '*',  # Bullet
            '€': 'EUR',
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        
        # Final fallback: encode to latin-1, ignoring errors, then decode back
        return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(user_data, caps_data, conts_data, extra_info, logo_path, logo_company_path=None, chart_paths=None, breakdown_data=None, summary_dict=None):
    pdf = CareerReport(logo_path, logo_company_path)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- USER INFO ---
    pdf.chapter_title("Información del Funcionario")
    pdf.set_font('Arial', '', 10)
    
    line_h = 6 # Row height
    
    # Data Cleaning
    name = pdf.sanitize_text(f"Nombre: {user_data.get('NOMBRE_FUNC', '')}")
    rut = pdf.sanitize_text(f"RUT: {user_data.get('RUT', '')}")
    cat = pdf.sanitize_text(f"Categoría: {user_data.get('CATEGORIA', '')}")
    nivel = pdf.sanitize_text(f"Nivel Carrera: {user_data.get('NIVEL', '')}")
    bienios = pdf.sanitize_text(f"Bienios: {user_data.get('BIENIOS', '')}")
    ptje = pdf.sanitize_text(f"Puntaje Total: {float(user_data.get('PTJE_CARR', 0)):.2f}")
    
    edad = pdf.sanitize_text(f"Edad: {user_data.get('EDAD', '')} años")
    prox = pdf.sanitize_text(f"Próx. Bienio: {extra_info.get('prox_bienio', 'N/A')}")
    meta = pdf.sanitize_text(f"Meta Próx. Nivel: {extra_info.get('meta_puntos', 0):.2f}")
    saldo = pdf.sanitize_text(f"Saldo Actual: {user_data.get('SALDO_PTJE', 0):.2f}")
    
    # Parse Salary
    try:
        raw_s = str(user_data.get('SUELDO_BASE', '0')).replace('.', '').replace(',', '').replace('$', '').strip()
        val_s = float(raw_s)
    except:
        val_s = 0
    aps_s = val_s * 2
    
    sueldo = pdf.sanitize_text(f"Sueldo Base + APS: ${int(aps_s):,}".replace(",", "."))
    
    # Custom Widths to avoid overlap
    w = [95, 45, 50]
    
    pdf.cell(w[0], line_h, name, 0)
    pdf.cell(w[1], line_h, cat, 0)
    pdf.cell(w[2], line_h, nivel, 0, 1)
    
    pdf.cell(w[0], line_h, rut, 0)
    pdf.cell(w[1], line_h, bienios, 0)
    pdf.cell(w[2], line_h, ptje, 0, 1)
    
    pdf.cell(w[0], line_h, prox, 0)
    pdf.cell(w[1], line_h, edad, 0)
    pdf.cell(w[2], line_h, meta, 0, 1)

    pdf.cell(w[0], line_h, saldo, 0)
    pdf.cell(w[1], line_h, sueldo, 0, 1) # Added salary here
    
    pdf.ln(3) 

    # --- SCORE EXPLANATION & BREAKDOWN (NEW) ---
    if breakdown_data:
        if pdf.get_y() > 230: pdf.add_page()
        pdf.chapter_title("Análisis Detallado de Puntaje")
        
        # Explanation Text
        t_expl = (
            "COMPONENTES DEL PUNTAJE: 1. Base (Bienios) | 2. Capacitación Sujeta a Tope (Ingreso a Planta + Cambio de Nivel + Arrastre). "
            "El Tope Global es de 4.500 (Cat A/B) o 3.500 (Cat C-F). El excedente se acumula en un 'Saldo'."
        )
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 5, pdf.sanitize_text(t_expl))
        pdf.ln(2)

        # Breakdown Table
        pdf.set_font('Arial', 'B', 8)
        w_bd = [15, 25, 25, 25, 25, 25, 25]  # ~165 total
        h_bd = ['Año', 'Pts Cursos', 'Tope Anual', 'Déf/Exc', 'Uso Saldo', 'Gen. Saldo', 'Saldo Fin']
        
        # Center the table
        start_x = (210 - sum(w_bd)) / 2
        pdf.set_x(start_x)
        
        for i, h in enumerate(h_bd):
            pdf.cell(w_bd[i], 6, pdf.sanitize_text(h), 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        for bd in breakdown_data:
            pdf.set_x(start_x)
            pdf.cell(w_bd[0], 5, str(bd.get('AÑO')), 1, 0, 'C')
            pdf.cell(w_bd[1], 5, f"{bd.get('PUNTOS_REALES',0):.1f}", 1, 0, 'C')
            pdf.cell(w_bd[2], 5, str(bd.get('LIMITE')), 1, 0, 'C')
            pdf.cell(w_bd[3], 5, f"{bd.get('DIFERENCIA',0):.1f}", 1, 0, 'C')
            pdf.cell(w_bd[4], 5, f"{bd.get('SALDO_USADO',0):.1f}", 1, 0, 'C')
            pdf.cell(w_bd[5], 5, f"{bd.get('SALDO_GENERADO',0):.1f}", 1, 0, 'C')
            pdf.cell(w_bd[6], 5, f"{bd.get('SALDO_ACUMULADO',0):.1f}", 1, 0, 'C')
            pdf.ln()
            pdf.cell(w_bd[6], 5, f"{bd.get('SALDO_ACUMULADO',0):.1f}", 1, 0, 'C')
            pdf.ln()
            
        pdf.ln(2)
        
        pdf.ln(2)
        
    # --- SUMMARY TOTALS (Arraste, Base, etc.) ---
    if summary_dict:
         pdf.set_font('Arial', '', 9)
         
         arrastre = summary_dict.get('ARRASTRE_PTS', 0)
         bienios_pts = summary_dict.get('VALOR_BIENIOS', 0)
         planta = summary_dict.get('BASE_PLANTA', 0)
         
         # Table of Components
         if pdf.get_y() > 240: pdf.add_page()
         pdf.chapter_title("Resumen de Componentes Base")
         pdf.set_font('Arial', '', 10)
         
         # Header
         w_sum = [60, 60, 60]
         pdf.cell(w_sum[0], 6, "Ingreso a Planta", 1, 0, 'C', 1)
         pdf.cell(w_sum[1], 6, "Arrastre (Histórico)", 1, 0, 'C', 1)
         pdf.cell(w_sum[2], 6, "Bienios", 1, 1, 'C', 1)
         
         # Values
         pdf.cell(w_sum[0], 7, f"{planta:,.1f}", 1, 0, 'C')
         pdf.cell(w_sum[1], 7, f"{arrastre:,.1f}", 1, 0, 'C')
         pdf.cell(w_sum[2], 7, f"{bienios_pts:,.1f}", 1, 1, 'C')
         
         pdf.ln(5)
         
         # Final Note
         pdf.set_font('Arial', 'I', 8)
         pdf.cell(0, 5, pdf.sanitize_text("(Puntaje Total = [Ingreso a Planta + Arrastre + Efectivo Anual (Topado)] + Bienios)"), 0, 1, 'C')
         
         # --- GAP STATUS ---
         if extra_info.get("cap_status_msg"):
             pdf.ln(3)
             pdf.set_font('Arial', 'B', 9) 
             # Clean markdown bold markers and emojis (simple replacement)
             raw_msg = extra_info.get("cap_status_msg")
             clean_msg = raw_msg.replace('**', '').replace('⚠️', '').replace('✅', '').strip()
             pdf.multi_cell(0, 5, pdf.sanitize_text(f"ESTADO TOPE GLOBAL: {clean_msg}"), 1, 'C')
         
         pdf.ln(2)

    # --- CONTRACTS SECTION ---
    if conts_data:
        if pdf.get_y() > 230: pdf.add_page()
        pdf.chapter_title("Resumen Contractual")
        pdf.set_font('Arial', 'B', 9)
        # Expanded headers and widths
        w_c = [40, 50, 25, 25, 20, 30] # Total 190
        header_c = ['Tipo Contrato', 'Cargo', 'Inicio', 'Término', 'Horas', 'Antigüedad']
        
        for i, h in enumerate(header_c):
            pdf.cell(w_c[i], 7, pdf.sanitize_text(h), 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        total_hrs_c = 0.0
        
        for c in conts_data:
            tipo = pdf.sanitize_text(str(c.get('TIPO_CONTRATO', '')))
            cargo = pdf.sanitize_text(str(c.get('CARGO', ''))[:25])
            ini_str = str(c.get('FECHA_INICIO', ''))
            fin_str = str(c.get('FECHA_TERMINO', ''))
            
            ini = pdf.sanitize_text(ini_str)
            fin = pdf.sanitize_text(fin_str if fin_str else 'Indefinido')
            
            hrs_str = str(c.get('HORAS', 0))
            hrs_disp = pdf.sanitize_text(hrs_str)
            try: total_hrs_c += float(hrs_str)
            except: pass
            
            # --- Calculate Individual Antiquity ---
            ant_str = "N/A"
            try:
                start_dt = datetime.datetime.strptime(ini_str.strip(), "%d/%m/%Y")
                if "PLANTA" in tipo.upper() or not fin_str.strip():
                     end_dt = datetime.datetime.now()
                else:
                     end_dt = datetime.datetime.strptime(fin_str.strip(), "%d/%m/%Y")
                
                delta_days = (end_dt - start_dt).days
                if delta_days < 0: delta_days = 0
                
                y_c = delta_days // 365
                rem_d = delta_days % 365
                m_c = rem_d // 30
                ant_str = f"{y_c}a {m_c}m"
            except:
                pass

            
            pdf.cell(w_c[0], 6, tipo, 1, 0, 'L')
            pdf.cell(w_c[1], 6, cargo, 1, 0, 'L')
            pdf.cell(w_c[2], 6, ini, 1, 0, 'C')
            pdf.cell(w_c[3], 6, fin, 1, 0, 'C')
            pdf.cell(w_c[4], 6, hrs_disp, 1, 0, 'C')
            pdf.cell(w_c[5], 6, pdf.sanitize_text(ant_str), 1, 0, 'C')
            pdf.ln()
            
        pdf.set_font('Arial', 'B', 9)
        # Total Hours Row
        pdf.cell(sum(w_c[:4]), 7, "Total Horas Semanales", 1, 0, 'R')
        pdf.cell(w_c[4], 7, f"{total_hrs_c:.1f}", 1, 0, 'C')
        pdf.cell(w_c[5], 7, "", 1, 0, 'C') # Empty for antiquity col on this row
        pdf.ln()

        # Total Antiquity Row (New)
        ant_real = extra_info.get('antiguedad_real', {'y': 0, 'm': 0})
        ant_total_str = f"{ant_real.get('y',0)} años, {ant_real.get('m',0)} meses"
        
        pdf.cell(sum(w_c[:5]), 7, pdf.sanitize_text("Antigüedad Total Acumulada (Legal)"), 1, 0, 'R')
        pdf.cell(w_c[5], 7, pdf.sanitize_text(ant_total_str), 1, 0, 'C')
        pdf.ln(5)
        
    # --- GRÁFICOS (CHARTS) ---
    if chart_paths:
        pdf.add_page()
        pdf.chapter_title("Análisis Gráfico")
        y_pos = pdf.get_y()
        # Charts 1 & 2
        p_nv = chart_paths.get('nivel')
        if p_nv and os.path.exists(p_nv): pdf.image(p_nv, x=10, y=y_pos, w=90)
        p_bi = chart_paths.get('bienio')
        if p_bi and os.path.exists(p_bi): pdf.image(p_bi, x=110, y=y_pos, w=90)
        pdf.ln(85)
        
        y_pos = pdf.get_y()
        # Charts 3 & 4
        p_yr = chart_paths.get('year')
        if p_yr and os.path.exists(p_yr): pdf.image(p_yr, x=10, y=y_pos, w=90)
        p_ct = chart_paths.get('contrato')
        if p_ct and os.path.exists(p_ct): pdf.image(p_ct, x=110, y=y_pos, w=90)
        pdf.ln(90)

    # --- SUMMARY & TRAINING DETAILS ---
    if pdf.get_y() > 230: pdf.add_page()
    pdf.chapter_title("Detalle Histórico de Capacitaciones")
    pdf.set_font('Arial', '', 10)
    
    total_caps = len(caps_data)
    total_horas = sum([c.get('HORAS', 0) for c in caps_data])
    if caps_data: avg_nota = sum([c.get('NOTA', 0) for c in caps_data]) / total_caps
    else: avg_nota = 0
        
    pdf.cell(60, 6, f"Cursos Realizados: {total_caps}", 0)
    pdf.cell(60, 6, f"Horas Totales: {total_horas}", 0)
    pdf.cell(60, 6, f"Nota Promedio: {avg_nota:.1f}", 0, 1)
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 8)
    w = [12, 60, 35, 35, 12, 12, 12]
    header = ['Año', 'Nombre', 'Entidad', 'Contexto', 'Hrs', 'Pts', 'Nota']
    
    for i, h in enumerate(header):
        pdf.cell(w[i], 7, pdf.sanitize_text(h), 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 8)
    for c in caps_data:
        anio = pdf.sanitize_text(str(c.get('AÑO_PRESENTACION', '')))
        nombre = pdf.sanitize_text(str(c.get('NOMBRE_CAPACITACION', '')))[:35]
        entidad = pdf.sanitize_text(str(c.get('ENTIDAD', '')))[:20]
        contexto = pdf.sanitize_text(str(c.get('CONTEXTO_PRESS', '')))[:20]
        horas = pdf.sanitize_text(str(c.get('HORAS', '')))
        pje = pdf.sanitize_text(f"{c.get('PJE_POND', 0):.1f}")
        nota = pdf.sanitize_text(f"{c.get('NOTA', 0):.1f}")
        
        pdf.cell(w[0], 6, anio, 1, 0, 'C')
        pdf.cell(w[1], 6, nombre, 1, 0, 'L')
        pdf.cell(w[2], 6, entidad, 1, 0, 'L')
        pdf.cell(w[3], 6, contexto, 1, 0, 'L')
        pdf.cell(w[4], 6, horas, 1, 0, 'C')
        pdf.cell(w[5], 6, pje, 1, 0, 'C')
        pdf.cell(w[6], 6, nota, 1, 0, 'C')
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')
