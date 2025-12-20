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
from inicio import *  # Asegúrate que `home_view(page, rut)` esté definido correctamente


def main_view(page):
    # Configuración inicial de la página
    page.title = "Gestión de Funcionarios - Carrera Funcionaria"
    page.bgcolor = "#F0F2F5"
    page.scroll = "auto"

    rut_red = variables.rut_actual
    rol_usuario = ""

    # Obtener rol del usuario autenticado
    for idx, log in leer_registro('login').items():
        if log.get('ID') == rut_red:
            rol_usuario = log.get('ROL', '')
            break

    def route_change(e):
        page.views.clear()

        # Diccionario de rutas con funciones lambda para evitar errores de tipo
        rutas = {
            '/': lambda p: home_view(p, rut_red),
            '/Contratos': lambda p: contrato_view(p),
            '/Capacitaciones': lambda p: cap_view(p),
        }

        # Agregar ruta "Nuevo Usuario" solo para usuarios autorizados
        if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
            rutas['/NuevoUsuario'] = lambda p: crear_usuario_view(p)

        # Redirigir a inicio si intenta acceder a /NuevoUsuario sin permisos
        if page.route == '/NuevoUsuario' and rol_usuario not in ['PROGRAMADOR', 'ADMIN']:
            page.go('/')
            return

        # Obtener la vista correspondiente a la ruta actual
        vista_func = rutas.get(page.route, lambda p: home_view(p, rut_red))

        # Construir menú de navegación
        acciones = [
            ft.TextButton('🏠 Inicio', on_click=lambda _: page.go('/'), style=ft.ButtonStyle(color="white")),
            ft.TextButton('📄 Contratos', on_click=lambda _: page.go('/Contratos'), style=ft.ButtonStyle(color="white")),
            ft.TextButton('🎓 Capacitaciones', on_click=lambda _: page.go('/Capacitaciones'), style=ft.ButtonStyle(color="white")),
        ]

        if rol_usuario in ['PROGRAMADOR', 'ADMIN']:
            acciones.append(
                ft.TextButton('👤 Nuevo Usuario', on_click=lambda _: page.go('/NuevoUsuario'), style=ft.ButtonStyle(color="white"))
            )

        acciones.append(
            ft.TextButton(
                text="🌐 Contacto",
                url="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e",
                style=ft.ButtonStyle(color="white")
            )
        )

        # Datos del usuario logueado
        usuario = variables.user_act
        cargo = variables.cargo_act

        # Renderizar vista principal
        page.views.append(
            ft.View(
                route=page.route,
                controls=[
                    ft.AppBar(
                        title=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("⚕️ Sistema de Gestión Carrera Funcionaria de Salud", color="white", size=25, overflow="ellipsis"),
                                    ft.Text(f'💻 {usuario}   💼 {cargo}', color='white', weight='bold', size=14),
                                ],
                                spacing=2,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START
                            ),
                            padding=ft.padding.only(left=10),
                            height=65,
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

    # Asignar función de manejo de rutas y navegar a inicio
    page.on_route_change = route_change
    page.go('/')
