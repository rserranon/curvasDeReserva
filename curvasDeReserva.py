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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import figure
import numpy as np


#fullDataFrame = pd.read_excel('Volados_Canal_20190101-20190126.xlsx', parse_dates=True,
fullDataFrame = pd.read_excel('Volados_Canal_Test_PVR_GDL_111_115_1_al_15_Enero_2019.xlsx', parse_dates=True,
    index_col=[6], usecols=[0, 2, 3, 4, 5, 6, 12, 13, 14,23,24,64])
#
#. use columns: 'iID_Master_Volado', 'vuelo', 'source', 'dest', 'ruta_volado', #  'equipo', 'fecha_vuelo_real', 'fecha_vuelo_programada', 'class', 'fbasis',
#       'canal'
#. index coulumn: 'fecha_emision' (6th posicion on usecols)

print("FULL FRAME COLUMNS")
print(fullDataFrame.columns)
print("")

print("FULL FRAME HEAD")
print(fullDataFrame.head())
# Same as head() -> print(fullDataFrame.iloc[:5, :11])
print("")

# Prepare selection criteria
# This is the only area to change query parameters
#
route = 'PVR-GDL' # use route 'MEX-ACA' or '***' for all
dateRange = ['2019-01-01','2019-01-12'] # use ['yyyy-mm-dd','yyyy-mm-dd']
flight = 111 # Fligh number (numeric) for specific flight:648 use None for all


# TODO falta el if de la ruta
criterioRuta = fullDataFrame.ruta_volado == route
criterioFecha = (fullDataFrame['fecha_vuelo_real']>=pd.to_datetime(dateRange[0])) & (fullDataFrame['fecha_vuelo_real']<=pd.to_datetime(dateRange[1]))
if (flight is None):
    criterioVuelo = True
else:
    criterioVuelo = fullDataFrame.vuelo == flight

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


if (flight == True):
    flightCount = dfAnalysis.vuelo.value_counts().sum()
else:
    flightCount = (dfAnalysis.vuelo == flight).value_counts()

print("FLIGHT COUNT")
print(f"Flight(s)[{flight}] value_count: {flightCount} ")
print("")

print("FLIGHT COUNT PER EQUIPMENT")
groups =dfAnalysis.groupby(['fecha_vuelo_real','vuelo','equipo']).equipo.nunique().reset_index(name="group_count")
groups['Seats'] = np.where(groups.equipo == 'AT7', 72,
                                 np.where(groups.equipo == 'ATR', 50, 0))
print(groups.head())
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

flightStr  = flight if flight != True else 'Todos'
routeStr = route if route != '***' else 'Todas'


with PdfPages('bookingsCurves.pdf') as pdf:
    title = "Curvas de Reservas"
    firstPage = plt.figure(figsize=(11.69, 8.27))
    firstPage.clf()
    firstPage.text(0.5,0.5,title,transform=firstPage.transFigure, size=22, ha='center')
    pdf.savefig()
    plt.close()

    title = f"Porcentaje Acumulado \n Fecha: {dateRange}, Ruta: {routeStr}, vuelo: {flightStr}"
    dfHistogram.plot.line(y = 'cum_percent')
    plt.title(title)
    pdf.savefig()  # saves the current figure into a pdf page
    plt.close()


    title = f"PAX Acumulados \n Fecha: {dateRange}, Ruta: {routeStr}, vuelo: {flightStr}"
    dfHistogram.plot.line(y = 'acumulado')
    plt.title(title)
    pdf.savefig()
    plt.close()


    # We can also set the file's metadata via the PdfPages object:
    # d = pdf.infodict()
    # d['Title'] = 'Bookings Curve PDF Example'
    # d['Author'] = u'Roberto Serrano'
    # d['Subject'] = 'How to create a multipage pdf file and set its metadata'
    # d['Keywords'] = 'bookings curves'
    # d['CreationDate'] = datetime.datetime('2019/02/06')
    # d['ModDate'] = datetime.datetime.today()

