// Viva deck builder: renders presentation/deck.json into an editable PowerPoint file.
//
//   npm run deck                 -> presentation/<deck.fileName>.pptx   (name from report.config.json)
//   node build_deck.cjs --qa     -> also one-slide decks in presentation/_qa (preview with Quick Look)
//   npm run deck:pdf             -> PDF of the deck via LibreOffice (renders charts too)
//
// deck.json = { "footer": "...", "theme": {optional colours}, "slides": [ { "type": ..., ... } ] }
// Slide types and their fields: skills/nmims-mba-project/references/deck-format.md.
// Every number on a slide must come from the report.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./deck_theme.cjs");

const ROOT = path.resolve(__dirname, "..");
const CFG = JSON.parse(fs.readFileSync(path.join(__dirname, "report.config.json"), "utf8"));
const deckArg = process.argv.slice(2).find((a) => a.endsWith(".json"));
const DECK_FILE = deckArg ? path.resolve(deckArg) : path.join(ROOT, "presentation", "deck.json");
const D = JSON.parse(fs.readFileSync(DECK_FILE, "utf8"));
const OUT_DIR = path.join(ROOT, "presentation");
const OUT = path.join(OUT_DIR, `${(CFG.deck && CFG.deck.fileName) || "Presentation"}.pptx`);
const LOGO = path.resolve(__dirname, CFG.logo || "../assets/NMIMS_CDOE_logo_cover.png");

// ---------- theme (fonts installed on every Mac and Windows PC, so previews match PowerPoint) ----------
const HEX = Object.assign({ ink: "1B2430", slate: "2E3A48", accent: "C8202F", grey: "5B6B7C", good: "2F7D6D", warn: "E8A33D", mist: "F2F4F7", line: "D9DEE4", mute: "8A96A3", white: "FFFFFF" }, D.theme || {});
const THEME = {
  name: D.themeName || "Project deck",
  headFontFace: "Georgia",
  bodyFontFace: "Arial",
  colors: { dk1: HEX.ink, lt1: HEX.white, dk2: HEX.slate, lt2: HEX.mist, accent1: HEX.accent, accent2: HEX.grey, accent3: HEX.good, accent4: HEX.warn, accent5: HEX.mute, accent6: HEX.line, hlink: HEX.accent, folHlink: HEX.mute },
};
const W = 13.333, H = 7.5, M = 0.6;
const FOOT = D.footer || `${CFG.cover.format}  ·  NMIMS CDOE`;

function makePres() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = CFG.cover.studentName || "";
  pres.title = D.title || CFG.cover.title || "Presentation";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  pres.defineSlideMaster({
    title: "Title dark", background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: M, y: 2.35, w: 8.6, h: 1.3, fontFace: THEME.headFontFace, fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: M, y: 3.75, w: 8.6, h: 1.0, fontSize: 20, color: C.accent6, valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "Content", background: { color: C.background1 }, margin: [0.5, 0.6, 0.6, 0.6],
    slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
    objects: [
      { text: { text: FOOT, options: { x: M, y: 7.0, w: 9, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
      { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.85, fontFace: THEME.headFontFace, fontSize: 30, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    ],
  });
  return pres;
}

// ---------- helpers ----------
const tb = (o) => Object.assign({ isTextBox: true, margin: 0, valign: "top" }, o);
const bullets = (items, o = {}) => items.map((t, j) => ({ text: t, options: Object.assign({ bullet: { indent: 18 }, breakLine: j < items.length - 1 }, o) }));
function card(s, pres, x, y, w, h, fill, line) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: line || fill, width: line ? 1 : 0 } });
}
function badge(s, pres, x, y, d, label, fill, color) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
  s.addText(String(label), tb({ x, y, w: d, h: d, align: "center", valign: "middle", fontSize: Math.max(12, Math.round(d * 26)), bold: true, color }));
}
function source(s, text) { if (text) s.addText(text, tb({ x: M, y: 6.55, w: W - 2 * M, h: 0.3, fontSize: 10, italic: true, color: HEX.mute })); }
function line(s, pres, x1, y1, x2, y2, { color, width = 2, dash = "solid", arrow = true }) {
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1, line: Object.assign({ color, width, dashType: dash }, arrow ? { endArrowType: "triangle" } : {}) });
}
const chartBase = {
  catAxisLabelColor: HEX.grey, valAxisLabelColor: HEX.grey, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  valGridLine: { color: HEX.line, size: 0.75 }, catGridLine: { style: "none" }, showTitle: true, titleFontSize: 14, titleColor: HEX.ink, dataLabelFontSize: 12, dataLabelColor: HEX.ink,
};
function barChart(s, pres, c, box) {
  const horizontal = c.kind === "bar";
  const n = c.values.length;
  const colors = c.highlight != null ? c.values.map((_, i) => (i === c.highlight ? HEX.accent : HEX.grey)) : [HEX.grey];
  s.addChart(pres.charts.BAR, [{ name: c.title || "Value", labels: c.labels, values: c.values }], Object.assign({}, chartBase, box, {
    barDir: horizontal ? "bar" : "col", chartColors: colors.length === n ? colors : [HEX.grey], showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: c.format || "General", title: c.title || "", showLegend: false, barGapWidthPct: 50,
    valAxisMinVal: 0, valAxisMaxVal: c.max || undefined, valAxisHidden: horizontal, valGridLine: horizontal ? { style: "none" } : chartBase.valGridLine,
    catAxisOrientation: horizontal ? "maxMin" : "minMax",
  }));
}

