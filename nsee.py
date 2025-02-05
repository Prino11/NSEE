# -*- coding: utf-8 -*-
"""NSEE

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xdi5ahsbNQKZBFRlfC3Ku2zDN29bFjJU

# Processo Seletivo NSEE
"""

!pip install pandas
!pip install dbfread

import pandas as pd
from dbfread import DBF


file_path = r'/content/drive/MyDrive/pacigeral_jun24.dbf'


# Função para ler o arquivo .dbf em partes
def read_dbf_in_chunks(file_path, chunk_size=300000):
    table = DBF(file_path, load=False, encoding='latin1')
    records = iter(table.records)

    chunk = []
    for record in records:
        chunk.append(record)

        if len(chunk) >= chunk_size:
            yield pd.DataFrame(chunk)
            chunk = []

    if chunk:
        yield pd.DataFrame(chunk)

# Função para calcular a diferença entre datas
def calculate_date_diff(df, col1, col2, new_col, intervals):
    df[col1] = pd.to_datetime(df[col1], errors='coerce')
    df[col2] = pd.to_datetime(df[col2], errors='coerce')
    df[new_col] = (df[col1] - df[col2]).dt.days
    df[new_col] = pd.cut(df[new_col], bins=intervals, labels=False, right=False)
    return df
#função binária óbito
def classify_obito(value):
    if value in [3, 4]:
        return 1
    else:
        return 0

def process_data(df):
    print("Colunas disponíveis no DataFrame:", df.columns)
 # Etapa 1: Selecionar pacientes com topografia de pulmão
    df = df[df['TOPOGRUP'] == 'C34']

    # Etapa 2: Selecionar pacientes de São Paulo
    df = df[df['UFRESID'] == 'SP']

    # Etapa 3: Selecionar pacientes com confirmação microscópica
    df = df[df['BASEDIAG'] == 3]

    # Etapa 4: Retirar categorias 0, X e Y da coluna ECGRUP
    df = df[~df['ECGRUP'].isin([0, 'X', 'Y'])]

    # Etapa 5: Retirar pacientes que fizeram Hormonioterapia e TMO
    df = df[~((df['HORMONIO'] == 1) & (df['TMO'] == 1))]

     # Etapa 6: Selecionar pacientes diagnosticados até 2019
    df = df[df['ANODIAG'] <= 2019]

     # Etapa 7: Retirar pacientes com idade menor que 20 anos
    df = df[df['IDADE'] >= 20]

     # Etapa 8: Calcular a diferença de datas

    df = calculate_date_diff(df, 'DTCONSULT', 'DTDIAG', 'CONSDIAG', [0, 31, 61, float('inf')])
    df = calculate_date_diff(df, 'DTDIAG', 'DTTRAT', 'DIAGTRAT', [0, 61, 91, float('inf')])
    df = calculate_date_diff(df, 'DTTRAT', 'DTCONSULT', 'TRATCONS', [0, 61, 91, float('inf')])

    # Etapa 9: Extrair apenas o número das colunas DRS e DRSINSTITU
    if 'DRSINSTITU' in df.columns:
        df['DRSINSTITU'] = df['DRSINSTITU'].str.extract(r'(\d+)')

    # Etapa 10: Criar a coluna binária de óbito
    df['OBITO'] = df['ULTINFO'].apply(classify_obito)


    # Etapa 11: Remover colunas irrelevantes
    columns_to_remove = [
        'UFNASC', 'UFRESID', 'CIDADE', 'DTCONSULT', 'CLINICA', 'DTDIAG',
        'BASEDIAG', 'TOPOGRUP', 'DESCTOPO', 'DESCMORFO', 'T', 'N', 'M',
        'PT', 'PN', 'PM', 'S', 'G', 'LOCALTNM', 'IDMITOTIC', 'PSA', 'GLEASON',
        'OUTRACLA', 'META01', 'META02', 'META03', 'META04', 'DTTRAT', 'NAOTRAT',
        'TRATAMENTO', 'TRATHOSP', 'TRATFANTES', 'TRATFAPOS', 'HORMONIO', 'TMO',
        'NENHUMANT', 'CIRURANT', 'RADIOANT', 'QUIMIOANT', 'HORMOANT', 'TMOANT',
        'IMUNOANT', 'OUTROANT', 'HORMOAPOS', 'TMOAPOS', 'DTULTINFO', 'CICI',
        'CICIGRUP', 'CICISUBGRU', 'FAIXAETAR', 'LATERALI', 'INSTORIG', 'RRAS',
        'ERRO', 'DTRECIDIVA', 'RECNENHUM', 'RECLOCAL', 'RECREGIO', 'RECDIST',
        'REC01', 'REC02', 'REC03', 'REC04', 'CIDO', 'DSCCIDO', 'HABILIT',
        'HABIT11', 'HABILIT1', 'CIDADEH', 'PERDASEG'
    ]
    df = df.drop(columns=columns_to_remove, errors='ignore')

    return df

df_cleaned_list = []
for df_chunk in read_dbf_in_chunks(file_path, chunk_size=300000):
    # Salvar o chunk não tratado em CSV
    pd.DataFrame(df_chunk).to_csv('dados_crus.csv', mode='a', header=False, index=False)

    df_cleaned = process_data(df_chunk)
    df_cleaned_list.append(df_cleaned)

final_df = pd.concat(df_cleaned_list, ignore_index=True)

# Exibição dos primeiros registros
print(final_df.head())

# Exportar os dados processados para CSV
final_df.to_csv('dados_processados.csv', index=False)