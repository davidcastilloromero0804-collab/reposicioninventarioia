import pandas as pd
import streamlit as st
import holidays
import requests
from datetime import datetime
import altair as alt

# --- CONFIGURACIÓN GLOBAL Y DISEÑO DE PÁGINA ---
st.set_page_config(page_title="OptiStock Pro | IA para Retail Colombia", page_icon="📊", layout="wide")

# --- INYECCIÓN DE ESTILOS CSS AVANZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    div.stMetric {
        background-color: white;
        border: 1px solid #e6e9ef;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(50,50,93,.11), 0 1px 3px rgba(0,0,0,.08);
    }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL MEJORADA (SIDEBAR) ---
with st.sidebar:
    st.title("OptiStock Pro 🚀")
    st.caption("Inteligencia Artificial para Retail")
    st.markdown("---")
    st.write("Optimiza tus compras considerando:")
    with st.expander("🇨🇴 Contexto Colombia", expanded=True):
        st.write("- Festivos Nacionales")
        st.write("- Pronóstico Climático Local (Medellín)")
        st.write("- Lead Time del Proveedor")
    st.markdown("---")
    st.markdown("Desarrollado para el mercado colombiano")

# --- ENCABEZADO PRINCIPAL ---
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0;">
        <div>
            <h1 style="margin: 0; color: #1e3a8a;">Sistema de Reabastecimiento Inteligente</h1>
            <p style="margin: 0; color: #4b5563; font-size: 1.1rem;">Predice la demanda, evita quiebres de stock y maximiza tus utilidades.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- MÓDULO DE CONTEXTO EXTERNO (MEDELLÍN) ---
def obtener_factor_contexto():
    factor_ajuste = 1.0
    info_contexto = []
    co_holidays = holidays.Colombia(years=datetime.now().year)
    hoy = datetime.now().date()
    proximos_dias = [hoy + pd.Timedelta(days=i) for i in range(4)]
    hay_puente = any(d in co_holidays for d in proximos_dias)
    
    if hay_puente:
        factor_ajuste += 0.15
        info_contexto.append("🎉 **¡Alerta de Puente Festivo!** Se anticipa un aumento del 15% en la demanda.")
    else:
        info_contexto.append("📅 Semana operativa estándar sin festivos próximos.")

    try:
        # Coordenadas exactas de Medellín
        url_clima = "https://api.open-meteo.com/v1/forecast?latitude=6.2518&longitude=-75.5636&current=temperature_2m,precipitation"
        respuesta = requests.get(url_clima, timeout=3).json()
        temperatura = respuesta['current']['temperature_2m']
        precipitacion = respuesta['current']['precipitation']
        
        if precipitacion > 0:
            factor_ajuste -= 0.05
            info_contexto.append(f"🌧️ **Clima en Medellín:** Lluvioso ({temperatura}°C). Ajuste a la baja por tráfico (-5%).")
        else:
            info_contexto.append(f"☀️ **Clima en Medellín:** Soleado/Seco ({temperatura}°C). Condiciones óptimas de venta.")
    except:
        info_contexto.append("🌤️ **Clima:** Datos no disponibles. Usando factor base.")
        
    return factor_ajuste, info_contexto

factor_externo, mensajes_contexto = obtener_factor_contexto()

with st.expander("🌍 Ver Análisis de Entorno y Ajustes de IA en Tiempo Real"):
    for msg in mensajes_contexto:
        st.write(f"- {msg}")

st.markdown("### Carga de Datos del Negocio")

with st.container():
    col_upload_a, col_upload_b = st.columns([3, 1])
    with col_upload_a:
        archivo_subido = st.file_uploader("📂 Sube tu reporte de inventario y ventas (CSV o Excel)", type=["csv", "xlsx"])
    with col_upload_b:
        st.write("") 
        st.write("") 
        st.caption("Descargar plantilla de ejemplo:")
        csv_template = pd.DataFrame({'producto': ['pan'], 'stock_actual': [100], 'ventas_ultimos_30_dias': [580], 'lead_time_dias': [2]}).to_csv(index=False)
        st.download_button("📥 Descargar Plantilla CSV", data=csv_template, file_name='plantilla_inventario.csv', mime='text/csv')

