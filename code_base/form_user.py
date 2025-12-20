import flet as ft
from campos_flet import *
from firebase_bd import *
from clases import *
from funciones import *


def user_view(page: ft.Page):
    page.bgcolor = "white"
    page.scroll = "auto"

    """reg = leer_registro('usuarios')
    edades = []
    total_hombres = 0
    total_mujeres = 0

    if reg:
        for idx, v in reg.items():
            inicio = v.get('FECHA_NAC', '')
            edad = calculo_años(inicio)
            
            if edad is not None:
                edades.append(edad)
                actualizar_registro('usuarios', {'EDAD': edad}, idx)

            genero = v.get('GENERO', '').upper()
            if genero == 'MASCULINO':
                total_hombres += 1
            elif genero == 'FEMENINO':
                total_mujeres += 1
"""
    usuario = campos_usuario()
    contrato = campos_contrato()

    cont_usuario = ft.Container(
        content=ft.Card(
            elevation=4,
            color="#FFFFFF",
            content=ft.Container(
                bgcolor="#F5F5F5",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("👥 Datos del Usuario", weight="bold", size=16, color="black"),
                    ft.ResponsiveRow([
                        ft.Container(usuario[0], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[1], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[2], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[4], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[3], col={"sm": 12}),
                        ft.Text('📅 Fecha de nacimiento:', size=14, weight='bold', color='black',text_align=ft.VerticalAlignment.CENTER),
                        ft.Container(usuario[5], col={"sm": 4}),
                        ft.Container(usuario[6], col={"sm": 4}),
                        ft.Container(usuario[7], col={"sm": 4}),
                    ])
                ])
            )
        ),
        padding=20,
        width=600
    )

    cont_cont = ft.Container(
        content=ft.Card(
            elevation=4,
            color="#FFFFFF",
            content=ft.Container(
                bgcolor="#F5F5F5",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("📄 Datos del Contrato", weight="bold", size=16, color="black"),
                    ft.ResponsiveRow([
                        ft.Container(contrato[0], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[1], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[2], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[4], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[3], col={"sm": 12}),
                        ft.Row([ft.Text("🗓️ Inicio del Contrato:", size=14, weight="bold", color="black"),
                                ft.Text("🗓️ Fin del Contrato:", size=14, weight="bold", color="black")],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.START),
                        ft.Container(contrato[5], col={"sm": 2}),
                        ft.Container(contrato[6], col={"sm": 2}),
                        ft.Container(contrato[7], col={"sm": 2}),
                        ft.Container(contrato[8], col={"sm": 2}),
                        ft.Container(contrato[9], col={"sm": 2}),
                        ft.Container(contrato[10], col={"sm": 2}),
                    ])
                ])
            )
        ),
        padding=20,
        width=600
    )

    def ingresar_registro(e):
        funcionario = Funcionario(*usuario)
        campos_cont = contrato

        nuevo_contrato = Contrato(
            usuario[1].value,
            campos_cont[0].value,
            campos_cont[1].value,
            campos_cont[2].value,
            campos_cont[3].value,
            campos_cont[4].value,
            campos_cont[5].value,
            campos_cont[6].value,
            campos_cont[7].value,
            campos_cont[8].value,
            campos_cont[9].value,
            campos_cont[10].value
        )

        ingresar_registro_bd('usuarios', funcionario.crear_dict_func())
        ingresar_registro_bd('contrato', nuevo_contrato.crear_dict_contrato())

    btn_guardar = ft.ElevatedButton("Guardar Registro",width= 250,icon=ft.Icons.SAVE, on_click=ingresar_registro)

    page.add(
        ft.Row([
            ft.Column([
                cont_usuario,
                cont_cont,
                btn_guardar
            ])],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.START)
    )

ft.app(target=user_view)
