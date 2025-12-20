import flet as ft
from user import *
from cap_cop import *
from contrato import *
from firebase_bd import *
import variables
from campos_flet import *
from funciones import *
from pruebas import *

def home_view(page):
    rut_red = variables.rut_actual
    usuarios_data = leer_registro('usuarios')
    contratos_data = leer_registro('contrato')
    datos_log = leer_registro('login')

    rol_usuario = ''
    for idx, log in datos_log.items():
        if log.get('ID') == variables.rut_actual:
            rol_usuario = log.get('ROL', '')
            break

    resumen_column = ft.Ref[ft.Column]()
    grafico_row = ft.Ref[ft.Row]()
    piechart_container_ref = ft.Ref[ft.Container]()

    if rol_usuario in ["PROGRAMADOR", "ADMIN"] and usuarios_data:
        rut_inicial = list(usuarios_data.values())[0].get("RUT")
    else:
        rut_inicial = rut_red

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

        try:
            edad = [i.get('EDAD') for i in data_user.values() if i.get('RUT') == rut][0]
            nivel = [i.get('NIVEL') for i in data_user.values() if i.get('RUT') == rut][0]
            cat = [i.get('CATEGORIA') for i in data_user.values() if i.get('RUT') == rut][0]
            pje_g = [i.get('PTJE_CARR') for i in data_user.values() if i.get('RUT') == rut][0]
            pje_ac = [i.get('SALDO_PTJE') for i in data_user.values() if i.get('RUT') == rut][0]
            prof = [i.get('PROFESION') for i in data_user.values() if i.get('RUT') == rut][0]

            t_cont = [i.get('TIPO_CONTRATO') for i in data_cont.values() if i.get('RUT') == rut][0]
            ing = [i.get('FECHA_INICIO') for i in data_cont.values() if i.get('RUT') == rut][0]
            cargo = [i.get('CARGO') for i in data_cont.values() if i.get('RUT') == rut][0]
            depen = [i.get('DEPENDENCIA') for i in data_cont.values() if i.get('RUT') == rut][0]
        except IndexError:
            edad = nivel = cat = pje_g = pje_ac = prof = t_cont = ing = cargo = depen = "N/A"

        horas_sum = sum(cap.get('HORAS', 0) for cap in data_cap.values() if cap.get('RUT') == rut)
        cant_cap = len([i for i in data_cap.values() if i.get('RUT') == rut])

        if resumen_column.current:
            resumen_column.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(name="person", color="blue"), ft.Text("Datos personales", weight="bold", size=16, color='black')]),
                        ft.Text(f"🪪RUT: {rut}", size=14, color='black'),
                        ft.Text(f"📅Edad: {edad} años", color='black'),
                        ft.Text(f"📈Nivel: {nivel}", color='black'),
                        ft.Text(f"💼Profesión: {prof}", color='black'),
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(name="badge", color="blue"), ft.Text("Datos laborales", weight="bold", size=16, color='black')]),
                        ft.Text(f"🗃️Categoría: {cat}", size=14, color='black'),
                        ft.Text(f"📄Contrato: {t_cont}", color='black'),
                        ft.Text(f"📅Ingreso: {ing}", color='black'),
                        ft.Text(f"💼Cargo: {cargo}", color='black'),
                        ft.Text(f"ℹ️Dependencia: {depen}", color='black'),
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(name="school", color="blue"), ft.Text("Capacitación", weight="bold", size=16, color='black')]),
                        ft.Text(f"📋N° Total de Capacitaciones: {cant_cap}", size=14, color='black'),
                        ft.Text(f"🕜Horas totales capacitación: {horas_sum}", size=14, color='black'),
                        ft.Text(f"📊Puntaje carrera: {pje_g}", color='black'),
                        ft.Text(f"📊Puntaje acumulado: {pje_ac}", color='black'),
                    ]),
                    bgcolor="#f0f0f0",
                    padding=15,
                    width=280,
                    border_radius=10
                )
            ]

        if grafico_row.current:
            grafico_row.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Puntaje Acumulado", size=14, color='black'),
                        ft.Container(width=120, height=20, bgcolor="green", border_radius=5),
                        ft.Text(f"{pje_ac} pts", size=12, color='black')
                    ]),
                    padding=10,
                    bgcolor="#E8F5E9",
                    border_radius=10,
                    width=300
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎯 Puntaje Carrera", size=14, color='black'),
                        ft.Container(width=120, height=20, bgcolor="blue", border_radius=5),
                        ft.Text(f"{pje_g} pts", size=12, color='black')
                    ]),
                    padding=10,
                    bgcolor="#E3F2FD",
                    border_radius=10,
                    width=300
                )
            ]

        if piechart_container_ref.current:
            piechart_container_ref.current.content = piechart_view(page, rut)

        page.update()

    dropdown_rut.on_change = lambda e: actualizar_info(e.control.value)

    def on_page_load(e):
        actualizar_info(rut_inicial)

    page.on_load = on_page_load

    return ft.Container(
        content=ft.Column([
            ft.Text("🏠 Tablero Resumen", size=24, weight="bold", color="black"),
            ft.Divider(height=1, color="grey"),
            dropdown_rut,
            ft.Row([
                ft.Column(ref=resumen_column, controls=[]),
                ft.Container(ref=piechart_container_ref),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=20, color="white"),
            ft.Text("🧾 Últimas Capacitaciones", size=20, weight="bold", color="black"),
            ft.Row(ref=grafico_row, controls=[]),
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


def main_view(page):
    page.title = "Gestión de Funcionarios - Carrera Funcionaria"
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"

    rut_red = variables.rut_actual
    rol_usuario = ''
    for idx, log in leer_registro('login').items():
        if log.get('ID') == variables.rut_actual:
            rol_usuario = log.get('ROL', '')
            break


    def route_change(e):
        page.views.clear()

        rutas = {
            '/': home_view,
            '/Contratos': contrato_view,
            '/Capacitaciones': cap_view,
        }

        # Solo agregar la ruta para crear usuario si el rol es ADMIN o PROGRAMADOR
        if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
            rutas['/NuevoUsuario'] = crear_usuario_view

        # Si el usuario intenta entrar a /NuevoUsuario y no tiene permiso, redirigir a home
        if page.route == '/NuevoUsuario' and rol_usuario not in ['PROGRAMADOR', 'ADMIN']:
            page.go('/')
            return

        vista_func = rutas.get(page.route, home_view)

        # Construir los botones del menú, ocultando "Nuevo Usuario" si no tiene permiso
        acciones = [
            ft.TextButton('🏠 Inicio', on_click=lambda _: page.go('/'), style=ft.ButtonStyle(color="white")),
            ft.TextButton('📄 Contratos', on_click=lambda _: page.go('/Contratos'), style=ft.ButtonStyle(color="white")),
            ft.TextButton('🎓 Capacitaciones', on_click=lambda _: page.go('/Capacitaciones'), style=ft.ButtonStyle(color="white")),
        ]
        if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
            acciones.append(ft.TextButton('👤 Nuevo Usuario', on_click=lambda _: page.go('/NuevoUsuario'), style=ft.ButtonStyle(color="white")))

        acciones.append(
            ft.TextButton(
                text="🌐 Contacto",
                url="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e",
                style=ft.ButtonStyle(color="white")
            )
        )

        #Se traen variables globales
        usuario = variables.user_act
        cargo = variables.cargo_act
        

        page.views.append(
            ft.View(
                route=page.route,
                controls=[
                    ft.AppBar(
                        title=ft.Container(
                            content=ft.Column([
                                ft.Text("⚕️ Sistema de Gestión Carrera Funcionaria de Salud", color="white", size=25, overflow="ellipsis"),
                                ft.Text(f'💻 {usuario}   💼 {cargo}', color='white', weight='bold', size=14),
                            ],
                            spacing=2,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START),
                            padding=ft.padding.only(left=10),
                            height=65,  # Puedes ajustar esto
                            alignment=ft.alignment.center_left
                        ),
                        bgcolor="#1976D2",
                        actions=acciones
                    ),
                    ft.Container(
                        content=vista_func(page),
                        expand=True,
                        padding=20
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        )
        page.update()

    page.on_route_change = route_change
    page.go('/')
