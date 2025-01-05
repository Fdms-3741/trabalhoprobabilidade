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

dataset['bytes'] = np.log10(dataset['bytes']+1)

dataset['hour'] = dataset['date_hour'].dt.hour
del dataset['date_hour']

# Média, var e std
res = dataset.groupby(['hour','device_type','flow_type']).apply(
    lambda x : pd.Series({
        "avg": x['bytes'].mean(),
        'std': np.std(x['bytes'],ddof=1),
        'var': np.var(x['bytes'],ddof=1) # Utiliza o denominador N - 1
    })
)

res = res.reset_index().pivot(index='hour',columns=['device_type','flow_type'])
res.columns = res.columns.reorder_levels([1,2,0])
res = res.T.sort_index().T
print(res)
res.to_latex("./resultados/questao3/estatisticas_gerais.tex")
maxHours = res.loc[:,(slice(None),slice(None),'avg')].idxmax()
print(maxHours)
maxHours.to_latex("./resultados/questao3/horarios_pico.tex")

# Boxplots
plt.clf()
sns.catplot(data=dataset,kind='box',x='hour',y='bytes',col='device_type',row='flow_type')
plt.savefig('./resultados/questao3/boxplots.png')

# Gráficos das estatísticas
res.columns.names = ('device_type','flow_type','statistic')
statsHour = res.melt(ignore_index=False,value_name='bytes').reset_index()

for stat in ['avg','std','var']:
    plt.clf()
    sns.relplot(data=statsHour[statsHour['statistic'] == stat],x='hour',y='bytes',row='device_type',col='flow_type')
    plt.suptitle(f'{stat} variation')
    plt.savefig(f'./resultados/questao3/variacao_{stat}.png')

plt.show()
