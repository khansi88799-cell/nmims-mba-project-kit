// Write a deck's theme colours into a .pptx produced by pptxgenjs.
// pptxgenjs writes Office's stock colour scheme; slides that use scheme colours
// (pres.SchemeColor.accent1 etc.) pick up these values once this has run.
//
//   const { applyTheme } = require("./deck_theme.cjs");
//   await applyTheme("deck.pptx", { name, colors: { dk1, lt1, dk2, lt2, accent1..accent6, hlink, folHlink } });
const fs = require("fs");
const JSZip = require("jszip");

const SLOTS = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];
const xmlEscape = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

async function applyTheme(file, theme) {
  const colors = theme.colors || {};
  for (const k of SLOTS) {
    if (!/^[0-9A-Fa-f]{6}$/.test(String(colors[k] || ""))) throw new Error(`theme.colors.${k} must be 6 hex digits without "#"`);
  }
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const part = "ppt/theme/theme1.xml";
  const f = zip.file(part);
  if (!f) throw new Error(`${file} has no ${part}`);
  const name = xmlEscape(theme.name || "Custom");
  const scheme = `<a:clrScheme name="${name}">` + SLOTS.map((k) => `<a:${k}><a:srgbClr val="${colors[k].toUpperCase()}"/></a:${k}>`).join("") + "</a:clrScheme>";
  let xml = await f.async("string");
  const next = xml.replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, () => scheme).replace(/(<a:theme\b[^>]*?\bname=")[^"]*"/, (_, h) => `${h}${name}"`);
  if (!next.includes(scheme)) throw new Error("No colour scheme found to replace");
  zip.file(part, next);
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

module.exports = { applyTheme };
