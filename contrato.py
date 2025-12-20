import flet as ft
from campos_flet import *
from firebase_bd import *
from clases import *
from funciones import *
import variables
from tablas import *
from datetime import datetime

def contrato_view(page: ft.Page):
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"

    rut_red = variables.rut_actual
    contrato = campos_contrato()  # debe retornar TextFields

    # Asegura que cada campo tenga on_change para reflejar los cambios
    for c in contrato:
        c.on_change = lambda e: page.update()

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
        campo_rut.on_change = lambda e: page.update()
    else:
        campo_rut = ft.Text(f"RUT: {rut_red}", color='black')

    header = encabezado('📄 Registro de nuevo contrato')

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
                    ft.Container(
                        content=ft.Row([
                            ft.Text("👤 RUT del Funcionario:", size=14, weight="bold", color="black"),
                            campo_rut
                        ]),
                        padding=ft.padding.only(bottom=10)
                    ),
                    ft.ResponsiveRow([
                        ft.Container(contrato[0], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[1], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[2], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[4], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[3], col={"sm": 12, "md": 12}),
                        ft.Container(contrato[6], col={"sm": 6, "md": 6}),
                        ft.Container(contrato[7], col={"sm": 6, "md": 6}),
                        ft.Row([
                            ft.Column([ft.Text("🗓️ Inicio Contrato:", size=14, weight="bold", color="black")]),
                            ft.Column([ft.Text("🗓️ Fin del Contrato:", size=14, weight="bold", color="black")])
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

    tabla_contract_control = None
    id_contrato_seleccionado = None

    def cargar_contrato(e: ft.ControlEvent):
        nonlocal tabla_contract_control, id_contrato_seleccionado

        for row in tabla_contract_control.rows:
            for cell in row.cells:
                if isinstance(cell.content, ft.Checkbox):
                    cell.content.value = False
        e.control.value = True
        page.update()

        idc_sel = e.control.key
        registro_contratos = leer_registro('contrato')
        contrato_sel = registro_contratos.get(idc_sel)
        id_contrato_seleccionado = idc_sel

        if contrato_sel:
            contrato[0].value = contrato_sel.get('TIPO_CONTRATO', '')
            contrato[1].value = contrato_sel.get('HORAS', '')
            contrato[2].value = contrato_sel.get('DEPENDENCIA', '')
            contrato[3].value = contrato_sel.get('CARGO', '')
            contrato[4].value = contrato_sel.get('REEMPLAZO', '')
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
                campo_rut.value = contrato_sel.get('RUT', '')

        page.update()

    tabla_contract_control = tabla_contrato(page, cargar_contrato)

    
    def guardar_usuario(e):
        rut_final = campo_rut.value if rol_actual in ['PROGRAMADOR', 'ADMIN'] else rut_red

        print("Valores actuales de los campos:")
        for i, c in enumerate(contrato):
            print(f"Campo {i}: {c.value}")

        if not rut_final:
            mensaje.value = "⚠️ Debe seleccionar un RUT"
            mensaje.color = "red"
            page.update()
            return

        nuevo_contrato = Contrato(
            rut_red,
            contrato[0].value, contrato[1].value, contrato[2].value,
            contrato[3].value, contrato[4].value,
            contrato[6].value, contrato[7].value, contrato[8].value,
            contrato[9].value, contrato[10].value, contrato[11].value,
            contrato[12].value, contrato[13].value
        )

        campos_obligatorios_planta = [
            contrato[0].value, contrato[1].value, contrato[2].value, contrato[3].value,
            contrato[4].value, contrato[6].value, contrato[7].value,
            contrato[8].value, contrato[9].value, contrato[10].value
        ]

        campos_obligatorios_general = [
            contrato[0].value, contrato[1].value, contrato[2].value, contrato[3].value,
            contrato[4].value, contrato[6].value, contrato[7].value,
            contrato[8].value, contrato[9].value, contrato[10].value, contrato[11].value,
            contrato[12].value, contrato[13].value
        ]

        campos_incompletos = False

        if contrato[0].value == 'Planta':
            if any(c == '' for c in campos_obligatorios_planta) and any(c == '' for c in funcionario):
                mensaje.value = "⚠️ Debes completar todos los campos obligatorios"
                mensaje.color = "red"
                page.update()
                campos_incompletos = True
        else:
            if any(c == '' for c in campos_obligatorios_general):
                mensaje.value = "⚠️ Debes completar todos los campos obligatorios"
                mensaje.color = "red"
                page.update()
                campos_incompletos = True

        if not campos_incompletos:
            mensaje.value = "✅ Ingreso de datos exitoso"
            mensaje.color = "green"
            variables.rut_actual = rut_red
            page.update()

        ingresar_registro_bd('contrato', nuevo_contrato.crear_dict_contrato())
        ingresar_registro_bd('actividad',{'TIPO':'INGRESO_CONTRATO','ELEMENTO':f'{nuevo_contrato.crear_dict_contrato()}','USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_actual, leer_registro('usuarios'), leer_registro('contrato'), rut_final)

        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            campo_rut.value = ''
        for c in contrato:
            c.value = ''

        mensaje.value = "✅ Contrato ingresado correctamente"
        mensaje.color = "green"
        puntaje_nv(rut_final, leer_registro('capacitaciones'))
        page.update()

    def actualizar_usuario(e):
        nonlocal id_contrato_seleccionado
        if not id_contrato_seleccionado:
            mensaje.value = "⚠️ Seleccione un usuario para actualizar"
            mensaje.color = "red"
            page.update()
            return

        rut_final = campo_rut.value if rol_actual in ['PROGRAMADOR', 'ADMIN'] else rut_red

        nuevo_contrato = Contrato(
            rut_final, contrato[0].value, contrato[1].value, contrato[2].value,
            contrato[3].value, contrato[4].value, contrato[6].value,
            contrato[7].value, contrato[8].value, contrato[9].value, contrato[10].value,
            contrato[11].value, contrato[12].value, contrato[13].value
        )

        actualizar_registro('contrato', nuevo_contrato.crear_dict_contrato(), id_contrato_seleccionado)
        ingresar_registro_bd('actividad',{'TIPO':'ACTUALIZ_CONTRATO','ELEMENTO':f'{nuevo_contrato.crear_dict_contrato()}','USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_actual, leer_registro('usuarios'), leer_registro('contrato'), rut_final)

        mensaje.value = "✅ Contrato actualizado correctamente"
        mensaje.color = "green"
        puntaje_nv(rut_final, leer_registro('capacitaciones'))
        page.update()

    def borrar_usuario(e):
        nonlocal id_contrato_seleccionado
        if not id_contrato_seleccionado:
            mensaje.value = "⚠️ Seleccione el contrato para borrar"
            mensaje.color = "red"
            page.update()
            return

        borrar_registro('contrato', id_contrato_seleccionado)
        ingresar_registro_bd('actividad',{'TIPO':'BORRAR_CONTRATO','ELEMENTO':id_contrato_seleccionado,'USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_actual, leer_registro('usuarios'), leer_registro('contrato'), rut_red)
        

        for c in contrato:
            c.value = ''
        if rol_actual in ['PROGRAMADOR', 'ADMIN']:
            campo_rut.value = ''

        id_contrato_seleccionado = None

        mensaje.value = "✅ Contrato eliminado correctamente"
        mensaje.color = "green"
        puntaje_nv(rut_red, leer_registro('capacitaciones'))
        page.update()

    btn_guardar = ft.ElevatedButton("Guardar Contrato", width=220, icon=ft.Icons.SAVE, on_click=guardar_usuario)
    btn_actualizar = ft.ElevatedButton("Actualizar Contrato", width=220, icon=ft.Icons.UPDATE, on_click=actualizar_usuario)
    btn_borrar = ft.ElevatedButton("Borrar Contrato", width=220, icon=ft.Icons.DELETE, on_click=borrar_usuario, bgcolor=ft.Colors.RED_ACCENT_100)

    contenido = ft.Column([
        header,
        ft.Row([
            ft.Column([cont_cont, ft.Row([btn_guardar, btn_actualizar, btn_borrar], spacing=10), mensaje]),
            ft.Column([tabla_contract_control], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
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
