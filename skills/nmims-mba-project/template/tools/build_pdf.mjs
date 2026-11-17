// Build the NMIMS CDOE project PDF from Markdown.
//
//   cd tools && npm run build            (uses report.config.json)
//   node build_pdf.mjs other.config.json
//
// Layout follows the NMIMS "Suggested Layout and Design Specifications":
// Calibri 11pt body (fonts from Microsoft Word; set Arial paths in report.config.json if Word is missing), 14pt bold section headings, 12pt bold sub-headings,
// 10pt table text, 1in margins, 1.15 line spacing, 6pt before/after,
// justified paragraphs, centred titles, "Page X of Y" bottom centre.
// The cover (Option A, approved 5 Nov 2026) carries no page number.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { marked } from "marked";
import puppeteer from "puppeteer-core";
import { PDFDocument } from "pdf-lib";
import { execFileSync } from "node:child_process";
import fontkit from "@pdf-lib/fontkit";
import { rgb } from "pdf-lib";

const here = path.dirname(fileURLToPath(import.meta.url));
const cfgPath = path.resolve(here, process.argv[2] || "report.config.json");
const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
const rel = (p) => path.resolve(path.dirname(cfgPath), p);

// Calibri ships inside Microsoft Word; fall back to Arial (also allowed by NMIMS) when Word is absent.
const ARIAL = "/System/Library/Fonts/Supplemental/";
if (!Object.values(cfg.fonts || {}).every((p) => fs.existsSync(p))) {
  console.warn("Calibri not found (is Microsoft Word installed?). Using Arial, which the guidelines also allow.");
  cfg.fonts = { regular: ARIAL + "Arial.ttf", bold: ARIAL + "Arial Bold.ttf", italic: ARIAL + "Arial Italic.ttf", boldItalic: ARIAL + "Arial Bold Italic.ttf" };
}
// Cover fields still holding [NEEDS: ...] block a final build.
const coverOpen = Object.entries(cfg.cover || {}).filter(([, v]) => /\[NEEDS:/.test(String(v))).map(([k]) => k);
if (coverOpen.length) {
  if (cfg.final) throw new Error(`Final build blocked: fill cover fields ${coverOpen.join(", ")} in report.config.json`);
  console.warn("Cover fields still to fill:", coverOpen.join(", "));
}
const CHROME = process.env.CHROME_PATH || [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
].find((p) => fs.existsSync(p));
if (!CHROME) throw new Error("Google Chrome not found. Install it or set CHROME_PATH.");

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---------- shared CSS ----------
const f = cfg.fonts;
const fontFace = `
@font-face{font-family:"BodyFont";src:url("${pathToFileURL(f.regular)}");font-weight:400;font-style:normal}
@font-face{font-family:"BodyFont";src:url("${pathToFileURL(f.bold)}");font-weight:700;font-style:normal}
@font-face{font-family:"BodyFont";src:url("${pathToFileURL(f.italic)}");font-weight:400;font-style:italic}
@font-face{font-family:"BodyFont";src:url("${pathToFileURL(f.boldItalic)}");font-weight:700;font-style:italic}`;
const FONT = `"BodyFont", Calibri, Arial, sans-serif`;

// ---------- cover (Option A) ----------
function coverHtml() {
  const c = cfg.cover;
  const logo = "data:image/png;base64," + fs.readFileSync(rel(cfg.logo)).toString("base64");
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${fontFace}
@page{size:A4;margin:0}
html,body{margin:0}
body{font-family:${FONT};color:#1f1f1f}
.page{width:210mm;height:297mm;box-sizing:border-box;padding:1in;position:relative;text-align:center}
.logo{width:88mm;margin-top:3mm}
.title{font-size:20pt;font-weight:700;line-height:1.3;margin:29mm 0 0}
.format{margin-top:6mm;font-size:11.5pt;letter-spacing:.14em;text-transform:uppercase;color:#5a5a5a}
.sub{margin-top:19mm;font-size:12pt;font-style:italic}
table{margin:6mm auto 0;border-collapse:collapse;font-size:12pt;text-align:left}
td{padding:1.6mm 2.6mm;vertical-align:top}
td:first-child{font-weight:700;white-space:nowrap}
.foot{position:absolute;left:1in;right:1in;bottom:1in;font-size:12pt;font-weight:700}
</style></head><body><div class="page">
<img class="logo" src="${logo}" alt="SVKM's NMIMS Centre for Distance and Online Education">
<p class="title">${esc(c.title).replace(/(\S+-\S+)/g, '<span style="white-space:nowrap">$1</span>')}</p>
<div class="format">${esc(c.format)}</div>
<div class="sub">Submitted by</div>
<table>
<tr><td>Student Name</td><td>${esc(c.studentName)}</td></tr>
<tr><td>SAP ID</td><td>${esc(c.sapId)}</td></tr>
<tr><td>Specialisation</td><td>${esc(c.specialisation)}</td></tr>
<tr><td>Programme</td><td>${esc(c.programme)}</td></tr>
${c.facultyGuide ? `<tr><td>Faculty Guide</td><td>${esc(c.facultyGuide)}</td></tr>` : ""}
</table>
<div class="foot">${esc(c.footer).replace("|", "&nbsp;|&nbsp;")}</div>
</div></body></html>`;
}

// ---------- body ----------
function loadMarkdown() {
  if (cfg.chapterDir) {
    const dir = rel(cfg.chapterDir);
    const files = fs.readdirSync(dir).filter((f) => /^\d\d_.*\.md$/.test(f) && !f.startsWith("00_")).sort();
    console.log("Chapters:", files.join(", "));
    const inc = (txt) => txt.replace(/<!--\s*include:\s*(\S+)\s*-->/g, (_, p) => fs.readFileSync(path.join(dir, p), "utf8").trim());
    return files.map((f) => inc(fs.readFileSync(path.join(dir, f), "utf8").trim())).join("\n\n");
  }
  return fs.readFileSync(rel(cfg.source), "utf8");
}

// Final builds need a passing originality report newer than every chapter
// (skills/originality-check: similarity.py --out ../output/originality).
function originalityGate() {
  const rep = rel(cfg.originalityReport || "../output/originality.json");
  if (!fs.existsSync(rep)) throw new Error(`Final build blocked: run the originality check first (missing ${rep}).`);
  const r = JSON.parse(fs.readFileSync(rep, "utf8"));
  if (!r.pass) throw new Error(`Final build blocked: originality check failed: ${(r.problems || []).join("; ")}`);
  const dir = rel(cfg.chapterDir);
  const newest = Math.max(...fs.readdirSync(dir).filter((f) => f.endsWith(".md")).map((f) => fs.statSync(path.join(dir, f)).mtimeMs));
  if (fs.statSync(rep).mtimeMs < newest) throw new Error("Final build blocked: chapters changed after the last originality check; run it again.");
  // The exact-phrase web check must be finished too: every phrase searched, every match resolved
  // (sample_phrases.py --status ../output/web_check.md writes this file).
  const web = rel(cfg.webCheckReport || "../output/web_check.json");
  if (!fs.existsSync(web)) throw new Error(`Final build blocked: finish the web check, then run sample_phrases.py --status (missing ${web}).`);
  const w = JSON.parse(fs.readFileSync(web, "utf8"));
  if (!w.complete) throw new Error(`Final build blocked: web check not complete (${w.searched} of ${w.total} phrases searched, ${(w.unresolved || []).length} match(es) unresolved).`);
  if (fs.statSync(web).mtimeMs < newest) throw new Error("Final build blocked: chapters changed after the last web check; refresh the checklist, search any new phrases and run --status again.");
}

function bodyHtml(pageNums = null) {
  let md = loadMarkdown();
  const open = md.match(/\[(NEEDS|VERIFY):[^\]]*\]/g) || [];
  if (open.length) console.warn(`Open placeholders: ${open.length} (${open.filter((x) => x.startsWith("[NEEDS")).length} NEEDS, ${open.filter((x) => x.startsWith("[VERIFY")).length} VERIFY)`);
  if (cfg.final && open.length) throw new Error("Final build blocked: resolve every [NEEDS]/[VERIFY] placeholder first.");
  if (cfg.final && cfg.chapterDir) originalityGate();
  if (!cfg.chapterDir && cfg.startAtHeading) {
    const i = md.indexOf(cfg.startAtHeading);
    if (i < 0) throw new Error(`startAtHeading not found: ${cfg.startAtHeading}`);
    md = md.slice(i);
  }
  md = md.replace(/^\*\*\*\s*$/gm, ""); // section rules -> handled by page breaks

  const renderer = new marked.Renderer();
  const baseCode = renderer.code.bind(renderer);
  renderer.code = (tok) => (tok.lang === "mermaid" ? `<figure class="diagram"><pre class="mermaid">${esc(tok.text)}</pre></figure>` : baseCode(tok));
  marked.use({ renderer, gfm: true });
  // protect display maths from markdown processing
  const maths = [];
  md = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, m) => `@@MATH${maths.push(m) - 1}@@`);
  let html = marked.parse(md);
  html = html.replace(/@@MATH(\d+)@@/g, (_, i) => `<div class="math">$$${esc(maths[+i])}$$</div>`);
  html = html.replace(/<p>((?:Table|Figure) \d+\.\d+:[^<]*)<\/p>/g, '<p class="caption">$1</p>');
  html = html.replace(/\[(NEEDS|VERIFY):([^\]]*)\]/g, '<mark class="ph">[$1:$2]</mark>');

  // ----- front matter: contents, list of tables, list of figures -----
  const strip = (h) => h.replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();
  const entries = [];
  html.replace(/<h([12])[^>]*>([\s\S]*?)<\/h\1>|<p class="caption">([\s\S]*?)<\/p>/g, (_, lvl, htxt, ctxt) => {
    if (lvl) entries.push({ kind: "h" + lvl, text: strip(htxt) });
    else entries.push({ kind: /^Table/.test(strip(ctxt)) ? "table" : "figure", text: strip(ctxt) });
    return _;
  });
  entries.forEach((e, i) => (e.page = pageNums ? pageNums[i] ?? "" : "00"));
  const row = (e, cls) => `<div class="toc-row ${cls}"><span class="t">${esc(e.text)}</span><span class="dots"></span><span class="n">${e.page}</span></div>`;
  const front = `
<section class="front"><div class="front-title">Contents</div>
${entries.filter((e) => e.kind[0] === "h").map((e) => row(e, e.kind)).join("\n")}
</section>
<section class="front"><div class="front-title">List of Tables</div>
${entries.filter((e) => e.kind === "table").map((e) => row(e, "cap")).join("\n")}
</section>
<section class="front"><div class="front-title">List of Figures</div>
${entries.filter((e) => e.kind === "figure").map((e) => row(e, "cap")).join("\n")}
</section>
<div class="sentinel">BODYSTART</div>`;
  bodyHtml.entries = entries.map((e) => e.text);
  html = front + html;

  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<style>
${fontFace}
@page{size:A4;margin:1in}
body{font-family:${FONT};font-size:11pt;line-height:1.15;color:#111;margin:0}
p,li{text-align:justify}
p{margin:6pt 0}
h1{font-size:14pt;font-weight:700;text-align:center;margin:0 0 12pt;break-before:page;break-after:avoid}
h1:first-of-type{break-before:auto}
h2,h3,h4{font-size:12pt;font-weight:700;margin:12pt 0 6pt;break-after:avoid}
ul,ol{margin:6pt 0;padding-left:22pt}
li{margin:3pt 0}
blockquote{margin:8pt 18pt;font-style:italic}
table{width:100%;border-collapse:collapse;margin:8pt 0;font-size:10pt;line-height:1.15;break-inside:auto}
th,td{border:0.6pt solid #9a9a9a;padding:3pt 5pt;vertical-align:top;text-align:left}
th{background:#ececec;font-weight:700}
tr{break-inside:avoid}
code{font-family:Menlo,Consolas,monospace;font-size:9pt}
figure.diagram{margin:10pt 0;text-align:center;break-inside:avoid}
figure.diagram svg{max-width:100%;height:auto;max-height:8.2in}
figure.diagram p, figure.diagram span, figure.diagram div{text-align:center !important}
figure.diagram svg text, figure.diagram svg tspan, figure.diagram svg .sectionTitle, figure.diagram svg .taskText, figure.diagram svg .taskTextOutsideRight, figure.diagram svg .tick text{font-family:${FONT} !important}
.math{margin:8pt 0;text-align:center}
p.caption{text-align:center;font-weight:700;font-size:10pt;margin:12pt 0 4pt;break-after:avoid}
mark.ph{background:#fff3a0;color:#6b4e00}
section.front{break-after:page}
.front-title{font-size:14pt;font-weight:700;text-align:center;margin:0 0 12pt}
.toc-row{display:flex;align-items:baseline;font-size:11pt;margin:3pt 0}
.toc-row .t{flex:0 1 auto;text-align:left}
.toc-row .dots{flex:1 1 auto;border-bottom:1pt dotted #888;margin:0 4pt;transform:translateY(-3pt);min-width:12pt}
.toc-row .n{flex:0 0 auto;min-width:16pt;text-align:right}
.toc-row.h1{font-weight:700;margin-top:7pt}
.toc-row.h2{padding-left:16pt}
.toc-row.cap{font-size:10.5pt}
.sentinel{font-size:2pt;line-height:0;height:0;color:#fff;overflow:visible}
p.caption + table, p.caption + figure{margin-top:2pt}
</style></head><body>
${html}
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script>
(async () => {
  try { renderMathInElement(document.body, {delimiters:[{left:"$$",right:"$$",display:true}], throwOnError:false}); } catch(e) { console.error(e); }
  mermaid.initialize({startOnLoad:false, theme:"neutral", themeVariables:{fontSize:"15px", fontFamily:'${FONT.replace(/"/g, "")}'}, flowchart:{nodeSpacing:28, rankSpacing:34, padding:8}, fontFamily:'${FONT.replace(/"/g, "")}', securityLevel:"strict"});
  try { await mermaid.run({querySelector:".mermaid"}); } catch(e) { console.error("mermaid", e); }
  await document.fonts.ready;
  window.__ready = true;
})();
</script></body></html>`;
}

async function toPdf(browser, html, opts, tmpName) {
  const tmp = path.join(here, ".build", tmpName);
  fs.mkdirSync(path.dirname(tmp), { recursive: true });
  fs.writeFileSync(tmp, html);
  const page = await browser.newPage();
  page.on("console", (m) => m.type() === "error" && console.error("[page]", m.text()));
  await page.goto(pathToFileURL(tmp).href, { waitUntil: "networkidle0", timeout: 120000 });
  if (opts.waitReady) await page.waitForFunction("window.__ready === true", { timeout: 120000 });
  const buf = await page.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true, ...opts.pdf });
  await page.close();
  return buf;
}

const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--allow-file-access-from-files"] });
try {
  const cover = await toPdf(browser, coverHtml(), { pdf: { margin: { top: 0, bottom: 0, left: 0, right: 0 } } }, "cover.html");
  const bodyOpts = {
    waitReady: true,
    pdf: { margin: { top: "1in", bottom: "1in", left: "1in", right: "1in" } },
  };
  // pass 1: placeholder page numbers, then locate every heading and caption
  const pass1 = await toPdf(browser, bodyHtml(), bodyOpts, "body.html");
  const p1 = path.join(here, ".build", "pass1.pdf");
  const ej = path.join(here, ".build", "entries.json");
  fs.writeFileSync(p1, pass1);
  fs.writeFileSync(ej, JSON.stringify(bodyHtml.entries));
  const py = fs.existsSync(path.join(here, ".venv/bin/python")) ? path.join(here, ".venv/bin/python") : "python3";
  const nums = JSON.parse(execFileSync(py, [path.join(here, "find_pages.py"), p1, ej], { encoding: "utf8" }));
  const missing = bodyHtml.entries.filter((_, i) => nums[i] == null);
  if (missing.length) console.warn("Contents: page not found for", missing);
  // pass 2: same layout, real numbers
  const body = await toPdf(browser, bodyHtml(nums), bodyOpts, "body.html");

  const out = await PDFDocument.create();
  for (const buf of [cover, body]) {
    const src = await PDFDocument.load(buf);
    (await out.copyPages(src, src.getPageIndices())).forEach((p) => out.addPage(p));
  }
  // Footer "Page X of Y", bottom centre, stamped with the embedded body font (cover unnumbered)
  out.registerFontkit(fontkit);
  const footFont = await out.embedFont(fs.readFileSync(f.regular), { subset: true });
  const pagesAll = out.getPages();
  const total = pagesAll.length - 1;
  pagesAll.slice(1).forEach((pg, i) => {
    const label = `Page ${i + 1} of ${total}`;
    const size = 9;
    const w = footFont.widthOfTextAtSize(label, size);
    pg.drawText(label, { x: (pg.getWidth() - w) / 2, y: 36, size, font: footFont, color: rgb(0.2, 0.2, 0.2) });
  });
  out.setTitle(cfg.cover.title);
  out.setAuthor(cfg.cover.studentName);
  out.setSubject(`${cfg.cover.format}, ${cfg.cover.programme}`);
  out.setCreator(cfg.cover.studentName);
  out.setProducer(cfg.cover.studentName);
  const dest = rel(cfg.output);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, await out.save());
  console.log(`Wrote ${dest} (${out.getPageCount()} pages: 1 cover + ${out.getPageCount() - 1} numbered)`);
} finally {
  await browser.close();
}
