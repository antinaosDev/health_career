import flet as ft
from campos_flet import *
from firebase_bd import *
from clases import *
from funciones import *
import variables

def user_view(page):
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"

    rut_red = variables.rut_actual  # Recuperamos el RUT global
    data_log = leer_registro('login')
    cat_red = variables.cat_actual
    variables.reg_user = leer_registro('usuarios')
    reg = variables.reg_user
    variables.reg_contracts = leer_registro('contrato')
    conts = variables.reg_contracts

    usuario = campos_usuario()
    contrato = campos_contrato()

    header = encabezado("⚕️ Sistema de Puntaje Carrera Funcionaria - Salud")

    titulo_usuario = ft.Text("👤 Registro de Datos del Funcionario", size=18, weight="bold", color="black")

    cont_usuario = ft.Container(
        content=ft.Card(
            elevation=6,
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    titulo_usuario,
                    ft.Text("Completa los campos requeridos (*):", size=13, color="grey"),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(content=ft.Text(f"RUT: {rut_red}", color='black'), col={"sm": 6, "md": 6}),
                        ft.Container(usuario[0], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[2], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[4], col={"sm": 6, "md": 6}),
                        ft.Container(usuario[3], col={"sm": 12}),
                        ft.Text('📅 Fecha de nacimiento:', size=14, weight='bold', color='black'),
                        ft.Container(usuario[5], col={"sm": 4}),
                        ft.Container(usuario[6], col={"sm": 4}),
                        ft.Container(usuario[7], col={"sm": 4}),
                    ])
                ])
            )
        ),
        padding=20,
        width=700
    )

    titulo_contrato = ft.Text("📄 Información de Contrato", size=18, weight="bold", color="black")

    cont_cont = ft.Container(
        content=ft.Card(
            elevation=6,
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    titulo_contrato,
                    ft.Text("Completa los campos requeridos (*):", size=13, color="grey"),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(contrato[0], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[1], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[2], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[4], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[3], col={"sm": 12, "md": 12}),
                        ft.Container(contrato[6], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[7], col={"sm": 6, "md": 6}),
                        ft.Row([
                            ft.Column([ft.Text("🗓️ Inicio Contrato:", size=14, weight="bold", color="black"),
                                       ft.Text(" ", size=10, color="red")]),
                            ft.Column([ft.Text("🗓️ Fin del Contrato:", size=14, weight="bold", color="black"),
                                       ft.Text("(*) Obligatorio para Honorarios y Plazo Fijo", size=10, color="red")])
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        ft.Container(contrato[8], col={"sm": 2}),
                        ft.Container(contrato[9], col={"sm": 2}),
                        ft.Container(contrato[10], col={"sm": 2}),
                        ft.Container(contrato[11], col={"sm": 2}),
                        ft.Container(contrato[12], col={"sm": 2}),
                        ft.Container(contrato[13], col={"sm": 2}),
                    ])
                ])
            )
        ),
        padding=20,
        width=700
    )

    mensaje_campos = ft.Text('', size=12, weight='bold', color='red')

    def ingresar_registro(e):
        funcionario = Funcionario(
            usuario[0].value, rut_red, usuario[2].value,
            usuario[3].value, usuario[4].value, usuario[5].value,
            usuario[6].value, usuario[7].value
        )

        nuevo_contrato = Contrato(
            rut_red,
            contrato[0].value, contrato[1].value, contrato[2].value,
            contrato[3].value, contrato[4].value,
            contrato[6].value, contrato[7].value, contrato[8].value,
            contrato[9].value, contrato[10].value, contrato[11].value,
            contrato[12].value, contrato[13].value
        )

        campos_obligatorios_planta = [
            usuario[0].value, rut_red, usuario[2].value,
            usuario[3].value, usuario[4].value, usuario[5].value,
            usuario[6].value, usuario[7].value,
            contrato[0].value, contrato[1].value, contrato[2].value, contrato[3].value,
            contrato[4].value, contrato[6].value, contrato[7].value,
            contrato[8].value, contrato[9].value, contrato[10].value
        ]

        campos_obligatorios_general = [
            usuario[0].value, rut_red, usuario[2].value,
            usuario[3].value, usuario[4].value, usuario[5].value,
            usuario[6].value, usuario[7].value,
            contrato[0].value, contrato[1].value, contrato[2].value, contrato[3].value,
            contrato[4].value, contrato[6].value, contrato[7].value,
            contrato[8].value, contrato[9].value, contrato[10].value, contrato[11].value,
            contrato[12].value, contrato[13].value
        ]

        campos_incompletos = False

        if contrato[0].value == 'Planta':
            if any(c == '' for c in campos_obligatorios_planta):
                mensaje_campos.value = "⚠️ Debes completar todos los campos obligatorios"
                mensaje_campos.color = "red"
                page.update()
                campos_incompletos = True
        else:
            if any(c == '' for c in campos_obligatorios_general):
                mensaje_campos.value = "⚠️ Debes completar todos los campos obligatorios"
                mensaje_campos.color = "red"
                page.update()
                campos_incompletos = True

        if not campos_incompletos:
            mensaje_campos.value = "✅ Ingreso de datos exitoso, espere un momento⏳"
            mensaje_campos.color = "green"
            page.update()

            ingresar_registro_bd('usuarios', funcionario.crear_dict_func())
            ingresar_registro_bd('contrato', nuevo_contrato.crear_dict_contrato())

            datos_log = leer_registro('login')
            rol_usuario = ''

            for idx, log in datos_log.items():
                if log.get('ID') == variables.rut_actual:
                    rol_usuario = log.get('ROL', '')
                    break

            data_u = leer_registro('usuarios')
            data_c = leer_registro('contrato')
            actualizacion_horaria(rol_usuario, data_u, data_c, rut_red)

            if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
                for usr in data_u.values():
                    rut_usr = usr.get('RUT')
                    puntaje_nv(rut_usr, leer_registro('capacitaciones'))
            else:
                puntaje_nv(rut_red, leer_registro('capacitaciones'))

            page.go("/main")

    btn_guardar = ft.ElevatedButton("Guardar Registro", width=250, icon=ft.Icons.SAVE, on_click=ingresar_registro)

    footer = pie_pagina()

    contenido = ft.Column([
        header,
        cont_usuario,
        cont_cont,
        btn_guardar,
        mensaje_campos,
        footer
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll='auto')

    return ft.Container(content=contenido, expand=True, bgcolor="#F0F2F5", padding=20, alignment=ft.alignment.center)
