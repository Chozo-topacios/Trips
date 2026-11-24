// Genera la versión estática para GitHub Pages en ./dist
// La dirección del servicio que llama a Claude se toma de la variable PLANIFICADOR_API
// (en GitHub: Settings → Secrets and variables → Actions → Variables).
import fs from "node:fs";
import path from "node:path";
import { buildPage, root } from "../src/page.js";

const out = path.join(root, "dist");
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });

const api = (process.env.PLANIFICADOR_API || "").trim().replace(/\/+$/, "");
fs.writeFileSync(path.join(out, "index.html"), buildPage({ base: "./" }));
fs.copyFileSync(path.join(root, "public", "claude-shim.js"), path.join(out, "claude-shim.js"));
for (const f of ["manifest.webmanifest", "icon-192.png", "icon-512.png"]) fs.copyFileSync(path.join(root, "public", f), path.join(out, f));
// Cada publicación cambia el nombre del caché, así el teléfono toma la versión nueva.
fs.writeFileSync(path.join(out, "sw.js"), fs.readFileSync(path.join(root, "public", "sw.js"), "utf8").replace("__BUILD__", Date.now().toString(36)));
fs.writeFileSync(path.join(out, "config.js"), `window.PLANIFICADOR_API = ${JSON.stringify(api)};\n`);
fs.writeFileSync(path.join(out, ".nojekyll"), "");
console.log(`dist/ listo. Servicio de guías: ${api || "(sin configurar)"}`);
