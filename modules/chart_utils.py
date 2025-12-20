import matplotlib.pyplot as plt
import pandas as pd
import os

# Set style
plt.style.use('ggplot')

def save_bar_chart(df, x_col, y_col, title, filename, horizontal=False, color='#006DB6'):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Sort for aesthetics if not already
    # df should be passed sorted
    
    if horizontal:
        bars = ax.barh(df[y_col], df[x_col], color=color)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        # Add labels
        ax.bar_label(bars, fmt='{:,.0f}')
    else:
        bars = ax.bar(df[x_col], df[y_col], color=color)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.bar_label(bars, fmt='{:,.0f}')
        
    ax.set_title(title, fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()
    return os.path.abspath(filename)

def save_pie_chart(df, names_col, values_col, title, filename):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    wedges, texts, autotexts = ax.pie(
        df[values_col], 
        labels=df[names_col], 
        autopct='%1.1f%%',
        startangle=90,
        colors=['#006DB6', '#42A5F5', '#FF9800', '#66BB6A', '#EF5350']
    )
    
    ax.set_title(title, fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()
    return os.path.abspath(filename)

def generate_fallback_charts_batch(kpi_data):
    """
    Recibe un diccionario con los DataFrames necesarios para generar los graficos.
    Keys expected: 
    - cat_counts (Categoría, Cantidad)
    - tipo_counts (Tipo, Cantidad)
    - cat_cost (CATEGORIA, Costo Total)
    - prof_cost (PROFESION, Costo Total)
    - prof_avg (PROFESION, Costo Promedio)
    - cat_avg (CATEGORIA, Costo Promedio)
    """
    paths = {}
    
    # 1. Dist Categoria
    if 'cat_counts' in kpi_data:
        paths['cat_counts'] = save_bar_chart(
            kpi_data['cat_counts'], 'Categoría', 'Cantidad', 
            "Dotación por Categoría", "temp_cat_counts.png", color='#006DB6'
        )

    # 2. Tipo Contrato
    if 'tipo_counts' in kpi_data:
        paths['tipo_counts'] = save_pie_chart(
            kpi_data['tipo_counts'], 'Tipo', 'Cantidad', 
            "Tipos de Contrato", "temp_tipo_counts.png"
        )
        
    # 2.1 Dist Genero (NEW)
    if 'sex_counts' in kpi_data:
        paths['sex_counts'] = save_pie_chart(
            kpi_data['sex_counts'], 'Género', 'Cantidad',
            "Distribución por Género", "temp_sex_counts.png"
        )
        
    # 3. Costo Categoria
    if 'cat_cost' in kpi_data:
        paths['cat_cost'] = save_bar_chart(
            kpi_data['cat_cost'], 'CATEGORIA', 'Costo Total', 
            "Costo Global por Categoría", "temp_cat_cost.png", color='#E53935'
        )

    # 4. Top Prof
    if 'prof_cost' in kpi_data:
        paths['prof_cost'] = save_bar_chart(
            kpi_data['prof_cost'], 'Costo Total', 'PROFESION', 
            "Top Profesiones (Costo Total)", "temp_prof_cost.png", horizontal=True, color='#43A047'
        )

    # 5. Avg Prof
    if 'prof_avg' in kpi_data:
        paths['prof_avg'] = save_bar_chart(
            kpi_data['prof_avg'], 'Costo Promedio', 'PROFESION', 
            "Costo Promedio (Profesión)", "temp_prof_avg.png", horizontal=True, color='#FB8C00'
        )

    # 6. Avg Cat
    if 'cat_avg' in kpi_data:
        paths['cat_avg'] = save_bar_chart(
            kpi_data['cat_avg'], 'Costo Promedio', 'CATEGORIA', 
            "Costo Promedio (Categoría)", "temp_cat_avg.png", horizontal=True, color='#FB8C00'
        )
        
    return paths
