from fpdf import FPDF
import datetime
import os
from funciones import dias_restantes_contrato

class HonorariosReport(FPDF):
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
        self.cell(0, 10, 'Ficha Resumen - Funcionario a Honorarios', 0, 1, 'C')
        
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
        self.cell(65, 10, f'Página {self.page_no()}/{self.alias_nb_pages}', 0, 0, 'R')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240) # We stick to a lighter gray or similar simple style
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

def create_pdf_honorarios(user_data, honorario_conts, estimated_salary_data, logo_path, logo_company_path=None, extra_info=None):
    pdf = HonorariosReport(logo_path, logo_company_path)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- USER INFO ---
    pdf.chapter_title("Información del Funcionario")
    pdf.set_font('Arial', '', 10)
    
    line_h = 6 # Row height
    
    name = pdf.sanitize_text(f"Nombre: {user_data.get('NOMBRE_FUNC', '')}")
    rut = pdf.sanitize_text(f"RUT: {user_data.get('RUT', '')}")
    cat = pdf.sanitize_text(f"Categoría: {user_data.get('CATEGORIA', '')}")
    prof = pdf.sanitize_text(f"Profesión: {user_data.get('PROFESION', '')}")
    edad = pdf.sanitize_text(f"Edad: {user_data.get('EDAD', '')} años")
    
    # Custom Widths
    w = [110, 80]
    
    pdf.cell(w[0], line_h, name, 0)
    pdf.cell(w[1], line_h, cat, 0, 1)
    
    pdf.cell(w[0], line_h, rut, 0)
    pdf.cell(w[1], line_h, prof, 0, 1)
    
    pdf.cell(w[0], line_h, edad, 0, 1)
    
    pdf.ln(5)

    # --- SALARY ESTIMATION ---
    if pdf.get_y() > 230: pdf.add_page()
    pdf.chapter_title("Estimación de Sueldo Mensual")
    pdf.set_font('Arial', '', 10)
    
    # Disclaimer
    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 5, pdf.sanitize_text("Nota: El cálculo de sueldo es estimativo, basado en un estándar (Nivel 15) de la categoría correspondiente y proporcional a las horas contratadas."))
    pdf.ln(3)

    # Table
    pdf.set_font('Arial', 'B', 9)
    # Headers: Concepto, Monto
    pdf.cell(100, 7, "Concepto", 1, 0, 'L', 1)
    pdf.cell(50, 7, "Monto Estimado", 1, 1, 'R', 1)
    
    # Values
    pdf.set_font('Arial', '', 9)
    
    est_total = estimated_salary_data.get('total_base_aps', 0)
    
    pdf.cell(100, 7, "Sueldo Base + Asignación APS (Base x 2)", 1, 0, 'L')
    pdf.cell(50, 7, f"${int(est_total):,}".replace(",", "."), 1, 1, 'R')
    
    pdf.ln(5)

    # --- CONTRACTS SECTION (Detailed) ---
    if honorario_conts:
        if pdf.get_y() > 230: pdf.add_page()
        pdf.chapter_title("Resumen Contractual")
        pdf.set_font('Arial', 'B', 8)
        # Expanded headers and widths [Type, Inst, Cargo, Start, End, Hrs, Ant]
        w_c = [25, 40, 45, 20, 20, 15, 25] # Total 190
        header_c = ['Tipo Contrato', 'Institución', 'Cargo', 'Inicio', 'Término', 'Horas', 'Antigüedad']
        
        for i, h in enumerate(header_c):
            pdf.cell(w_c[i], 7, pdf.sanitize_text(h), 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        total_hrs_c = 0.0
        
        for c in honorario_conts:
            tipo = pdf.sanitize_text(str(c.get('TIPO_CONTRATO', '')))[:18]
            inst = pdf.sanitize_text(str(c.get('NOMBRE_INSTITUCION', '')))[:22]
            cargo = pdf.sanitize_text(str(c.get('CARGO', '')))[:28]
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
                # Logic: If Planta or No End Date -> End = Now.
                if "PLANTA" in tipo.upper() or not fin_str.strip():
                     end_dt = datetime.datetime.now()
                else:
                     end_dt = datetime.datetime.strptime(fin_str.strip(), "%d/%m/%Y")
                     if end_dt > datetime.datetime.now(): # Cap future
                         end_dt = datetime.datetime.now()
                
                delta_days = (end_dt - start_dt).days
                if delta_days < 0: delta_days = 0
                
                y_c = delta_days // 365
                rem_d = delta_days % 365
                m_c = rem_d // 30
                ant_str = f"{y_c}a {m_c}m"
            except:
                pass

            pdf.cell(w_c[0], 6, tipo, 1, 0, 'L')
            pdf.cell(w_c[1], 6, inst, 1, 0, 'L')
            pdf.cell(w_c[2], 6, cargo, 1, 0, 'L')
            pdf.cell(w_c[3], 6, ini, 1, 0, 'C')
            pdf.cell(w_c[4], 6, fin, 1, 0, 'C')
            pdf.cell(w_c[5], 6, hrs_disp, 1, 0, 'C')
            pdf.cell(w_c[6], 6, pdf.sanitize_text(ant_str), 1, 0, 'C')
            pdf.ln()
            
        pdf.set_font('Arial', 'B', 9)
        # Total Hours Row
        pdf.cell(sum(w_c[:5]), 7, "Total Horas Semanales", 1, 0, 'R')
        pdf.cell(w_c[5], 7, f"{total_hrs_c:.1f}", 1, 0, 'C')
        pdf.cell(w_c[6], 7, "", 1, 0, 'C') 
        pdf.ln()

        # Total Antiquity Rows
        if extra_info:
             ant_real = extra_info.get('antiguedad_real', {'y': 0, 'm': 0})
             # ant_carrera removed per request
             
             ant_total_str = f"{ant_real.get('y',0)} años, {ant_real.get('m',0)} meses"
             
             # Row 1: Global (The only one)
             pdf.cell(sum(w_c[:6]), 7, pdf.sanitize_text("Antigüedad Total (Histórica)"), 1, 0, 'R')
             pdf.cell(w_c[6], 7, pdf.sanitize_text(ant_total_str), 1, 0, 'C')
             pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')
