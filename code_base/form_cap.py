import flet as ft 
from funciones import puntaje_nv
from campos_flet import *
from clases import *
from firebase_bd import *

def cap_view(page: ft.Page):
    page.bgcolor = 'white'
    page.scroll = 'auto'

    # Cargar RUTs únicos
    registro = leer_registro('usuarios')
    lista_rut = [v.get('RUT', '') for v in registro.values()]
    ruts_unicos = list(set(lista_rut))

    # Campo desplegable de RUTs
    rut = drop_field('Seleccione su rut', ruts_unicos)
    categoria_text = ft.Text('Categoría: ', size=17,weight='BOLD',color='black')
    nombre_text = ft.Text('Nombre: ', size=17,weight='BOLD',color='black')

    capacitacion = campos_capacitacion()
    btn_guardar = ft.ElevatedButton('Guardar', on_click=lambda e: ing_cap(e))

    # Actualizar categoría cuando el usuario seleccione su RUT
    def actualizar_categoria(e):
        rut_seleccionado = rut.value
        categoria = "No encontrado"
        for v in registro.values():
            if v.get('RUT', '') == rut_seleccionado:
                categoria = v.get('CATEGORIA', 'No encontrado')
                nombre = v.get('NOMBRE_FUNC', 'No encontrado')
                break
        categoria_text.value = f'Categoría: {categoria}'
        nombre_text.value = f'Nombre: {nombre}'
        page.update()

    rut.on_change = actualizar_categoria

    # Función para guardar capacitación
    def ing_cap(e):
        if not rut.value:
            print("Debe seleccionar un RUT")
            return
        
        categoria_actual = categoria_text.value.replace('Categoría: ', '')

        cap = Capacitacion(
        rut.value,
        categoria_actual,
        capacitacion[0].value,
        capacitacion[1].value,
        capacitacion[2].value,
        capacitacion[3].value,
        capacitacion[4].value,
        capacitacion[5].value,
        capacitacion[6].value
    )

        dict_cap = cap.crear_dict_capacitacion()
        ingresar_registro_bd('capacitaciones', dict_cap)
        puntaje_nv(rut.value)
        print("Registro guardado correctamente")

    cap_cont = ft.Container(
    content=ft.Card(
        elevation=4,
        color="#FFFFFF",
        content=ft.Container(
            bgcolor="#F5F5F5",
            border_radius=12,
            padding=20,
            content=ft.Column([
                ft.Text("🎓 Ingreso de Capacitación", weight="bold", size=18, color="#333333"),
                ft.Divider(),

                ft.Row([
                    ft.Text("Selecciona el RUT:", size=14, weight="bold",color='black'),
                    rut
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Container(
                    categoria_text,
                    padding=10,
                    bgcolor="#E0E0E0",
                    border_radius=8,
                    margin=ft.margin.only(top=10, bottom=20)),

                    ft.Container(
                    nombre_text,
                    padding=10,
                    bgcolor="#E0E0E0",
                    border_radius=8,
                    margin=ft.margin.only(top=10, bottom=20))
                ],alignment=ft.MainAxisAlignment.CENTER),
 
                ft.Text("Datos de la Capacitación:", size=16, weight="bold",color='black'),
                ft.ResponsiveRow([
                    ft.Container(capacitacion[0], col=6, padding=5),  # Nombre capacitación
                    ft.Container(capacitacion[1], col=6, padding=5),  # Entidad
                    ft.Container(capacitacion[2], col=4, padding=5),  # Horas
                    ft.Container(capacitacion[3], col=4, padding=5),  # Nivel técnico
                    ft.Container(capacitacion[4], col=4, padding=5),  # Nota
                    ft.Container(ft.Column([ft.Text('Año cursado:',color='black'), capacitacion[5]]), col=6, padding=5),
                    ft.Container(ft.Column([ft.Text('Año presentado:',color='black'), capacitacion[6]]), col=6, padding=5),
                ]),

                ft.Container(
                    btn_guardar,
                    alignment=ft.alignment.center,
                    padding=10,
                    margin=ft.margin.only(top=20)
                )
            ])
        )
    ),
    padding=20,
    width=700
    )

    page.add(cap_cont)

ft.app(target=cap_view)
