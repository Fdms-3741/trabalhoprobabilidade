# Questao 5 - Correlações entre taxas 
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
dataset['hour'] = dataset['date_hour'].dt.hour
dataset['bytes'] = np.log10(dataset['bytes']+1)

# Para essa questão, serão comparados 3 datasets devido ao resultado diferente 
# para upload e download no dataset do Chromecast
peakData = dataset[\
    ((dataset['device_type'] == "Smart TV") & (dataset['hour'] == 20)) |\
    ((dataset['device_type'] == "Chromecast") & (dataset['hour'] == 22)) |\
    ((dataset['device_type'] == "Chromecast") & (dataset['hour'] == 23))\
]

relData = peakData.pivot(index=['date_hour','hour','device_type','device_id'],columns='flow_type',values='bytes').reset_index()
relData.index.name=''

if dropZeroValues:
    relData = relData[(relData['bytes_down'] != 0) | (relData['bytes_up'] != 0)]

def CalculateGTest(data):
    edges = np.histogram_bin_edges(data['bytes_down'],bins='sturges')
    histDown, _ = np.histogram(data['bytes_down'],bins=edges)
    histUp, _ = np.histogram(data['bytes_up'],bins=edges)
    if np.sum(histDown) != np.sum(histUp):
        raise Exception(f"Different sizes on {data.name}: {np.sum(histUp)} up and {np.sum(histDown)} down")
    # Com lambda = 0, o resultado é o mesmo de um G-test
    results = sp.stats.power_divergence(histUp,histDown,lambda_=0)
    return pd.Series({"statistic":results[0],'p-value':results[1]})

res = relData.groupby(['hour','device_type']).apply(CalculateGTest,include_groups=False)
res.to_latex(resultsDir+f"gtest_result{'' if dropZeroValues else '_czero'}.tex")
print(res)
