// Arma el documento completo de la página a partir del fragmento del artifact.
// Lo usan el servidor (src/server.js) y la publicación en GitHub Pages (scripts/build-pages.mjs).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
export const fragmentPath = path.join(root, "artifact", "planificador.html");

export function buildPage({ base = "/" } = {}) {
  const fragment = fs.readFileSync(fragmentPath, "utf8");
  return `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Guías de viaje día por día en carro o avión: naturaleza, pueblos y sitios turísticos.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧭</text></svg>">
<style>body{margin:0}</style>
<script src="${base}config.js"></script>
<script src="${base}claude-shim.js"></script>
</head>
<body>
${fragment}
</body>
</html>`;
}
