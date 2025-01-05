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
#   Data e hora            datetime64[ns]
#   Tipo de dispositivo            object
#   Id do dispositivo               int64
#   Direção do fluxo               object
#   bps                           float64


for method in ['add1','dropna']:
    dataset = LoadDataset() 

    if method == 'add1':
        # Somar 1 compensa entradas com valores zero
        dataset['bps'] = np.log10(dataset['bps']+1)
    elif method == 'dropna':
        dataset = dataset.replace(0,np.nan)
        dataset.dropna(subset='bps',inplace=True)
        dataset['bps'] = np.log10(dataset['bps'])
    else:
        raise NotImplementedError 
    #
    # Questão 2 
    #
    # Descrição: O objetivo dessa questão é determinar estatísticas básicas para todo o conjunto de dados. 
    #

    globalStats = pd.DataFrame({
            "$n$":  dataset.groupby(['Tipo de dispositivo','Direção do fluxo'])['bps'].count(),
            "Média":  dataset.groupby(['Tipo de dispositivo','Direção do fluxo'])['bps'].mean(),
            "Desvio padrão":  dataset.groupby(['Tipo de dispositivo','Direção do fluxo'])['bps'].var(ddof=1),
            "Variância":  dataset.groupby(['Tipo de dispositivo','Direção do fluxo'])['bps'].std(ddof=1)
    })

    print(globalStats)

    # Salva resultados como tabela no latex
    globalStats.to_latex(f'./resultados/questao2/global_stats_{method}.tex',escape=True)

    # Histogramas
    fig = sns.displot(data=dataset,kind='hist',bins='sturges',x='bps',row='Tipo de dispositivo',col='Direção do fluxo')
    fig.set(xlim=(-0.25,8.25))
    plt.savefig(f'./resultados/questao2/histograms_{method}.png')
    print("Histograms made")

    # ECDFs 
    fig = sns.displot(data=dataset,kind='ecdf',x='bps',row='Tipo de dispositivo',col='Direção do fluxo')
    fig.set(xlim=(-0.25,8.25))
    plt.savefig(f'./resultados/questao2/ecdfs_{method}.png')
    print("ECDFs made")

    # Boxplots
    sns.catplot(data=dataset,kind='box',x='Tipo de dispositivo',hue='Direção do fluxo',y='bps')
    plt.savefig(f"./resultados/questao2/boxplots_{method}.png")

