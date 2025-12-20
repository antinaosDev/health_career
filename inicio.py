from decimal import DivisionByZero
import flet as ft
from user import *
from cap_cop import *
from contrato import *
from firebase_bd import *
import variables
from campos_flet import *
from funciones import *
from pruebas import *
from indices import *
from tablas import *

def home_view(page,rut):
    rut_red = rut
    usuarios_data = leer_registro('usuarios')
    contratos_data = leer_registro('contrato')
    datos_log = leer_registro('login')

    rol_usuario = ''
    for idx, log in datos_log.items():
        if log.get('ID') == rut_red:
            rol_usuario = log.get('ROL', '')
            break

    resumen_column = ft.Ref[ft.Column]()
    resumen_row = ft.Ref[ft.Row]()
    resumen_tabla = ft.Ref[ft.Column]()
    grafico_row = ft.Ref[ft.Row]()
    piechart_container_ref = ft.Ref[ft.Container]()
    barchart_container_ref = ft.Ref[ft.Container]()
    barchart2_container_ref = ft.Ref[ft.Container]()  # 🆕 REFERENCIA NUEVA

    rut_inicial = list(usuarios_data.values())[0].get("RUT") if rol_usuario in ["PROGRAMADOR", "ADMIN"] else rut_red

    dropdown_rut = ft.Dropdown(
        label="Selecciona un RUT",
        options=[ft.dropdown.Option(usr.get("RUT")) for usr in usuarios_data.values()],
        visible=rol_usuario in ["PROGRAMADOR", "ADMIN"],
        width=300
    )

    def actualizar_info(rut):
        data_user = leer_registro('usuarios')
        data_cap = leer_registro('capacitaciones')
        data_cont = leer_registro('contrato')

        
        nom = [i.get('NOMBRE_FUNC') for i in data_user.values() if i.get('RUT') == rut][0]
        edad = [i.get('EDAD') for i in data_user.values() if i.get('RUT') == rut][0]
        nivel = [i.get('NIVEL') for i in data_user.values() if i.get('RUT') == rut][0]
        cat = [i.get('CATEGORIA') for i in data_user.values() if i.get('RUT') == rut][0]
        pje_g = [i.get('PTJE_CARR') for i in data_user.values() if i.get('RUT') == rut][0]
        pje_ac = [i.get('SALDO_PTJE') for i in data_user.values() if i.get('RUT') == rut][0]
        prof = [i.get('PROFESION') for i in data_user.values() if i.get('RUT') == rut][0]
        bienio = [i.get('BIENIOS') for i in data_user.values() if i.get('RUT') == rut][0]

        t_cont = ','.join([i.get('TIPO_CONTRATO') for i in data_cont.values() if i.get('RUT') == rut])
        ing = ','.join([i.get('FECHA_INICIO') for i in data_cont.values() if i.get('RUT') == rut])
        cargo = [i.get('CARGO') for i in data_cont.values() if i.get('RUT') == rut][0]
        depen = [i.get('DEPENDENCIA') for i in data_cont.values() if i.get('RUT') == rut][0]
        cant_cont = len([cap.get('FECHA_INICIO') for cap in data_cont.values() if cap.get('RUT') == rut])
        horas_cont = ','.join([str(i.get('HORAS')) for i in data_cont.values() if i.get('RUT') == rut])
        

        #Promedio calificaciones
        calificaciones = [i.get('NOTA') for i in data_cap.values() if i.get('RUT') == rut]

        #Prevenir errores de la division por cero
        if len(calificaciones) == 0:
            prom_calif = 0
        else:
            prom_calif = round((sum(calificaciones) / len(calificaciones)), 1)

        #Cantidad de capacitaciones
        cant_cap = len([cap.get('NOMBRE_CAPACITACION') for cap in data_cap.values() if cap.get('RUT') == rut])
        horas_sum = sum(hora.get('HORAS') for hora in data_cap.values() if hora.get('RUT') == rut)
        
        #Asignación postgrado
        data_capacitacion = leer_registro('capacitaciones')

        horas_cap = [hora.get('HORAS') for hora in data_capacitacion.values()
                    if hora.get('RUT') == rut and hora.get('ES_POSTGRADO') == 'SI']

        suma_horas = sum(horas_cap)
        porcentaje_asig = porcentaje_postgrado(suma_horas,rut)
        


        #Calculo diferencias de puntos siguiente nivel
        dif = 0
        for idl,nv in indices_niveles.items():
            if cat in idl:
                for id,val in nv.items():
                    if val == nivel:
                        dif = id[1] + 1 - pje_g

        #Calculo del total de capacitaciones por nivel tecnico
        t_a = len([i.get('NIVEL_TECNICO') for i in data_cap.values() if i.get('RUT') == rut and i.get('NIVEL_TECNICO') == 'Alto'])
        t_m = len([i.get('NIVEL_TECNICO') for i in data_cap.values() if i.get('RUT') == rut and i.get('NIVEL_TECNICO') == 'Medio'])
        t_b = len([i.get('NIVEL_TECNICO') for i in data_cap.values() if i.get('RUT') == rut and i.get('NIVEL_TECNICO') == 'Bajo']) 

        
        #SUELDO BASE re ajuste mas APS
        sueldo_base = sueldo_base_lista = [int(str(sueldo.get('SUELDO_BASE')).replace(',', '')) for sueldo in usuarios_data.values() if sueldo.get('RUT') == rut
    and sueldo.get('SUELDO_BASE') not in (None, 'None', '')]

        sueldo_base = sueldo_base_lista[0] if sueldo_base_lista else 0
        base_aps = int(sueldo_base) * 2


        mensaje_texto = ft.Text("")  # Texto informativo que se actualizará con mensajes
        mensaje_2 = ft.Text("")

        if resumen_row.current:
            # Botón para seleccionar archivo
            boton_carga = cargar_archivo(page, rol_usuario, usuarios_data, rut_red, mensaje_texto)

            resumen_row.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Text('Carga masiva de capacitaciones⏫', color='blue', weight='bold', size=14),
                        boton_carga,  # Botón
                        # Usamos ft.TextButton para crear un hipervínculo
                        ft.TextButton(
                            text="📄Descarga planilla base", 
                            url="https://docs.google.com/spreadsheets/d/1U6Lk-nhc7VYRYHQQFPn9FjcLlS029_0t/edit?usp=sharing&ouid=109770254279701890924&rtpof=true&sd=true", 
                            style=ft.ButtonStyle(color="blue")
                        ),
                        mensaje_texto,
                        ft.Text('Exportar información 📂', color='blue', weight='bold', size=14),
                        export_to_excel(page, mensaje_2, rol_usuario, rut_red),  # Texto que se actualizará durante la carg
                        
                    mensaje_2
                    ]),
                    bgcolor="#ffffff",
                    padding=15,
                    width=280,
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name=ft.Icons.CALL_MADE_OUTLINED, color="blue"),
                            ft.Text("Nivel", weight="bold", size=20, color='blue')
                        ]),
                        ft.Text(f"{nivel}", color='black', weight='bold', size=20)
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name=ft.Icons.SCORE, color="blue"),
                            ft.Text("Puntaje carrera", weight="bold", size=20, color='blue')
                        ]),
                        ft.Text(f"{pje_g}", color='black', weight='bold', size=20)
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name=ft.Icons.DIFFERENCE, color="blue"),
                            ft.Text("Puntos prox. Nivel", weight="bold", size=20, color='blue')
                        ]),
                        ft.Text(f"{dif}", color='black', weight='bold', size=20)
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name=ft.Icons.SCORE, color="blue"),
                            ft.Text("Saldo puntaje", weight="bold", size=20, color='blue')
                        ]),
                        ft.Text(f"{pje_ac}", color='black', weight='bold', size=20)
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                )
            ]


        if resumen_column.current:
            resumen_column.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(name="person", color="blue"), ft.Text("Datos personales", weight="bold", size=16, color='black')]),
                        ft.Text(f"🪪Nombre: {nom}", size=14, color='black'),
                        ft.Text(f"🆔RUT: {rut}", size=14, color='black'),
                        ft.Text(f"📅Edad: {edad} años", color='black'),
                        ft.Text(f"💼Profesión: {prof}", color='black'),
                    ]),
                    bgcolor="#f0f0f0", padding=15, width=280, border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(name="badge", color="blue"), ft.Text("Datos laborales", weight="bold", size=16, color='black')]),
                        ft.Text(f"🗃️Categoría: {cat}", size=14, color='black'),
                        ft.Text(f"📋Cantidad contratos: {cant_cont}", color='black'),
                        ft.Text(f"📄Contrato: {t_cont}", color='black'),
                        ft.Text(f"🕜Horas contrato: {horas_cont}", color='black'),
                        ft.Text(f"➕Bienio: {bienio}", color='black'),
                        ft.Text(f"💰BASE + APS: {base_aps:,.0f}", color='black'),
                        ft.Text(f"📅Ingreso: {ing}", color='black'),
                        ft.Text(f"💼Cargo: {cargo}", color='black'),
                        ft.Text(f"ℹ️Dependencia: {depen}", color='black'),
                    ]),
                    bgcolor="#f0f0f0", padding=15, width=280, border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(name="school", color="blue"), ft.Text("Capacitación", weight="bold", size=16, color='black')]),
                        ft.Text(f"📋N° Total de Capacitaciones: {cant_cap}", size=14, color='black'),
                        ft.Text(f"🕜Horas totales capacitación: {horas_sum}", size=14, color='black'),
                        ft.Text(f"📊Promedio Notas: {prom_calif}", size=14, color='black'),
                        ft.Text(f"🗂️Nv.Técnico Alto: {t_a}", size=14, color='black'),
                        ft.Text(f"🗂️Nv.Técnico Medio: {t_m}", size=14, color='black'),
                        ft.Text(f"🗂️Nv.Técnico Bajo: {t_b}", size=14, color='black'),
                        ft.Text(f"🎓Asignación postgrado: {porcentaje_asig}", size=14, color='black'),
                    ]),
                    bgcolor="#f0f0f0", padding=15, width=280, border_radius=10
                )
            ]

        if piechart_container_ref.current:
            piechart_container_ref.current.content = piechart_view(rut, page)

        if barchart_container_ref.current:
            barchart_container_ref.current.content = barchart_view(page, rut)

        if barchart2_container_ref.current:  # 🆕 ACTUALIZAR NUEVO CONTENEDOR
            barchart2_container_ref.current.content = barchart_view_2(page, rut)
        
        if resumen_tabla.current:
            resumen_tabla.current.controls = [table_view(page, rut)]


        page.update()

    dropdown_rut.on_change = lambda e: actualizar_info(e.control.value)

    contenido_pagina = ft.Container(
        content=ft.Column([
            ft.Text("🏠 Tablero Resumen", size=24, weight="bold", color="black"),
            ft.Divider(height=1, color="grey"),
            dropdown_rut,
            ft.Row(ref=resumen_row, controls=[], alignment=ft.MainAxisAlignment.START),

            ft.Row([
                ft.Column(ref=resumen_column, controls=[]),
                ft.Row([ft.Column([
                        ft.Text("📈 Capacitaciones por año", size=16, weight="bold", color='black'),
                        ft.Container(ref=barchart2_container_ref, width=350, height=350)
                        ]),
                        ft.VerticalDivider(width=10),
                    ft.Column([
                        ft.Text("📊 Horas por Año", size=16, weight="bold", color='black'),
                        ft.Container(ref=piechart_container_ref, width=350, height=350)
                    ]),
                    ft.VerticalDivider(width=10),
                    ft.Column([
                        ft.Text("📉 Puntaje acumulado por Año", size=16, weight="bold", color='black'),
                        ft.Container(ref=barchart_container_ref, width=350, height=350)
                    ]),
                ])
            ], alignment=ft.MainAxisAlignment.START),

            ft.Divider(height=20, color="white"),
            ft.Text("🧾 Listado de Capacitaciones", size=20, weight="bold", color="black"),
            ft.Row(ref=resumen_tabla),
            ft.Divider(height=15, color="white"),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=25,
        scroll='auto'),
        bgcolor="white",
        expand=True,
        padding=25
    )

    actualizar_info(rut_inicial)

    return contenido_pagina

    """page.add(contenido_pagina)

ft.app(target=home_view)"""
