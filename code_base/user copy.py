import flet as ft
from campos_flet import *
from firebase_bd import *
from clases import *
import variables
from funciones import *
from tablas import * 

def crear_usuario_view(page):
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"

    rut_red = variables.rut_actual
    usuario = campos_usuario()
    contrato = campos_contrato()
    mensaje = ft.Text('', size=12, weight='bold', color='red')

    registro = leer_registro('usuarios')
    lista_rut = [v.get('RUT', '') for v in registro.values()]
    ruts_unicos = list(set(lista_rut))

    data_log = leer_registro('login')
    rol_actual = None

    for _, log in data_log.items():
        if log.get('ID') == rut_red:
            rol_actual = log.get('ROL')
            break

    if rol_actual in ['PROGRAMADOR', 'ADMIN']:
        campo_rut = text_field_rut('Ingrese RUT', 'Ej: 12.345.678-9')
    else:
        campo_rut = ft.Text(f"RUT: {rut_red}", color='black')

    header = encabezado('👤 Registro de Nuevo Funcionario')
    cont_usuario = ft.Container(
        content=ft.Card(
            elevation=6,
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("Complete los campos requeridos (*):", size=13, color="grey"),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(content=campo_rut, col={"sm": 6, "md": 6}),
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

    cont_cont = ft.Container(
        content=ft.Card(
            elevation=6,
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=20,
                content=ft.Column([
                    ft.Text("📄 Información de Contrato", size=18, weight="bold", color="black"),
                    ft.Text("Complete los campos requeridos (*):", size=13, color="grey"),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(contrato[0], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[1], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[2], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[4], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[3], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[5], col={"sm": 6, "md": 6}),
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

    def guardar_usuario(e):
        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            rut_final = campo_rut.value
        else:
            rut_final = rut_red

        if not rut_final:
            mensaje.value = "⚠️ Debe ingresar un RUT"
            mensaje.color = "red"
            page.update()
            return

        funcionario = Funcionario(
            usuario[0].value, rut_final, usuario[2].value,
            usuario[3].value, usuario[4].value, usuario[5].value,
            usuario[6].value, usuario[7].value
        )

        nuevo_contrato = Contrato(
            rut_final, contrato[0].value, contrato[1].value, contrato[2].value,
            contrato[3].value, contrato[4].value, contrato[5].value, contrato[6].value,
            contrato[7].value, contrato[8].value, contrato[9].value, contrato[10].value,
            contrato[11].value, contrato[12].value, contrato[13].value
        )

        campos_obligatorios = [
            rut_final, usuario[0].value, usuario[2].value, usuario[3].value,
            usuario[4].value, usuario[5].value, usuario[6].value, usuario[7].value,
            contrato[0].value, contrato[1].value, contrato[2].value, contrato[3].value,
            contrato[4].value, contrato[5].value, contrato[6].value, contrato[7].value,
            contrato[8].value, contrato[9].value, contrato[10].value, contrato[11].value,
            contrato[12].value, contrato[13].value
        ]

        if any(c == '' for c in campos_obligatorios):
            mensaje.value = "⚠️ Debes completar todos los campos obligatorios"
            mensaje.color = "red"
            page.update()
            return

        ingresar_registro_bd('usuarios', funcionario.crear_dict_func())
        ingresar_registro_bd('contrato', nuevo_contrato.crear_dict_contrato())

        reg = leer_registro('usuarios')
        conts = leer_registro('contrato')

        if rol_actual in ['PROGRAMADOR', 'ADMIN']:

            if reg:
                for idx, v in reg.items():
                    inicio = v.get('FECHA_NAC', '')
                    edad = calculo_años(inicio)
                    actualizar_registro('usuarios', {'EDAD': edad}, idx)
            if conts:
                for idc, vc in conts.items():
                    in_c = vc.get('FECHA_INICIO', 0)
                    ter_c = vc.get('FECHA_TERMINO', 0)
                    if vc.get('TIPO_CONTRATO') == 'Planta':
                        ant = calculo_años(in_c)
                        actualizar_registro('contrato', {'ANTIGUEDAD': ant}, idc)
                    else:
                        ant = calculo_años(in_c, ter_c)
                        actualizar_registro('contrato', {'ANTIGUEDAD': ant}, idc)
        else:
            if reg:
                for idx, v in reg.items():
                    inicio = v.get('FECHA_NAC', '')
                    rut_verif = v.get('RUT','')
                    if rut_verif == rut_final:
                        edad = calculo_años(inicio)
                        actualizar_registro('usuarios', {'EDAD': edad}, idx)
            if conts:
                for idc, vc in conts.items():
                    in_c = vc.get('FECHA_INICIO', 0)
                    ter_c = vc.get('FECHA_TERMINO', 0)
                    rut_verif = vc.get('RUT','')
                    if rut_verif == rut_final:
                        if vc.get('TIPO_CONTRATO') == 'Planta':
                            ant = calculo_años(in_c)
                            actualizar_registro('contrato', {'ANTIGUEDAD': ant}, idc)
                        else:
                            ant = calculo_años(in_c, ter_c)
                            actualizar_registro('contrato', {'ANTIGUEDAD': ant}, idc)

        registro_u = leer_registro('usuarios')
        lista_rut = [v.get('RUT', '') for v in registro.values()]
        ruts_unicos = list(set(lista_rut))
        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            for r in ruts_unicos:
                puntaje_nv(r)
        else:
            for idus,vus in registro_u.items():
                if vus.get('RUT') == rut_final:
                    puntaje_nv(rut_final)


        mensaje.value = "✅ Usuario y contrato registrados exitosamente"
        mensaje.color = "green"
        page.update()

    btn_guardar = ft.ElevatedButton("Guardar Usuario y Contrato", width=250, icon=ft.Icons.SAVE, on_click=guardar_usuario)

    footer = pie_pagina()

    contenido = ft.Column(
    [
        header,
        ft.Row(
            [
                ft.Column(
                    [
                        cont_usuario,
                        cont_cont,
                        btn_guardar,
                        mensaje,
                    ],
                    alignment=ft.MainAxisAlignment.START  # Alineación vertical hacia arriba
                ),
                ft.Column(
                    [
                        tabla_user(page)
                    ],
                    alignment=ft.MainAxisAlignment.START,  # Alinea la tabla arriba
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Centra horizontalmente
                ),
            ],
            alignment=ft.MainAxisAlignment.START,  # Asegura que las columnas se ubiquen desde arriba
            vertical_alignment=ft.CrossAxisAlignment.START  # Alinea verticalmente desde arriba
        ),
        footer
    ],
    alignment=ft.MainAxisAlignment.START,  # Coloca el contenido de la columna superiormente
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    expand=True,
    scroll="auto"
)

    return ft.Container(
        content=contenido,
        expand=True,
        bgcolor="#F0F2F5",
        padding=20,
        alignment=ft.alignment.top_center  # Centrado horizontalmente, arriba verticalmente
    )