// ---------- slide types ----------
const T = {};
T.title = (pres, s, d) => {
  card(s, pres, M, 0.6, 3.9, 1.55, HEX.white);
  if (fs.existsSync(LOGO)) s.addImage({ path: LOGO, x: M + 0.15, y: 0.72, w: 3.6, h: 1.31, altText: "University logo" });
  s.addText(d.title || CFG.cover.title, { placeholder: "title" });
  if (d.subtitle) s.addText(d.subtitle, { placeholder: "body" });
  const c = CFG.cover;
  const lines = d.lines || [
    `${c.format}  ·  ${c.programme}`,
    String(c.footer || "").replace(/\s*\|\s*/g, "  ·  "),
    `${c.studentName}  ·  SAP ID ${c.sapId}  ·  ${c.specialisation}`,
  ].concat(c.facultyGuide ? [`Faculty Guide: ${c.facultyGuide}`] : []);
  s.addText(lines.map((t, i) => ({ text: t, options: { breakLine: i < lines.length - 1 } })), tb({ x: M, y: 5.0, w: 9.4, h: 1.7, fontSize: 15, color: HEX.line, paraSpaceAfter: 5 }));
  (d.badges || []).slice(0, 3).forEach((b, i) => {
    const y = 1.0 + i * 1.75, col = [HEX.grey, HEX.good, HEX.accent][i];
    s.addShape(pres.shapes.OVAL, { x: 10.35, y, w: 1.4, h: 1.4, fill: { color: col }, line: { color: col, width: 0 } });
    s.addText(b, tb({ x: 9.95, y: y + 0.42, w: 2.2, h: 0.56, align: "center", valign: "middle", fontSize: 14, bold: true, color: HEX.white }));
  });
};
T.story = (pres, s, d) => {
  card(s, pres, M, 1.5, 6.6, 4.85, HEX.mist);
  s.addText(d.heading || "", tb({ x: M + 0.35, y: 1.75, w: 6.0, h: 0.45, fontSize: 20, bold: true, color: HEX.ink, fontFace: THEME.headFontFace }));
  s.addText(bullets(d.bullets || []), tb({ x: M + 0.35, y: 2.35, w: 5.95, h: 3.8, fontSize: 15, color: HEX.ink, paraSpaceAfter: 10 }));
  (d.stats || []).slice(0, 3).forEach((st, i) => {
    const y = 1.5 + i * 1.65;
    s.addText(st.value, tb({ x: 7.75, y, w: 5.0, h: 0.85, fontSize: 40, bold: true, color: HEX.accent, fontFace: THEME.headFontFace, valign: "bottom" }));
    s.addText(st.label, tb({ x: 7.75, y: y + 0.9, w: 5.0, h: 0.5, fontSize: 15, color: HEX.slate }));
  });
  source(s, d.source);
};
T.chart_text = (pres, s, d) => {
  barChart(s, pres, d.chart, { x: M, y: 1.5, w: 5.6, h: 4.85 });
  s.addText(d.heading || "", tb({ x: 6.75, y: 1.5, w: 6.0, h: 0.45, fontSize: 20, bold: true, color: HEX.ink, fontFace: THEME.headFontFace }));
  s.addText(bullets(d.bullets || []), tb({ x: 6.75, y: 2.05, w: 6.0, h: 2.6, fontSize: 16, color: HEX.ink, paraSpaceAfter: 8 }));
  if (d.callout) {
    card(s, pres, 6.75, 4.85, 5.98, 1.45, HEX.mist);
    s.addText(d.callout, tb({ x: 7.0, y: 5.0, w: 5.5, h: 1.2, fontSize: 15, color: HEX.ink, valign: "middle" }));
  }
  source(s, d.source);
};
T.chart_cards = (pres, s, d) => {
  barChart(s, pres, d.chart, { x: M, y: 1.5, w: 6.4, h: 4.85 });
  (d.cards || []).slice(0, 3).forEach((c, i) => {
    const y = 1.5 + i * 1.65;
    card(s, pres, 7.35, y, 5.38, 1.45, HEX.mist);
    badge(s, pres, 7.55, y + 0.4, 0.6, i + 1, HEX.accent, HEX.white);
    s.addText(c.title, tb({ x: 8.35, y: y + 0.17, w: 4.2, h: 0.4, fontSize: 16, bold: true, color: HEX.ink }));
    s.addText(c.text, tb({ x: 8.35, y: y + 0.6, w: 4.2, h: 0.75, fontSize: 14, color: HEX.slate }));
  });
  source(s, d.source);
};
T.cards = (pres, s, d) => {
  const items = (d.items || []).slice(0, 8), perRow = items.length <= 3 ? items.length : 4, rows = Math.ceil(items.length / perRow);
  const gx = 0.24, cw = (W - 2 * M - (perRow - 1) * gx) / perRow, ch = rows === 1 ? 3.6 : 2.15;
  items.forEach((it, i) => {
    const col = i % perRow, row = Math.floor(i / perRow), x = M + col * (cw + gx), y = 1.55 + row * (ch + 0.3);
    card(s, pres, x, y, cw, ch, row === 0 ? HEX.mist : HEX.white, row === 0 ? null : HEX.line);
    s.addText(it.label, tb({ x: x + 0.25, y: y + 0.22, w: cw - 0.5, h: 0.55, fontSize: 24, bold: true, color: HEX.accent, fontFace: THEME.headFontFace }));
    s.addText(it.text, tb({ x: x + 0.25, y: y + 0.9, w: cw - 0.5, h: ch - 1.1, fontSize: 16, color: HEX.ink }));
  });
  source(s, d.source);
};
T.scoring = (pres, s, d) => {
  const c = Object.assign({ kind: "bar", max: 100 }, d.chart);
  if (c.highlight == null) c.highlight = c.values.indexOf(Math.max(...c.values));
  barChart(s, pres, c, { x: M, y: 1.5, w: 7.4, h: 4.85 });
  card(s, pres, 8.35, 1.5, 4.38, 4.85, HEX.mist);
  s.addText(d.heading || "", tb({ x: 8.65, y: 1.75, w: 3.8, h: 0.8, fontSize: 18, bold: true, color: HEX.ink, fontFace: THEME.headFontFace }));
  (d.rows || []).slice(0, 3).forEach(([a, b], i) => {
    const y = 2.75 + i * 0.95;
    s.addText(a, tb({ x: 8.65, y, w: 2.5, h: 0.75, fontSize: 15, color: HEX.slate, valign: "middle" }));
    s.addText(b, tb({ x: 11.1, y, w: 1.45, h: 0.75, fontSize: 18, bold: true, color: HEX.accent, align: "right", valign: "middle" }));
  });
  if (d.note) s.addText(d.note, tb({ x: 8.65, y: 5.65, w: 3.8, h: 0.4, fontSize: 12, italic: true, color: HEX.mute }));
};
T.steps = (pres, s, d) => {
  const steps = (d.steps || []).slice(0, 6), n = steps.length || 1, gap = 0.17, bw = (W - 2 * M - (n - 1) * gap) / n;
  steps.forEach((st, i) => {
    const x = M + i * (bw + gap), last = i === n - 1;
    card(s, pres, x, 1.6, bw, 2.55, last ? HEX.good : HEX.mist);
    badge(s, pres, x + 0.2, 1.8, 0.55, i + 1, last ? HEX.white : HEX.accent, last ? HEX.good : HEX.white);
    s.addText(st.title, tb({ x: x + 0.2, y: 2.5, w: bw - 0.4, h: 0.65, fontSize: 15, bold: true, color: last ? HEX.white : HEX.ink }));
    s.addText(st.text, tb({ x: x + 0.2, y: 3.2, w: bw - 0.4, h: 0.85, fontSize: 13, color: last ? HEX.white : HEX.slate }));
  });
  (d.notes_cards || []).slice(0, 2).forEach((nt, i) => {
    const x = M + i * 6.13;
    card(s, pres, x, 4.5, 6.0, 1.85, HEX.mist);
    s.addText(nt.title, tb({ x: x + 0.3, y: 4.68, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: HEX.ink }));
    s.addText(nt.text, tb({ x: x + 0.3, y: 5.12, w: 5.4, h: 1.1, fontSize: 14, color: HEX.slate }));
  });
};
T.flow = (pres, s, d) => {
  // nodes on a grid: {id, title, sub, row, col, style: "core" | "plain" | "muted"}; edges: {from, to, label, kind: "money" | "info"}
  const nodes = d.nodes || [], edges = d.edges || [];
  const R = Math.max(...nodes.map((n) => n.row)) + 1, Cn = Math.max(...nodes.map((n) => n.col)) + 1;
  const top = 1.5, bottom = 6.2, gx = 0.9, bw = Math.min(3.2, (W - 2 * M - (Cn - 1) * gx) / Cn), bh = R >= 3 ? 0.9 : 1.05;
  const colX = (c) => M + c * ((W - 2 * M - bw) / Math.max(1, Cn - 1));
  const rowY = (r) => (R === 1 ? (top + bottom - bh) / 2 : top + r * ((bottom - top - bh) / (R - 1)));
  const box = {};
  nodes.forEach((n) => {
    const x = Cn === 1 ? (W - bw) / 2 : colX(n.col), y = rowY(n.row);
    box[n.id] = { x, y, w: bw, h: bh, cx: x + bw / 2, cy: y + bh / 2 };
    const fill = n.style === "core" ? HEX.ink : n.style === "muted" ? HEX.mist : HEX.white;
    const txt = n.style === "core" ? HEX.white : HEX.ink;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.1, fill: { color: fill }, line: { color: n.style === "plain" || !n.style ? HEX.grey : fill, width: 1.25 } });
    s.addText([{ text: n.title, options: { bold: true, fontSize: 15, breakLine: !!n.sub } }].concat(n.sub ? [{ text: n.sub, options: { fontSize: 11 } }] : []), tb({ x: x + 0.1, y, w: bw - 0.2, h: bh, align: "center", valign: "middle", color: txt }));
  });
  const clip = (b, dx, dy) => { const t = Math.min(dx ? (b.w / 2) / Math.abs(dx) : Infinity, dy ? (b.h / 2) / Math.abs(dy) : Infinity); return [b.cx + dx * t, b.cy + dy * t]; };
  const pairTotal = {}, pairSeen = {};
  const pk = (e) => [e.from, e.to].sort().join("|");
  edges.forEach((e) => (pairTotal[pk(e)] = (pairTotal[pk(e)] || 0) + 1));
  edges.forEach((e) => {
    const A = box[e.from], B = box[e.to];
    if (!A || !B) throw new Error(`flow edge ${e.from} -> ${e.to}: unknown node`);
    const key = pk(e), k = (pairSeen[key] = (pairSeen[key] || 0) + 1) - 1, n = pairTotal[key];
    // a stable "canonical" direction so parallel edges between the same two boxes spread symmetrically
    const P = box[key.split("|")[0]], Q = box[key.split("|")[1]];
    const cdx = Q.cx - P.cx, cdy = Q.cy - P.cy, clen = Math.hypot(cdx, cdy) || 1, sh = (k - (n - 1) / 2) * 0.32;
    const ox = (-cdy / clen) * sh, oy = (cdx / clen) * sh;
    const dx = B.cx - A.cx, dy = B.cy - A.cy;
    const [x1, y1] = clip(A, dx, dy), [x2, y2] = clip(B, -dx, -dy);
    const money = (e.kind || "money") === "money";
    line(s, pres, x1 + ox, y1 + oy, x2 + ox, y2 + oy, money ? { color: HEX.accent, width: 2.25 } : { color: HEX.mute, width: 1.5, dash: "dash" });
    if (e.label) {
      const lw = Math.min(2.0, Math.max(1.1, e.label.length * 0.085)), lh = e.label.length > 22 ? 0.5 : 0.32;
      const sx = Math.sign(ox), sy = Math.sign(oy), vertical = Math.abs(y2 - y1) > Math.abs(x2 - x1);
      const mx = (x1 + x2) / 2 + ox + (vertical && sx ? sx * (lw / 2 + 0.1) : 0);
      const my = (y1 + y2) / 2 + oy + (!vertical && sy ? sy * (lh / 2 + 0.06) : 0);
      s.addText(e.label, tb({ x: mx - lw / 2, y: my - lh / 2, w: lw, h: lh, fontSize: 11, color: money ? HEX.accent : HEX.grey, align: "center", valign: "middle", fill: { color: HEX.white } }));
    }
  });
  line(s, pres, 0.6, 6.6, 1.2, 6.6, { color: HEX.accent, width: 2.25, arrow: false });
  s.addText(d.moneyLabel || "Money", tb({ x: 1.3, y: 6.45, w: 1.2, h: 0.3, fontSize: 11, color: HEX.ink, valign: "middle" }));
  line(s, pres, 2.5, 6.6, 3.1, 6.6, { color: HEX.mute, width: 1.5, dash: "dash", arrow: false });
  s.addText(d.infoLabel || "Data and decisions", tb({ x: 3.2, y: 6.45, w: 2.2, h: 0.3, fontSize: 11, color: HEX.ink, valign: "middle" }));
  if (d.note) s.addText(d.note, tb({ x: 5.5, y: 6.45, w: 7.2, h: 0.3, fontSize: 11, italic: true, color: HEX.grey, valign: "middle" }));
};
T.revenue = (pres, s, d) => {
  (d.items || []).slice(0, 4).forEach((it, i) => {
    const x = M + (i % 2) * 3.15, y = 1.5 + Math.floor(i / 2) * 2.0;
    card(s, pres, x, y, 3.0, 1.8, HEX.mist);
    s.addText(it.value, tb({ x: x + 0.25, y: y + 0.18, w: 2.6, h: 0.65, fontSize: 28, bold: true, color: HEX.accent, fontFace: THEME.headFontFace }));
    s.addText(it.label, tb({ x: x + 0.25, y: y + 0.85, w: 2.6, h: 0.35, fontSize: 15, bold: true, color: HEX.ink }));
    s.addText(it.text || "", tb({ x: x + 0.25, y: y + 1.2, w: 2.6, h: 0.5, fontSize: 12, color: HEX.slate }));
  });
  if (d.note) s.addText(d.note, tb({ x: M, y: 5.65, w: 6.15, h: 0.7, fontSize: 15, bold: true, color: HEX.ink, valign: "middle" }));
  if (d.chart) barChart(s, pres, Object.assign({ kind: "col" }, d.chart), { x: 7.15, y: 1.5, w: 5.58, h: 4.85 });
  source(s, d.source);
};
T.finance = (pres, s, d) => {
  const c = d.chart;
  s.addChart(pres.charts.BAR, c.series.map((se) => ({ name: se.name, labels: c.labels, values: se.values })), Object.assign({}, chartBase, {
    x: M, y: 1.5, w: 7.6, h: 4.85, barDir: "col", chartColors: [HEX.grey, HEX.accent, HEX.good].slice(0, c.series.length), showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: c.format || "0.0", title: c.title || "", showLegend: c.series.length > 1, legendPos: "b", legendFontSize: 12, legendColor: HEX.ink, barGapWidthPct: 60,
  }));
  (d.kpis || []).slice(0, 4).forEach((k, i) => {
    const y = 1.5 + i * 1.22;
    s.addText(k.value, tb({ x: 8.65, y, w: 4.1, h: 0.62, fontSize: 28, bold: true, color: HEX.accent, fontFace: THEME.headFontFace, valign: "bottom" }));
    s.addText(k.label, tb({ x: 8.65, y: y + 0.65, w: 4.1, h: 0.45, fontSize: 14, color: HEX.slate }));
  });
  source(s, d.source);
};
T.invest = (pres, s, d) => {
  const c = d.chart;
  s.addChart(pres.charts.DOUGHNUT, [{ name: c.title || "Use of funds", labels: c.labels, values: c.values }], {
    x: M, y: 1.45, w: 5.6, h: 4.95, holeSize: 55, chartColors: [HEX.ink, HEX.accent, HEX.grey, HEX.good, HEX.warn, HEX.mute].slice(0, c.values.length), showPercent: true, showValue: false,
    showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: HEX.ink, legendFontFace: "+mn-lt", dataLabelColor: HEX.white, dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: c.title || "", titleFontSize: 14, titleColor: HEX.ink, titleFontFace: "+mn-lt",
  });
  (d.gates || []).slice(0, 3).forEach((g, i) => {
    const y = 1.5 + i * 1.32;
    card(s, pres, 6.6, y, 6.13, 1.15, HEX.mist);
    s.addText(g.name, tb({ x: 6.85, y: y + 0.15, w: 1.3, h: 0.4, fontSize: 16, bold: true, color: HEX.accent }));
    s.addText(g.date || "", tb({ x: 6.85, y: y + 0.6, w: 1.3, h: 0.35, fontSize: 13, color: HEX.slate }));
    s.addText(g.text, tb({ x: 8.2, y: y + 0.15, w: 4.35, h: 0.85, fontSize: 14, color: HEX.ink, valign: "middle" }));
  });
  if (d.note) s.addText(d.note, tb({ x: 6.6, y: 5.5, w: 6.13, h: 0.85, fontSize: 14, color: HEX.ink, valign: "middle" }));
};
T.roadmap = (pres, s, d) => {
  const ph = (d.phases || []).slice(0, 4), n = ph.length || 1, gap = 0.24, bw = (W - 2 * M - (n - 1) * gap) / n;
  line(s, pres, M + 0.3, 2.05, W - M - 0.3, 2.05, { color: HEX.line, width: 3, arrow: false });
  ph.forEach((p, i) => {
    const x = M + i * (bw + gap);
    badge(s, pres, x + bw / 2 - 0.4, 1.65, 0.8, p.code, i === (d.highlight ?? -1) ? HEX.accent : HEX.ink, HEX.white);
    s.addText(p.date || "", tb({ x, y: 2.6, w: bw, h: 0.35, fontSize: 13, color: HEX.slate, align: "center" }));
    card(s, pres, x, 3.05, bw, 3.25, HEX.mist);
    s.addText(p.name, tb({ x: x + 0.25, y: 3.25, w: bw - 0.5, h: 0.45, fontSize: 18, bold: true, color: HEX.ink, fontFace: THEME.headFontFace }));
    s.addText(bullets(p.items || []), tb({ x: x + 0.25, y: 3.8, w: bw - 0.45, h: 2.35, fontSize: 14, color: HEX.ink, paraSpaceAfter: 6 }));
  });
  source(s, d.source);
};
T.changes = (pres, s, d) => {
  s.addText(d.fromLabel || "Started with", tb({ x: M, y: 1.45, w: 5.2, h: 0.4, fontSize: 14, bold: true, color: HEX.mute }));
  s.addText(d.toLabel || "Ended with", tb({ x: 7.05, y: 1.45, w: 5.6, h: 0.4, fontSize: 14, bold: true, color: HEX.good }));
  (d.rows || []).slice(0, 6).forEach((r, i) => {
    const y = 1.92 + i * 0.75;
    card(s, pres, M, y, 5.4, 0.62, HEX.mist);
    s.addText(r.from, tb({ x: M + 0.2, y, w: 5.0, h: 0.62, fontSize: 15, color: HEX.slate, valign: "middle" }));
    line(s, pres, 6.15, y + 0.31, 6.85, y + 0.31, { color: HEX.accent, width: 2 });
    card(s, pres, 7.05, y, 5.68, 0.62, HEX.white, HEX.good);
    s.addText(r.to, tb({ x: 7.25, y, w: 5.35, h: 0.62, fontSize: 15, color: HEX.ink, valign: "middle" }));
  });
};
T.learnings = (pres, s, d) => {
  (d.items || []).slice(0, 4).forEach((it, i) => {
    const x = M + (i % 2) * 6.2, y = 1.5 + Math.floor(i / 2) * 2.45;
    card(s, pres, x, y, 5.93, 2.2, HEX.mist);
    badge(s, pres, x + 0.3, y + 0.3, 0.6, i + 1, HEX.ink, HEX.white);
    s.addText(it.title, tb({ x: x + 1.1, y: y + 0.28, w: 4.6, h: 0.7, fontSize: 17, bold: true, color: HEX.ink }));
    s.addText(it.text, tb({ x: x + 1.1, y: y + 1.0, w: 4.6, h: 1.05, fontSize: 14, color: HEX.slate }));
  });
  source(s, d.source);
};
T.horizons = (pres, s, d) => {
  (d.columns || []).slice(0, 3).forEach((c, i) => {
    const x = M + i * 4.12, col = [HEX.grey, HEX.slate, HEX.accent][i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 3.88, h: 0.75, rectRadius: 0.12, fill: { color: col }, line: { color: col, width: 0 } });
    s.addText(c.title, tb({ x, y: 1.5, w: 3.88, h: 0.75, fontSize: 18, bold: true, color: HEX.white, align: "center", valign: "middle" }));
    card(s, pres, x, 2.45, 3.88, 2.75, HEX.mist);
    s.addText(bullets(c.items || []), tb({ x: x + 0.3, y: 2.7, w: 3.3, h: 2.4, fontSize: 15, color: HEX.ink, paraSpaceAfter: 12 }));
  });
  if (d.approach) {
    card(s, pres, M, 5.45, W - 2 * M, 0.9, HEX.white, HEX.line);
    s.addText([{ text: "Approach: ", options: { bold: true, color: HEX.accent } }, { text: d.approach }], tb({ x: M + 0.3, y: 5.45, w: W - 2 * M - 0.6, h: 0.9, fontSize: 15, color: HEX.ink, valign: "middle" }));
  }
};
T.closing = (pres, s, d) => {
  s.addText(d.title || "Thank you", { placeholder: "title" });
  if (d.subtitle) s.addText(d.subtitle, { placeholder: "body" });
  (d.asks || []).slice(0, 3).forEach((a, i) => {
    const x = M + i * 4.12;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.9, w: 3.88, h: 1.6, rectRadius: 0.12, fill: { color: HEX.slate }, line: { color: HEX.slate, width: 0 } });
    s.addText(a.title, tb({ x: x + 0.3, y: 5.08, w: 3.3, h: 0.45, fontSize: 18, bold: true, color: HEX.white }));
    s.addText(a.text, tb({ x: x + 0.3, y: 5.55, w: 3.3, h: 0.8, fontSize: 14, color: HEX.line }));
  });
  if (d.thanks) s.addText(d.thanks, tb({ x: 9.6, y: 0.6, w: 3.13, h: 0.5, fontSize: 18, italic: true, color: HEX.line, align: "right" }));
};

