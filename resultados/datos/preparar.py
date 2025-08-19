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
        }

    admin, validos = [
        pd.read_csv(os.path.join(base, ELECCION, f"{i}.csv"))
        for i in ["admin", "validos"]
    ]
    for df in [admin, validos]:
        df["codigo"] = identificar(df, "CodigoLocalidad", "CodigoRecinto")

    recinto_nombres = admin.groupby("codigo").NombreRecinto.first().to_dict()
    data = {
        codigo: procesarRecinto(recinto) for codigo, recinto in df.groupby("codigo")
    }

    with open(os.path.join(base, "resultados.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False)


def preparar_recintos():
    recintos = gpd.read_file("./geo/2025/recintos.gpkg")
    recintos["c"] = identificar(recintos, "asiento", "recinto")
    recintos[["c", "geometry"]].to_file(os.path.join(base, "recintos.geojson"))


def preparar_progreso():
    padron_total = 7937138
    df = pd.read_csv(os.path.join(base, ELECCION, "participacion.csv"))
    completo = df.VotoEmitido.sum() / padron_total
    with open(os.path.join(base, "progreso"), "w") as f:
        f.write(str(completo))


base = os.path.dirname(__file__)
preparar_recintos()
preparar_resultados()
preparar_progreso()