if archivo_subido is not None:
    if archivo_subido.name.endswith('.csv'):
        df_inventario = pd.read_csv(archivo_subido)
    else:
        df_inventario = pd.read_excel(archivo_subido)
        
    with st.expander("🔍 Vista Previa de Datos Cargados", expanded=False):
        st.dataframe(df_inventario, use_container_width=True)
    
    if st.button("🚀 Generar Plan de Reabastecimiento Inteligente", type="primary"):
        
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
            
            dias_restantes = stock_actual / venta_diaria if venta_diaria > 0 else 999
            
            if dias_restantes <= lead_time + 2:
                cantidad_a_pedir = int((venta_diaria * 15) - stock_actual)
                estado = "🔴 URGENTE: Pedir Ya"
                urgentes += 1
            elif dias_restantes > 60:
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
        
        st.markdown("### 📈 Tablero de Control Global")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Total Productos", len(df_resultado))
        col2.metric("🔴 Alertas Urgentes", urgentes)
        col3.metric("🟡 Stock Saludable", normales)
        col4.metric("🟢 En Sobrestock", sobredos)
        
        st.markdown("### 📉 Análisis Visual de Riesgo y Oportunidad")
        
        # Corrección del gráfico de dispersión usando alt.Scale en lugar de alt.Range
        chart_scatter = alt.Chart(df_resultado).mark_circle(size=120).encode(
            x=alt.X('Stock Actual', title='Unidades en Inventario'),
            y=alt.Y('Días Restantes', title='Días de Cobertura Restantes', scale=alt.Scale(domain=[0, 60])),
            color=alt.Color('Estado de Stock', scale=alt.Scale(domain=['🟢 SOBRESTOCK: Monitorear', '🟡 NORMAL: Saludable', '🔴 URGENTE: Pedir Ya'], range=['#10b981', '#f59e0b', '#ef4444'])),
            tooltip=['Producto', 'Stock Actual', 'Días Restantes', 'Estado de Stock']
        ).properties(
            title='Relación Stock Actual vs Días de Cobertura'
        ).interactive()
        
        chart_bars = alt.Chart(df_resultado[df_resultado['Cantidad Sugerida a Pedir'] > 0]).mark_bar().encode(
            x=alt.X('Producto', sort='-y'),
            y=alt.Y('Cantidad Sugerida a Pedir', title='Unidades Sugeridas a Comprar'),
            color=alt.value('#2563eb'),
            tooltip=['Producto', 'Cantidad Sugerida a Pedir']
        ).properties(
            title='Órdenes de Compra Sugeridas (Productos Críticos)'
        ).interactive()
        
        c1, c2 = st.columns(2)
        c1.altair_chart(chart_scatter, use_container_width=True)
        c2.altair_chart(chart_bars, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📋 Detalle de Sugerencias de Reabastecimiento")
        st.dataframe(df_resultado, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📤 Exportar Reporte Final")
        csv = df_resultado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Orden de Compra en CSV (Formato Excel)",
            data=csv,
            file_name='plan_reabastecimiento_saas.csv',
            mime='text/csv',
        )
else:
    st.markdown("""
        <div style="background-color: #e0f2fe; padding: 30px; border-radius: 12px; text-align: center; border: 1px solid #bae6fd;">
            <h2 style="color: #0284c7;">👋 ¡Bienvenido a OptiStock Pro!</h2>
            <p style="font-size: 1.1rem; color: #075985;">Para comenzar tu análisis predictivo en Medellín, por favor carga tu archivo de inventario en la sección superior.</p>
        </div>
    """, unsafe_allow_html=True)
