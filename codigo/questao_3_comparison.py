# Questão 3 - Comparar as médias nos casos com e sem valores nulos
# Autor: Fernando Dias 
#
from itertools import product 

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns

from utils import LoadDataset

resultsDir = f"./resultados/questao3comparison/"

# Caso sem zeros
dataset = LoadDataset()

dataset.replace(0.0,np.nan,inplace=True)
dataset.dropna(inplace=True)
dataset['bps'] = np.log10(dataset['bps']+1)

dataset['Hora'] = dataset['Data e hora'].dt.hour
del dataset['Data e hora']

# Média, var e std
res = dataset.groupby(['Hora','Tipo de dispositivo','Direção do fluxo']).apply(
    lambda x : pd.Series({
        "Média": x['bps'].mean(),
        'Desvio padrão': np.std(x['bps'],ddof=1),
        'Variância': np.var(x['bps'],ddof=1) # Utiliza o denominador N - 1
    })
)

res = res.reset_index().pivot(index='Hora',columns=['Tipo de dispositivo','Direção do fluxo'])
res.columns = res.columns.reorder_levels([1,2,0])
res = res.T.sort_index().T
rangeNonZeroHours = res.loc[:,(slice(None),slice(None),'Média')].apply(lambda x: pd.Series({"Máximo":x.max(),"Mínimo":x.min()}))
rangeNonZeroHours = rangeNonZeroHours.T
rangeNonZeroHours.index = rangeNonZeroHours.index.droplevel(2)
rangeNonZeroHours = rangeNonZeroHours.reset_index()

# Caso com zeros
dataset = LoadDataset()

dataset['bps'] = np.log10(dataset['bps']+1)

dataset['Hora'] = dataset['Data e hora'].dt.hour
del dataset['Data e hora']

# Média, var e std
res = dataset.groupby(['Hora','Tipo de dispositivo','Direção do fluxo']).apply(
    lambda x : pd.Series({
        "Média": x['bps'].mean(),
        'Desvio padrão': np.std(x['bps'],ddof=1),
        'Variância': np.var(x['bps'],ddof=1) # Utiliza o denominador N - 1
    })
)

res = res.reset_index().pivot(index='Hora',columns=['Tipo de dispositivo','Direção do fluxo'])
res.columns = res.columns.reorder_levels([1,2,0])
res = res.T.sort_index().T
rangeZeroHours = res.loc[:,(slice(None),slice(None),'Média')].apply(lambda x: pd.Series({"Máximo":x.max(),"Mínimo":x.min()}))
rangeZeroHours = rangeZeroHours.T
rangeZeroHours.index = rangeZeroHours.index.droplevel(2)
rangeZeroHours = rangeZeroHours.reset_index()

rangeData = pd.concat([rangeNonZeroHours[['Tipo de dispositivo','Direção do fluxo','Mínimo','Máximo']],rangeZeroHours[['Mínimo','Máximo']]],axis=1)
rangeData = rangeData.set_index(['Tipo de dispositivo','Direção do fluxo'])
rangeData.columns = pd.MultiIndex.from_tuples(list(product(['Sem zeros','Com zeros'],['Mínimo','Máximo'])))
print(rangeData) 
rangeData.to_latex(resultsDir+'tabela_comparacao.tex')
