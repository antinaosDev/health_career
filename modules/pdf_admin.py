from fpdf import FPDF
import datetime
import os

class GlobalReport(FPDF):
    def __init__(self, logo_path=None, logo_company_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.logo_company_path = logo_company_path
        
    def header(self):
        # Logos
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, 25)
        if self.logo_company_path and os.path.exists(self.logo_company_path):
            self.image(self.logo_company_path, 175, 8, 25)
            
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Informe de Gestión Global', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Departamento de Salud Familiar', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generado el: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        
        # Left: System
        self.cell(0, 10, 'Sistema de Gestión de Carrera Funcionaria', 0, 0, 'L')
        
        # Center: Developer
        self.set_x(0)
        self.cell(0, 10, 'Desarrollado por Alain Antinao Sepúlveda', 0, 0, 'C')
        
        # Right: Page
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'R')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(0, 109, 182) # Brand Blue
        self.set_text_color(255)
        self.cell(0, 8, f'  {label}', 0, 1, 'L', 1)
        self.set_text_color(0)
        self.ln(4)

    def add_chart_pair(self, img_path1, img_path2, title1="", title2=""):
        y = self.get_y()
        # Chart 1
        if img_path1 and os.path.exists(img_path1):
            self.image(img_path1, x=10, y=y, w=90)
        else:
            self.set_xy(10, y+20)
            self.set_font('Arial', 'I', 8)
            self.cell(90, 10, "Gráfico no disponible", 1, 0, 'C')
            
        # Chart 2
        if img_path2:
            if os.path.exists(img_path2):
                self.image(img_path2, x=110, y=y, w=90)
            else:
                self.set_xy(110, y+20)
                self.set_font('Arial', 'I', 8)
                self.cell(90, 10, "Gráfico no disponible", 1, 0, 'C')
            
        self.set_xy(10, y+65) # Move down (assuming chart height ~60)
        
        # Titles
        self.set_font('Arial', 'B', 9)
        self.cell(90, 5, title1, 0, 0, 'C')
        self.cell(10, 5, "", 0, 0) # Gap
        self.cell(90, 5, title2, 0, 1, 'C')
        self.ln(10)

