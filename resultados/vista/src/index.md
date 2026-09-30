---
theme: dashboard
title: Bolivia 2025
toc: false
sidebar: false
---

<link 
  rel="stylesheet" 
  type="text/css" 
  href="https://unpkg.com/maplibre-gl@4.0.2/dist/maplibre-gl.css"
>

<link 
  rel="stylesheet" 
  type="text/css" 
  href="index.css"
>

<div class="header">
  <div class="title">Bolivia 2025</div>
  <div class="subtitle">${v.texto.subtitulo}</div>
  <div class="vuelta">${vueltaInput}</div>
  <div class="timestamp">Actualizado el ${formatos.fecha.format(new Date(timestamp))}</div>
  <div class="progreso">Contado al ${formatos.porcentaje(progreso)}</div>
  <div class="cambio_input">${vistaInput}</div>
  <div class="descripcion">${v.texto.descripcion}</div>
  <div class="resultado_global">${resultado_global}</div>
  <div class="fuente">Fuentes: resultados del Sistema de Consolidación Oficial de Resultados de Cómputo y coordenadas del sistema GeoElectoral del Órgano Electoral Plurinacional.</div>
</div>

<div id="mapa"></div>

```js
const resultado_global = plotResultado(resultados_globales[vista], {
  fontSizeMultiplier: 0.8,
});
```

```js
const vueltas = ["primera", "segunda"];
const vueltas_folder = {
  primera: "resultados/datos/",
  segunda: "resultados/datos/segunda_vuelta/",
};
const vueltaInput = Inputs.radio(vueltas, {
  value: "segunda",
  required: true,
  format: (d) => `${d} vuelta`,
});
const vuelta = Generators.input(vueltaInput);
```

```js
// Dependencias externas
import maplibregl from "npm:maplibre-gl@4.0.2";
```

```js
// Módulos locales
import { partidos, formatos } from "./components/definiciones.js";
import { capa_recintos } from "./components/capas.js";
import { estiloClaro, estiloOscuro } from "./components/basemap.js";
import {
  crearMapa,
  actualizarCapas,
  colormap_categorias,
  colormap_lineal,
} from "./components/mapa.js";
import { ordenarResultado } from "./components/helpers.js";
```

```js
// Definir vistas
const vistas = {
  validos: {
    colores: {
      fondo: "#ffffffdd",
      texto_fuerte: "#000",
      texto_suave: "#a0a0a0ff",
      fondo_suave: "#ccc",
      invert: 0,
    },
    texto: {
      subtitulo: "Votos para presidente",
      descripcion:
        "Cada punto es un recinto cuyo color representa a la organización ganadora y cuyo tamaño al número de votos válidos"
    },
    mapa: {
      estilo: estiloClaro,
      radio: "validos",
    },
    datos: {
      campo_resultado: "r",
    },
  },
  participacion: {
    colores: {
      fondo: "#000000ff",
      texto_fuerte: "#fbfbfbff",
      texto_suave: "#e9e9e9ff",
      fondo_suave: "#5a5a5aff",
      invert: 1,
    },
    texto: {
      subtitulo:
        "Participación electoral",
      descripcion:
        "Cada punto es un recinto cuyo color representa al porcentaje de votos nulos + blancos sobre el total de habilitados y cuyo tamaño al número de votos habilitados"
    },
    mapa: {
      estilo: estiloOscuro,
      radio: "total",
    },
    datos: {
      campo_resultado: "p",
    },
  },
};
```

```js
// Seleccionar vistas
const opciones = Object.keys(vistas);
const etiquetas = {
  validos: "votos válidos",
  participacion: "votos nulos y blancos",
};
const vistaInput = Inputs.radio(opciones, {
  value: "validos",
  required: true,
  format: (d) => etiquetas[d] ?? d,
});
const vista = Generators.input(vistaInput);
```

```js
const v = vistas[vista];
```

```js
// Definir colores para puntos
const recinto_colores = {
  validos: colormap_categorias(
    "partido",
    Object.entries(partidos).map(([k, v]) => [k, v.colores[0]]),
    {
      fallback: "#ccc",
    }
  ),
  participacion: colormap_lineal("invalido", [
    [0, "#09151fff"],
    [0.25, "#20554bff"],
    [0.5, "#7dae61ff"],
    [0.7, "#bcdf77ff"],
    [0.9, "#f4ff90ff"],
  ]),
};
```

```js
// Definir capas
const capas = {
  recintos: capa_recintos(
    recintos,
    v.mapa.radio,
    recinto_colores[vista],
    "partido"
  ),
};
```

```js
// Crear mapa
const map = crearMapa("#mapa");
invalidation.then(() => map.remove());
const popup = new maplibregl.Popup({
  closeButton: false,
  closeOnClick: false,
});
```

```js
// Aplicar capas
await actualizarCapas(map, v.mapa.estilo, capas, {
  sources: ["recintos"],
  layers: ["recintos"],
  hover: { recintos_hover: "recintos" },
});
```

```js
// Actualizar definiciones de estilo con la vista
const actualizarCSS = function (values) {
  Object.entries(values).forEach(([key, value]) =>
    document.documentElement.style.setProperty(`--${key}`, value)
  );
};
actualizarCSS(v.colores);
```

