# Relatório 

Nesse diretório está contido os arquivos .tex para compilação do relatório através do LaTeX. 

## Preparação

Um passo importante antes de compilar o relatório é garantir que um link (simbólico) para o subdiretório de resultados no diretório código existe. Caso esse link não exista, ele deve ser criado com o comando abaixo, que deve ser executado nesse diretório.

```
ln -s ../codigo/resultados/ 
```

Em seguida, **caso não existam resultados nesse diretório**, deve-se ir ao diretório de código e executar o script `utils.py` e todas as questões duas vezes, cada vez com ambos o argumento opcional `True` ou `False`. 

## Compilação

Qualquer instalação do latex deve ser capaz de compilar o relatório. Esse relatório foi compilado em uma distro debian 12, com a instalação dos pacotes `texlive` e `latexmk` via apt. 

Utilizando a ferramenta `latexmk`, o comando de compilação é simplesmente:

```
latexmk
```
