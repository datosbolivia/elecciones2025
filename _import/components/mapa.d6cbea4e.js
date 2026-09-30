import maplibregl from "../../_npm/maplibre-gl@6.11.2/356c9cfd.js";

export const crearMapa = (selector) => {
  const container = document.querySelector(selector);
  const map = new maplibregl.Map({
    container: container,
    center: [-65., -16.5],
    zoom: 5.2,
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

  return map;
};

export const actualizarCapas = async (map, estilo, capas, definiciones) => {
  const crearCapas = (
    map,
    capas,
    { sources = [], layers = [], hover = {} }
  ) => {
    for (const source of sources)
      map.getSource(source) || map.addSource(source, capas[source].source);
    for (const layer of layers)
      map.getLayer(layer) || map.addLayer(capas[layer].layer);
    for (const [id, layer] of Object.entries(hover))
      map.getLayer(id) || map.addLayer(capas[layer].hover);
  };
  map.setStyle(estilo, { diff: false });
  await map.once("style.load", () => {
    crearCapas(map, capas, definiciones);
  });
};

export const colormap_categorias = (campo, categorias, { fallback = "#ccc" } = {}) => [
  "match",
  ["get", campo],
  ...categorias.flat(),
  fallback,
];

export const colormap_lineal = (campo, segmentos, { coalesceTo = 0 } = {}) => [
  "interpolate",
  ["linear"],
  ["coalesce", ["to-number", ["get", campo]], coalesceTo],
  ...segmentos.flat(),
];
