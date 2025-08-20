---
theme: dashboard
title: Bolivia 2025
toc: false
sidebar: false
---

```js
import maplibregl from "npm:maplibre-gl";
import { PMTiles, Protocol } from "npm:pmtiles";
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);
```

<link rel="stylesheet" type="text/css" href="https://unpkg.com/maplibre-gl@4.0.2/dist/maplibre-gl.css">

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
  #observablehq-main, #observablehq-center {
    margin: 0;
    min-height: 100vh;
  }
  .header {
    color: var(--texto_fuerte);
    background: var(--fondo);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: sticky;
    z-index:4;
    top: 0;
    left: 0;
    height: 110px;
    padding: 10px;
    .title {
      font-family: serif;
      font-size: 1.5rem;
      font-weight: 600;
    }
    .subtitle {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
      font-family: "Inter", sans-serif;
      font-weight: 600;
      font-size: .8em;
      .timestamp {
        font-weight: 400;
        opacity: .4;
        font-family: mono;
        font-size: .7rem;
      }
    }
    .cambio_input {
      form {
        min-height: 0 !important;
        margin: 7px 0 0 0 !important;
      }
      form div {
        display: flex;
        align-items: end;
        justify-content: center;
        background-color: var(--fondo);
      }
      input {
          display: none;
      }
      label {
        color: var(--texto_suave);
        padding: 3px 6px;
        font-size: 0.8em;
        opacity: 0.8;
        border-bottom: 2px solid var(--fondo);
        cursor: pointer;
      }
      label:hover {
        border-color: var(--border); */
      } 
      label:has(input[type="radio"]:checked) {
        color: var(--texto_fuerte);
        background: var(--fondo);
        border-bottom: 2px solid var(--texto_suave);
      }
    }
  }
  #mapa {
    position: absolute; 
    top: 110px; 
    bottom: 0; 
    width: 100%;
  }
  .maplibregl-popup {
    max-width: 400px;
    .maplibregl-popup-content {
      background: var(--fondo);
      box-shadow: 0 4px 12px rgba(136, 160, 195, 0.4); 
    }
  }

  .maplibregl-popup-anchor-bottom .maplibregl-popup-tip {
    border-top-color: var(--fondo) !important;
  }

  .popup_header {
    font-family: "Inter";
    text-align: center;
    opacity: .5;
    font-size: .9em;
    text-transform: uppercase;
    margin-bottom: 10px;
    color: var(--texto_fuerte);
  }
</style>

```js
// Selección de vistas
const vistaInput = Inputs.radio(["validos", "participacion"], {
  value: "validos",
  required: true,
  format: (d) => (d == "validos" ? "votos válidos" : "votos nulos y blancos"),
});
const vista = Generators.input(vistaInput);
```

```js
// Vistas
const vistas = {
  validos: {
    colores: {
      fondo: "#fff",
      texto_fuerte: "#000",
      texto_suave: "#a0a0a0ff",
      fondo_suave: "#ccc",
    },
    texto: {
      subtitulo: "Votos para presidente dentro del país",
    },
    mapa: {
      estilo:
        "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json",
      color_recintos: colores_partidos,
      etiquetas:
        "https://a.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png",
    },
  },
  participacion: {
    colores: {
      fondo: "#000000ff",
      texto_fuerte: "#fbfbfbff",
      texto_suave: "#e9e9e9ff",
      fondo_suave: "#5a5a5aff",
    },
    texto: {
      subtitulo: "Participación electoral dentro del país",
    },
    mapa: {
      estilo:
        "https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json",
      color_recintos: colores_participacion,
      etiquetas:
        "https://a.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}.png",
    },
  },
};
```

```js
const v = vistas[vista];
```

