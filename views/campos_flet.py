import flet as ft


# TextField común
def text_field(titulo, base):
    return ft.TextField(label=titulo, hint_text=base, color='black', text_size=12)

# TextField solo numérico
def num_field(titulo, base, largo):
    return ft.TextField(label=titulo, hint_text=base, color='black', text_size=12,
                        input_filter=ft.NumbersOnlyInputFilter(), max_length=largo)

# Dropdown
def drop_field(titulo, lista):
    return ft.Dropdown(
        label=titulo,
        options=[ft.dropdown.Option(c) for c in lista],
        text_size=12,
        color='black',
        width=300
    )

def text_field_rut(titulo, base):
    campo = ft.TextField(
        label=titulo,
        hint_text=base,
        color='black',
        text_size=12,
        max_length=12  # Ajusta según lo necesites
    )

    def formatear_rut(e):
        rut = campo.value.replace(".", "").replace("-", "").upper()
        
        if not rut[:-1].isdigit() or rut[-1] not in "0123456789K":
            campo.error_text = "Formato inválido (Ej: 12.345.678-9)"
        else:
            rut_num = rut[:-1]
            dv = rut[-1]
            rut_formateado = f"{int(rut_num):,}".replace(",", ".") + f"-{dv}"
            campo.value = rut_formateado
            campo.error_text = None

        campo.update()

    campo.on_blur = formatear_rut
    return campo

def formatear_rut_simple(rut):
    rut = rut.replace(".", "").replace("-", "").upper()
    if len(rut) < 2:
        return rut
    rut_num = rut[:-1]
    dv = rut[-1]
    try:
        rut_formateado = f"{int(rut_num):,}".replace(",", ".") + f"-{dv}"
        return rut_formateado
    except ValueError:
        return rut


def text_field_calificacion(titulo, base):
    campo = ft.TextField(
        label=titulo,
        hint_text=base,
        color='black',
        text_size=12,
        max_length=4  # Ej: "6.7" o "10.0"
    )

    def validar_calificacion(e):
        valor = campo.value.strip()

        # Acepta números del 1 al 10 con un decimal opcional
        import re
        if re.fullmatch(r'^(10(\.0)?|[1-9](\.\d)?)$', valor):
            campo.error_text = None
        else:
            campo.error_text = "Ingresa una calificación válida (ej: 6 o 5.8)"

        campo.update()

    campo.on_blur = validar_calificacion
    return campo

def text_field_moneda(titulo, base=""):
    campo = ft.TextField(
        label=titulo,
        hint_text=base,
        color='black',
        text_size=12,
        keyboard_type=ft.KeyboardType.NUMBER,  # Solo permite números
    )

    def formatear_moneda(e):
        valor = campo.value.replace(".", "").strip()

        if valor.isdigit():
            valor_int = int(valor)
            campo.value = f"{valor_int:,}".replace(",", ".")  # Formato miles
            campo.error_text = None
        elif valor == "":
            campo.error_text = None  # Permitir vacío
        else:
            campo.error_text = "Solo números"
            valor = ""
        
        campo.update()

    campo.on_blur = formatear_moneda

    return campo

    


# ----------------CAMPOS USUARIO-----------------
def campos_usuario():
    nombre = text_field('(*) Nombre', 'Ingrese su nombre')
    rut = text_field_rut('(*) Rut', 'Ej: 12.345.678-9')
    genero = drop_field('(*) Género', ['Masculino', 'Femenino', 'Prefiero no decirlo'])
    profesion = text_field('(*) Profesión', 'Ingrese su profesión')
    categoria = drop_field('(*) Categoría', ['A', 'B', 'C', 'D', 'E', 'F'])
    dia_nac = num_field('(*) Día', 'EJ:01', 2)
    mes_nac = num_field('(*) Mes', 'EJ:12', 2)
    año_nac = num_field('(*) Año', 'EJ:2004', 4)

    return nombre, rut, genero, profesion, categoria, dia_nac, mes_nac, año_nac

