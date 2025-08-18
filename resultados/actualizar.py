#!/usr/bin/env python3

import base64
from io import BytesIO
import requests
import pandas as pd
import os

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import ProtocolError
from http.client import RemoteDisconnected
import time
import random


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
        "Connection": "close",
    }

    url = "https://computo.oep.org.bo/api/v1/descargar"

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)

    with requests.Session() as s:
        s.mount("https://", adapter)
        s.headers.update(HEADERS)

        for intento in range(1, 4):
            try:
                archivo = s.post(
                    url,
                    json={"tipoArchivo": "CSV"},
                    timeout=(10, 60),
                )
                archivo.raise_for_status()
                break
            except (requests.ConnectionError, ProtocolError, RemoteDisconnected) as e:
                if intento == 3:
                    raise
                print(f"intento {intento} falló: {e}. reintentando...")
                time.sleep(1.5**intento + random.uniform(0, 0.5))

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
