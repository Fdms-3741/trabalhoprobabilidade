#
# Questão 4 - Análise do tráfego nos horários de pico 
# Autor: Fernando Dias 
#
#
import re

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
dataset['hour'] = dataset['date_hour'].dt.hour
if dropZeroValues: 
    dataset = dataset.replace(0,np.nan)
    dataset.dropna(subset='bytes',inplace=True)
dataset['bytes'] = np.log10(dataset['bytes']+1)

# Passo 1 - Criação do dataset 
# Filtrando pelos horários de pico encontrados na questão anterior
peakData = dataset[\
    ((dataset['device_type'] == "Smart TV") & (dataset['hour'] == 20)) |\
    ((dataset['device_type'] == "Chromecast") & (dataset['flow_type'] == 'bytes_up') & (dataset['hour'] == 22)) |\
    ((dataset['device_type'] == "Chromecast") & (dataset['flow_type'] == 'bytes_down') & (dataset['hour'] == 23))\
]

# Contagem dos dados 
countColumns = peakData[['device_type','flow_type','hour']].value_counts()
print(countColumns)
countColumns.to_latex(resultsDir+'contagem_dados.tex')

# Removendo colunas desnecessárias
del peakData['date_hour']
del peakData['hour']

print("Working dataset:")
print(peakData)

# Passo 2 - Histogramas
fig = sns.displot(data=peakData,common_bins=False, common_norm=False, kind='hist',bins='sturges',stat='density',x='bytes',row='device_type',col='flow_type')

# Passo 3 - Cálculo do MLE
# A função fit do scipy já utiliza o método de máxima verossimilhança para otimização de parâmetros
normalFit = peakData.groupby(['device_type','flow_type'])['bytes'].apply(sp.stats.norm.fit, method='mle')
normalFit = pd.DataFrame({
    'mu':normalFit.apply(lambda x: x[0]),
    'sigma2':normalFit.apply(lambda x: x[1])
})
print("Normal fit")
print(normalFit)
normalFit.to_latex(resultsDir+'mle_normal.tex')

# O argumento floc faz com que a função não tente otimizar a posição da variável x, para o caso de x' = x + offset
gammaFit = peakData.groupby(['device_type','flow_type'])['bytes'].apply(sp.stats.gamma.fit,floc=-1e-5, method='mle')
gammaFit = pd.DataFrame({
    'alpha':gammaFit.apply(lambda x: x[0]),
    'lambda':gammaFit.apply(lambda x: 1/x[2]) 
})
print("Gamma fit")
print(gammaFit)
gammaFit.to_latex(resultsDir+'mle_gamma.tex')

# Passo 4 - Fazer o plot das distribuições utilizando os parâmetros encontrados
for ax in fig.axes.ravel():
    devType  = re.search(r'device_type\s=\s(\S+(\s\w+)?)',ax.get_title())[1]
    flowType = re.search(r'flow_type\s=\s(\S+)',ax.get_title())[1]

    x0,x1 = ax.get_xlim()
    x = np.linspace(x0,x1,200)
    
    # Normal  
    ax.plot(x,
        sp.stats.norm.pdf(
            x,
            normalFit.loc[(devType,flowType),'mu'],
            scale=normalFit.loc[(devType,flowType),'sigma2']
            )
        )

    # Gamma dist 
    ax.plot(x,
        sp.stats.gamma.pdf(
            x,
            a=gammaFit.loc[(devType,flowType),'alpha'],
            scale=1/gammaFit.loc[(devType,flowType),'lambda']
            )
        )
    ax.set_xlim(x0,x1)
plt.savefig(resultsDir+"histogramas.png")

# Passo 5 - Probability plots
fig, ax = plt.subplots(2,2,figsize=(16,9))

for idx, (names, data) in enumerate(peakData.groupby(['device_type','flow_type'])):
    pplot = sm.ProbPlot(
        data=data['bytes'],
        dist=sp.stats.norm,
        loc=normalFit.loc[names,'mu'],
        scale=normalFit.loc[names,'sigma2']
    )
    pplot.probplot(ax=ax.ravel()[idx],line='45')
    ax.ravel()[idx].set_title(f"device_type = {names[0]} | flow_type = {names[1]}")

fig.suptitle("Probability plots para a distr. normal")
plt.savefig(resultsDir+'probability_plots_normal.png')

fig, ax = plt.subplots(2,2,figsize=(16,9))

for idx, (names, data) in enumerate(peakData.groupby(['device_type','flow_type'])):
    pplot = sm.ProbPlot(
        data=data['bytes'],
        dist=sp.stats.gamma,
        distargs=(gammaFit.loc[names,'alpha'],),
        loc=0,
        scale=1/gammaFit.loc[names,'lambda']
    )
    pplot.probplot(ax=ax.ravel()[idx],line='45')
    ax.ravel()[idx].set_title(f"device_type = {names[0]} | flow_type = {names[1]}")

fig.suptitle("Probability plots para a distr. gamma")
plt.savefig(resultsDir+'probability_plots_gamma.png')

# Passo 6 - QQPlot

# O processo de interpolação já é feito pela biblioteca statsmodels
# É necessário apenas definir o primeiro dataset como o dataset menor
fig,ax = plt.subplots(1,2)

for idx, (flowName, data) in enumerate(peakData.groupby('flow_type')):
    deviceData = []
    for df in data.groupby('device_type'):
        deviceData.append(df)

    # Define qual o dataset menor
    smallDf, bigDf = (0,1)
    if deviceData[smallDf][1].shape[0] > deviceData[bigDf][1].shape[0]:
        smallDf, bigDf = bigDf, smallDf 

    sm.qqplot_2samples(deviceData[smallDf][1]['bytes'],deviceData[bigDf][1]['bytes'],line='45',ax=ax[idx])
    ax[idx].set_title(f'flow_type = {flowType}')
    ax[idx].set_xlabel(f'{deviceData[smallDf][0]}')
    ax[idx].set_ylabel(f'{deviceData[bigDf][0]}')

fig.suptitle("QQPlots")
plt.savefig(resultsDir+"qqplots.png")
plt.show()
