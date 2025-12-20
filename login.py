import flet as ft
from cap_cop import *
from user_cop import *
from main import *
from inicio import *
from firebase_bd import *
from datetime import datetime
import variables
from funciones import *
from campos_flet import *
from clases import *


def login_view(page: ft.Page):
    usuario = ft.TextField(label="Usuario", width=300, color='black', border_color="#1976D2")
    password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, color='black', border_color="#1976D2")
    mensaje = ft.Text("", size=12, color="red")

    #---------------Almacenamiento de Variables globales-------------------
    #Lectura de usuarios
    reg = leer_registro('usuarios')
    #Lectura de contratos
    conts = leer_registro('contrato')
    #Lectura de permisos
    datos_log = leer_registro('login')

    page.bgcolor = "#F0F2F5"
    page.scroll = 'auto'

    rol_usuario = ''
    id_r = ''
    for idx, log in datos_log.items():
        if log.get('ID') == variables.rut_actual:
            rol_usuario = log.get('ROL', '')
            id_r = log.get('ID')
            break

    actualizacion_horaria(rol_usuario,reg,conts,id_r)

    def validar_login(e): 
        #Se hace verificación que el usuario y clave sean los correctos
        for idx, usr in datos_log.items():
            if usr.get('USER') == usuario.value and usr.get('PASS') == password.value:
                mensaje.value = "✅ Bienvenido, por favor esper un momento ⌛"
                mensaje.color = "green"
                page.update()

                variables.rut_actual = usr.get('ID')
                rut_red = variables.rut_actual 
                variables.cat_actual = usr.get('CATEGORIA')

                rol_usuario = ''
        
                for idx, log in datos_log.items():
                    if log.get('ID') == variables.rut_actual:
                        rol_usuario = log.get('ROL', '')
                        break
                 
                
                 
                registrado = any(val.get('RUT') == usr.get('ID') for val in reg.values()) if reg else False

                if registrado:
                   
                    data_user = leer_registro('usuarios')
                    data_cont = leer_registro('contrato')
                    usuario_g = [i.get('NOMBRE_FUNC') for i in data_user.values() if i.get('RUT') == rut_red]
                    cargo_g = [i.get('CARGO') for i in data_cont.values() if i.get('RUT') == rut_red]
                    cat_g = [i.get('CATEGORIA') for i in data_user.values() if i.get('RUT') == rut_red]
                    variables.user_act = usuario_g
                    variables.cargo_act =cargo_g
                    page.go("/main")
                else:
                    page.go("/user")
                    
                return

        mensaje.value = "⚠️ Credenciales incorrectas"
        mensaje.color = "red"
        page.update()

    header = encabezado("⚕️ Sistema Gestión Carrera Funcionaria de Salud")

    tarjeta_login = ft.Container(
        content=ft.Card(
            elevation=8,
            content=ft.Container(
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=25,
                content=ft.Column([
                    ft.Text("🔒 Ingreso al Sistema", size=20, weight="bold", color="#333333"),
                    ft.Text("Accede con tus credenciales de funcionario", size=13, color="grey"),
                    ft.Divider(),
                    ft.Text("Usuario:", size=14, weight="bold", color="black"),
                    usuario,
                    ft.Text("Contraseña:", size=14, weight="bold", color="black"),
                    password,
                    ft.ElevatedButton("Ingresar", width=300, icon=ft.Icons.LOGIN, on_click=validar_login),
                    mensaje
                ], spacing=12)
            )
        ),
        width=400
    )

    footer = pie_pagina()

    fondo = ft.Image(
        src="https://drive.google.com/uc?export=view&id=1Mb875ubQiPiMjg-Q8SGGrxsDmkmEstu8",
        height=300,
        #fit=ft.ImageFit.COVER
    )

    return ft.Container(
        expand=True,
        content=ft.Stack([
            ft.Column([
                header,
                ft.Row([fondo,
                ft.Container(content=tarjeta_login, alignment=ft.alignment.center_left, expand=True)]),
                footer
            ],scroll='auto', expand=True)
        ])
    )


# Vista Principal con rutas
def inicio_view(page: ft.Page):
    page.title = "Gestión Funcionarios"
    page.bgcolor = "#FFFFFF"

    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(ft.View("/", [login_view(page)], bgcolor='white', scroll='auto'))

        elif page.route == "/user":
            import user_cop  # Solo importar si es necesario
            vista = user_cop.user_view(page)
            page.views.append(ft.View("/user", [vista], bgcolor='white', scroll='auto'))

        elif page.route == "/main":
            
            page.scroll = 'auto'
            page.bgcolor = 'white'
            main_view(page)

        page.update()

    page.on_route_change = route_change
    page.go("/")


# Ejecuta la app
#ft.app(target=inicio_view,view=ft.WEB_BROWSER)
ft.app(target=inicio_view)