#!/usr/bin/env python

import pandas as pd
import geopandas as gpd
import json
import os


ELECCION = "presidente"


def identificar(df, codigo_localidad, codigo_recinto):
    return df[[codigo_localidad, codigo_recinto]].apply(
        lambda _: ".".join([str(__) for __ in _]), axis=1
    )


def preparar_resultados():
    def procesarRecinto(recinto):
        resultados = recinto.groupby("opcion").conteo.sum()
        ganador = resultados.div(recinto.conteo.sum()).sort_values().tail(1)
        return {
            "n": recinto_nombres[recinto["codigo"].values[0]],
            "g": ganador.index[0],
            "r": resultados.to_dict(),
            "p": recinto_participacion[recinto["codigo"].values[0]],
        }

    admin, validos, participacion = [
        pd.read_csv(os.path.join(base, ELECCION, f"{i}.csv"))
        for i in ["admin", "validos", "participacion"]
    ]
    for df in [admin, validos, participacion]:
        df["codigo"] = identificar(df, "CodigoLocalidad", "CodigoRecinto")

    recinto_nombres = admin.groupby("codigo").NombreRecinto.first().to_dict()

    columnas_participacion = {
        "TotalVotoNulo": "n",
        "VotoBlanco": "b",
        "VotoValido": "v",
    }
    recinto_participacion = (
        participacion.rename(columns=columnas_participacion)
        .groupby("codigo")[list(columnas_participacion.values())]
        .sum()
        .to_dict(orient="index")
    )
    data = {
        codigo: procesarRecinto(recinto) for codigo, recinto in validos.groupby("codigo")
    }

    with open(os.path.join(base, "resultados.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False)

    total_actas = 35253
    completo = admin.shape[0] / total_actas
    with open(os.path.join(base, "progreso"), "w") as f:
        f.write(str(completo))


def preparar_recintos():
    recintos = gpd.read_file("./geo/2025/recintos.gpkg")
    recintos["c"] = identificar(recintos, "asiento", "recinto")
    recintos[["c", "geometry"]].to_file(os.path.join(base, "recintos.geojson"))


base = os.path.dirname(__file__)
preparar_recintos()
preparar_resultados()