def create_global_pdf(kpis, charts_paths, upgrades_data, logo_path, logo_c_path):
    pdf = GlobalReport(logo_path, logo_c_path)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- 1. RESUMEN EJECUTIVO (KPIs) ---
    pdf.chapter_title("Resumen Ejecutivo")
    pdf.set_font('Arial', '', 10)
    
    # 4 Col Grid
    w = 47.5
    h = 20
    
    # Headers
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240)
    pdf.cell(w, 8, "Gasto Mensual", 1, 0, 'C', 1)
    pdf.cell(w, 8, "Dotación Total", 1, 0, 'C', 1)
    pdf.cell(w, 8, "Total Contratos", 1, 0, 'C', 1)
    pdf.cell(w, 8, "Sueldo Promedio", 1, 1, 'C', 1)
    
    # Values
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(w, 12, kpis['gasto'], 1, 0, 'C')
    pdf.cell(w, 12, str(kpis['dotacion']), 1, 0, 'C')
    pdf.cell(w, 12, str(kpis['contratos']), 1, 0, 'C')
    pdf.cell(w, 12, kpis['promedio'], 1, 1, 'C')
    pdf.ln(10)
    
    # --- 2. DOTACION Y CONTRATOS ---
    pdf.chapter_title("Análisis Estructural")
    pdf.add_chart_pair(
        charts_paths.get('cat_counts'), 
        charts_paths.get('tipo_counts'), 
        "Distribución por Categoría",
        "Tipos de Contrato"
    )
    
    pdf.add_chart_pair(
        charts_paths.get('sex_counts'),
        None,
        "Distribución por Género",
        ""
    )
    
    # --- 3. ANALISIS FINANCIERO ---
    pdf.chapter_title("Análisis Financiero")
    pdf.add_chart_pair(
        charts_paths.get('cat_cost'), 
        charts_paths.get('prof_cost'), 
        "Costo Global por Categoría",
        "Top Profesiones (Mayor Gasto)"
    )
    
    pdf.add_page()
    
    # --- 4. COSTOS UNITARIOS ---
    pdf.chapter_title("Costos Unitarios Promedio")
    pdf.add_chart_pair(
        charts_paths.get('prof_avg'), 
        charts_paths.get('cat_avg'), 
        "Costo Promedio: Profesiones",
        "Costo Promedio: Categorías"
    )
    
    # --- 5. PREDICTIVO DE ASCENSOS ---
    pdf.chapter_title("Proyección de Ascensos")
    
    # Table 1: Inmediatos
    imm = upgrades_data.get('immediate', [])
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, f"Ascensos Inmediatos / Pendientes ({len(imm)})", 0, 1)
    
    if imm:
        pdf.set_font('Arial', 'B', 8)
        # Func(50), Rut(20), Cat(10), N.Act(15), N.New(15), Causa(50), Impact(25)
        # Total 185
        wc = [55, 20, 10, 15, 15, 45, 25]
        hnds = ['Funcionario', 'RUT', 'Cat', 'N.Act', 'N.Nue', 'Causa', 'Impacto']
        
        for i, h in enumerate(hnds):
            pdf.cell(wc[i], 6, h, 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 7)
        for u in imm:
            pdf.cell(wc[0], 6, str(u['Funcionario'])[:30], 1)
            pdf.cell(wc[1], 6, str(u['RUT']), 1, 0, 'C')
            pdf.cell(wc[2], 6, str(u['Cat']), 1, 0, 'C')
            pdf.cell(wc[3], 6, str(u['Nivel Actual']), 1, 0, 'C')
            pdf.cell(wc[4], 6, str(u['Nivel Nuevo']), 1, 0, 'C')
            pdf.cell(wc[5], 6, str(u['Causa'])[:35], 1)
            pdf.cell(wc[6], 6, f"${int(u['Impacto Mensual']):,}".replace(',', '.'), 1, 0, 'R')
            pdf.ln()
        
        cost_im = sum([u['Impacto Mensual'] for u in imm])
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(sum(wc[:-1]), 6, "Total Impacto Mensual", 1, 0, 'R')
        pdf.cell(wc[-1], 6, f"${int(cost_im):,}".replace(',', '.'), 1, 0, 'R')
        pdf.ln(8)
    else:
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 8, "No se detectan ascensos pendientes.", 0, 1)
        pdf.ln(5)

    # Table 2: Proximos
    upc = upgrades_data.get('upcoming', [])
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, f"Proyección a 60 Días ({len(upc)})", 0, 1)
    
    if upc:
        pdf.set_font('Arial', 'B', 8)
        # Func(55), Rut(20), Cat(10), N.Act(15), N.Pro(15), Dias(20), Impact(50) -> Adjusted
        wc = [55, 20, 10, 15, 15, 20, 25]
        hnds = ['Funcionario', 'RUT', 'Cat', 'N.Act', 'N.Pro', 'Días Rest.', 'Impacto']
        
        for i, h in enumerate(hnds):
            pdf.cell(wc[i], 6, h, 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 7)
        for u in upc:
            pdf.cell(wc[0], 6, str(u['Funcionario'])[:30], 1)
            pdf.cell(wc[1], 6, str(u['RUT']), 1, 0, 'C')
            pdf.cell(wc[2], 6, str(u['Cat']), 1, 0, 'C')
            pdf.cell(wc[3], 6, str(u['Nivel Actual']), 1, 0, 'C')
            pdf.cell(wc[4], 6, str(u['Nivel Proy.']), 1, 0, 'C')
            pdf.cell(wc[5], 6, str(u['Días Restantes']), 1, 0, 'C')
            pdf.cell(wc[6], 6, f"${int(u['Impacto Mensual']):,}".replace(',', '.'), 1, 0, 'R')
            pdf.ln()

        cost_up = sum([u['Impacto Mensual'] for u in upc])
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(sum(wc[:-1]), 6, "Total Proyectado", 1, 0, 'R')
        pdf.cell(wc[-1], 6, f"${int(cost_up):,}".replace(',', '.'), 1, 0, 'R')
    else:
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 8, "No se proyectan cambios en el corto plazo.", 0, 1)

    return pdf.output(dest='S').encode('latin-1')
