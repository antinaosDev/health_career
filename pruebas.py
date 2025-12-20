# piechart.py
import flet as ft
from firebase_bd import *

def obtener_datos_por_año(rut_ev):
    datos = [
        (i.get("AÑO_PRESENTACION"), i.get("HORAS"))
        for i in leer_registro("capacitaciones").values() if i.get('RUT') == rut_ev
    ]
    horas_por_año = {}
    for año, horas in datos:
        if año not in horas_por_año:
            horas_por_año[año] = 0
        horas_por_año[año] += horas
    return horas_por_año

def piechart_view(rut_ev, page):
    normal_radius = 70
    hover_radius = 90

    normal_title_style = ft.TextStyle(size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    hover_title_style = ft.TextStyle(
        size=10,
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD,
        shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.BLACK54),
    )

    horas_por_año = obtener_datos_por_año(rut_ev)

    colores = [
        ft.Colors.BLUE, ft.Colors.YELLOW, ft.Colors.PURPLE, ft.Colors.GREEN,
        ft.Colors.RED, ft.Colors.ORANGE, ft.Colors.TEAL, ft.Colors.CYAN,
        ft.Colors.PINK, ft.Colors.LIME,
    ]

    secciones = []
    for idx, (año, horas) in enumerate(horas_por_año.items()):
        secciones.append(
            ft.PieChartSection(
                value=horas,
                title=f"{año}\n{horas}h",
                title_style=normal_title_style,
                color=colores[idx % len(colores)],
                radius=normal_radius,
            )
        )

    def on_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(chart.sections):
            if idx == e.section_index:
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.radius = normal_radius
                section.title_style = normal_title_style
        chart.update()

    chart = ft.PieChart(
        sections=secciones,
        sections_space=3,
        center_space_radius=20,
        on_chart_event=on_chart_event,
        expand=True,
    )

    return ft.Container(
        content=chart,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        padding=20,
        border_radius=10,
        expand=True,
    )


def obtener_datos_por_punto(rut_ev):
    datos = [
        (i.get("AÑO_PRESENTACION"), i.get("PJE_POND"))
        for i in leer_registro("capacitaciones").values() if i.get('RUT') == rut_ev
    ]
    horas_por_año = {}
    for año, pje in datos:
        if año not in horas_por_año:
            horas_por_año[año] = 0
        horas_por_año[año] += pje
    return horas_por_año

def barchart_view(page, rut):
    horas_por_año = obtener_datos_por_año(rut)

    colores = [
        ft.Colors.BLUE,
        ft.Colors.YELLOW,
        ft.Colors.PURPLE,
        ft.Colors.GREEN,
        ft.Colors.RED,
        ft.Colors.ORANGE,
        ft.Colors.TEAL,
        ft.Colors.CYAN,
        ft.Colors.PINK,
        ft.Colors.LIME,
    ]

    bar_groups = []
    bottom_labels = []

    for idx, (año, pje) in enumerate(sorted(horas_por_año.items())):
        bar_groups.append(
            ft.BarChartGroup(
                x=idx,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=pje,
                        width=40,
                        color=colores[idx % len(colores)],
                        border_radius=5,
                    ),
                ],
            )
        )
        bottom_labels.append(
            ft.ChartAxisLabel(
                value=idx,
                label=ft.Container(
                    content=ft.Text(str(año), size=12, color="black"),
                    padding=ft.padding.symmetric(vertical=5),
                    alignment=ft.alignment.center,
                    height=20,
                )
            )
        )

    chart = ft.BarChart(
        bar_groups=bar_groups,
        border=None,
        left_axis=None#ft.ChartAxis(
            #labels_size=40,
            #title=ft.Text("Horas", color="black"),
            #title_size=14,
        #)
        ,
        bottom_axis=ft.ChartAxis(
            labels=bottom_labels,
            labels_size=50,  # ✅ Este valor aumenta el espacio para que las etiquetas no se corten
            title=ft.Text("", color="black"),
            title_size=14,
        ),
        horizontal_grid_lines=None,
        vertical_grid_lines=None #ft.ChartGridLines(
            #color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            #width=1,
        #)
        ,
        interactive=True,
        expand=True,
    )

    return ft.Container(
        content=chart,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        padding=ft.padding.symmetric(horizontal=20, vertical=60),  # Padding más generoso
        border_radius=10,
        expand=True,
    )



from collections import defaultdict


# Función para contar capacitaciones por año según el RUT
def capacitaciones_por_año(rut_ev):
    datos = leer_registro("capacitaciones").values()
    cap_por_año = defaultdict(int)

    for cap in datos:
        if cap.get('RUT') == rut_ev:
            año = cap.get("AÑO_PRESENTACION")
            if año:
                cap_por_año[año] += 1

    return dict(cap_por_año)

# Gráfico de barras para mostrar la cantidad de capacitaciones por año
def barchart_view_2(page, rut):
    cap_por_año = capacitaciones_por_año(rut)

    colores = [
        ft.Colors.BLUE,
        ft.Colors.YELLOW,
        ft.Colors.PURPLE,
        ft.Colors.GREEN,
        ft.Colors.RED,
        ft.Colors.ORANGE,
        ft.Colors.TEAL,
        ft.Colors.CYAN,
        ft.Colors.PINK,
        ft.Colors.LIME,
    ]

    bar_groups = []
    bottom_labels = []

    for idx, (año, cantidad) in enumerate(sorted(cap_por_año.items())):
        bar_groups.append(
            ft.BarChartGroup(
                x=idx,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=cantidad,
                        width=40,
                        color=colores[idx % len(colores)],
                        border_radius=5,
                    ),
                ],
            )
        )
        bottom_labels.append(
            ft.ChartAxisLabel(
                value=idx,
                label=ft.Container(
                    content=ft.Text(str(año), size=12, color="black"),
                    padding=ft.padding.symmetric(vertical=5),
                    alignment=ft.alignment.center,
                    height=30,
                )
            )
        )

    chart = ft.BarChart(
        bar_groups=bar_groups,
        border=None,
        left_axis=None, #ft.ChartAxis(
            #labels_size=30,
            #title=ft.Text("Cantidad", color="black"),
            #title_size=14)
        
        bottom_axis=ft.ChartAxis(
            labels=bottom_labels,
            labels_size=50,
            title=ft.Text(" ", color="black"),
            title_size=14,
        ),
        horizontal_grid_lines=None,
        vertical_grid_lines=None,
        interactive=True,
        expand=True,
    )

    return ft.Container(
        content=chart,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        padding=ft.padding.symmetric(horizontal=20, vertical=60),
        border_radius=10,
        expand=True,
    )