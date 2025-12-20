import flet as ft
from flet import *
from firebase_bd import * 




def main(page: ft.Page):
    page.title = "Scroll horizontal y vertical"
    page.window_width = 2000
    page.window_height = 600
    
   
    data = leer_registro('capacitaciones')
    header = [v.keys() for k,v in data.items()][0]
    
    # Definir las columnas de la tabla
    col = [DataColumn(Text(f'{i}')) for i in header]
    """columns = [
        DataColumn(Text("Nombre")),
        DataColumn(Text("Edad")),
        DataColumn(Text("Ciudad")),
    ]
    """
    fil = [
        DataRow(
        cells=[DataCell(Text(str(dict.get(key, "")))) for key in header]
    )
    for dict in data.values()
]
    """#valores de las filas
    for dict in data.values():
        for row in dict.values():
            print(row)"""
    """
        # Definir las filas con valores
        rows = [
            DataRow(cells=[
                DataCell(Text("Juan")),
                DataCell(Text("28")),
                DataCell(Text("Madrid")),
            ]),
            DataRow(cells=[
                DataCell(Text("Ana")),
                DataCell(Text("34")),
                DataCell(Text("Barcelona")),
            ]),
            DataRow(cells=[
                DataCell(Text("Luis")),
                DataCell(Text("23")),
                DataCell(Text("Valencia")),
            ]),
        ]"""

    # Crear la tabla y añadirla a la página
    table = DataTable(
        columns=col,
        rows=fil,
        border=ft.border.all(1, ft.Colors.GREY_400),
        heading_row_color=ft.Colors.BLUE_700)
    # Envolver tabla en Row (scroll horizontal)
    horizontal_scroll = ft.Row(
        controls=[
            ft.Container(content=table, width=1200)  # Forzar scroll horizontal
        ],
        scroll="auto",
    )

    # Envolver Row en ListView para scroll vertical
    scrollable_view = ft.ListView(
        controls=[horizontal_scroll],
        expand=True,
        padding=10,
        spacing=10
    )

    page.add(scrollable_view)

ft.app(target=main)