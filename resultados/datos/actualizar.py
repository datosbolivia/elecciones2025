#!/usr/bin/env python3

import requests
import base64
import pandas as pd
from io import BytesIO
import os


def actualizar():
    def descargar():
        HEADERS = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
        }

        response = requests.post(
            "https://computo.oep.org.bo/api/v1/descargar",
            headers=HEADERS,
            json={"tipoArchivo": "CSV"},
        )

        date = response.json()["fecha"]
        data = pd.read_csv(BytesIO(base64.b64decode(response.json().get("archivo"))))
        return date, data

    def formar(date, data):
        base = os.path.dirname(__file__)
        elecciones = {
            "PRESIDENTE": "presidente",
            "DIPUTADO CIRCUNSCRIPCIÓN UNINOMINAL": "uninominales",
            "DIPUTADO CIRCUNSCRIPCIÓN ESPECIAL": "especiales",
        }
        indice = ["CodigoLocalidad", "CodigoRecinto", "CodigoMesa"]
        partidos = {
            "Voto1": "AP",
            "Voto2": "LYP-ADN",
            "Voto3": "APB-SUMATE",
            "Voto5": "LIBRE",
            "Voto6": "FP",
            "Voto7": "MAS-IPSP",
            "Voto9": "UNIDAD",
            "Voto10": "PDC",
        }
        columnas = {
            "admin": [
                "CodigoPais",
                "NombrePais",
                "CodigoDepartamento",
                "NombreDepartamento",
                "CodigoCircunscripcionU",
                "CodigoCircunscripcionE",
                "CodigoProvincia",
                "NombreProvincia",
                "CodigoSeccion",
                "NombreMunicipio",
                "NombreLocalidad",
                "NombreRecinto",
                "NumeroMesa",
            ],
            "validos": [
                "Voto1",
                "Voto2",
                "Voto3",
                "Voto5",
                "Voto6",
                "Voto7",
                "Voto9",
                "Voto10",
            ],
            "participacion": [
                "InscritosHabilitados",
                "VotoValido",
                "VotoBlanco",
                "VotoNuloDirecto",
                "VotoNuloDeclinacion",
                "TotalVotoNulo",
                "VotoEmitido",
                "VotoValidoReal",
                "VotoEmitidoReal",
            ],
        }
        for descripcion, eleccion in elecciones.items():
            data_eleccion = data[data.Descripcion == descripcion].copy()
            for recorte in ["admin", "validos", "participacion"]:
                data_recorte = data_eleccion.set_index(indice)[columnas[recorte]].copy()
                if recorte == "validos":
                    data_recorte = data_recorte.rename(columns=partidos)
                    data_recorte = (
                        data_recorte.stack()
                        .rename_axis(index={None: "opcion"})
                        .reset_index(name="conteo")
                        .set_index(indice)
                    )
                folder = os.path.join(base, eleccion)
                os.makedirs(folder, exist_ok=True)
                data_recorte.to_csv(os.path.join(folder, f"{recorte}.csv"))
        with open(os.path.join(base, "timestamp"), "w") as f:
            f.write(date)

    date, data = descargar()
    formar(date, data)


actualizar()
