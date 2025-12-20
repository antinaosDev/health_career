import flet as ft
from funciones import *
from campos_flet import *
from clases import *
from firebase_bd import *
import variables
from tablas import *
from clases import *
from datetime import datetime

def cap_view(page):
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"

    rut_red = variables.rut_actual
    registro = leer_registro('usuarios')
    lista_rut = [v.get('RUT', '') for v in registro.values()]
    ruts_unicos = list(set(lista_rut))

    data_log = leer_registro('login')
    rol_usuario = ''

    for idx, log in data_log.items():
        if log.get('ID') == rut_red:
            rol_usuario = log.get('ROL', '')
            break

    categoria_text = ft.Text('Categoría: ', size=16, weight='bold', color='black')
    nombre_text = ft.Text('Nombre: ', size=16, weight='bold', color='black')
    mensaje = ft.Text('', size=12, weight='bold', color='red')

    capacitacion = campos_capacitacion()

    if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
        campo_rut = text_field_rut('Ingrese RUT', 'Ej: 11.111.111-1')

        def actualizar_categoria(e):
            rut_seleccionado = campo_rut.value.replace('.', '').replace('-', '').upper()
            categoria = "No encontrado"
            nombre = "No encontrado"
            for v in registro.values():
                if v.get('RUT', '').replace('.', '').replace('-', '').upper() == rut_seleccionado:
                    categoria = v.get('CATEGORIA', 'No encontrado')
                    nombre = v.get('NOMBRE_FUNC', 'No encontrado')
                    break
            categoria_text.value = f'Categoría: {categoria}'
            nombre_text.value = f'Nombre: {nombre}'
            page.update()

        campo_rut.on_blur = actualizar_categoria

    else:
        campo_rut = rut_red
        categoria = "No encontrado"
        nombre = "No encontrado"
        for v in registro.values():
            if v.get('RUT', '') == rut_red:
                categoria = v.get('CATEGORIA', 'No encontrado')
                nombre = v.get('NOMBRE_FUNC', 'No encontrado')
                break
        categoria_text.value = f'Categoría: {categoria}'
        nombre_text.value = f'Nombre: {nombre}'

    # Filtrar las capacitaciones si el rol no es ADMIN ni PROGRAMADOR
    capacitaciones_filtradas = leer_registro('capacitaciones')
    if rol_usuario not in ['PROGRAMADOR', 'ADMIN']:
        capacitaciones_filtradas = {k: v for k, v in capacitaciones_filtradas.items() if v.get('RUT') == rut_red}

    def ing_cap(e):
        rut_final = campo_rut.value if isinstance(campo_rut, ft.TextField) else campo_rut
        if not rut_final:
            mensaje.value = "⚠️ Debe ingresar un RUT"
            mensaje.color = "red"
            page.update()
            return

        categoria_actual = categoria_text.value.replace('Categoría: ', '')

        cap = Capacitacion(
            rut_final, categoria_actual,
            capacitacion[0].value, capacitacion[1].value, capacitacion[2].value,
            capacitacion[3].value, capacitacion[4].value, capacitacion[5].value,
            capacitacion[6].value, capacitacion[7].value,capacitacion[8].value
        )
        diccionario = cap.crear_dict_capacitacion()
        ingresar_registro_bd('capacitaciones', cap.crear_dict_capacitacion())
        ingresar_registro_bd('actividad',{'TIPO':'INGRESO_CAP.','ELEMENTO':f'{diccionario}','USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
        actualizacion_horaria(rol_usuario,leer_registro('usuarios'),leer_registro('contrato'),rut_final)
        

        registro_u = leer_registro('usuarios')
        lista_rut = [v.get('RUT', '') for v in registro.values()]
        ruts_unicos = list(set(lista_rut))
        if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
            for r in ruts_unicos:
                puntaje_nv(r, leer_registro('capacitaciones'))
        else:
            for idus, vus in registro_u.items():
                if vus.get('RUT') == rut_final:
                    puntaje_nv(rut_final, leer_registro('capacitaciones'))

        mensaje.value = "✅ Capacitación guardada exitosamente"
        mensaje.color = "green"
        page.update()

    def actualizar_cap(e):
        rut_final = campo_rut.value if isinstance(campo_rut, ft.TextField) else campo_rut
        if not rut_final:
            mensaje.value = "⚠️ Debe ingresar un RUT"
            mensaje.color = "red"
            page.update()
            return

        categoria_actual = categoria_text.value.replace('Categoría: ', '')

        cap = Capacitacion(
            rut_final, categoria_actual,
            capacitacion[0].value, capacitacion[1].value, capacitacion[2].value,
            capacitacion[3].value, capacitacion[4].value, capacitacion[5].value,
            capacitacion[6].value, capacitacion[7].value,capacitacion[8].value
        )
        dict_cap = cap.crear_dict_capacitacion()

        for id, cap in leer_registro('capacitaciones').items():
            if capacitacion[0].value == cap.get('NOMBRE_CAPACITACION'):
                actualizar_registro('capacitaciones', dict_cap, id)
                ingresar_registro_bd('actividad',{'TIPO':'ACTUALIZACION_CAP','ELEMENTO':f'{dict_cap}','USUARIO':rut_red,'FECHA':f'{datetime.now()}'})
                actualizacion_horaria(rol_usuario,leer_registro('usuarios'),leer_registro('contrato'),rut_final)

        mensaje.value = "✅ Capacitación actualizada exitosamente"
        mensaje.color = "green"
        page.update()

    def eliminar_cap(e):
        rut_final = campo_rut.value if isinstance(campo_rut, ft.TextField) else campo_rut
        if not rut_final:
            mensaje.value = "⚠️ Debe ingresar un RUT"
            mensaje.color = "red"
            page.update()
            return

        for id, cap in leer_registro('capacitaciones').items():
            if capacitacion[0].value == cap.get('NOMBRE_CAPACITACION'):
                borrar_registro('capacitaciones', id)
                ingresar_registro_bd('actividad',{'TIPO':'BORRA_CAP','ELEMENTO':f'{id}','USUARIO':rut_final,'FECHA':f'{datetime.now()}'})
                actualizacion_horaria(rol_usuario,leer_registro('usuarios'),leer_registro('contrato'),rut_red)

        mensaje.value = "✅ Capacitación eliminada exitosamente"
        mensaje.color = "green"
        page.update()

    def seleccionar_fila(e):
        key = e.control.key.split('|')
        rut_seleccionado, nombre_seleccionado = key[0], key[1]

        # Buscar la capacitación seleccionada
        for cap in leer_registro('capacitaciones').values():
            if cap.get("RUT") == rut_seleccionado and cap.get("NOMBRE_CAPACITACION") == nombre_seleccionado:
                # Llenar los campos con los datos correspondientes
                categoria_text.value = f"Categoría: {cap.get('CATEGORIA', '')}"
                nombre_text.value = f"Nombre: {cap.get('NOMBRE_FUNC', '')}"
                capacitacion[0].value = cap.get('NOMBRE_CAPACITACION', '')
                capacitacion[1].value = cap.get('ENTIDAD', '')
                capacitacion[2].value = cap.get('HORAS', '')
                capacitacion[3].value = cap.get('NIVEL_TECNICO', '')
                capacitacion[4].value = cap.get('NOTA', '')
                capacitacion[5].value = cap.get('AÑO_INICIO', '')
                capacitacion[6].value = cap.get('AÑO_PRESENTACION', '')
                capacitacion[7].value = cap.get('CONTEXTO_PRESS', '')
                capacitacion[8].value = cap.get('ES_POSTGRADO', '')

                # Actualizar el campo de RUT con el RUT de la fila seleccionada
                if isinstance(campo_rut, ft.TextField):
                    campo_rut.value = rut_seleccionado  # Asignar el RUT al campo de texto

                break

        page.update()  # Actualizar la página con los nuevos valores

    tabla = tabla_capacitacion(page, capacitaciones=capacitaciones_filtradas, on_select=seleccionar_fila)

    header = encabezado("🎓 Registro de Capacitación")

    # Formulario de Capacitación
    formulario = ft.Container(
        content=ft.Card(
            elevation=8,
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=25,
                content=ft.Column([  
                    ft.Text("⚕️ Ingreso de Capacitación", size=18, weight="bold", color="#333333"),
                    ft.Text("Complete los campos requeridos (*):", size=13, color="grey"),
                    ft.Divider(),
                    ft.Row([  
                        ft.Text("RUT:", size=14, weight='bold', color="black"),
                        campo_rut if isinstance(campo_rut, ft.TextField) else ft.Text(campo_rut, size=14, color="black")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10),
                    ft.Row([
                        ft.Container(categoria_text, padding=10, bgcolor="#E0E0E0", border_radius=8, expand=True),
                        ft.Container(nombre_text, padding=10, bgcolor="#E0E0E0", border_radius=8, expand=True)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("Datos de la Capacitación:", size=16, weight="bold", color="black"),
                    ft.ResponsiveRow([  
                        ft.Container(capacitacion[0], col={"sm": 6, "md": 6}, padding=5),
                        ft.Container(capacitacion[1], col={"sm": 6, "md": 6}, padding=5),
                        ft.Container(capacitacion[2], col={"sm": 4, "md": 4}, padding=5),
                        ft.Container(capacitacion[3], col={"sm": 4, "md": 4}, padding=5),
                        ft.Container(capacitacion[4], col={"sm": 4, "md": 4}, padding=5),
                        ft.Container(ft.Column([ft.Text("Año cursado:", color="black"), capacitacion[5]]), col={"sm": 6, "md": 6}, padding=5),
                        ft.Container(ft.Column([ft.Text("Año presentado:", color="black"), capacitacion[6]]), col={"sm": 6, "md": 6}, padding=5),
                        ft.Container(capacitacion[7], col={"sm": 6, "md": 6}, padding=5),
                        ft.Container(capacitacion[8], col={"sm": 6, "md": 6}, padding=5),
                        ft.Container(ft.Card(
                            ft.Text('Categoría ingreso a planta suma pje completo, a diferencia de Cambio de Nivel que tiene tope de 150 pts por año.',
                                    size=9, color='red')
                        , color='white'), col={"sm": 12, "md": 12}, padding=5),
                    ]),
                    ft.Row([  
                        ft.ElevatedButton('Guardar Registro', icon=ft.Icons.SAVE, width=200, on_click=ing_cap),
                        ft.ElevatedButton('Actualizar Registro', icon=ft.Icons.EDIT, width=200, on_click=actualizar_cap),
                        ft.ElevatedButton('Eliminar Registro', icon=ft.Icons.DELETE, width=200, on_click=eliminar_cap)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    mensaje
                ], spacing=12)
            )
        ),
        width=700,
        padding=20
    )

    fila_contenido = ft.Row([  
        formulario,
        ft.Container(tabla, padding=20, expand=True)
    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)

    contenido = ft.Column(
        [header, fila_contenido, pie_pagina()],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll="auto"
    )

    return ft.Container(
        content=contenido,
        expand=True,
        bgcolor="#F0F2F5",
        padding=20,
        alignment=ft.alignment.top_center
    )

def tabla_capacitacion(page, capacitaciones, on_select):
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
    for cap in capacitaciones.values():  # Usamos los datos pasados como argumento
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