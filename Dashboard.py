from bs4 import BeautifulSoup
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import warnings
import io

warnings.filterwarnings("ignore")

def formato_numero(valor,prefijo=""):
    for unidad in ["", "mil"]:
        if valor < 1000:
            return f"{prefijo}{valor:.2f} {unidad}"
        valor /= 1000
    return f"{prefijo}{valor:.2f} millones"

#############

st.set_page_config(layout="wide")

st.title("DASHBOARD DE VENTAS &#128722;")

url = "https://ahcamachod.github.io/productos"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
json_data = soup.pre.contents[0]
datos = pd.read_json(io.StringIO(json_data))
datos["Fecha de Compra"]= pd.to_datetime(datos["Fecha de Compra"], format="%d/%m/%Y")

#############

regiones_dict = {"Bogotá" :"Andina", "Medellín" :"Andina", "Cali" :"Pacífica",
                "Pereira" :"Andina", "Barranquilla" :"Caribe", "Cartagena" :"Caribe",
                "Cúcuta":"Andina", "Bucaramanga":"Andina", "Riohacha":"Caribe",
                "Santa Marta":"Caribe","Leticia":"Amazónica","Pasto":"Andina","Manzinales":"Andina",
                "Neiva":"Andina","Villavicencio":"Orinoquía","Armenia":"Andina","Soacha":"Andina",
                "Valledupar":"Caribe", "Inirida":"Amazónica"}

datos["Región"] = datos["Lugar de Compra"].map(regiones_dict)
datos["Año"] = datos["Fecha de Compra"].dt.year

#############

regiones= ["Colombia", "Caribe", "Pacífica", "Andina", "Orinoquía", "Amazónica"]

st.sidebar.title("Filtros")
region = st.sidebar.selectbox("Region", regiones)
if region == "Colombia":
    datos = datos.loc[datos["Región"]!="Colombia"]
else:
    datos = datos.loc[datos["Región"]==region]

todos_anos = st.sidebar.checkbox("Datos de todo el periodo", value=True)
if todos_anos:
    datos = datos
else:
    ano = st.sidebar.slider("Año", 2020,2023)
    datos = datos.loc[datos["Año"]==ano]

filtro_vendedores = st.sidebar.multiselect("Vendedores",datos.Vendedor.unique())
if filtro_vendedores:
    datos = datos[datos["Vendedor"].isin(filtro_vendedores)]
else:
    datos = datos
#############

fact_ciudades = datos.groupby("Lugar de Compra")["Precio"].sum()
fact_ciudades = datos.drop_duplicates(subset="Lugar de Compra")[["Lugar de Compra", "lat", "lon"]].merge(fact_ciudades, left_on="Lugar de Compra",
                                                                                                         right_index=True).sort_values("Precio", ascending=False)
ventas_ciudades = datos.groupby("Lugar de Compra")["Precio"].agg(["count"])
ventas_ciudades = datos.drop_duplicates(subset="Lugar de Compra")[["Lugar de Compra", "lat", "lon"]].merge(ventas_ciudades, left_on="Lugar de Compra",
                                                                                                         right_index=True).sort_values("count", ascending=False)

facturacion_mensual= datos.set_index("Fecha de Compra").groupby(pd.Grouper(freq="ME"))["Precio"].sum().reset_index()
facturacion_mensual["Año"]= facturacion_mensual["Fecha de Compra"].dt.year
facturacion_mensual["Mes"]= facturacion_mensual["Fecha de Compra"].dt.month_name()

ventas_mensual= datos.set_index("Fecha de Compra").groupby(pd.Grouper(freq="ME"))["Precio"].agg(["count"]).reset_index()
ventas_mensual["Año"]= facturacion_mensual["Fecha de Compra"].dt.year
ventas_mensual["Mes"]= facturacion_mensual["Fecha de Compra"].dt.month_name()

facturacion_cat= datos.groupby("Categoría del Producto")[["Precio"]].sum().sort_values("Precio",ascending=False)

ventas_cat = (datos.groupby("Categoría del Producto")["Precio"].count().sort_values(ascending=False).reset_index(name="Cantidad de Ventas"))

vendedores= pd.DataFrame(datos.groupby("Vendedor")["Precio"].agg(["sum", "count"]))

#############

fig_fact = px.scatter_geo(fact_ciudades, lat="lat", lon="lon", scope="south america", size="Precio", template="seaborn", hover_name="Lugar de Compra",
                             hover_data={"lat":False, "lon":False}, title="Facturacion por ciudad")
