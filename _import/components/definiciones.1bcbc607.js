import { format } from "../../_npm/d3@7.9.0/080cf928.js";
import { FileAttachment } from "../../_observablehq/stdlib.300f231b.js";

export const partidos = {
  AP: {
    foto: await FileAttachment({"name":"../../imagenes/ap.webp","mimeType":"image/webp","path":"../../_file/imagenes/ap.8f26d418.webp","lastModified":1790807836580,"size":18424}, import.meta.url).url(),
    colores: ["#00b5ee", "#4f7d35"],
  },
  "LYP-ADN": {
    foto: await FileAttachment({"name":"../../imagenes/lyp-adn.webp","mimeType":"image/webp","path":"../../_file/imagenes/lyp-adn.19b6d52b.webp","lastModified":1790807836581,"size":295964}, import.meta.url).url(),
    colores: ["#a91521", "#2f2f30"],
  },
  "APB-SUMATE": {
    foto: await FileAttachment({"name":"../../imagenes/apb-sumate.webp","mimeType":"image/webp","path":"../../_file/imagenes/apb-sumate.6be31528.webp","lastModified":1790807836581,"size":48160}, import.meta.url).url(),
    colores: ["#430956", "#cb010d"],
  },
  LIBRE: {
    foto: await FileAttachment({"name":"../../imagenes/libre.webp","mimeType":"image/webp","path":"../../_file/imagenes/libre.f3b956c2.webp","lastModified":1790807836581,"size":14496}, import.meta.url).url(),
    colores: ["#f50303", "#1d65c5"],
  },
  FP: {
    foto: await FileAttachment({"name":"../../imagenes/fp.webp","mimeType":"image/webp","path":"../../_file/imagenes/fp.7f1aa632.webp","lastModified":1790807836581,"size":10220}, import.meta.url).url(),
    colores: ["#1897d5", "#59c4f0"],
  },
  "MAS-IPSP": {
    foto: await FileAttachment({"name":"../../imagenes/mas-ipsp.webp","mimeType":"image/webp","path":"../../_file/imagenes/mas-ipsp.337a492c.webp","lastModified":1790807836581,"size":38746}, import.meta.url).url(),
    colores: ["#143a83", "#585755"],
  },
  UNIDAD: {
    foto: await FileAttachment({"name":"../../imagenes/unidad.webp","mimeType":"image/webp","path":"../../_file/imagenes/unidad.2fd99556.webp","lastModified":1790807836581,"size":44812}, import.meta.url).url(),
    colores: ["#feb447", "#083c6b"],
  },
  PDC: {
    foto: await FileAttachment({"name":"../../imagenes/pdc.webp","mimeType":"image/webp","path":"../../_file/imagenes/pdc.ffe97178.webp","lastModified":1790807836581,"size":47182}, import.meta.url).url(),
    colores: ["#05636b", "#dd0710"],
  },
};

export const formatos = {
  fecha: new Intl.DateTimeFormat("es", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    timeZone: "UTC",
  }),
  porcentaje: format(".1%"),
};
