import flet as ft
from flet import *
from firebase_bd import *
import variables

def table_view(page, rut):

    """columns = [
        DataColumn(Text("Nombre")),
        DataColumn(Text("Edad")),
        DataColumn(Text("Ciudad")),
    ]
    """
    """rows = [
            DataRow(cells=[
                DataCell(Text("Juan")),
                DataCell(Text("28")),
                DataCell(Text("Madrid")),
            ]),
            DataRow(cells=[
                DataCell(Text("Ana")),
                DataCell(Text("34")),
                DataCell(Text("Barcelona")),
            ])
    ]"""
        
    page.scroll = 'auto'
    data_cap = leer_registro('capacitaciones')
    encabezado = ['RUT','AÑO_INICIO','AÑO_PRESENTACION','NOMBRE_CAPACITACION','NOTA','HORAS','NIVEL_TECNICO','PJE_POND']

    cols = [DataColumn(Text(f'{col}')) for col in encabezado]
    
    filas = [
    ft.DataRow(
        cells=[
            ft.DataCell(
                ft.Container(
                    content=ft.Text(
                        str(caps.get(k, '')),
                        max_lines=4,
                        overflow="ellipsis"
                    ),
                    width=680 if k == 'NOMBRE_CAPACITACION' else None
                )
            )
            for k in encabezado
        ]
    )
    for caps in data_cap.values()
    if caps.get('RUT', '') == rut
]




    table = ft.DataTable(
    columns=cols,
    rows=filas,
    heading_row_color=ft.Colors.BLUE_700,
    column_spacing=20,
    divider_thickness=1,
    border=ft.border.all(1, ft.Colors.GREY_400),
    show_checkbox_column=False,
    horizontal_margin=10,
    heading_text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
    data_text_style=ft.TextStyle(size=12,color='black'),
)

    
    return table
    """ page.add(table)
    ft.app(target=main)"""


def tabla_contrato_view(page:ft.Page):
    datos_contratos = leer_registro('contrato')

    encabezados = [nom_col for nom_col in datos_contratos.values()][0]
    encabezados = ['CARGO', 'DEPENDENCIA', 'FECHA_INICIO', 
                   'HORAS', 'NOMBRE_INSTITUCION', 'REEMPLAZO', 'RUT', 
                   'TIPO_CONTRATO', 'TIPO_INSTITUCION']

    columnas = [DataColumn(Text(f'{col}')) for col in encabezados]

    filas = [
        DataRow(
            cells= [
                DataCell(Text(str(i.get(k)))) for k in encabezados
            ]
        )
        for i in datos_contratos.values() 
    ]
    
    table = ft.DataTable(
        columns=columnas,
        rows= filas
    )

    return table
    """page.add(table)

    print(encabezados)
ft.app(target=tabla_contrato_view)"""



def tabla_user(page, cargar_usuario_callback):
    data_user = leer_registro('usuarios')
    encabezados = ['RUT', 'NOMBRE_FUNC', 'CATEGORIA']

    columnas = [ft.DataColumn(ft.Text(col)) for col in encabezados]
    columnas.append(ft.DataColumn(ft.Text("Seleccionar")))  # Columna checkbox

    filas = []
    for i in data_user.values():
        celdas = [ft.DataCell(ft.Text(str(i.get(k, '')), color="black")) for k in encabezados]

        # Checkbox con clave o data = RUT para identificar al usuario
        chk = ft.Checkbox(key=i.get('RUT'), on_change=cargar_usuario_callback)

        celdas.append(ft.DataCell(chk))
        filas.append(ft.DataRow(cells=celdas))

    tabla = ft.DataTable(
        columns=columnas,
        rows=filas,
        heading_row_color='blue'
    )

    return tabla


def tabla_contrato(page: ft.Page, cargar_contrato_fn):
    rut_actual = variables.rut_actual

    data_login = leer_registro('login')
    rol_actual = None
    for _, log in data_login.items():
        if log.get('ID') == rut_actual:
            rol_actual = log.get('ROL')
            break

    registros_contrato = leer_registro('contrato')
    encabezados = ['RUT', 'CARGO', 'DEPENDENCIA', 'HORAS']

    columnas = [ft.DataColumn(ft.Text(col)) for col in encabezados]
    columnas.append(ft.DataColumn(ft.Text("Seleccionar")))  # Columna checkbox al final

    filas = []
    for idc, contrato in registros_contrato.items():  # <-- ahora usamos el ID del contrato
        rut = contrato.get("RUT", "")
        if rol_actual not in ['ADMIN', 'PROGRAMADOR'] and rut != rut_actual:
            continue

        celdas = [ft.DataCell(ft.Text(str(contrato.get(c, '')), color="black")) for c in encabezados]

        chk = ft.Checkbox(key=idc, on_change=cargar_contrato_fn)  # <-- clave única del contrato
        celdas.append(ft.DataCell(chk))

        filas.append(ft.DataRow(cells=celdas))

    tabla = ft.DataTable(
        columns=columnas,
        rows=filas,
        heading_row_color='blue'
    )

    return tabla



def tabla_capacitacion(page, on_select):
    registros = leer_registro("capacitaciones")
    checkboxes = []  # Para desmarcar los demás al seleccionar uno

    # Esta función se llama cuando el checkbox cambia
    def checkbox_changed(e):
        # Desmarcar los demás checkboxes cuando uno se selecciona
        for cb in checkboxes:
            if cb != e.control:
                cb.value = False
                cb.update()
        on_select(e)

    # Encabezados de la tabla
    encabezados = ["RUT", "NOMBRE_CAPACITACION", "AÑO_PRESENTACION"]
    columnas = [ft.DataColumn(ft.Text(col)) for col in encabezados]
    columnas.append(ft.DataColumn(ft.Text("Seleccionar")))  # Columna checkbox al final

    # Filas de la tabla con los datos de cada capacitación
    filas = []
    for cap in registros.values():
        rut = cap.get("RUT", "")
        nombre = cap.get("NOMBRE_CAPACITACION", "")
        año_presentacion = cap.get("AÑO_PRESENTADO", "")
        
        # Crea una clave única para cada checkbox, para poder identificar cuál fue seleccionado
        key = f"{rut}|{nombre}"

        # Crear el checkbox para esta fila
        checkbox = ft.Checkbox(key=key, on_change=checkbox_changed)
        checkboxes.append(checkbox)

        # Crear las celdas de esta fila
        celdas = [
            ft.DataCell(ft.Text(str(rut), color="black")),
            ft.DataCell(ft.Text(str(nombre), color="black")),
            ft.DataCell(ft.Text(str(año_presentacion), color="black")),
            ft.DataCell(checkbox)  # Agregar el checkbox como última celda
        ]
        filas.append(ft.DataRow(cells=celdas))  # Añadir la fila a la tabla

    # Crear la tabla con las columnas y filas
    tabla = ft.DataTable(
        columns=columnas,
        rows=filas,
        heading_row_color='blue'
    )

    return tabla