// ---------- build ----------
async function build(slides, file) {
  const pres = makePres();
  let last = null;
  for (const d of slides) {
    const fn = T[d.type];
    if (!fn) throw new Error(`Unknown slide type "${d.type}". Types: ${Object.keys(T).join(", ")}`);
    const sec = d.section || "Deck";
    if (sec !== last) { pres.addSection({ title: sec }); last = sec; }
    const dark = d.type === "title" || d.type === "closing";
    const s = pres.addSlide({ masterName: dark ? "Title dark" : "Content", sectionTitle: sec });
    if (!dark) s.addText(d.title || "", { placeholder: "title" });
    fn(pres, s, d);
    if (d.notes) s.addNotes(d.notes);
  }
  await pres.writeFile({ fileName: file });
  await applyTheme(file, THEME);
}

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  await build(D.slides, OUT);
  console.log(`Wrote ${OUT} (${D.slides.length} slides)`);
  if (process.argv.includes("--qa")) {
    const qa = path.join(OUT_DIR, "_qa");
    fs.mkdirSync(qa, { recursive: true });
    for (let i = 0; i < D.slides.length; i++) await build([D.slides[i]], path.join(qa, `slide_${String(i + 1).padStart(2, "0")}.pptx`));
    console.log(`QA decks in ${qa}  (preview: qlmanage -t -s 1600 -o ${qa} ${qa}/*.pptx; charts need LibreOffice: npm run deck:pdf)`);
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
