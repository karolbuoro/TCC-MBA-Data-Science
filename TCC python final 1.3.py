# -*- coding: utf-8 -*-
"""
MBA DATA SCIENCE E ANALYTICS
TRABALHO DE CONCLUSÃO DE CURSO
 
@author: karolini.araujo
"""

import pandas as pd
import geopandas as gpd
import libpysal
import esda
import unicodedata
import numpy as np
import matplotlib.pyplot as plt


# carregando a malha
malha = gpd.read_file(
    r"C:\Users\karolini.araujo\Documents\MBA Data Science\Bases Dados\SP_Municipios_2025"
)


# carregando os dados
arquivo = r"C:\Users\karolini.araujo\Documents\MBA Data Science\Bases Dados\Base Dados TCC.xlsx"

resumo = pd.read_excel(
    arquivo,
    sheet_name="Resumo Municipal"
)

# padronizacao dos nomes

def padronizar_nome(nome):
    nome = str(nome).strip().upper()
    nome = unicodedata.normalize("NFD", nome)
    nome = "".join(c for c in nome if unicodedata.category(c) != "Mn")
    nome = nome.replace("-", " ")
    nome = " ".join(nome.split())
    return nome


malha["MUNICIPIO_PADRAO"] = malha["NM_MUN"].apply(padronizar_nome)
resumo["MUNICIPIO_PADRAO"] = resumo["NOME DO MUNICÍPIO"].apply(padronizar_nome)


# merge

base_moran = malha.merge(
    resumo,
    on="MUNICIPIO_PADRAO",
    how="inner"
)

print("Base após o merge:", base_moran.shape)


# verificaçao

print(
    base_moran[["Indicador A", "ÍNDICE CLIMÁTICO"]].isna().sum()
)

# exclusao ilhabelea

base_moran = base_moran[
    base_moran["MUNICIPIO_PADRAO"] != "ILHABELA"
].copy()

print("Base para o Moran:", base_moran.shape)

# matriz espacial

w = libpysal.weights.Queen.from_dataframe(base_moran)

# Padronização por linha

w.transform = "r"

print("Matriz espacial criada!")
print("Número de municípios:", w.n)
print("Ilhas:", w.islands)


# moran bivariado

moran_bv = esda.Moran_BV(
    base_moran["Indicador A"],
    base_moran["ÍNDICE CLIMÁTICO"],
    w,
    permutations=999
)

print("\n===== MORAN BIVARIADO =====")
print("Índice de Moran:", moran_bv.I)
print("p-valor:", moran_bv.p_sim)


#quadrantes

x = base_moran["Indicador A"].values
y = base_moran["ÍNDICE CLIMÁTICO"].values

# Padronização das variáveis
x_pad = (x - x.mean()) / x.std()
y_pad = (y - y.mean()) / y.std()

# Índice Climático dos municípios vizinhos
lag_y = w.sparse @ y_pad


quadrantes = np.where(
    (x_pad >= 0) & (lag_y >= 0),
    "Alto-Alto",

    np.where(
        (x_pad < 0) & (lag_y < 0),
        "Baixo-Baixo",

        np.where(
            (x_pad >= 0) & (lag_y < 0),
            "Alto-Baixo",

            "Baixo-Alto"
        )
    )
)


#result quadrante

base_moran["QUADRANTE"] = quadrantes

resumo_quadrantes = (
    base_moran["QUADRANTE"]
    .value_counts()
    .rename_axis("QUADRANTE")
    .reset_index(name="MUNICIPIOS")
)

resumo_quadrantes["PERCENTUAL"] = (
    resumo_quadrantes["MUNICIPIOS"]
    / len(base_moran)
    * 100
).round(2)

print("\n===== QUADRANTES =====")
print(resumo_quadrantes)


# mapa p visualizacao

base_moran.plot(
    column="QUADRANTE",
    categorical=True,
    legend=True,
    figsize=(10, 10),
    edgecolor="black",
    linewidth=0.2
)

plt.title(
    "Moran Bivariado: Indicador A × Índice Climático"
)

plt.axis("off")
plt.show()