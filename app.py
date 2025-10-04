
import requests
import pandas as pd
import streamlit as st
import datetime
import plotly.express as px

# Clave API de AEMET proporcionada por el usuario
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJnb256YWxvLm1hcnRpbmV6QHNmcGF1bGEuY29tIiwianRpIjoiOTExMmVlNDEtNzI1Yy00NWI1LTg3NjctNzk3YmRlYTZmNjlkIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NTk1ODQxMjQsInVzZXJJZCI6IjkxMTJlZTQxLTcyNWMtNDViNS04NzY3LTc5N2JkZWE2ZjY5ZCIsInJvbGUiOiIifQ.iUjANKo6s5zpgEztajUPzDNYwFERvsi-BZU52grEAMA"

# Coordenadas de la Plaza de la Encarnación en Sevilla
LATITUD = 37.3937
LONGITUD = -5.9901

# Encabezado educativo
st.title("Uso de los satélites de la NASA y datos de AEMET para automatizar un huerto escolar")
st.markdown("""
Esta aplicación educativa utiliza datos meteorológicos reales obtenidos por satélites de la NASA y estaciones de AEMET para controlar automáticamente un huerto escolar, optimizando el uso de agua, luz y temperatura para alimentar a 10 personas.

**Datos utilizados:** NASA POWER y AEMET  
**Controles automáticos:** riego, ventilación, sombra, seguimiento solar  
**Objetivo:** sostenibilidad, autosuficiencia, educación
""")

# Función para obtener estaciones de observación convencionales
def obtener_estaciones():
    url = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
    headers = {"accept": "application/json", "api_key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        datos_url = response.json()["datos"]
        estaciones = requests.get(datos_url).json()
        return estaciones
    else:
        st.error("No se pudo obtener estaciones de AEMET.")
        return []

# Filtrar estaciones cercanas a Sevilla
def filtrar_estaciones_cercanas(estaciones, latitud, longitud, radio_km=50):
    cercanas = []
    for est in estaciones:
        try:
            lat = float(est["latitud"])
            lon = float(est["longitud"])
            distancia = ((lat - latitud)**2 + (lon - longitud)**2)**0.5 * 111  # Aproximación en km
            if distancia <= radio_km:
                cercanas.append(est)
        except:
            continue
    return cercanas

# Obtener observaciones de una estación
def obtener_observaciones(estacion_id):
    url = f"https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/{estacion_id}"
    headers = {"accept": "application/json", "api_key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        datos_url = response.json()["datos"]
        observaciones = requests.get(datos_url).json()
        return observaciones
    else:
        st.error("No se pudo obtener observaciones de AEMET.")
        return []

# Obtener estaciones y filtrar por cercanía
estaciones = obtener_estaciones()
estaciones_cercanas = filtrar_estaciones_cercanas(estaciones, LATITUD, LONGITUD)

# Mostrar observaciones de la primera estación cercana
if estaciones_cercanas:
    estacion = estaciones_cercanas[0]
    st.subheader(f"Estación meteorológica cercana: {estacion['nombre']} ({estacion['indicativo']})")
    observaciones = obtener_observaciones(estacion["indicativo"])
    if observaciones:
        df = pd.DataFrame(observaciones)
        df["fint"] = pd.to_datetime(df["fint"])
        df = df.sort_values("fint")

        # Mostrar gráficos
        variables = {
            "ta": "Temperatura (°C)",
            "hr": "Humedad relativa (%)",
            "pres": "Presión (hPa)",
            "vv": "Velocidad del viento (m/s)",
            "prec": "Precipitación (mm)"
        }

        for var, label in variables.items():
            if var in df.columns:
                fig = px.line(df, x="fint", y=var, title=label, labels={"fint": "Fecha", var: label})
                st.plotly_chart(fig)

        # Alertas climáticas
        if "ta" in df.columns and df["ta"].max() > 35:
            st.warning("⚠️ Alerta: La temperatura ha superado los 35°C. Activar ventiladores o sombra.")

        if "prec" in df.columns and df["prec"].sum() == 0:
            st.info("🌧️ No se espera lluvia. Activar riego si la tierra está seca.")

        # Simulación de radiación solar alta
        radiacion_simulada = 850  # W/m²
        if radiacion_simulada > 800:
            st.warning("☀️ Alta radiación solar detectada. Ajustar paneles solares para generar sombra (seguimiento solar con Arduino).")

else:
    st.error("No se encontraron estaciones cercanas a Sevilla.")

# Diseño conceptual del huerto
st.subheader("Fuentes de agua sostenibles")
st.markdown("""
- 💧 **Algas**: extracción de humedad  
- 🌧️ **Contenedores de lluvia**  
- 🌫️ **Condensación del aire**: combinación de oxígeno (O₂) con hidrógeno (H₂)
""")

# Automatización del huerto escolar
st.subheader("Automatización del huerto escolar")
st.markdown("""
- 🌱 Sensores de humedad del suelo  
- 💨 Ventiladores y calefactores  
- 🌳 Servomotores para sombra  
- 🚿 Sistema de riego inteligente  
""")