```js
// Cargar datos
const gh = `https://raw.githubusercontent.com/datosbolivia/elecciones2025/refs/heads/main/${vueltas_folder[vuelta]}`;
const recintos = await d3.json(`${gh}recintos.geojson`);
const resultados = await d3.json(`${gh}resultados.json`);
const timestamp = await fetch(`${gh}timestamp`).then((r) => r.text());
const progreso = await fetch(`${gh}progreso`).then((r) => r.text());
```

```js
// Hidratar coordenadas de recintos con datos de resultados
for (const feature of recintos.features) {
  // Código de recinto
  const codigo = feature.properties.c;
  const resultado = resultados[codigo];
  // Total de votos válidos
  feature.properties.validos = resultado
    ? Object.values(resultado.r).reduce((s, v) => s + v, 0)
    : 0;
  // Total de habilitados
  feature.properties.total = resultado
    ? Object.values(resultado.p).reduce((s, v) => s + v, 0)
    : 0;
  // Partido ganador
  feature.properties.partido = resultado?.g ?? null;
  // Porcentaje de votos nulos + blancos / habilitados
  feature.properties.invalido = resultado?.p
    ? (resultado.p.b + resultado.p.n) /
      (resultado.p.b + resultado.p.n + resultado.p.v)
    : null;
}
```

```js
// Resultados a nivel global
function resultadoGlobal(resultados, key) {
  return Object.values(resultados).reduce((acc, resultado) => {
    for (const [opcion, votos] of Object.entries(resultado[key])) {
      acc[opcion] = (acc[opcion] || 0) + votos;
    }
    return acc;
  }, {});
}
const resultados_globales = {
  validos: resultadoGlobal(resultados, "r"),
  participacion: resultadoGlobal(resultados, "p"),
};
```

```js
// Popups
let locked = false;
const mouseenter = function (e) {
  map.getCanvas().style.cursor = "pointer";
  const feature = e.features[0];
  const resultado = resultados[feature.properties.c] ?? null;
  const grafico = plotResultado(resultado[v.datos.campo_resultado]);
  popup
    .setHTML(
      `<div class="popup_plot">
    <div class="popup_header">${resultado ? resultado.n : ""}</div>
    ${grafico.outerHTML}
    </div>`
    )
    .setLngLat(feature.geometry.coordinates)
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
function plotResultado(resultado, { fontSizeMultiplier = 1 } = {}) {
  if (!resultado) return "";
  function plotVista(data, vista, colores) {
    if (vista == "participacion") {
      const etiquetas = {
        v: "VÁLIDOS",
        b: "BLANCOS",
        n: "NULOS",
      };
      const paleta = {
        v: colores.texto_suave,
        b: "#f3ff83",
        n: "#f3ff83",
      };
      const label = Plot.text(data, {
        x: 0,
        y: "opcion",
        text: (d) => etiquetas[d.opcion],
        fill: (d) => paleta[d.opcion],
        fillOpacity: 0.8,
        fontSize: 30,
        fontWeight: 600,
        lineAnchor: "middle",
        textAnchor: "end",
        dy: 15,
        dx: -12,
        fontFamily: "Inter",
      });
      return {
        label,
        fill: (d) => paleta[d.opcion],
        fillOpacity: (d) => (d.opcion === "v" ? 0.5 : 1),
        marginLeft: 180,
      };
    }
    const label = Plot.image(data, {
      x: 0,
      y: "opcion",
      src: (d) => partidos[d.opcion].foto,
      dx: -50,
      dy: 5,
      r: 30,
      width: 85,
    });
    return {
      label,
      fill: (d) => partidos[d.opcion].colores[0],
      fillOpacity: 0.7,
      marginLeft: 80,
    };
  }

  function plotBarras({
    data,
    colores,
    label,
    fill,
    fillOpacity,
    marginLeft,
    fontSizeMultiplier,
  }) {
    return Plot.plot({
      margin: 0,
      marginLeft: marginLeft,
      marginRight: 10,
      height: data.length * 90,
      x: { axis: null, domain: [0, 1] },
      y: { axis: null, domain: data.map((d) => d.opcion) },
      marks: [
        label,
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: colores.fondo_suave,
          fillOpacity: 0.2,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: "porcentaje",
          y: "opcion",
          fill,
          fillOpacity,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.barX(data, {
          x: 1,
          y: "opcion",
          fill: null,
          stroke: colores.texto_suave,
          strokeOpacity: 0.5,
          strokeWidth: 1,
          insetTop: 40,
          insetBottom: 10,
          r: 15,
        }),
        Plot.text(data, {
          x: 1,
          y: "opcion",
          text: (d) => d3.format(".2%")(d.porcentaje),
          fill: colores.texto_fuerte,
          fillOpacity: 0.7,
          fontSize: 30 * fontSizeMultiplier,
          lineAnchor: "bottom",
          textAnchor: "end",
          dy: -18,
          dx: -5,
          fontFamily: "Inter",
        }),
        Plot.text(data, {
          x: 0,
          y: "opcion",
          text: (d) => `${d3.format(",")(d.conteo)} votos`,
          fill: colores.texto_fuerte,
          fillOpacity: 0.5,
          fontSize: 30 * fontSizeMultiplier,
          lineAnchor: "bottom",
          textAnchor: "start",
          dy: -18,
          dx: 5,
          fontFamily: "Inter",
        }),
      ],
    });
  }

  const data = ordenarResultado(resultado, {
    sort: vista === "validos",
  });
  const colores = vistas[vista].colores;
  const { label, fill, fillOpacity, marginLeft } = plotVista(
    data,
    vista,
    colores
  );

  return plotBarras({
    data,
    colores,
    label,
    fill,
    fillOpacity,
    marginLeft,
    fontSizeMultiplier,
  });
}
```
