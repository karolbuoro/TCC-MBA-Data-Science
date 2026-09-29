# -*- coding: utf-8 -*-
"""
MBA DATA SCIENCE E ANALYTICS
TRABALHO DE CONCLUSÃO DE CURSO
 
@author: karolini.araujo
"""
#importacao das bibliotecas
import pandas as pd
import numpy as np
import h3
import matplotlib.pyplot as plt
import os
import geopandas as gpd
from shapely.geometry import Polygon
from matplotlib.patches import Patch
 
#importacao da planilha
df=pd.read_excel(
    r"C:\Users\karolini.araujo\Documents\MBA Data Science\Bases Dados\Base Dados TCC.xlsx")
print(df.head())
print (df.columns)
 
#associacao dos hexagonos h3
RES=6 #quanto maior a resolucao, menor o tamanho hexagono
df["H3"]=df.apply( #criacao de uma nova coluna
    lambda linha: h3.latlng_to_cell(linha["LATITUDE"],linha["LONGITUDE"],RES),
    axis=1) #linha a linha
print(df[["LATITUDE", "LONGITUDE", "H3"]].head())
 
#contagem de empresas por hexagonos
empresas_hex=(df
    .groupby("H3") #agrupamento de registros por hexagonos
    .size() #qtd empresas por grupo
    .reset_index(name="TOTAL_EMPRESAS")) #resultado em tabela
print(empresas_hex.head())
 
#classificacao das empresas/hexagonos/grupos
classificacao_hex=(df
    .groupby(["H3", "CLASSIFICAÇÃO"]) #agrupamento por hexagono e tipo de estabelecimento
    .size()
    .reset_index(name="TOTAL"))
print(classificacao_hex.head())
 
classificacao_hex=(
    classificacao_hex
    .pivot(
        index="H3",
        columns="CLASSIFICAÇÃO",
        values="TOTAL")
    .fillna(0) 
    .reset_index())
print(classificacao_hex.head())
 
#geracao da geometria dos hexagonos
 
def h3_para_poligono(h):
    coords = h3.cell_to_boundary(h) #vertices dos hexagonos
    return Polygon([(lng, lat) for lat, lng in coords]) #vertices em poligonos
 
empresas_hex["geometry"] = (
    empresas_hex["H3"]
    .apply(h3_para_poligono) 
)
 
#conversao espacial
gdf = gpd.GeoDataFrame(
    empresas_hex,
    geometry="geometry",
    crs="EPSG:4326" #sistema de coordenadas geograficas
)
 
print(gdf.head())
 
#geracao do mapa de sp
fig, ax = plt.subplots(figsize=(14,10))
 
gdf.plot( 
    column="TOTAL_EMPRESAS",
    cmap="viridis",
    legend=True,
    linewidth=0.05,
    edgecolor="white",
 
    legend_kwds={
        "shrink":0.7},
 
    ax=ax) #aparencia do mapa
 
ax.set_title(
    "Distribuição dos estabelecimentos por hexágono H3",
    fontsize=16)
 
ax.set_xlabel(
    "Longitude",
    fontsize=12)
 
ax.set_ylabel(
    "Latitude",
    fontsize=12)
 
cbar = ax.get_figure().axes[-1]
cbar.set_ylabel(
    "Número de estabelecimentos por hexágono",
    fontsize=12
)
 
plt.tight_layout()
 
plt.show()
 
 
# identificacao de hexagono extremo - outlier
# definir limite dos outliers
limite = gdf["TOTAL_EMPRESAS"].quantile(0.99)
 
gdf_normal = gdf[
    gdf["TOTAL_EMPRESAS"] <= limite]
 
gdf_outlier = gdf[
    gdf["TOTAL_EMPRESAS"] > limite]
 
# figura
fig, ax = plt.subplots(figsize=(14,10))
 
# mapa principal
gdf_normal.plot(
    column="TOTAL_EMPRESAS",
    cmap="viridis",
    legend=True,
    linewidth=0.05,
    edgecolor="white",
 
    legend_kwds={
        "shrink":0.7},
 
    ax=ax)
 
# desenho outlier
gdf_outlier.plot(
    color="red",
    edgecolor="black",
    linewidth=0.3,
    ax=ax)
 
# legenda manual dos outliers
legenda_outlier = [
    Patch(
        facecolor="red",
        edgecolor="black",
        label=f"Outlier (> {round(limite)})")]
 
ax.legend(
    handles=legenda_outlier,
    loc="lower left")
 
# titulo
ax.set_title(
    "Distribuição dos estabelecimentos por hexágono H3",
    fontsize=16)
 
# eixos
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
 
# titulo barra de cores
cbar = ax.get_figure().axes[-1]
 
cbar.set_ylabel(
    "Número de estabelecimentos por hexágono",
    fontsize=12)
 
plt.tight_layout()
 
plt.show()
 
