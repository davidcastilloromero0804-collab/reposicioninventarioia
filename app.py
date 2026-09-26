import pandas as pd
import streamlit as st
import holidays
import requests
from datetime import datetime
import altair as alt # Importar altair para gráficos avanzados

# --- CONFIGURACIÓN GLOBAL Y DISEÑO DE PÁGINA ---
# Usamos una paleta de colores personalizada en el archivo de configuración de Streamlit si es posible,
# pero para hacerlo autónomo, usaremos st.markdown para inyectar estilos globales (CSS).
st.set_page_config(page_title="OptiStock Pro | IA para Retail Colombia", page_icon="📊", layout="wide")

# --- INYECCIÓN DE ESTILOS CSS AVANZADOS ---
# Esta sección cambia el aspecto de los botones, métricas, tablas y contenedores para que parezca una app web profesional.
st.markdown("""
    <style>
    /* Colores globales y fondo del cuerpo principal */
    .main {
        background-color: #f0f2f6;
    }

    /* Estilo para las tarjetas de métricas (KPIs) */
    div.stMetric {
        background-color: white;
        border: 1px solid #e6e9ef;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(50,50,93,.11), 0 1px 3px rgba(0,0,0,.08);
        transition: all .3s ease;
    }
    div.stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(50,50,93,.10), 0 3px 6px rgba(0,0,0,.08);
    }

    /* Estilo para los botones */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all .2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }
    /* Estilo para el botón principal (call to action) */
    div.stButton > button.st-emotion-cache-1r6sls0 { /* Botón de tipo "primary" en streamlit */
        background-color: #007bff;
        color: white;
        border: none;
    }
    div.stButton > button.st-emotion-cache-1r6sls0:hover {
        background-color: #0056b3;
        color: white;
    }

    /* Estilo para los DataFrames/Tablas */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(50,50,93,.11);
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL MEJORADA (SIDEBAR) ---
with st.sidebar:
    # Puedes usar una imagen propia alojada en internet o un ícono de emoji/text
    st.image("https://raw.githubusercontent.com/davidcastilloromero0804-collab/reposicioninventarioia/main/dashboard/ai_icon.png", width=90)
    st.title("OptiStock Pro 🚀")
    st.caption("Inteligencia Artificial para Retail")
    st.markdown("---")
    st.write("Optimiza tus compras considerando:")
    with st.expander("🇨🇴 Contexto Colombia", expanded=True):
        st.write("- Festivos Nacionales")
        st.write("- Pronóstico Climático Local")
        st.write("- Lead Time del Proveedor")
    st.markdown("---")
    st.markdown("Desarrollado por **Equipo de IA Colaborativa**")
    st.markdown("**Soporte:** david.castillo0804@gmail.com")


# --- ENCABEZADO PRINCIPAL ---
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0;">
        <div>
            <h1 style="margin: 0; color: #1e3a8a;">Sistema de Reabastecimiento Inteligente</h1>
            <p style="margin: 0; color: #4b5563; font-size: 1.1rem;">Predice la demanda, evita quiebres de stock y maximiza tus utilidades.</p>
        </div>
        <img src="https://raw.githubusercontent.com/davidcastilloromero0804-collab/reposicioninventarioia/main/dashboard/logo_saas.png" alt="Logo SaaS" width="150" style="border-radius: 8px;">
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- MÓDULO DE CONTEXTO EXTERNO (INTELIGENCIA) ---
def obtener_factor_contexto():
    factor_ajuste = 1.0
    info_contexto = []
    co_holidays = holidays.Colombia(years=datetime.now().year)
    hoy = datetime.now().date()
    proximos_dias = [hoy + pd.Timedelta(days=i) for i in range(4)]
    hay_puente = any(d in co_holidays for d in proximos_dias)
    
    if hay_puente:
        factor_ajuste += 0.15
        info_contexto.append("🎉 **¡Alerta de Puente Festivo!** Se anticipa un aumento del 15% en la demanda de productos de consumo masivo.")
    else:
        info_contexto.append("📅 Semana operativa estándar sin festivos próximos.")

    try:
        # Coordenadas de Bogotá por defecto (puedes cambiarlas a Medellín o principal tienda)
        url_clima = "https://api.open-meteo.com/v1/forecast?latitude=4.6097&longitude=-74.0817&current=temperature_2m,precipitation"
        respuesta = requests.get(url_clima, timeout=3).json()
        temperatura = respuesta['current']['temperature_2m']
        precipitacion = respuesta['current']['precipitation']
        
        if precipitacion > 0:
            factor_ajuste -= 0.05
            info_contexto.append(f"🌧️ **Clima en Bogotá:** Lluvioso ({temperatura}°C). Ajuste a la baja de tráfico en tienda (-5%).")
        else:
            info_contexto.append(f"☀️ **Clima en Bogotá:** Soleado ({temperatura}°C). Condiciones óptimas de venta.")
    except:
        info_contexto.append("🌤️ **Clima:** Datos no disponibles. Usando factor base.)")
        
    return factor_ajuste, info_contexto

factor_externo, mensajes_contexto = obtener_factor_contexto()

with st.expander("🌍 Ver Análisis de Entorno y Ajustes de IA en Tiempo Real"):
    for msg in mensajes_contexto:
        st.write(f"- {msg}")

st.markdown("### Carga de Datos del Negocio")

# --- ÁREA DE CARGA DE ARCHIVO ---
# Diseño de contenedor para la carga
with st.container():
    col_upload_a, col_upload_b = st.columns([3, 1])
    with col_upload_a:
        archivo_subido = st.file_uploader("📂 Sube tu reporte de inventario y ventas (CSV o Excel)", type=["csv", "xlsx"], help="El archivo debe contener columnas como: producto, stock_actual, ventas_ultimos_30_dias, lead_time_dias")
    with col_upload_b:
        st.write("") # Espaciador
        st.write("") # Espaciador
        st.caption("Descargar plantilla de ejemplo:")
        csv_template = pd.DataFrame({'producto': ['Ejemplo A'], 'stock_actual': [50], 'ventas_ultimos_30_dias': [200], 'lead_time_dias': [3]}).to_csv(index=False)
        st.download_button("📥 Descargar Plantilla CSV", data=csv_template, file_name='plantilla_inventario.csv', mime='text/csv')

if archivo_subido is not None:
    # Leer datos
    if archivo_subido.name.endswith('.csv'):
        df_inventario = pd.read_csv(archivo_subido)
    else:
        df_inventario = pd.read_excel(archivo_subido)
        
    with st.expander("🔍 Vista Previa de Datos Cargados", expanded=False):
        st.dataframe(df_inventario, use_container_width=True)
    
    # Botón principal de acción
    if st.button("🚀 Generar Plan de Reabastecimiento Inteligente", type="primary"):
        
        # --- MOTOR MATEMÁTICO Y LÓGICA DE IA ---
        # Cálculo de promedios y ajuste por contexto
        df_inventario['venta_diaria_base'] = df_inventario['ventas_ultimos_30_dias'] / 30.0
        df_inventario['Venta Diaria Ajustada (IA)'] = (df_inventario['venta_diaria_base'] * factor_externo).round(2)
        
        sugerencias = []
        urgentes = 0
        normales = 0
        sobredos = 0
        
        for index, row in df_inventario.iterrows():
            stock_actual = row['stock_actual']
            venta_diaria = row['Venta Diaria Ajustada (IA)']
            lead_time = row['lead_time_dias']
            
            # Calcular días restantes de stock
            dias_restantes = stock_actual / venta_diaria if venta_diaria > 0 else 999
            
            # Lógica de decisión de pedido
            if dias_restantes <= lead_time + 2: # Alerta si el stock cubre el lead time + buffer de seguridad
                # Sugerencia de compra: cubrir 15 días de venta proyectada
                cantidad_a_pedir = int((venta_diaria * 15) - stock_actual)
                estado = "🔴 URGENTE: Pedir Ya"
                urgentes += 1
            elif dias_restantes > 60: # Si hay demasiado stock
                estado = "🟢 SOBRESTOCK: Monitorear"
                cantidad_a_pedir = 0
                sobredos += 1
            else:
                estado = "🟡 NORMAL: Saludable"
                cantidad_a_pedir = 0
                normales += 1
                
            sugerencias.append({
                "Producto": row['producto'],
                "Stock Actual": stock_actual,
                "Venta Diaria (IA)": venta_diaria,
                "Días Restantes": round(dias_restantes, 1),
                "Estado de Stock": estado,
                "Cantidad Sugerida a Pedir": max(0, cantidad_a_pedir)
            })
            
        df_resultado = pd.DataFrame(sugerencias)
        
        st.markdown("---")
        st.success("✅ ¡Análisis completado exitosamente por el motor de IA!")
        
        # --- PANELES DE MÉTRICAS CLAVE (KPIs) ---
        st.markdown("### 📈 Tablero de Control Global")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Total Productos", len(df_resultado))
        col2.metric("🔴 Alertas Urgentes", urgentes)
        col3.metric("🟡 Stock Saludable", normales)
        col4.metric("🟢 En Sobrestock", sobredos)
        
        # --- VISUALIZACIONES GRÁFICAS AVANZADAS ---
        st.markdown("### 📉 Análisis Visual de Riesgo y Oportunidad")
        
        # Gráfico 1: Dispersión (Stock vs Días Restantes)
        # Este gráfico permite ver rápidamente cuáles son los productos más críticos (arriba a la izquierda)
        chart_scatter = alt.Chart(df_resultado).mark_circle(size=100).encode(
            x=alt.X('Stock Actual', title='Unidades en Inventario'),
            y=alt.Y('Días Restantes', title='Días de Cobertura Restantes', scale=alt.Scale(domain=[0, 60])),
            color=alt.Color('Estado de Stock', scale=alt.Range(range=['#10b981', '#f59e0b', '#ef4444'])),
            tooltip=['Producto', 'Stock Actual', 'Días Restantes', 'Estado de Stock']
        ).properties(
            title='Relación Stock Actual vs Días de Cobertura'
        ).interactive()
        
        # Gráfico 2: Barras (Cantidad a Pedir vs Producto)
        chart_bars = alt.Chart(df_resultado[df_resultado['Cantidad Sugerida a Pedir'] > 0]).mark_bar().encode(
            x=alt.X('Producto', sort='-y'),
            y=alt.Y('Cantidad Sugerida a Pedir', title='Unidades Sugeridas a Comprar'),
            color=alt.value('#2563eb'), # Color azul profesional
            tooltip=['Producto', 'Cantidad Sugerida a Pedir']
        ).properties(
            title='Órdenes de Compra Sugeridas (Productos Críticos)'
        ).interactive()
        
        # Mostrar gráficos en columnas
        c1, c2 = st.columns(2)
        c1.altair_chart(chart_scatter, use_container_width=True)
        c2.altair_chart(chart_bars, use_container_width=True)
        
        # --- TABLA DE RESULTADOS FINAL ---
        st.markdown("---")
        st.markdown("### 📋 Detalle de Sugerencias de Reabastecimiento")
        # Usamos el dataframe de streamlit para que el usuario pueda ordenar y buscar dentro de la tabla
        st.dataframe(df_resultado, use_container_width=True)
        
        # --- EXPORTACIÓN ---
        st.markdown("---")
        st.markdown("### 📤 Exportar Reporte Final")
        csv = df_resultado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Orden de Compra en CSV (Formato Excel)",
            data=csv,
            file_name='plan_reabastecimiento_saas.csv',
            mime='text/csv',
        )
        st.info("💡 **Consejo:** Una vez descargado, abre el archivo CSV directamente en Excel para gestionar la compra con tus proveedores.")

else:
    # Mensaje inicial antes de cargar archivo
    st.markdown("""
        <div style="background-color: #e0f2fe; padding: 30px; border-radius: 12px; text-align: center; border: 1px solid #bae6fd;">
            <h2 style="color: #0284c7;">👋 ¡Bienvenido a OptiStock Pro!</h2>
            <p style="font-size: 1.1rem; color: #075985;">Para comenzar tu análisis predictivo, por favor carga tu archivo de inventario en la sección superior.</p>
            <p style="color: #0c4a6e;">Asegúrate de que las columnas coincidan con la plantilla de ejemplo.</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.write("")