# ----------------CAMPOS CONTRATO-----------------
def campos_contrato():
    tipo_cont = drop_field('(*) Tipo de Contrato', ['Honorario', 'Plazo fijo', 'Planta'])
    horas_cont = num_field('(*) Horas contrato', 'Indique las horas', 2)
    dependencia = drop_field('(*) Dependencia laboral', ['CESFAM CHOLCHOL', 'PSR HUENTELAR', 'PSR HUAMAQUI', 'PSR MALALCHE','OTRO'])
    cargo = text_field('(*) Cargo de desempeño', 'Ej: Administrativo')
    reemplazo = drop_field('(*) Es reemplazo:', ['SI', 'NO'])
    monto = text_field_moneda("(*) Monto Bruto en Pesos", "Ej: 1.000.000")
    tipo_inst = drop_field('(*) Tipo de Institución:', ['Centro de Salud', 'Sector Público', 'Sector Privado'])
    nom_inst = text_field('(*) Nombre de la Institución', 'Ej: Hospital____, Municipalidad de ____, etc')
    dia_inic = num_field('(*) Día', 'EJ:01', 2)
    mes_inic = num_field('(*) Mes', 'EJ:12', 2)
    año_inic = num_field('(*) Año', 'EJ:2024', 4)
    dia_ter = num_field('Día', 'EJ:01', 2)
    mes_ter = num_field('Mes', 'EJ:10', 2)
    año_ter = num_field('Año', 'EJ:2024', 4)

    return tipo_cont, horas_cont, dependencia, cargo, reemplazo,monto,tipo_inst,nom_inst, dia_inic, mes_inic, año_inic, dia_ter, mes_ter, año_ter

# ----------------CAMPOS CAPACITACIÓN-----------------
def campos_capacitacion():
    nombre_cap = text_field('(*) Nombre de la Capacitación', 'Ej: Curso de ____')
    entidad = text_field('(*) Entidad que dicta', 'Ej: Universidad _____')
    horas_cap = num_field('(*) Horas capacitación', 'Indique las horas', 4)
    nv_tec = drop_field('(*) Nivel técnico', ['Bajo', 'Medio', 'Alto'])
    nota = text_field_calificacion('(*) Calificación final','Ej:6.0, 7, 5.2')
    año_inic = num_field('(*) Año', 'Año en que se cursó la capacitación. Ej: 202X', 4)
    año_pres = num_field('(*) Año', 'Año en que se presentó a RRRHH. Ej: 202X', 4)
    cont_press = drop_field('(*) Contexto presentación', ['Ingreso a Planta', 'Cambio de Nivel'])
    post = drop_field('(*) ¿Cuenta como postgrado?', ['SI', 'NO'])

    return nombre_cap, entidad, horas_cap, nv_tec, nota, año_inic, año_pres,cont_press,post#Se agrego post

#=========================HEADER==================================

def encabezado(titulo):
    return ft.Container(
            content=ft.Row([
                ft.Text(titulo, size=22, weight="bold", color="white"),
                ft.Container(
                    content=ft.Text("Desarrollado por PHD. Alain Antinao S", size=12, color="white", italic=True),
                    alignment=ft.alignment.center_right,
                    expand=True
                )
            ]),
            bgcolor="#1976D2",
            padding=15,
            border_radius=5
        )
def pie_pagina():
    return ft.Container(
        content=ft.TextButton(
            text="🌐 Más información / Contacto",
            url="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e",
            style=ft.ButtonStyle(color="blue"),
        ),
        alignment=ft.alignment.center,
        padding=10
    )

##########Obtener archivo#############

def crear_picker_excel(page, on_result_callback):
    picker = ft.FilePicker(on_result=on_result_callback)
    page.overlay.append(picker)
    page.update()
    return picker
