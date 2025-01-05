# Código do trabalho

Esse diretório contém todos os códigos que geram os resultados e gráficos contidos no relatório. 

Todos os códigos devem ser executados com a versão do python 3.12. As bibliotecas utilizadas são:

 - numpy
 - pandas
 - scipy
 - matplotlib
 - seaborn 
 - statsmodels

## Preparação

As dependências podem ser facilmente instaladas através do gerenciador de ambientes [miniconda](https://docs.anaconda.com/miniconda/). Após a instalação dessa ferramenta o ambiente virtual pode ser criado com o comando:

```
conda env create -f environment.yml
```

Após isso, basta acessar o ambiente com o comando `conda activate probest`.

## Uso

Esse diretório contém vários scripts separados por questão e um script chamado `utils.py` que lida com formatações gerais dos datasets. Antes de executar qualquer questão, deve-se executar o script `utils.py` sem argumentos:

```
python3 utils.py
```

Esse comando resultará em um arquivo `.pickle` que contém o dataset pré-processado, o que agiliza a inicialização das questões. 

A partir de agora, qualquer script pode ser executado com o seguinte comando

```
python3 questao_X.py [True|False]
```

Onde `X` é o número da questão seguindo o PDF do enunciado do trabalho. Todos os scripts possuem o mesmo comportamento de exibir na tela todos os gráficos e todas as tabelas que serão utilizadas no relatório. Todas as imagens são exibidas simultâneamente assim que o script termina a execução.

O argumento opcional define o valor booleano da variável `dropZeroValues`, na qual uma etapa adicional de pré-processamento aos dados é feito onde os valores nulos são removidos antes do cálculo do logaritmo. As consequências dessa etapa adicional são discutidas no relatório.
