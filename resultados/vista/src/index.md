---
theme: dashboard
title: Bolivia 2025
toc: false
sidebar: false
---

<link rel="stylesheet" type="text/css" href="https://unpkg.com/maplibre-gl@4.0.2/dist/maplibre-gl.css">

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
  #observablehq-main, #observablehq-center {
    margin: 0;
    min-height: 100vh;
  }
  .header {
    color: black;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: sticky;
    z-index:4;
    background: white;
    top: 0;
    left: 0;
    height: 100px;
    background: #fff;
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
  }
  #mapa {
    position: absolute; 
    top: 100px; 
    bottom: 0; 
    width: 100%;
  }
  .maplibregl-popup {
      max-width: 400px;
      font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
  }
  .popup_header {
    font-family: "Inter";
    text-align: center;
    opacity: .3;
    font-size: .9em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
</style>

<div class="header">
  <div class="title">Bolivia 2025</div>
  <div class="subtitle"><span>Votos para presidente dentro del país</span><span class="timestamp">actualizado el ${timestamp_string} y contado al ${d3.format(".2%")(progreso)}</span></div>
</div>

```js
import maplibregl from "npm:maplibre-gl";
import { PMTiles, Protocol } from "npm:pmtiles";
```

```js
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);
```

```js
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
let fotos = {
  AP: await FileAttachment("imagenes/ap.webp").url(),
  "LYP-ADN": await FileAttachment("imagenes/lyp-adn.webp").url(),
  "APB-SUMATE": await FileAttachment("imagenes/apb-sumate.webp").url(),
  LIBRE: await FileAttachment("imagenes/libre.webp").url(),
  FP: await FileAttachment("imagenes/fp.webp").url(),
  "MAS-IPSP": await FileAttachment("imagenes/mas-ipsp.webp").url(),
  UNIDAD: await FileAttachment("imagenes/unidad.webp").url(),
  PDC: await FileAttachment("imagenes/pdc.webp").url(),
};
let colores = {
  AP: ["#00b5ee", "#4f7d35"],
  "LYP-ADN": ["#a91521", "#2f2f30"],
  "APB-SUMATE": ["#430956", "#cb010d"],
  LIBRE: ["#f50303", "#1d65c5"],
  FP: ["#1897d5", "#59c4f0"],
  "MAS-IPSP": ["#143a83", "#585755"],
  UNIDAD: ["#feb447", "#083c6b"],
  PDC: ["#05636b", "#dd0710"],
};
let fondo = {
  gris: "#ccc",
  texto: "#a0a0a0ff",
};
```

```js
// consolidar resultados y recintos

for (const feature of recintos.features) {
  const codigo = feature.properties.c;
  const resultado = resultados[codigo];
  feature.properties.partido = resultado?.g ?? null;
}

let colores_expresion = ["match", ["get", "partido"]];
for (const [opcion, color] of Object.entries(colores))
  colores_expresion.push(opcion, color[0]);
colores_expresion.push(fondo.gris);
```

```js
const labels = {
  source: {
    type: "raster",
    tiles: [
      "https://a.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png",
    ],
    tileSize: 256,
  },
  layer: {
    id: "labels-layer",
    type: "raster",
    source: "labels",
    paint: {
      "raster-opacity": 0.8,
    },
  },
};

const recintos_hover = {
  id: "recintos_hover",
  type: "circle",
  source: "recintos",
  filter: ["!=", ["get", "partido"], null],
  paint: {
    "circle-color": "rgba(0,0,0,0)",
    "circle-radius": [
      "interpolate",
      ["exponential", 1.2],
      ["zoom"],
      6,
      10,
      10,
      14,
      12,
      18,
      14,
      22,
      16,
      26,
      18,
      30,
    ],
  },
};
```

```js
function plot_resultado(resultado) {
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
          src: (d) => fotos[d.opcion],
          dx: -50,
          dy: 10,
          r: 28,
          width: 80,
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: fondo.gris,
          fillOpacity: 0.3,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: "porcentaje",
          y: "opcion",
          fill: (d) => colores[d.opcion][0],
          fillOpacity: 0.5,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: null,
          stroke: fondo.texto,
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
          fill: fondo.texto,
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
          fill: fondo.texto,
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
const div = display(document.createElement("div"));
div.id = "mapa";
const map = new maplibregl.Map({
  container: div,
  center: [-65.482, -17.237],
  zoom: 5,
  style:
    "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json",
  scrollZoom: true,
  attributionControl: {
    compact: true,
    customAttribution:
      "<a href='https://mauforonda.github.io/'>Mauricio Foronda</a>",
  },
});

map.on("load", function () {
  map.addSource("recintos", {
    type: "geojson",
    data: recintos,
  });

  map.addLayer({
    id: "recintos",
    type: "circle",
    source: "recintos",
    paint: {
      "circle-radius": [
        "interpolate",
        ["exponential", 1.4],
        ["zoom"],
        6,
        2,
        10,
        4,
        12,
        6,
        14,
        9,
        16,
        12,
        18,
        16,
      ],
      "circle-color": colores_expresion,
      "circle-opacity": 0.5,
    },
  });

  map.addSource("labels", labels.source);
  map.addLayer(labels.layer);

  map.addLayer(recintos_hover);
});

const popup = new maplibregl.Popup({
  closeButton: false,
  closeOnClick: false,
});

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
