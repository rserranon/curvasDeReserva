#
# Decription: Script para generar chart de curvas de reservas históricas
#             a partir de la fecha de vuelo, para todas las rutas o rutas
#             individuales, para todos los vuelos o vuelos individuales y
#             oara un rango de fechas <inicio> <fin>
#
# Author:     Roberto Serrano
# Date:       2019/01/08
#
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import figure
import numpy as np
import calendar

fullDataFrame = pd.read_csv('Volados_Canal_201810-201901.csv', parse_dates=[6,7,8],
#fullDataFrame = pd.read_excel('Volados_Canal_20190101-20190126.xlsx', parse_dates=True,
    index_col=[6], usecols=[0, 2, 3, 4, 5, 6, 12, 13, 14,23,24,64])
#
#. use columns: 'iID_Master_Volado', 'vuelo', 'source', 'dest', 'ruta_volado', #  'equipo', 'fecha_vuelo_real', 'fecha_vuelo_programada', 'class', 'fbasis',
#       'canal'
#. index coulumn: 'fecha_emision' (6th posicion on usecols)

# fullDataFrame carga todos los datos del archivo
print("FULL FRAME COLUMNS")
print(fullDataFrame.columns)
print("")

print("FULL FRAME HEAD")
print(fullDataFrame.head())
# Same as head() -> print(fullDataFrame.iloc[:5, :11])
print("")

# Several lines/pages criteria

routesGroup = ['MEX-ACA','ACA-MEX','MEX-GDL','GDL-MEX','GDL-PVR','PVR-GDL']
cal= calendar.Calendar()
#Get the weeks of yyyy, mm
weeksMonth  = cal.monthdatescalendar(2019, 1)
print(f"numer of weks: {len(weeksMonth)}")

print("First week")
#1st day of week 1
print(weeksMonth[0][0])
#last day of week 1
print(weeksMonth[0][-1])

# We are ready to process each week of the month

# Prepare selection criteria
# This is the only area to change query parameters
#
route = 'ALL' # use route (i.e. 'MEX-ACA') or ['ALL'] for all
dateRange = ['2018-10-01','2018-10-31'] # use ['yyyy-mm-dd','yyyy-mm-dd']
flight = 648 # Fligh number (numeric) for specific flight:648 use None for all


# TODO falta el if de la ruta
if (route == 'ALL'):
    criterioRuta = fullDataFrame.ruta_volado != route # todas las rutas distintas a ALL
else:
    criterioRuta = fullDataFrame.ruta_volado == route

# curiosidad para saber de que tipo es el criterio de las rutas
# en relaidad es una serie de pandas: <class 'pandas.core.series.Series'>
print(type(criterioRuta))

# fechas en el rando de la lista dataRange[0] a [1]
criterioFecha = (fullDataFrame['fecha_vuelo_real']>=pd.to_datetime(dateRange[0])) & (fullDataFrame['fecha_vuelo_real']<=pd.to_datetime(dateRange[1]))

# TODO el criyerio vuelo debería ser un filtro sobre criterioFecha dado que es un subset del dataframe filtrado
if (flight is None):
    criterioVuelo = True
else:
    criterioVuelo = (fullDataFrame.vuelo == flight)
print(f"criterio vuelo: {criterioVuelo}")


selector = (criterioRuta & criterioFecha & criterioVuelo)

# Filter Analisys Data Frame
dfAnalysis = fullDataFrame.loc[(selector) , fullDataFrame.columns.isin(['fecha_vuelo_real','vuelo','ruta_volado', 'equipo', 'dias_anticipacion'])]

dfAnalysis.sort_index()
print("DF ANALYSIS HEAD")
print(dfAnalysis.head())
print("")

# Calculate advance bookings in days
dfAnalysis['dias_anticipacion'] = (dfAnalysis.index.get_level_values('fecha_emision') - dfAnalysis.fecha_vuelo_real).dt.days

print("DF ANALYSIS DESCRIBE")
print(dfAnalysis.describe(include='all'))
print("")

#flightCount = dfAnalysis.vuelo.nunique()
flightCountSet = dfAnalysis.groupby(['fecha_vuelo_real','vuelo']).vuelo.nunique().reset_index(name="vuelo_fecha_count")
flightCount = flightCountSet.vuelo_fecha_count.count()

print("FLIGHT COUNT SET")
print(f"No. de Vuelos(flightCount): {flightCount}")
print("")
print(flightCountSet.head())
print("")

