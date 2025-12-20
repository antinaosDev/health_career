import flet as ft
from campos_flet import *
from firebase_bd import *
from clases import *
from funciones import *
import variables
from tablas import *
from datetime import datetime

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
        campo_rut = text_field_rut('Ingrese RUT', 'Ej:12.345.678-9')
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

    tabla_user_control = None

    # Variables para guardar los IDs seleccionados de usuario y contrato
    id_usuario_seleccionado = None
    id_contrato_seleccionado = None

    def cargar_usuario(e: ft.ControlEvent):
        nonlocal tabla_user_control, id_usuario_seleccionado, id_contrato_seleccionado
        # Deseleccionar todos los checkbox
        for row in tabla_user_control.rows:
            for cell in row.cells:
                if isinstance(cell.content, ft.Checkbox):
                    cell.content.value = False
        e.control.value = True
        page.update()

        rut_sel = e.control.key
        registro_usuarios = leer_registro('usuarios')
        registro_contratos = leer_registro('contrato')

        id_usuario_seleccionado = None
        id_contrato_seleccionado = None

        usuario_sel = None
        for idu, u in registro_usuarios.items():
            if u.get('RUT') == rut_sel:
                usuario_sel = u
                id_usuario_seleccionado = idu
                break

        contrato_sel = None
        for idc, c in registro_contratos.items():
            if c.get('RUT') == rut_sel:
                contrato_sel = c
                id_contrato_seleccionado = idc
                break

        if usuario_sel:
            usuario[0].value = usuario_sel.get('NOMBRE_FUNC', '')
            usuario[1].value = usuario_sel.get('RUT', '')
            usuario[2].value = usuario_sel.get('GENERO', '')
            usuario[3].value = usuario_sel.get('PROFESION', '')
            usuario[4].value = usuario_sel.get('CATEGORIA', '')

            fecha_nac = usuario_sel.get('FECHA_NAC', '')
            if fecha_nac and '/' in fecha_nac:
                partes = fecha_nac.split('/')
                if len(partes) == 3:
                    usuario[5].value = partes[0]
                    usuario[6].value = partes[1]
                    usuario[7].value = partes[2]

        if contrato_sel:
            contrato[0].value = contrato_sel.get('TIPO_CONTRATO', '')
            contrato[1].value = contrato_sel.get('HORAS', '')
            contrato[2].value = contrato_sel.get('DEPENDENCIA', '')
            contrato[3].value = contrato_sel.get('CARGO', '')
            contrato[4].value = contrato_sel.get('REEMPLAZO', '')
            #contrato[5].value = contrato_sel.get('SUELDO_BRUTO', '')
            contrato[6].value = contrato_sel.get('TIPO_INSTITUCION', '')
            contrato[7].value = contrato_sel.get('NOMBRE_INSTITUCION', '')

            fecha_inicio = contrato_sel.get('FECHA_INICIO', '')
            if fecha_inicio and '/' in fecha_inicio:
                partes = fecha_inicio.split('/')
                if len(partes) == 3:
                    contrato[8].value = partes[0]
                    contrato[9].value = partes[1]
                    contrato[10].value = partes[2]

            fecha_termino = contrato_sel.get('FECHA_TERMINO', '')
            if fecha_termino and '/' in fecha_termino:
                partes = fecha_termino.split('/')
                if len(partes) == 3:
                    contrato[11].value = partes[0]
                    contrato[12].value = partes[1]
                    contrato[13].value = partes[2]

        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            campo_rut.value = rut_sel

        page.update()

    tabla_user_control = tabla_user(page, cargar_usuario)

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
            contrato[3].value, contrato[4].value, contrato[6].value,
            contrato[7].value, contrato[8].value, contrato[9].value, contrato[10].value,
            contrato[11].value, contrato[12].value, contrato[13].value
        )

        campos_obligatorios = [
            rut_final, usuario[0].value, usuario[2].value, usuario[3].value,
            usuario[4].value, usuario[5].value, usuario[6].value, usuario[7].value,
            contrato[0].value, contrato[1].value, contrato[2].value, contrato[3].value,
            contrato[4].value, contrato[6].value, contrato[7].value,
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
        ingresar_registro_bd('actividad',{'TIPO':'INGRESO_USUARIO','ELEMENTO':f'{nuevo_contrato.crear_dict_contrato()}','USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_actual,leer_registro('usuarios'),leer_registro('contrato'),rut_final)

        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            campo_rut.value = ''
        for c in usuario + contrato:
            c.value = ''

        mensaje.value = "✅ Usuario y contrato ingresados correctamente"
        mensaje.color = "green"
        page.update()

    # Función actualizar registros usuario y contrato
    def actualizar_usuario(e):
        nonlocal id_usuario_seleccionado, id_contrato_seleccionado
        if not id_usuario_seleccionado or not id_contrato_seleccionado:
            mensaje.value = "⚠️ Seleccione un usuario para actualizar"
            mensaje.color = "red"
            page.update()
            return

        rut_final = campo_rut.value if rol_actual in ['PROGRAMADOR', 'ADMIN'] else rut_red

        funcionario = Funcionario(
            usuario[0].value, rut_final, usuario[2].value,
            usuario[3].value, usuario[4].value, usuario[5].value,
            usuario[6].value, usuario[7].value
        )
        nuevo_contrato = Contrato(
            rut_final, contrato[0].value, contrato[1].value, contrato[2].value,
            contrato[3].value, contrato[4].value, contrato[6].value,
            contrato[7].value, contrato[8].value, contrato[9].value, contrato[10].value,
            contrato[11].value, contrato[12].value, contrato[13].value
        )

        actualizar_registro('usuarios', funcionario.crear_dict_func(), id_usuario_seleccionado)
        actualizar_registro('contrato', nuevo_contrato.crear_dict_contrato(), id_contrato_seleccionado)
        ingresar_registro_bd('actividad',{'TIPO':'ACTUALIZACION_USUARIO','ELEMENTO':f'{nuevo_contrato.crear_dict_contrato()}','USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_actual,leer_registro('usuarios'),leer_registro('contrato'),rut_final)

        mensaje.value = "✅ Usuario y contrato actualizados correctamente"
        mensaje.color = "green"
        page.update()

    # Función borrar registros usuario y contrato
    def borrar_usuario(e):
        nonlocal id_usuario_seleccionado, id_contrato_seleccionado
        if not id_usuario_seleccionado or not id_contrato_seleccionado:
            mensaje.value = "⚠️ Seleccione un usuario para borrar"
            mensaje.color = "red"
            page.update()
            return

        borrar_registro('usuarios', id_usuario_seleccionado)
        borrar_registro('contrato', id_contrato_seleccionado)
        ingresar_registro_bd('actividad',{'TIPO':'BORRAR_USUARIO','ELEMENTO':id_usuario_seleccionado,'USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_actual,leer_registro('usuarios'),leer_registro('contrato'),rut_red)
        

        for c in usuario + contrato:
            c.value = ''
        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            campo_rut.value = ''

        id_usuario_seleccionado = None
        id_contrato_seleccionado = None

        mensaje.value = "✅ Usuario y contrato eliminados correctamente"
        mensaje.color = "green"
        page.update()

        # Podrías refrescar la tabla o recargar la vista aquí si quieres

    btn_guardar = ft.ElevatedButton("Guardar Usuario y Contrato", width=220, icon=ft.Icons.SAVE, on_click=guardar_usuario)
    btn_actualizar = ft.ElevatedButton("Actualizar Usuario y Contrato", width=220, icon=ft.Icons.UPDATE, on_click=actualizar_usuario)
    btn_borrar = ft.ElevatedButton("Borrar Usuario y Contrato", width=220, icon=ft.Icons.DELETE, on_click=borrar_usuario, bgcolor=ft.Colors.RED_ACCENT_100)

    contenido = ft.Column([
        header,
        ft.Row([
            ft.Column([
                cont_usuario,
                cont_cont,
                ft.Row([btn_guardar, btn_actualizar, btn_borrar], spacing=10),
                mensaje
            ], alignment=ft.MainAxisAlignment.START),
            ft.Column([tabla_user_control], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
        pie_pagina()
    ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll="auto")

    return ft.Container(
        content=contenido,
        expand=True,
        bgcolor="#F0F2F5",
        padding=20,
        alignment=ft.alignment.top_center
    )