```js
document.documentElement.style.setProperty("--fondo", v.colores.fondo);
document.documentElement.style.setProperty(
  "--texto_fuerte",
  v.colores.texto_fuerte
);
document.documentElement.style.setProperty(
  "--fondo_suave",
  v.colores.fondo_suave
);
document.documentElement.style.setProperty(
  "--texto_suave",
  v.colores.texto_suave
);

map.setStyle(v.mapa.estilo, { diff: false });
map.once("styledata", () => {
  if (!map.getSource("recintos"))
    map.addSource("recintos", capa_recintos.source);
  if (!map.getSource("etiquetas"))
    map.addSource("etiquetas", capa_etiquetas.source);
  if (!map.getLayer("recintos")) map.addLayer(capa_recintos.layer);
  if (!map.getLayer("etiquetas")) map.addLayer(capa_etiquetas.layer);
  if (!map.getLayer("recintos_hover")) map.addLayer(capa_recintos_hover);
});
```

<div class="header">
  <div class="title">Bolivia 2025</div>
  <div class="subtitle"><span>${v.texto.subtitulo}</span><span class="timestamp">actualizado el ${timestamp_string} y contado al ${d3.format(".2%")(progreso)}</span></div>
  <div class="cambio_input">${vistaInput}</div>
</div>

```js
// Datos

const gh =
  "https://raw.githubusercontent.com/datosbolivia/elecciones2025/refs/heads/main/resultados/datos/";
const recintos = await d3.json(`${gh}recintos.geojson`);
const resultados = await d3.json(`${gh}resultados.json`);
const timestamp = await fetch(`${gh}timestamp`).then((r) => r.text());
const dateFormatter = new Intl.DateTimeFormat("es", {
  year: "numeric",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
  timeZone: "UTC",
});
const timestamp_string = dateFormatter.format(new Date(timestamp));
const progreso = await fetch(`${gh}progreso`).then((r) => r.text());
```

```js
// Consolidar resultados y recintos

for (const feature of recintos.features) {
  const codigo = feature.properties.c;
  const resultado = resultados[codigo];
  feature.properties.total = resultado
    ? Object.values(resultado.r).reduce((s, v) => s + v, 0)
    : 0;
  feature.properties.partido = resultado?.g ?? null;
  feature.properties.invalido = resultado?.p
    ? (resultado.p.b + resultado.p.n) /
      (resultado.p.b + resultado.p.n + resultado.p.v)
    : null;
}
```

```js
const partidos = {
  fotos: {
    AP: await FileAttachment("imagenes/ap.webp").url(),
    "LYP-ADN": await FileAttachment("imagenes/lyp-adn.webp").url(),
    "APB-SUMATE": await FileAttachment("imagenes/apb-sumate.webp").url(),
    LIBRE: await FileAttachment("imagenes/libre.webp").url(),
    FP: await FileAttachment("imagenes/fp.webp").url(),
    "MAS-IPSP": await FileAttachment("imagenes/mas-ipsp.webp").url(),
    UNIDAD: await FileAttachment("imagenes/unidad.webp").url(),
    PDC: await FileAttachment("imagenes/pdc.webp").url(),
  },
  colores: {
    AP: ["#00b5ee", "#4f7d35"],
    "LYP-ADN": ["#a91521", "#2f2f30"],
    "APB-SUMATE": ["#430956", "#cb010d"],
    LIBRE: ["#f50303", "#1d65c5"],
    FP: ["#1897d5", "#59c4f0"],
    "MAS-IPSP": ["#143a83", "#585755"],
    UNIDAD: ["#feb447", "#083c6b"],
    PDC: ["#05636b", "#dd0710"],
  },
};

let colores_partidos = ["match", ["get", "partido"]];
for (const [opcion, color] of Object.entries(partidos.colores))
  colores_partidos.push(opcion, color[0]);
colores_partidos.push("#ccc");
```

```js
const colores_participacion = [
  "interpolate",
  ["linear"],
  ["coalesce", ["to-number", ["get", "invalido"]], 0],
  0,
  "#1e4160",
  0.25,
  "#17b79c",
  0.5,
  "#abea87",
  0.7,
  "#f3ff83",
  1,
  "#eaff2eff",
];
```