fig_fact.update_geos(fitbounds="locations")

fig_fact_mes = px.line(facturacion_mensual, x="Mes", y="Precio", markers=True, range_y=(0, facturacion_mensual.max()), color="Año",line_dash="Año",
                        template="seaborn", title="Facturacion mensual")
fig_fact_mes.update_layout(yaxis_title="Facturacion")

fig_ventas_mes = px.line(ventas_mensual, x="Mes", y="count", markers=True, range_y=(0, ventas_mensual.max()), color="Año",line_dash="Año",
                        template="seaborn", title="Cantidad de ventas mensual")
fig_ventas_mes.update_layout(yaxis_title="Cantidad de ventas")

fig_fact_ciudades = px.bar(fact_ciudades, x="Lugar de Compra", y="Precio",text_auto=True, template="seaborn", title="Top Ciudades (Facturacion)")
fig_fact_ciudades.update_layout(yaxis_title="Facturacion")


fig_ventas_ciudades = px.bar(ventas_ciudades, x="Lugar de Compra", y="count",text_auto=True, template="seaborn", title="Top Ciudades (Cantidad de Ventas)")
fig_ventas_ciudades.update_layout(yaxis_title="Cantidad de ventas")
fig_ventas = px.scatter_geo(ventas_ciudades, lat="lat", lon="lon", scope="south america", size="count", template="seaborn", hover_name="Lugar de Compra",
                             hover_data={"lat":False, "lon":False}, title="Cantidad de ventas por ciudad")
fig_ventas.update_geos(fitbounds="locations")
fig_fact_cat= px.bar(facturacion_cat,text_auto=True, template="seaborn", title="Top Categorias (Facturacion)")
fig_fact_cat.update_layout(yaxis_title="Facturacion")

fig_ventas_cat= px.bar(ventas_cat, x="Categoría del Producto", y="Cantidad de Ventas", text_auto=True, template="seaborn", title="Top Categorias (Cantidad de Ventas)")
fig_ventas_cat.update_layout(yaxis_title="Cantidad de ventas")

#############

tab1, tab2, tab3 = st.tabs(["Facturacion", "Cantidad de ventas", "Vendedores"]) 

with tab1:
    col1,col2 = st.columns(2)

    with col1:
        st.metric("Facturacion", formato_numero(datos["Precio"].sum(), "COP"))
        st.plotly_chart(fig_fact, use_container_width=True)
        st.plotly_chart(fig_fact_ciudades, use_container_width=True)
    with col2:
        st.metric("Cantidad de ventas", formato_numero(datos.shape[0]))
        st.plotly_chart(fig_fact_mes, use_container_width=True)
        st.plotly_chart(fig_fact_cat, use_container_width=True)
with tab2:
    col1,col2 = st.columns(2)
    ct_cantidad_ventas = st.number_input ("Lugar de Compra", 2,10,5)
    with col1:
        st.metric("Facturacion", formato_numero(datos["Precio"].sum(), "COP"))
        st.plotly_chart(fig_ventas, use_container_width=True)
        st.plotly_chart(fig_ventas_ciudades, use_container_width=True)
    with col2:
        st.metric("Cantidad de ventas", formato_numero(datos.shape[0]))
        st.plotly_chart(fig_ventas_mes, use_container_width=True)
        st.plotly_chart(fig_ventas_cat, use_container_width=True)
with tab3:
    col1,col2 = st.columns(2)
    ct_vendedores = st.number_input ("Cantidad de vendedores", 2,10,5)
    with col1:
        st.metric("Facturacion", formato_numero(datos["Precio"].sum(), "COP"))
        fig_facturacion_vendedores= px.bar(vendedores[["sum"]].sort_values("sum").head(ct_vendedores),
                                            y=vendedores[["sum"]].sort_values("sum").head(ct_vendedores).index, x="sum",
                                            text_auto=True, template="seaborn", title=f"Top {ct_vendedores} Vendedores (Facturacion)")
        st.plotly_chart(fig_facturacion_vendedores, use_container_width=True)
    with col2:
        st.metric("Cantidad de ventas", formato_numero(datos.shape[0]))
        fig_cantidad_ventas= px.bar(vendedores[["count"]].sort_values("count").head(ct_vendedores),
                                    y=vendedores[["count"]].sort_values("count").head(ct_vendedores).index, x="count",
                                    text_auto=True, template="seaborn", title=f"Top {ct_vendedores} Vendedores (Cantidad de ventas)")
        st.plotly_chart(fig_cantidad_ventas, use_container_width=True)

        st.dataframe(datos)