if (flight == True):
    paxCount = dfAnalysis.vuelo.value_counts().sum()
else:
    paxCount = (dfAnalysis.vuelo == flight).value_counts()

print("PAX COUNT")
#print(type(paxCount))
print(f"Flight(s):[{flight}] PAX count: {paxCount} ")
print("")

print("FLIGHT COUNT PER DATE, FLIGHT, EQUIPMENT")
groups =dfAnalysis.groupby(['fecha_vuelo_real','vuelo','equipo']).equipo.nunique().reset_index(name="group_count")
groups['Seats'] = np.where(groups.equipo == 'AT7', 72,
                                 np.where(groups.equipo == 'ATR', 48, 0))
print(groups.head(10))
print(f"Suma Asientos = : {groups['Seats'].sum()}")
print("")

# Histogram value counts
seriesHistogram = dfAnalysis.dias_anticipacion.value_counts()

# Convert to Data Frame
dfHistogram = seriesHistogram.to_frame()



# Plot cumulative line
dfHistogram.sort_index(inplace = True, ascending = True)

# Add cumulative column HAS TO BE AFTER SORT
dfHistogram['acumulado'] = dfHistogram.dias_anticipacion.cumsum()

# Add cumulative percentage. TODO Fix it to reflect actual LF % HAS TO BE AFTER SORT
dfHistogram['cum_percent'] = 100 * (1 - ((groups['Seats'].sum() - dfHistogram.dias_anticipacion.cumsum())/groups['Seats'].sum()))

print("HISTOGRAM DATA")
print(dfHistogram)
print("")

#print(dfHistogram.index)
#dfHistogram.plot.line(y = 'cum_percent')
#dfHistogram.plot.line(y = 'acumulado')

#plt.plot(x = dfHistogram.sort_index(), dfHistogram['cum_percent'])
#plt.show()


# TODO figure out how to get in in a PDF

flightStr  = flight if flight != None else 'Todos'
routeStr = route if route != 'ALL' else 'Todas'


with PdfPages(f'Curvas-{dateRange[0]}-{dateRange[1]}-{routeStr}.pdf') as pdf:
    title = "Curvas de Reservas"
    subTitle = f"Vuelos del: {dateRange[0]} al {dateRange[1]} \n Ruta: {routeStr}"
    firstPage = plt.figure(figsize=(8.5, 11))
    firstPage.clf()
    firstPage.text(0.5,0.6,title,transform=firstPage.transFigure, size=22, ha='center')
    firstPage.text(0.5,0.4,subTitle,transform=firstPage.transFigure, size=18, ha='center')
    firstPage.text(0.5,0.2,"Planeacion Financiera & BI",transform=firstPage.transFigure, size=14, ha='center')
    pdf.savefig()
    plt.close()

    title = f"Porcentaje Acumulado Fecha: {dateRange} \n Ruta: {routeStr}, vuelo(s): {flightStr}, No. Vuelos: {flightCount}"
    # This is the way to plot two series (with a list) and with an alternate scale chart = dfHistogram.plot.line(grid=True, y = ['cum_percent','acumulado'], secondary_y = 'acumulado')
    chart = dfHistogram.plot.line(grid=True, y = ['cum_percent'])
    chart.set_xlim(-100, 0)
    chart.set_xlabel("Días de anticipación")
    chart.set_ylabel("puntos porcentuales de LF")
    plt.title(title)
    pdf.savefig()  # saves the current figure into a pdf page
    plt.close()


    title = f"PAX Acumulados Fecha: {dateRange} \n Ruta: {routeStr}, vuelo(s): {flightStr}, No. vuelos: {flightCount}"
    chart = dfHistogram.plot.line(grid=True, y = 'acumulado')
    chart.set_xlim(-100, 0)
    chart.set_xlabel("Días de anticipación")
    chart.set_ylabel("Pasajeros (PAX)")
    plt.title(title)
    pdf.savefig()
    plt.close()


    # We can also set the file's metadata via the PdfPages object:
    document = pdf.infodict()
    document['Title'] = 'Bookings Curve PDF Example'
    document['Author'] = 'Roberto Serrano'
    document['Subject'] = 'How to create a multipage pdf file and set its metadata'
    document['Keywords'] = 'bookings curves'
    document['CreationDate'] = datetime.datetime.strptime('08042019', '%d%m%Y') 
    document['ModDate'] = datetime.datetime.today()