```js
// Capas

const capa_etiquetas = {
  source: {
    type: "raster",
    tiles: [v.mapa.etiquetas],
    tileSize: 256,
  },
  layer: {
    id: "etiquetas-layer",
    type: "raster",
    source: "etiquetas",
    paint: {
      "raster-opacity": 0.8,
    },
  },
};

const capa_recintos = {
  source: {
    type: "geojson",
    data: recintos,
  },
  layer: {
    id: "recintos",
    type: "circle",
    source: "recintos",
    paint: {
      "circle-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        6,
        ["min", 2, ["max", 1, ["*", 0.03, ["to-number", ["get", "total"]]]]],
        12,
        ["min", 7, ["max", 2, ["*", 0.02, ["to-number", ["get", "total"]]]]],
        16,
        ["min", 21, ["max", 3, ["*", 0.08, ["to-number", ["get", "total"]]]]],
      ],
      "circle-color": v.mapa.color_recintos,
      "circle-opacity": 0.5,
    },
  },
};

const capa_recintos_hover = {
  id: "recintos_hover",
  type: "circle",
  source: "recintos",
  filter: ["!=", ["get", "partido"], null],
  paint: {
    "circle-color": "rgba(0,0,0,0)",
    "circle-radius": [
      "interpolate",
      ["exponential", 1.3],
      ["zoom"],
      6,
      8,
      10,
      11,
      12,
      14,
      14,
      17,
      16,
      20,
      18,
      22,
    ],
  },
};
```

```js
const div = display(document.createElement("div"));
div.id = "mapa";
const map = new maplibregl.Map({
  container: div,
  center: [-65.482, -17.237],
  zoom: 5,
  scrollZoom: true,
  attributionControl: {
    compact: true,
    customAttribution:
      "<a href='https://mauforonda.github.io/'>Mauricio Foronda</a>",
  },
});

map.addControl(new maplibregl.NavigationControl());
map.addControl(
  new maplibregl.GeolocateControl({
    positionOptions: {
      enableHighAccuracy: true,
    },
    showAccuracyCircle: false,
    showUserLocation: true,
  }),
  "top-right"
);

invalidation.then(() => map.remove());
```

```js
const popup = new maplibregl.Popup({
  closeButton: false,
  closeOnClick: false,
});
```

```js
let locked = false;
const mouseenter = function (e) {
  map.getCanvas().style.cursor = "pointer";
  const recinto_feature = e.features[0];
  const resultado = resultados[recinto_feature.properties.c] ?? null;
  const grafico = plot_resultado(resultado);
  popup
    .setHTML(
      `<div class="popup_plot">
    <div class="popup_header">${resultado ? resultado.n : ""}</div>
    ${grafico.outerHTML}
    </div>`
    )
    .setLngLat(recinto_feature.geometry.coordinates)
    .addTo(map);
};

const mouseleave = function () {
  map.getCanvas().style.cursor = "";
  if (!locked) popup.remove();
};

map.on("mouseenter", "recintos_hover", mouseenter);
map.on("mouseleave", "recintos_hover", mouseleave);

map.on("click", "recintos_hover", () => {
  locked = true;
});

map.on("click", (e) => {
  if (
    !map.queryRenderedFeatures(e.point, { layers: ["recintos_hover"] }).length
  ) {
    locked = false;
    popup.remove();
  }
});
```

