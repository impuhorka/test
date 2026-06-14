import { readdirSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { join, basename } from "path";
import { Resvg } from "@resvg/resvg-js";

const schemesDir = "docs/schemes";
const pngDir = join(schemesDir, "png");
mkdirSync(pngDir, { recursive: true });

const files = readdirSync(schemesDir).filter((f) => f.endsWith(".svg"));

for (const file of files) {
  const svg = readFileSync(join(schemesDir, file), "utf8");
  const resvg = new Resvg(svg, {
    fitTo: { mode: "width", value: 1800 },
    font: { loadSystemFonts: true },
  });
  const png = resvg.render().asPng();
  const out = join(pngDir, basename(file, ".svg") + ".png");
  writeFileSync(out, png);
  console.log("OK:", out);
}
