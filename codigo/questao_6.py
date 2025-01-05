# Questao 6 - Correlações entre taxas 
# Autor: Fernando Dias 
#
# Descrição: 
#
import sys 

import numpy as np
import scipy as sp
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 

from utils import LoadDataset

dataset = LoadDataset()

# Mude para alternar entre resultados
dropZeroValues = False
if len(sys.argv) == 2:
    dropZeroValues = bool(sys.argv[1])

resultsDir = "./resultados/questao6/"

# Importando e convertendo dataset 
dataset = LoadDataset()
dataset['Hora'] = dataset['Data e hora'].dt.hour
dataset['bps'] = np.log10(dataset['bps']+1)

# Para essa questão, serão comparados 3 datasets devido ao resultado diferente 
# para upload e download no dataset do Chromecast
peakData = dataset[\
    ((dataset['Tipo de dispositivo'] == "Smart TV") & (dataset['Hora'] == 20)) |\
    ((dataset['Tipo de dispositivo'] == "Chromecast") & (dataset['Hora'] == 22)) |\
    ((dataset['Tipo de dispositivo'] == "Chromecast") & (dataset['Hora'] == 23))\
]

relData = peakData.pivot(index=['Data e hora','Hora','Tipo de dispositivo','Id do dispositivo'],columns='Direção do fluxo',values='bps').reset_index()
relData.index.name=''

if dropZeroValues:
    relData = relData[(relData['Download'] != 0) | (relData['Upload'] != 0)]

def CalculateGTest(data):
    edges = np.histogram_bin_edges(data['Download'],bins='sturges')
    histDown, _ = np.histogram(data['Download'],bins=edges)
    histUp, _ = np.histogram(data['Upload'],bins=edges)
    if np.sum(histDown) != np.sum(histUp):
        raise Exception(f"Different sizes on {data.name}: {np.sum(histUp)} up and {np.sum(histDown)} down")
    # Com lambda = 0, o resultado é o mesmo de um G-test
    results = sp.stats.power_divergence(histUp,histDown,lambda_=0)
    return pd.Series({"Estatística":results[0],r'$p$-valor':results[1]})

res = relData.groupby(['Hora','Tipo de dispositivo']).apply(CalculateGTest,include_groups=False)
res.to_latex(resultsDir+f"gtest_result{'' if dropZeroValues else '_czero'}.tex")
print(res)
