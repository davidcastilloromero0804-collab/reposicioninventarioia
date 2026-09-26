import pandas as pd
import streamlit as st

# Configuración inicial de la página web
st.set_page_config(page_title="Reabastecimiento Predictivo IA", layout="wide")

st.title("📦 Sistema Inteligente de Reabastecimiento para Retail")
st.write("Sube el reporte de inventario y ventas de tu tienda para calcular las alertas de compra.")

# 1. Componente en la web para que el usuario suba su archivo Excel o CSV
archivo_subido = st.file_uploader("Sube tu archivo CSV o Excel con el inventario", type=["csv", "xlsx"])

if archivo_subido is not None:
    # Leer el archivo que subió el comerciante
    if archivo_subido.name.endswith('.csv'):
        df_inventario = pd.read_csv(archivo_subido)
    else:
        df_inventario = pd.read_excel(archivo_subido)
        
    st.write("### Datos cargados correctamente:")
    st.dataframe(df_inventario.head())
    
    # Botón para ejecutar la lógica de IA/Predicción
    if st.button("Analizar Inventario y Calcular Pedidos"):
        
        # --- MOTOR MATEMÁTICO DE PREDICCIÓN ---
        df_inventario['venta_diaria_promedio'] = df_inventario['ventas_ultimos_30_dias'] / 30.0
        
        sugerencias = []
        for index, row in df_inventario.iterrows():
            stock_actual = row['stock_actual']
            venta_diaria = row['venta_diaria_promedio']
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
                "Días de Inventario Restantes": round(dias_restantes, 1),
                "Estado": estado,
                "Cantidad Sugerida a Pedir": max(0, cantidad_a_pedir)
            })
            
        df_resultado = pd.DataFrame(sugerencias)
        
        # --- MOSTRAR RESULTADOS VISUALES EN LA WEB ---
        st.success("¡Análisis completado con éxito!")
        st.write("### 📊 Sugerencias de Reabastecimiento para el Comerciante")
        st.dataframe(df_resultado)
        
        # Botón para descargar el reporte listo
        csv = df_resultado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Orden de Compra en CSV",
            data=csv,
            file_name='orden_compra_sugerida.csv',
            mime='text/csv',
        )
else:
    st.info("💡 Por favor, sube un archivo para comenzar o usa un formato con columnas: `producto`, `stock_actual`, `ventas_ultimos_30_dias`, `lead_time_dias`.")
