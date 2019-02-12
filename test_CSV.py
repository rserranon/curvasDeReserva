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


fullDataFrame = pd.read_csv('Volados_Canal_201810-201901.csv', parse_dates=True,
#fullDataFrame = pd.read_excel('Volados_Canal_Test_PVR_GDL_111_115_1_al_15_Enero_2019.xlsx', parse_dates=True,
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
