import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import warnings
import io
warnings.filterwarnings("ignore")

@st.cache_data
def convierte_csv(df):
    return df.to_csv(index=False, sep="#").encode("utf-8")

def mensaje_exito():
    exito= st.success("Archivo descargado correctamente", icon="✅")
    time.sleep(3)
    exito.empty()
#############

st.title("DATOS BRUTOS")

url = "https://ahcamachod.github.io/productos"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
json_data = soup.pre.contents[0]
datos = pd.read_json(io.StringIO(json_data))
datos["Fecha de Compra"]= pd.to_datetime(datos["Fecha de Compra"], format="%d/%m/%Y")

with st.expander("Columnas"):
    columnas = st.multiselect("Selecciona las columnas a mostrar", list(datos.columns), list(datos.columns))

st.sidebar.title("Filtros")

with st.sidebar.expander("Nombre del producto"):
    nombre_producto = st.multiselect("Selecciona los productos a mostrar", datos["Producto"].unique(),datos["Producto"].unique())

with st.sidebar.expander("Categoría del producto"):
    categoria_producto = st.multiselect("Selecciona las categorías a mostrar", datos["Categoría del Producto"].unique(),datos["Categoría del Producto"].unique())

with st.sidebar.expander("Precio del producto"):
    precio_producto = st.slider("Selecciona el rango de precios", float(datos["Precio"].min()), float(datos["Precio"].max()), (float(datos["Precio"].min()), float(datos["Precio"].max())))

with st.sidebar.expander("Costo de envío del producto"):
    costo_envio = st.slider("Selecciona el rango de costos de envío", float(datos["Costo de envío"].min()), float(datos["Costo de envío"].max()), (float(datos["Costo de envío"].min()), float(datos["Costo de envío"].max())))

with st.sidebar.expander("Fecha de compra"):
    fecha_compra = st.date_input("Selecciona la fecha de compra", value=(datos["Fecha de Compra"].min(), datos["Fecha de Compra"].max()))

with st.sidebar.expander("Nombre del vendedor"):
    nombre_vendedor = st.multiselect("Selecciona los vendedores a mostrar", datos["Vendedor"].unique(),datos["Vendedor"].unique())

with st.sidebar.expander("Lugar de compra"):
    lugar_compra = st.multiselect("Selecciona los lugares de compra a mostrar", datos["Lugar de Compra"].unique(),datos["Lugar de Compra"].unique())

with st.sidebar.expander("Calificación del producto"):
    calificacion_producto = st.slider("Selecciona el rango de calificaciones", int(datos["Calificación"].min()), int(datos["Calificación"].max()), (int(datos["Calificación"].min()), int(datos["Calificación"].max())))

with st.sidebar.expander("Método de pago"):
    metodo_pago = st.multiselect("Selecciona los métodos de pago a mostrar", datos["Método de pago"].unique(),datos["Método de pago"].unique())

with st.sidebar.expander("Cantidad de cuotas"):
    cantidad_cuotas = st.slider("Selecciona el rango de cantidad de cuotas", int(datos["Cantidad de cuotas"].min()), int(datos["Cantidad de cuotas"].max()), (int(datos["Cantidad de cuotas"].min()), int(datos["Cantidad de cuotas"].max())))

query = """
Producto in @nombre_producto and \
@precio_producto[0] <= Precio <= @precio_producto[1] and \
@fecha_compra[0] <= `Fecha de Compra` <= @fecha_compra[1] and \
@costo_envio[0] <= `Costo de envío` <= @costo_envio[1] and \
`Categoría del Producto` in @categoria_producto and \
`Vendedor` in @nombre_vendedor and \
`Lugar de Compra` in @lugar_compra and \
`Calificación` in @calificacion_producto and \
`Método de pago` in @metodo_pago and \
`Cantidad de cuotas` in @cantidad_cuotas
"""

datos_filtrados = datos.query(query)
datos_filtrados = datos_filtrados[columnas]

st.dataframe(datos_filtrados, use_container_width=True)

st.markdown(f"La tabla posee :blue[{datos_filtrados.shape[0]}] filas y :blue[{datos_filtrados.shape[1]}] columnas.")

st.markdown("Escribe un nombre para el archivo CSV a descargar (sin extensión):")

col1, col2 = st.columns([2, 1])

with col1:
    nombre_archivo = st.text_input("", label_visibility="collapsed", value="datos_brutos")
    nombre_archivo += ".csv"

with col2:
    st.download_button("Descargar CSV", data=convierte_csv(datos_filtrados), file_name=nombre_archivo,
                        mime="text/csv", on_click=mensaje_exito)