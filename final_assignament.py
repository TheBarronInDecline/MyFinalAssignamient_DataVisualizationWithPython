#Importamos las biblotecas necesarias 
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

#Cargamos el dataset de ventas de autos en un dataframe
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

#Establecemos nuestra aplicacion dash
app = dash.Dash(__name__)

#Establecemos las opciones para el Dropdown que nos va a permitir elegir el tipo de reporte estadistico que queremos ver
dropdown_options = [{"label":"Yearly Statistics", "value": "Yearly Statistics"}
                    ,{"label": "Recession Period Statistics", "value": "Recession Period Statistics"}]

#Creamos una lista de años para el Dropdown que nos va a permitir elegir el año en que se basan las estadisticas a presentar 
year_list = [i for i in range(1980, 2024, 1)]

#Planteamos el Layout de nuestro Dashboard
app.layout = html.Div(children=[html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center',"color":"#503D36","font-size":24})
                                ,html.Div([html.Label("Select Statistics:"),dcc.Dropdown(id="dropdown-statistics",options=dropdown_options,value="Select Statistics",placeholder="Select a report type",style={"width":"80%","padding":"3px","font-size":"20px","text_align-last":"center"})])
                                ,html.Div(dcc.Dropdown(id="select-year",options=[{'label': i, 'value': i} for i in year_list],value="Select-year",placeholder="Select-year",style={"width":"80%","padding":"3px","font-size":"20px","text_align-last":"center"}))
                                ,html.Div([html.Div(id="output-container",className="chart-grid",style={"diplay":"flex"}),])
                                ])

#Creamos el decorador para la callback function "update_input_container()"
@app.callback(
    Output(component_id="select-year",component_property="disabled")
    ,Input(component_id="dropdown-statistics",component_property="value"))

#La idea de esta funcion es habilitar o bloquear(con "component_property="disabled"") el dropdown "select-year", 
#en funcion de que elija el usuario en el dropdown "dropdown-statistics". Si elije "Yearly Statistics" se habilita el siguente dropdown,
#sino se bloquea.
def update_input_container(selected_statistics):
    if selected_statistics == "Yearly Statistics":
        return False
    else:
        return True

#Creamos el decorador para la callback function "update_output_container()"
@app.callback(
    Output(component_id="output-container",component_property="children")
    ,[Input(component_id="dropdown-statistics",component_property="value")
    ,Input(component_id="select-year",component_property="value")])