#dados
 
# quantidade total de estabelecimentos
total_estabelecimentos = len(df)
 
# total de hexagonos gerados
total_hex = df["H3"].nunique()
 
# quantidade media de empresas por hexagono
media_empresas = empresas_hex["TOTAL_EMPRESAS"].mean()
 
# mediana
mediana_empresas = empresas_hex["TOTAL_EMPRESAS"].median()
 
# maximo de empresas em um hexagono
max_empresas = empresas_hex["TOTAL_EMPRESAS"].max()
 
# minimo
min_empresas = empresas_hex["TOTAL_EMPRESAS"].min()
 
# area media aproximada do hexagono 
area_hex = h3.average_hexagon_area(RES, unit="km^2")
 
# percentual de ocupacao
hex_ocupados = len(empresas_hex)
perc_ocupacao = (hex_ocupados / total_hex) * 100
 
print("\RESULTADOS H3")
print("Resolução H3:", RES)
print("Total estabelecimentos:", total_estabelecimentos)
print("Total hexágonos:", total_hex)
print("Hexágonos ocupados:", hex_ocupados)
print("Cobertura (%):", round(perc_ocupacao,2))
print("Área média hexágono (km²):", round(area_hex,2))
print("Média empresas/hex:", round(media_empresas,2))
print("Mediana empresas/hex:", mediana_empresas)
print("Máximo empresas/hex:", max_empresas)
print("Mínimo empresas/hex:", min_empresas)
 
# percentual por hexagonp
#  coluna total
classificacao_hex["TOTAL"] = (
    classificacao_hex["Grupo A"] +
    classificacao_hex["Grupo B"])
 
# percentual Grupo A
classificacao_hex["PERC_A"] = (
    classificacao_hex["Grupo A"] /
    classificacao_hex["TOTAL"]) * 100
 
# percentual Grupo B
classificacao_hex["PERC_B"] = (
    classificacao_hex["Grupo B"] /
    classificacao_hex["TOTAL"]) * 100
 
print(
    classificacao_hex[
        [   "H3",
            "Grupo A",
            "Grupo B",
            "TOTAL",
            "PERC_A",
            "PERC_B"
        ]].head())
 
media_a = classificacao_hex["PERC_A"].mean()
media_b = classificacao_hex["PERC_B"].mean()
 
max_a = classificacao_hex["PERC_A"].max()
max_b = classificacao_hex["PERC_B"].max()
 
hex_a = (
    classificacao_hex["PERC_A"] >
    classificacao_hex["PERC_B"]).sum()
 
hex_b = (
    classificacao_hex["PERC_B"] >
    classificacao_hex["PERC_A"]).sum()
 
print("Média Grupo A:", round(media_a,2))
print("Média Grupo B:", round(media_b,2))
 
print("Maior percentual Grupo A:", round(max_a,2))
print("Maior percentual Grupo B:", round(max_b,2))
 
print("Hex predominante Grupo A:", hex_a)
print("Hex predominante Grupo B:", hex_b)
 
# estatisticas descritivas dos indicadores municipais
 
resumo = pd.read_excel(
    r"C:\Users\karolini.araujo\Documents\MBA Data Science\Bases Dados\Base Dados TCC.xlsx",
    sheet_name="Resumo Municipal"
)
 
# variáveis para análise
variaveis = [
    "POPULAÇÃO ESTIMADA",
    "Indicador B",
    "Indicador A",
    "Proporção A"
]
 
# estatísticas descritivas
estatisticas_desc_indic = resumo[variaveis].describe().T
 
# cálculo do coeficiente de variação
 
cv_a = (
    estatisticas_desc_indic.loc["Indicador A", "std"] /
    estatisticas_desc_indic.loc["Indicador A", "mean"]
) * 100

cv_b = (
    estatisticas_desc_indic.loc["Indicador B", "std"] /
    estatisticas_desc_indic.loc["Indicador B", "mean"]
) * 100
 
print("Coeficiente de variação - Grupo A:", cv_a)
print("Coeficiente de variação - Grupo B:", cv_b)
 
 
# Boxplot dos Indicadores A e B
 
dados_ab = resumo[
    ["Indicador A", "Indicador B"]
]
 
plt.figure(figsize=(8, 6))
 
dados_ab.boxplot()
 
plt.title("Distribuição dos indicadores A e B")
plt.ylabel("Estabelecimentos por 1.000 habitantes")
plt.grid(axis="y", alpha=0.3)
 
plt.tight_layout()
plt.show()
 
 
# Boxplot da Proporção A
 
dados_proporcao = resumo[
    ["Proporção A"]
]
 
plt.figure(figsize=(6, 6)) 
 
dados_proporcao.boxplot()
 
plt.title("Distribuição da proporção de estabelecimentos do Grupo A")
plt.ylabel("Proporção (%)")
plt.grid(axis="y", alpha=0.3)


