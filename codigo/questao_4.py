#
# Questão 4 - Análise do tráfego nos horários de pico 
# Autor: Fernando Dias 
#
#
import re
import sys

import numpy as np
import scipy as sp
import pandas as pd 
import seaborn as sns 
import statsmodels.api as sm
import matplotlib.pyplot as plt 

from utils import LoadDataset 

# Mude para alternar entre resultados
dropZeroValues = False 
if len(sys.argv) == 2:
    dropZeroValues = bool(sys.argv[1])

resultsDir = f"./resultados/questao4{'czero' if not dropZeroValues else ''}/"

# Importando e convertendo dataset 
dataset = LoadDataset()
dataset['Hora'] = dataset['Data e hora'].dt.hour
if dropZeroValues: 
    dataset = dataset.replace(0,np.nan)
    dataset.dropna(subset='bps',inplace=True)
dataset['bps'] = np.log10(dataset['bps']+1)

# Passo 1 - Criação do dataset 
# Filtrando pelos horários de pico encontrados na questão anterior
peakData = dataset[\
    ((dataset['Tipo de dispositivo'] == "Smart TV") & (dataset['Hora'] == 20)) |\
    ((dataset['Tipo de dispositivo'] == "Chromecast") & (dataset['Direção do fluxo'] == 'Upload') & (dataset['Hora'] == 22)) |\
    ((dataset['Tipo de dispositivo'] == "Chromecast") & (dataset['Direção do fluxo'] == 'Download') & (dataset['Hora'] == 23))\
]

# Contagem dos dados 
countColumns = peakData[['Tipo de dispositivo','Direção do fluxo','Hora']].value_counts()
print(countColumns)
countColumns.to_latex(resultsDir+'contagem_dados.tex')

# Removendo colunas desnecessárias
del peakData['Data e hora']
del peakData['Hora']

print("Working dataset:")
print(peakData)

# Passo 2 - Histogramas
fig = sns.displot(data=peakData,common_bins=False, common_norm=False, kind='hist',bins='sturges',stat='density',x='bps',row='Tipo de dispositivo',col='Direção do fluxo')

# Passo 3 - Cálculo do MLE
# A função fit do scipy já utiliza o método de máxima verossimilhança para otimização de parâmetros
normalFit = peakData.groupby(['Tipo de dispositivo','Direção do fluxo'])['bps'].apply(sp.stats.norm.fit, method='mle')
normalFit = pd.DataFrame({
    r'$\mu$':normalFit.apply(lambda x: x[0]),
    r'$\sigma^2$':normalFit.apply(lambda x: x[1])
})
print("Normal fit")
print(normalFit)
normalFit.to_latex(resultsDir+'mle_normal.tex')

# O argumento floc faz com que a função não tente otimizar a posição da variável x, para o caso de x' = x + offset
gammaFit = peakData.groupby(['Tipo de dispositivo','Direção do fluxo'])['bps'].apply(sp.stats.gamma.fit,floc=-1e-5, method='mle')
gammaFit = pd.DataFrame({
    r'$\alpha$':gammaFit.apply(lambda x: x[0]),
    r'$\lambda$':gammaFit.apply(lambda x: 1/x[2]) 
})
print("Gamma fit")
print(gammaFit)
gammaFit.to_latex(resultsDir+'mle_gamma.tex')

# Passo 4 - Fazer o plot das distribuições utilizando os parâmetros encontrados
for ax in fig.axes.ravel():
    devType  = re.search(r'Tipo de dispositivo\s=\s(\S+(\s\w+)?)',ax.get_title())[1]
    flowType = re.search(r'Direção do fluxo\s=\s(\S+)',ax.get_title())[1]

    x0,x1 = ax.get_xlim()
    x = np.linspace(x0,x1,200)
    
    # Normal  
    ax.plot(x,
        sp.stats.norm.pdf(
            x,
            normalFit.loc[(devType,flowType),r'$\mu$'],
            scale=normalFit.loc[(devType,flowType),r'$\sigma^2$']
            )
        )

    # Gamma dist 
    ax.plot(x,
        sp.stats.gamma.pdf(
            x,
            a=gammaFit.loc[(devType,flowType),r'$\alpha$'],
            scale=1/gammaFit.loc[(devType,flowType),r'$\lambda$']
            )
        )
    ax.set_xlim(x0,x1)
plt.savefig(resultsDir+"histogramas.png")

# Passo 5 - Probability plots
fig, ax = plt.subplots(2,2,figsize=(16,9))

for idx, (names, data) in enumerate(peakData.groupby(['Tipo de dispositivo','Direção do fluxo'])):
    pplot = sm.ProbPlot(
        data=data['bps'],
        dist=sp.stats.norm,
        loc=normalFit.loc[names,r'$\mu$'],
        scale=normalFit.loc[names,r'$\sigma^2$']
    )
    pplot.probplot(ax=ax.ravel()[idx],line='45')
    ax.ravel()[idx].set_title(f"Tipo de dispositivo = {names[0]} | Direção do fluxo = {names[1]}")

plt.savefig(resultsDir+'probability_plots_normal.png')

fig, ax = plt.subplots(2,2,figsize=(16,9))

for idx, (names, data) in enumerate(peakData.groupby(['Tipo de dispositivo','Direção do fluxo'])):
    pplot = sm.ProbPlot(
        data=data['bps'],
        dist=sp.stats.gamma,
        distargs=(gammaFit.loc[names,r'$\alpha$'],),
        loc=0,
        scale=1/gammaFit.loc[names,r'$\lambda$']
    )
    ax.ravel()[idx].set_title(f"Tipo de dispositivo = {names[0]} | Direção do fluxo = {names[1]}")
    pplot.probplot(ax=ax.ravel()[idx],line='45')

plt.savefig(resultsDir+'probability_plots_gamma.png')

# Passo 6 - QQPlot

# O processo de interpolação já é feito pela biblioteca statsmodels
# É necessário apenas definir o primeiro dataset como o dataset menor
fig,ax = plt.subplots(1,2)

for idx, (flowName, data) in enumerate(peakData.groupby('Direção do fluxo')):
    deviceData = []
    for df in data.groupby('Tipo de dispositivo'):
        deviceData.append(df)

    # Define qual o dataset menor
    smallDf, bigDf = (0,1)
    if deviceData[smallDf][1].shape[0] > deviceData[bigDf][1].shape[0]:
        smallDf, bigDf = bigDf, smallDf 

    ax[idx].set_title(f'Direção do fluxo = {flowName}')
    ax[idx].set_xlabel(f'{deviceData[smallDf][0]}')
    ax[idx].set_ylabel(f'{deviceData[bigDf][0]}')
    sm.qqplot_2samples(deviceData[smallDf][1]['bps'],deviceData[bigDf][1]['bps'],line='45',ax=ax[idx])

plt.savefig(resultsDir+"qqplots.png")