#Nosostros establecimos en el layout un espacio para poner graficos "output-container", este espacio va a ser ocupado por 4 graficos,
#estos graficos van a ser distintos segun el usario elija "Recession Period Statistics" o "Yearly Statistics". La funcionalidad
#de la callback function "update_output_container()" es justamente esa, separar el conjunto de graficos en funcion de cual fue la eleccion del
#usario en el primer dropdown.
def update_output_container(input_statistics, input_year):
    if input_statistics == "Recession Period Statistics":
        #Filtramos los datos solo para mostrar periodos de recesion economica, y pasamos a crear los 4 graficos de este tipo de reporte
        recession_data = data[data["Recession"]==1]

        #Grafico 1 = Grafico lineal para representar la fluctiacion de las ventas promedio de los autos año a año en tiempo de recession
        #Agrupamos los datos de ventas, promediados por año
        yearly_rec = recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        #Graficamos con plotly.express. vamos a asignar todos los graficos a core components(dcc.Graph), en este caso, el componete "R_chart1"
        R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x="Year",y="Automobile_Sales", title="Average Automobile sales fluctuation over recession periods (Year wise)"))

        #Grafico 2 = Grafico de barras para representar la venta promedio de vehiculos en funcion de su categoria en tiempos de recession
        #Agrupamos los datos de ventas promedio por categoria 
        type_rec = recession_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        #Graficamos con plotly.express
        R_chart2 = dcc.Graph(figure=px.bar(type_rec,x="Vehicle_Type",y="Automobile_Sales",title="Average automobile sales by vehicle type during recession periods"))

        #Grafico 3 = Grafico de tarta para representar el gasto total de publicidad distribuido por cada categoria de vehiculo durante preriodos recesivos
        #Agrupamos los datos en funcion de la catergoria de auto y sumamos el gasto en publicidad de cada categoria para objetner el total 
        exp_rec = recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
        #Graficamos con Plotly express
        R_chart3 = dcc.Graph(figure=px.pie(exp_rec,values="Advertising_Expenditure",names="Vehicle_Type", title="Vehicle type total advertising expenditure during recession periods"))
        
        #Grafico 4 = Grafico de barras que representa el efecto de la tasa de desempleo en las ventas promedio de distintas categorias de autos durante tiempos recesivos
        #Agrupamos los datos de ventas promedio en funcion de la categoria de auto y en funcion de la tasa de desempleo
        unem_re = recession_data.groupby(["Vehicle_Type","unemployment_rate"])["Automobile_Sales"].mean().reset_index()
        #Graficamos con plotly.express
        R_chart4 = dcc.Graph(figure=px.bar(unem_re, x="unemployment_rate", y="Automobile_Sales",color="Vehicle_Type",labels={"unemployment_rate":"Unemployment Rate","Automobile_Sales":"Average Automobile Sales"},title="Effect of unemployment rate on vehicle type and sales"))

        #Ahora vamos a llevar los graficos creados a el espacio "output-container". Estos graficos se van a separar en 2 segmentos (html.Div),
        #recordemos usar style={"display":"flex"} para que quede un grafico junto a otro
        return[html.Div(className="chart-item", children=[html.Div(children=R_chart1),html.Div(children=R_chart2)],style={'display': 'flex'})
               ,html.Div(className="chart-item", children=[html.Div(children=R_chart3),html.Div(children=R_chart4)],style={"display": "flex"})]
    elif input_year and input_statistics == "Yearly Statistics":
        #Filtramos los datos para que nos muestren informacion año a año
        yearly_data = data[data["Year"]== input_year]
    
        #Grafico 1 = Grafico lineal que represenya la ventas promedio anuales de autos
        #Agrupamos los datos de ventas promedio por año 
        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        #Graficamos con plotly.express 
        Y_chart1 = dcc.Graph(figure=px.line(yas,x="Year",y="Automobile_Sales",title="Yearly averge automobile sales"))

        #Grafico 2 = Grafico lineal que representa las ventas mensuales totales en un año especifico
        #Agrupamos los datos de ventas por mes y sumanos el total de cada mes
        mas = data.groupby("Month")["Automobile_Sales"].sum().reset_index()
        #Graficamos con plotly.express
        Y_chart2 = dcc.Graph(figure=px.line(mas,x="Month",y="Automobile_Sales",title="Total Monthly Automobile Sales"))

        #Grafico 3 = Grafico de barras que representa el numero promedio de autos vendidos por categoria en un año establedido por el usario
        #Agrupamos los datos de ventas promedio por año dado
        avr_vdata = yearly_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        #Graficamos con plotly.express
        Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata,x="Vehicle_Type",y="Automobile_Sales",title="Average Vehicles Sold by Vehicle Type in the year {}".format(input_year)))

        #Grafico 4 = Grafico de tarta que representa el gasto total en publicidad de autos por categoria
        #Agrupamos los datos de gasto total en publicidad por la categoria de auto 
        exp_data = data.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
        #Graficamos con PLotly.express
        Y_chart4 = dcc.Graph(figure=px.pie(exp_data,values="Advertising_Expenditure",names="Vehicle_Type",title="Total Advertisment Expenditure for Each Vehicle"))

        #Ahora vamos a llevar los graficos creados a el espacio "output-container". Estos graficos se van a separar en 2 segmentos (html.Div),
        #recordemos usar style={"display":"flex"} para que quede un grafico junto a otro
        return [html.Div(className="chart-item",children=[html.Div(Y_chart1),html.Div(Y_chart2)],style={"display":"flex"})
                ,html.Div(className="chart-item",children=[html.Div(Y_chart3),html.Div(Y_chart4)],style={"display":"flex"})]
#Ejecutamos la aplicacion para obtener el dashboard
if __name__ == '__main__':
    app.run_server(debug=True)