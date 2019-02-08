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


fullDataFrame = pd.read_excel('Volados_Canal_20190101-20190126.xlsx', parse_dates=True,
    index_col=[5], usecols=[0, 2, 3, 4, 5, 12, 13, 14,23,24,64])
#
#. use columns: 'iID_Master_Volado', 'vuelo', 'source', 'dest', 'ruta_volado',
#       'fecha_vuelo_real', 'fecha_vuelo_programada', 'class', 'fbasis',
#       'canal'
#. index coulumn: 'fecha_emision'

# Test data
print(fullDataFrame.head())

# Prepare selection criteria
route = '***'
dateRange = ['2019-01-01','2019-01-26']
flight = True # 648

criterioRuta = fullDataFrame.ruta_volado != route # fullDataFrame.ruta_volado == route == True
criterioFecha = (fullDataFrame['fecha_vuelo_real']>=pd.to_datetime(dateRange[0])) & (fullDataFrame['fecha_vuelo_real']<=pd.to_datetime(dateRange[1]))
criterioVuelo = True # fullDataFrame.vuelo == flight
selector = (criterioRuta & criterioFecha & criterioVuelo)

# Filter Analisys Data Frame
dfAnalysis = fullDataFrame.loc[(selector) , fullDataFrame.columns.isin(['fecha_vuelo_real','vuelo','ruta_volado', 'dias_anticipacion'])]

dfAnalysis.sort_index()

# Calculate advance bookings in days
dfAnalysis['dias_anticipacion'] = (dfAnalysis.index.get_level_values('fecha_emision') - dfAnalysis.fecha_vuelo_real).dt.days

print(dfAnalysis.describe(include='all'))

# Histogram value counts
seriesHistogram = dfAnalysis.dias_anticipacion.value_counts()

# Convert to Data Frame
dfHistogram = seriesHistogram.to_frame()



# Plot cumulative line
dfHistogram.sort_index(inplace = True, ascending = False)

# Add cumulative column HAS TO BE AFTER SORT
dfHistogram['acumulado'] = dfHistogram.dias_anticipacion.cumsum()

# Add cumulative percentage. TODO Fix it to reflect actual LF % HAS TO BE AFTER SORT
dfHistogram['cum_percent'] = 100 * (1 - dfHistogram.dias_anticipacion.cumsum()/dfHistogram.dias_anticipacion.sum())

print(dfHistogram)
#print(dfHistogram.index)
#dfHistogram.plot.line(y = 'cum_percent')
#dfHistogram.plot.line(y = 'acumulado')

#plt.plot(x = dfHistogram.sort_index(), dfHistogram['cum_percent'])
#plt.show()


# TODO figure out how to get in in a PDF

flightStr  = flight if flight != True else 'Todos'
routeStr = routeStr if route != '***' else 'Todas'


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

