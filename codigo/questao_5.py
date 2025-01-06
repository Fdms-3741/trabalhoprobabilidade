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

resultsDir = f"./resultados/{'questao5' if dropZeroValues else 'questao5czero'}/"

print(resultsDir)

# Importando e convertendo dataset 
dataset = LoadDataset()
dataset['Hora'] = dataset['Data e hora'].dt.hour
# dropZeroValues resolvido abaixo
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
    # Se pelo menos uma coluna é zero, toda a linha é removida
    relData = relData[(relData['Download'] != 0) & (relData['Upload'] != 0)]

# Coeficiente de pearson
corrRes = relData.groupby(['Hora','Tipo de dispositivo'])[['Upload','Download']].apply(lambda x: sp.stats.pearsonr(x.iloc[:,0],x.iloc[:,1]))
corrRes = corrRes.apply(lambda x: pd.Series({r'$\rho$':x[0],r'$p$-valor':x[1]}))
print(corrRes)
corrRes.to_latex(resultsDir+"corr_results.tex")

# Plot de correlação
fig,ax = plt.subplots(1,3,figsize=(14,7))
for idx, (name,data) in enumerate(relData.groupby(['Hora','Tipo de dispositivo'])):
    ax[idx].scatter(data['Upload'],data['Download'])
    ax[idx].set_title(f"{name[1]} @ {name[0]}hrs")
plt.savefig(resultsDir+'correlation_plots.png')

