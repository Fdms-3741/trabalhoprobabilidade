#
# Cálculo dos resultados 
# Autor: Fernando Dias 
#  
# Descrição: Esse arquivo mostra o código que realiza a importação dos dados do
# dataset, tratamento e cálculo das estatísticas relevantes. 
# Todos os resultados são calculados simultaneamente e seus resultados salvos 
# em um diretório de resultados

import numpy as np 
import scipy as sp 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 

from utils import LoadDataset

#
# "Questão 1" - Importação e tratamento de dados
#
# Colunas:
#   date_hour      datetime64[ns]
#   device_type            object
#   device_id               int64
#   flow type              object
#   bytes                 float64
#   dtype: object

for method in ['add1','dropna']:
    dataset = LoadDataset() 

    if method == 'add1':
        # Somar 1 compensa entradas com valores zero
        dataset['bytes'] = np.log10(dataset['bytes']+1)
    elif method == 'dropna':
        dataset = dataset.replace(0,np.nan)
        dataset.dropna(subset='bytes',inplace=True)
        dataset['bytes'] = np.log10(dataset['bytes'])
    else:
        raise NotImplementedError 
    #
    # Questão 2 
    #
    # Descrição: O objetivo dessa questão é determinar estatísticas básicas para todo o conjunto de dados. 
    #

    globalStats = pd.DataFrame({
            "count":  dataset.groupby(['device_type','flow_type'])['bytes'].count(),
            "average":  dataset.groupby(['device_type','flow_type'])['bytes'].mean(),
            "std_dev":  dataset.groupby(['device_type','flow_type'])['bytes'].var(ddof=1),
            "variance":  dataset.groupby(['device_type','flow_type'])['bytes'].std(ddof=1)
    })

    print(globalStats)

    # Salva resultados como tabela no latex
    globalStats.to_latex(f'./resultados/questao2/global_stats_{method}.tex')

    # Histogramas
    fig = sns.displot(data=dataset,kind='hist',bins='sturges',x='bytes',row='device_type',col='flow_type')
    fig.set(xlim=(-0.25,8.25))
    plt.savefig(f'./resultados/questao2/histograms_{method}.png')
    print("Histograms made")

    # ECDFs 
    fig = sns.displot(data=dataset,kind='ecdf',x='bytes',row='device_type',col='flow_type')
    fig.set(xlim=(-0.25,8.25))
    plt.savefig(f'./resultados/questao2/ecdfs_{method}.png')
    print("ECDFs made")

    # Boxplots
    sns.catplot(data=dataset,kind='box',x='device_type',hue='flow_type',y='bytes')
    plt.savefig(f"./resultados/questao2/boxplots_{method}.png")

plt.show()