```js
function plot_resultado(resultado) {
  if (vista == "validos") {
    return plot_validos(resultado);
  } else {
    return plot_participacion(resultado);
  }
}

function plot_participacion(resultado) {
  if (resultado) {
    const p = Object.entries(resultado.p);
    const total = p.reduce((s, [, v]) => s + v, 0);
    const data = p.map(([opcion, conteo]) => ({
      opcion,
      conteo,
      porcentaje: conteo / total,
    }));

    const etiquetas_participacion = {
      v: "VÁLIDOS",
      b: "BLANCOS",
      n: "NULOS",
    };

    const colores_participacion = {
      v: vistas.participacion.colores.texto_suave,
      b: "#f3ff83",
      n: "#f3ff83",
    };

    return Plot.plot({
      margin: 0,
      marginLeft: 180,
      marginRight: 10,
      height: data.length * 90,
      x: { axis: null, domain: [0, 1] },
      y: { axis: null, domain: data.map((d) => d.opcion) },
      marks: [
        Plot.text(data, {
          x: 0,
          y: "opcion",
          text: (d) => etiquetas_participacion[d.opcion],
          fill: (d) => colores_participacion[d.opcion],
          fillOpacity: 0.8,
          fontSize: 30,
          fontWeight: 600,
          lineAnchor: "middle",
          textAnchor: "end",
          dy: 15,
          dx: -12,
          fontFamily: "Inter",
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: vistas.participacion.colores.fondo_suave,
          fillOpacity: 0.3,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: "porcentaje",
          y: "opcion",
          fill: (d) => colores_participacion[d.opcion],
          fillOpacity: (d) => (d.opcion == "v" ? 0.5 : 1),
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: null,
          stroke: vistas.validos.colores.texto_suave,
          strokeOpacity: 0.5,
          strokeWidth: 1,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.text(data, {
          x: 1,
          y: "opcion",
          text: (d) => d3.format(".1%")(d.porcentaje),
          fill: vistas.participacion.colores.texto_suave,
          fontSize: 35,
          lineAnchor: "bottom",
          textAnchor: "end",
          dy: -15,
          dx: -5,
          fontFamily: "Inter",
        }),
        Plot.text(data, {
          x: 0,
          y: "opcion",
          text: (d) => `${d.conteo} votos`,
          fill: vistas.participacion.colores.texto_suave,
          fillOpacity: 0.8,
          fontSize: 30,
          lineAnchor: "bottom",
          textAnchor: "start",
          dy: -15,
          dx: 5,
          fontFamily: "Inter",
        }),
      ],
    });
  } else {
    return "";
  }
}
```

```js
// Gráfica de barras para votos por partido

function plot_validos(resultado) {
  if (resultado) {
    const r = Object.entries(resultado.r);
    const total = r.reduce((s, [, v]) => s + v, 0);
    const data = r
      .map(([opcion, conteo]) => ({
        opcion,
        conteo,
        porcentaje: conteo / total,
      }))
      .sort((a, b) => b.conteo - a.conteo);

    return Plot.plot({
      margin: 0,
      marginLeft: 80,
      marginRight: 10,
      height: data.length * 90,
      x: { axis: null, domain: [0, 1] },
      y: { axis: null, domain: data.map((d) => d.opcion) },
      marks: [
        Plot.image(data, {
          x: 0,
          y: "opcion",
          src: (d) => partidos.fotos[d.opcion],
          dx: -50,
          dy: 10,
          r: 28,
          width: 80,
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: vistas.validos.colores.fondo_suave,
          fillOpacity: 0.3,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: "porcentaje",
          y: "opcion",
          fill: (d) => partidos.colores[d.opcion][0],
          fillOpacity: 0.5,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: null,
          stroke: vistas.validos.colores.texto_suave,
          strokeOpacity: 0.5,
          strokeWidth: 1,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.text(data, {
          x: 1,
          y: "opcion",
          text: (d) => d3.format(".1%")(d.porcentaje),
          fill: vistas.validos.colores.texto_suave,
          fontSize: 35,
          lineAnchor: "bottom",
          textAnchor: "end",
          dy: -15,
          dx: -5,
          fontFamily: "Inter",
        }),
        Plot.text(data, {
          x: 0,
          y: "opcion",
          text: (d) => `${d.conteo} votos`,
          fill: vistas.validos.colores.texto_suave,
          fillOpacity: 0.8,
          fontSize: 30,
          lineAnchor: "bottom",
          textAnchor: "start",
          dy: -15,
          dx: 5,
          fontFamily: "Inter",
        }),
      ],
    });
  } else {
    return "";
  }
}
```
