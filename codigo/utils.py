# utils.py
# Autor: Fernando Dias 
#
# Descrição: Funções utilitárias

import numpy as np 
import pandas as pd 

def ProcessDataset(a):
    # Remover zeros dos dados 
    a['date_hour'] = pd.to_datetime(a['date_hour'])
    a = a.set_index(['date_hour','device_id'])
    return a 

def LogarithmColumns(a,mode='add1'):
    if mode == 'add1':
        a['bytes_up'] = np.log10(a['bytes_up']+1)
        a['bytes_down'] = np.log10(a['bytes_down']+1)
    else:
        raise NotImplementedError 


def SaveDataset(a,name='processed_dataset.pickle'):
    a.to_pickle(name)

def LoadDataset(name='processed_dataset.pickle'):
    return pd.read_pickle(name)

def ImportDatasets():
    chromecast = pd.read_csv('../dados/dataset_chromecast.csv')
    smarttv = pd.read_csv('../dados/dataset_smart-tv.csv')
    return chromecast,smarttv 

def ImportGlobalDataset():
    chromecast, smarttv = ImportDatasets()
    chromecast, smarttv = ProcessDataset(chromecast), ProcessDataset(smarttv)
    # Concatenates both datasets, separate by column category
    chromecast['device_type'] = "Chromecast"
    smarttv['device_type'] = "Smart TV"
    dataset = pd.concat([chromecast.reset_index(),smarttv.reset_index()],ignore_index=True)
    # Creates long form dataset 
    dataset = dataset.melt(id_vars=['date_hour','device_type','device_id'],var_name='flow_type',value_name='bytes')
    # Converts type to datetime 
    dataset['date_hour'] = pd.to_datetime(dataset['date_hour'])
    return dataset

if __name__ == '__main__':
    df = ImportGlobalDataset()
    df.sort_values(by=['device_type','flow_type','date_hour'],inplace=True)
    SaveDataset(df)
    print(df)
    print(df.columns)
    print(df.dtypes)
