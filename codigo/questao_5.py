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
dropZeroValues = True 
if len(sys.argv) == 2:
    dropZeroValues = bool(sys.argv[1])

resultsDir = f"./resultados/{'questao5' if dropZeroValues else 'questao5czero'}/"

# Importando e convertendo dataset 
dataset = LoadDataset()
dataset['hour'] = dataset['date_hour'].dt.hour
# dropZeroValues resolvido abaixo
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
    # Se pelo menos uma coluna é zero, toda a linha é removida
    relData = relData[(relData['bytes_down'] != 0) & (relData['bytes_up'] != 0)]

# Coeficiente de pearson
corrRes = relData.groupby(['hour','device_type'])[['bytes_up','bytes_down']].apply(lambda x: sp.stats.pearsonr(x.iloc[:,0],x.iloc[:,1]))
corrRes = corrRes.apply(lambda x: pd.Series({'rho':x[0],'p-value':x[1]}))
print(corrRes)
corrRes.to_latex(resultsDir+"corr_results.tex")

# Plot de correlação
fig,ax = plt.subplots(1,3)
for idx, (name,data) in enumerate(relData.groupby(['hour','device_type'])):
    ax[idx].scatter(data['bytes_up'],data['bytes_down'])
    ax[idx].set_title(f"Correlation for {name[1]} @ {name[0]}hrs")
plt.savefig(resultsDir+'correlation_plots.png')

plt.show()
