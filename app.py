import pandas as pd
import streamlit as st
import holidays
import requests
from datetime import datetime

st.set_page_config(page_title="Reabastecimiento Predictivo IA - Colombia", layout="wide")

st.title("📦 Sistema Inteligente de Reabastecimiento con IA (Colombia)")
st.write("Sube el reporte de inventario. La IA ajustará la predicción considerando festivos y el clima actual.")

# --- MÓDULO DE CONTEXTO COLOMBIANO (Festivos y Clima) ---
def obtener_factor_contexto():
    factor_ajuste = 1.0
    info_contexto = []
    
    # 1. Verificar festivos en Colombia para este año
    co_holidays = holidays.Colombia(years=datetime.now().year)
    hoy = datetime.now().date()
    
    # Revisar si hay festivo en los próximos 3 días (efecto puente)
    proximos_dias = [hoy + pd.Timedelta(days=i) for i in range(4)]
    hay_puente = any(d in co_holidays for d in proximos_dias)
    
    if hay_puente:
        factor_ajuste += 0.15 # Aumenta un 15% la proyección por efecto fin de semana largo
        info_contexto.append("🎉 ¡Atención! Hay un puente festivo pròximo en Colombia (Ajuste de demanda +15%).")
    else:
        info_contexto.append("📅 Semana normal sin festivos cercanos.")

    # 2. Simulación / Consulta de Clima en Medellín (puedes cambiar la ciudad)
    # Usamos una API abierta o simulación inteligente basada en temporada de lluvias local
    try:
        # Coordenadas de Medellín por defecto
        url_clima = "https://api.open-meteo.com/v1/forecast?latitude=6.2518&longitude=-75.5636&current=temperature_2m,precipitation"
        respuesta = requests.get(url_clima, timeout=3).json()
        temperatura = respuesta['current']['temperature_2m']
        precipitacion = respuesta['current']['precipitation']
        
        if precipitacion > 0:
            factor_ajuste -= 0.05
            info_contexto.append(f"🌧️ Clima actual en Medellín: Lluvioso ({temperatura}°C). Ajuste leve por menor tráfico en tienda.")
        else:
            info_contexto.append(f"☀️ Clima actual en Medellín: Soleado/Seco ({temperatura}°C). Condiciones óptimas de consumo.")
    except:
        info_contexto.append("🌤️ Clima estándar considerado.")
        
    return factor_ajuste, info_contexto

# Cargar contexto actual
factor_externo, mensajes_contexto = obtener_factor_contexto()

with st.expander("🌍 Ver Contexto Externo Analizado por la IA"):
    for msg in mensajes_contexto:
        st.write(f"- {msg}")

# Subir archivo
archivo_subido = st.file_uploader("Sube tu archivo CSV o Excel con el inventario", type=["csv", "xlsx"])

if archivo_subido is not None:
    if archivo_subido.name.endswith('.csv'):
        df_inventario = pd.read_csv(archivo_subido)
    else:
        df_inventario = pd.read_excel(archivo_subido)
        
    st.write("### Datos cargados correctamente:")
    st.dataframe(df_inventario.head())
    
    if st.button("Analizar Inventario con IA y Contexto"):
        
        # --- MOTOR MATEMÁTICO ENRIQUECIDO CON IA ---
        # La venta diaria base se multiplica por el factor externo (Clima + Festivos)
        df_inventario['venta_diaria_base'] = df_inventario['ventas_ultimos_30_dias'] / 30.0
        df_inventario['venta_diaria_ajustada'] = df_inventario['venta_diaria_base'] * factor_externo
        
        sugerencias = []
        for index, row in df_inventario.iterrows():
            stock_actual = row['stock_actual']
            venta_diaria = row['venta_diaria_ajustada']
            lead_time = row['lead_time_dias']
            
            dias_restantes = stock_actual / venta_diaria if venta_diaria > 0 else 999
            
            if dias_restantes <= lead_time + 2:
                cantidad_a_pedir = int((venta_diaria * 15) - stock_actual)
                estado = "🔴 URGENTE: Pedir ya"
            elif dias_restantes > 30:
                estado = "🟢 SOBRESTOCK: Cuidado con perecer"
                cantidad_a_pedir = 0
            else:
                estado = "🟡 NORMAL: Stock saludable"
                cantidad_a_pedir = 0
                
            sugerencias.append({
                "Producto": row['producto'],
                "Stock Actual": stock_actual,
                "Venta Diaria Estimada (IA)": round(venta_diaria, 2),
                "Días de Inventario Restantes": round(dias_restantes, 1),
                "Estado": estado,
                "Cantidad Sugerida a Pedir": max(0, cantidad_a_pedir)
            })
            
        df_resultado = pd.DataFrame(sugerencias)
        
        st.success("¡Análisis predictivo completado con éxito!")
        st.write("### 📊 Sugerencias de Reabastecimiento Inteligente")
        st.dataframe(df_resultado)
        
        csv = df_resultado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Orden de Compra Optimizada",
            data=csv,
            file_name='orden_compra_inteligente.csv',
            mime='text/csv',
        )
else:
    st.info("💡 Sube un archivo con columnas: `producto`, `stock_actual`, `ventas_ultimos_30_dias`, `lead_time_dias`.")
