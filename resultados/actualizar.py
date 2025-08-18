#!/usr/bin/env python3

import base64
from io import BytesIO
import requests
import pandas as pd
import os


def descarga():
    HEADERS = {
        "authority": "computo.oep.org.bo",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "accept": "application/json, text/plain, */*",
        "dnt": "1",
        "captcha": "nocaptcha",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "content-type": "application/json",
        "origin": "https://computo.oep.org.bo",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://computo.oep.org.bo/",
        "accept-language": "en-US,en;q=0.9,es;q=0.8",
    }

    url = "https://computo.oep.org.bo/api/v1/descargar"

    for attempt in range(3):  # retry up to 3 times
        try:
            archivo = requests.post(
                url,
                headers=HEADERS,
                json={"tipoArchivo": "CSV"},
                timeout=30,
            )
            archivo.raise_for_status()
            break
        except Exception as e:
            if attempt == 2:
                raise
            print(f"intento {attempt + 1} falló: {e}. reintentando...")

    return pd.read_csv(BytesIO(base64.b64decode(archivo.json()["archivo"])))


def consolidar(df):
    ahora = pd.Timestamp.utcnow().floor("s")
    base = os.path.dirname(__file__)
    indice = ["CodigoMesa", "CodigoRecinto"]
    elecciones = [
        {"valor": "PRESIDENTE", "folder": "presidente"},
        {"valor": "DIPUTADO CIRCUNSCRIPCIÓN UNINOMINAL", "folder": "uninominales"},
    ]
    partidos = {
        1: "AP",
        2: "LYP-ADN",
        3: "APB-SUMATE",
        5: "LIBRE",
        6: "FP",
        7: "MAS-IPSP",
        8: "MORENA",
        9: "UNIDAD",
        10: "PDC",
    }

    recortes = {
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
            "CodigoLocalidad",
            "NombreLocalidad",
            "NombreRecinto",
            "NumeroMesa",
        ],
        "validos": [
            "Voto1",
            "Voto2",
            "Voto3",
            "Voto4",
            "Voto5",
            "Voto6",
            "Voto7",
            "Voto8",
            "Voto9",
            "Voto10",
            "Voto11",
            "Voto12",
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

    for eleccion in elecciones:
        os.makedirs(os.path.join(base, eleccion["folder"]), exist_ok=True)
        e = df[df.Descripcion == eleccion["valor"]].copy()

        e.set_index(indice)[recortes["admin"]].to_csv(
            os.path.join(base, eleccion["folder"], "admin.csv")
        )

        os.makedirs(os.path.join(base, eleccion["folder"], "validos"), exist_ok=True)
        e.set_index(indice)[recortes["validos"]].rename(
            columns={f"Voto{c}": partidos[c] for c in partidos}
        ).to_csv(
            os.path.join(
                base,
                eleccion["folder"],
                "validos",
                f"{ahora.strftime('%Y-%m-%dT%H:%M:%SZ')}.csv",
            )
        )

        os.makedirs(
            os.path.join(base, eleccion["folder"], "participacion"), exist_ok=True
        )
        e.set_index(indice)[recortes["participacion"]].to_csv(
            os.path.join(
                base,
                eleccion["folder"],
                "participacion",
                f"{ahora.strftime('%Y-%m-%dT%H:%M:%SZ')}.csv",
            )
        )


df = descarga()
consolidar(df)
