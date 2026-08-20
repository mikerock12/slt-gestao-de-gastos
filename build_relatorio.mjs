/* Empacota o JS do relatório num arquivo só (IIFE), com Three.js e GSAP dentro.
   O .exe apenas injeta os dados e o CSS na hora de gerar o HTML. */
import { build } from "esbuild";
import { mkdirSync, statSync } from "node:fs";

mkdirSync("recursos/relatorio", { recursive: true });

await build({
  entryPoints: ["fonte_relatorio/app.js"],
  bundle: true,
  format: "iife",
  target: ["chrome100", "firefox100", "safari15", "edge100"],
  minify: true,
  legalComments: "none",
  outfile: "recursos/relatorio/app.bundle.js",
  logLevel: "info",
});

const kb = (p) => (statSync(p).size / 1024).toFixed(0);
console.log(`\napp.bundle.js — ${kb("recursos/relatorio/app.bundle.js")} KB`);
