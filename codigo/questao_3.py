# Questão 3 
# Autor: Fernando Dias 
#
# Objetivo: Calcular as estatísticas por horário 

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns

from utils import LoadDataset

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
print(res)
res.to_latex("./resultados/questao3/estatisticas_gerais.tex")
maxHours = res.loc[:,(slice(None),slice(None),'Média')].idxmax()
print(maxHours)
maxHours.to_latex("./resultados/questao3/horarios_pico.tex")

# Boxplots
plt.clf()
sns.catplot(data=dataset,kind='box',x='Hora',y='bps',col='Tipo de dispositivo',row='Direção do fluxo')
plt.savefig('./resultados/questao3/boxplots.png')

# Gráficos das estatísticas
res.columns.names = ('Tipo de dispositivo','Direção do fluxo','Estatística')
statsHour = res.melt(ignore_index=False,value_name='bps').reset_index()

for stat in np.unique(statsHour['Estatística']):
    plt.clf()
    sns.relplot(data=statsHour[statsHour['Estatística'] == stat],x='Hora',y='bps',row='Tipo de dispositivo',col='Direção do fluxo')
    plt.savefig(f'./resultados/questao3/variacao_{stat}.png')

