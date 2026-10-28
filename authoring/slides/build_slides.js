/**
 * Build the editable Solen BI 22 h presentation (V7) from slides.json.
 * Node >= 18, pptxgenjs 4.0.1. Run from the course root:
 *   node authoring/slides/build_slides.js
 * Writes presentation/Solen_CODEX_BI_22h.pptx and authoring/slides/layout_manifest.json.
 * No download, no AI call. A missing picture stops the build.
 */
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const BASE = __dirname;
const ROOT = process.env.SOLEN_ASSET_ROOT ? path.resolve(process.env.SOLEN_ASSET_ROOT) : path.resolve(BASE, '../..');
const OUT_DIR = path.resolve(BASE, '../../presentation');
const spec = JSON.parse(fs.readFileSync(path.join(BASE, 'slides.json'), 'utf8'));

const C = { navy: '2B3180', deep: '07152F', orange: 'FF9A3C', pale: 'F3F5FC', ink: '1A1F4D', muted: '5A6478',
  white: 'FFFFFF', line: 'DCE2F0', mid: '7A80C2', red: 'A12E39', redPale: 'FBEDEE', orangePale: 'FFF1E3' };
const SECTIONS = { A: 'BIENVENUE CHEZ SOLEN DIGITAL', B: 'CE QUE VOUS SAUREZ FAIRE', C: 'GIT ET GITHUB', D: 'CODEX FREE',
  E: 'LES NOTIONS BI', F: 'LES CINQ SÉANCES', G: 'LE CATALOGUE', H: 'SOUTENANCE', I: 'SOURCES ET LICENCES' };
const LOGO_LEADERS = path.join(ROOT, 'authoring/assets/leaders-logo.jpeg');
// Copie réduite (1200 px, proportions et transparence gardées) de authoring/assets/solen-digital-horizontal.png
const LOGO_SOLEN = path.join(BASE, 'assets/solen-digital-horizontal-1200.png');
const W = 13.333, X0 = 0.6, CW = 12.133, X1 = X0 + CW;

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Youssef Douma';
pptx.company = 'Leaders University';
pptx.subject = 'Langage avancé : IA, Codex et BI · Solen BI 22 h · V7';
pptx.title = 'Langage avancé : IA, Codex et BI — votre première mission chez Solen Digital';
pptx.lang = 'fr-FR';
pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'fr-FR' };
const ST = pptx.ShapeType;
const manifest = [];
let slideNo = 0;

// ---------- helpers ----------
function need(rel) { const p = path.resolve(ROOT, rel); if (!fs.existsSync(p)) throw new Error('Image absente : ' + rel); return p; }
function pngSize(p) {
  const b = fs.readFileSync(p);
  if (b.readUInt32BE(0) === 0x89504e47) return [b.readUInt32BE(16), b.readUInt32BE(20)];
  let i = 2; // JPEG
  while (i < b.length) { const m = b[i + 1], len = b.readUInt16BE(i + 2); if (m >= 0xc0 && m <= 0xc3) return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)]; i += 2 + len; }
  throw new Error('Taille illisible : ' + p);
}
function rect(s, x, y, w, h, fill, line, r = 0.1) {
  s.addShape(r ? ST.roundRect : ST.rect, { x, y, w, h, rectRadius: r || undefined, fill: { color: fill }, line: { color: line || fill, width: 0.75 } });
}
function text(s, t, x, y, w, h, size, color = C.ink, bold = false, extra = {}) {
  s.addText(t, { x, y, w, h, fontFace: 'Arial', fontSize: size, color, bold, margin: 0, valign: 'middle', paraSpaceAfter: 0, ...extra });
  manifest.push({ slide: slideNo, text: typeof t === 'string' ? t : t.map(r => r.text).join(''), x, y, w, h, size });
}
function circle(s, label, x, y, d, fill = C.navy, size = 16, color = C.white) {
  s.addShape(ST.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  text(s, label, x, y, d, d, size, color, true, { align: 'center' });
}
function arrow(s, x1, y1, x2, y2, color = C.orange, width = 2.5) {
  s.addShape(ST.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width, endArrowType: 'triangle' } });
}
function pillW(label) { return Math.max(1.2, 0.125 * label.length + 0.45); }
function pill(s, label, x, y, fill, color, w) {
  const ww = w || pillW(label);
  s.addShape(ST.roundRect, { x, y, w: ww, h: 0.4, rectRadius: 0.2, fill: { color: fill }, line: { color: fill } });
  text(s, label, x, y, ww, 0.4, 14, color, true, { align: 'center' });
  return ww;
}
function fitImage(file, bx, by, bw, bh) {
  const [pw, ph] = pngSize(file); const r = pw / ph;
  let w = bw, h = bw / r; if (h > bh) { h = bh; w = bh * r; }
  return { w, h, x: bx, y: by + (bh - h) / 2 };
}
// Picture shown through a crop window [l, t, r, b] in source pixels, at `scale` inches per pixel.
// pptxgenjs: w/h = whole picture at that scale, sizing = the visible window (written as srcRect).
function addCropped(s, file, crop, x, y, scale, altText) {
  const [pw, ph] = pngSize(file), [l, t, r, b] = crop;
  s.addImage({ path: file, x, y, w: pw * scale, h: ph * scale, altText,
    sizing: { type: 'crop', x: l * scale, y: t * scale, w: (r - l) * scale, h: (b - t) * scale } });
}
function solenOnWhite(s, x, y, h) { // dark background: logo on a white rounded panel, proportions kept
  const [pw, ph] = pngSize(LOGO_SOLEN); const lw = h * pw / ph, pad = 0.18;
  s.addShape(ST.roundRect, { x, y, w: lw + 2 * pad, h: h + 2 * pad, rectRadius: 0.14, fill: { color: C.white }, line: { color: C.white } });
  s.addImage({ path: LOGO_SOLEN, x: x + pad, y: y + pad, w: lw, h, altText: 'Logo fourni : Solen Digital' });
  return lw + 2 * pad;
}
function note(s, msg) {
  rect(s, X0, 6.12, CW, 0.62, C.pale, C.pale, 0.08);
  circle(s, 'i', X0 + 0.16, 6.27, 0.32, C.orange, 14, C.deep);
  text(s, msg, X0 + 0.65, 6.15, CW - 0.85, 0.56, 15, C.navy, true);
}
function kicker(s, d) {
  circle(s, d.section, X0, 0.3, 0.36, C.navy, 14);
  text(s, SECTIONS[d.section] + (d.kicker ? '  ·  ' + d.kicker : ''), X0 + 0.5, 0.3, 9.0, 0.36, 14, C.navy, true, { charSpacing: 0.5 });
}
function header(s, d) {
  kicker(s, d);
  text(s, d.title, X0, 0.78, 10.6, 0.85, d.title.length > 52 ? 26 : 30, C.ink, true);
}
// Compact header for full-width visuals: one title line with the honesty label on its right.
function visualHeader(s, d, label, fill, color) {
  kicker(s, d);
  const lw = pillW(label), tw = CW - lw - 0.3;
  const fsz = [28, 26, 24, 22].find(f => d.title.length * f * 0.0080 <= tw) || 20;
  text(s, d.title, X0, 0.74, tw, 0.6, fsz, C.ink, true);
  pill(s, label, X1 - lw, 0.84, fill, color, lw);
}
// Numbered points in one row under a visual.
function itemRow(s, items, y, h) {
  const n = items.length, gap = 0.35, w = (CW - gap * (n - 1)) / n;
  items.forEach((it, i) => {
    const x = X0 + i * (w + gap);
    circle(s, String(i + 1), x, y + 0.02, 0.4, C.orange, 14, C.deep);
    text(s, it, x + 0.52, y, w - 0.52, h, 17, C.ink, false, { valign: 'top' });
  });
}
function sideItems(s, items, x, y, w, size = 17) {
  items.forEach((it, i) => {
    circle(s, String(i + 1), x, y + i * 1.12 + 0.02, 0.4, C.orange, 14, C.deep);
    text(s, it, x + 0.55, y + i * 1.12, w - 0.55, 0.95, size, C.ink, false, { valign: 'top' });
  });
}


// Logos, footer and slide number live once in the master (keeps the file small).
(() => {
  const [pw, ph] = pngSize(LOGO_SOLEN), lh = 0.36, lw = lh * pw / ph;
  pptx.defineSlideMaster({
    title: 'SOLEN', background: { color: C.white },
    objects: [
      { image: { path: LOGO_SOLEN, x: X1 - lw - 0.52, y: 0.32, w: lw, h: lh, altText: 'Logo fourni : Solen Digital' } },
      { image: { path: LOGO_LEADERS, x: X1 - 0.42, y: 0.29, w: 0.42, h: 0.42, altText: 'Logo fourni : Leaders University' } },
      { text: { text: 'Solen BI 22 h · V7 · Youssef Douma · Leaders University', options: { x: X0, y: 7.06, w: 8, h: 0.26, fontFace: 'Arial', fontSize: 12, color: C.muted, margin: 0 } } },
    ],
    slideNumber: { x: X1 - 0.8, y: 7.06, w: 0.8, h: 0.26, fontFace: 'Arial', fontSize: 12, color: C.muted, bold: true, align: 'right', margin: 0 },
  });
})();

// ---------- layouts ----------
const L = {};
L.cover = (s, d) => {
  s.background = { color: C.deep };
  s.addShape(ST.ellipse, { x: 8.9, y: 3.5, w: 6.2, h: 6.2, fill: { color: C.navy }, line: { color: C.navy } });
  const pw = solenOnWhite(s, 0.75, 0.6, 0.62);
  s.addImage({ path: LOGO_LEADERS, x: 0.75 + pw + 0.3, y: 0.6, w: 0.98, h: 0.98, altText: 'Logo fourni : Leaders University' });
  text(s, 'LICENCE BI · ÉDITION SOLEN · V7', 0.78, 1.95, 9, 0.4, 15, C.orange, true, { charSpacing: 1.5 });
  text(s, d.title, 0.75, 2.45, 10.5, 1.3, 44, C.white, true);
  text(s, d.subtitle, 0.78, 3.8, 10, 0.7, 28, C.white, false);
  text(s, d.tagline, 0.78, 5.15, 10.8, 0.5, 18, C.orange, true);
  text(s, 'Youssef Douma · Leaders University · faits officiels vérifiés le 28/10/2026', 0.78, 6.75, 10, 0.3, 14, C.white);
};
L.divider = (s, d) => {
  s.background = { color: C.deep };
  circle(s, d.section, 0.75, 1.55, 1.2, C.orange, 44, C.deep);
  text(s, 'PARTIE ' + d.section + ' / I', 2.25, 1.6, 8, 0.4, 14, C.orange, true, { charSpacing: 1.5 });
  text(s, d.title, 2.25, 2.05, 10.2, 1.3, 40, C.white, true, { valign: 'top' });
  text(s, d.subtitle, 2.25, 3.55, 10, 0.9, 22, C.white, false, { valign: 'top' });
  const pw = solenOnWhite(s, 0.75, 6.25, 0.42);
  s.addImage({ path: LOGO_LEADERS, x: 0.75 + pw + 0.25, y: 6.25, w: 0.78, h: 0.78, altText: 'Logo fourni : Leaders University' });
  text(s, String(slideNo).padStart(2, '0') + ' / ' + spec.slides.length, X1 - 1.5, 7.04, 1.5, 0.28, 12, C.white, true, { align: 'right' });
};
L.closing = (s, d) => {
  s.background = { color: C.deep };
  const pw = solenOnWhite(s, 0.75, 0.6, 0.55);
  s.addImage({ path: LOGO_LEADERS, x: 0.75 + pw + 0.3, y: 0.6, w: 0.9, h: 0.9, altText: 'Logo fourni : Leaders University' });
  text(s, d.title, 0.75, 1.95, 11.5, 1.2, 38, C.white, true);
  d.items.forEach((v, i) => { circle(s, String(i + 1), 0.8, 3.55 + i * 0.85, 0.5, C.orange, 18, C.deep); text(s, v, 1.55, 3.55 + i * 0.85, 10.5, 0.5, 22, C.white); });
  text(s, 'Codex écrit le code. Vous décidez, vous contrôlez, vous expliquez.', 0.8, 6.45, 11.5, 0.45, 20, C.orange, true);
};
// Full-width visual (diagram or capture): crop window from slides.json, width as large as the height allows.
const VIS_TOP = 1.5, VIS_BOTTOM = 6.95;
function visual(s, d, file, maxH, minW) {
  const [pw, ph] = pngSize(file), crop = d.crop || [0, 0, pw, ph];
  const cw = crop[2] - crop[0], ch = crop[3] - crop[1];
  const w = Math.min(CW, maxH * cw / ch), h = w * ch / cw, scale = w / cw, x = X0 + (CW - w) / 2;
  if (w < minW) throw new Error(`Visuel trop étroit (${(w / W * 100).toFixed(0)} % de la largeur) : ${d.id}`);
  rect(s, x - 0.06, VIS_TOP - 0.06, w + 0.12, h + 0.12, C.white, C.line, 0.06);
  addCropped(s, file, crop, x, VIS_TOP, scale, d.alt || d.caption || d.title);
  manifest.push({ slide: slideNo, image: d.image, crop, x, y: VIS_TOP, w, h, widthShare: +(w / W).toFixed(3) });
  return { x, y: VIS_TOP, w, h };
}
L.picture = (s, d) => {
  visualHeader(s, d, 'SCHÉMA · pas une capture', C.pale, C.navy);
  const file = need(d.image), rowH = 1.05, lineH = 0.5;
  const below = d.items ? rowH + 0.2 : (d.takeaway ? lineH + 0.15 : 0);
  const box = visual(s, d, file, VIS_BOTTOM - VIS_TOP - below, 0.85 * W);
  const y = box.y + box.h + 0.25;
  if (d.items) itemRow(s, d.items, y, Math.min(rowH, VIS_BOTTOM - y));
  else if (d.takeaway) text(s, d.takeaway, X0, y - 0.05, CW, lineH, 17, C.navy, true, { align: 'center' });
};
L.capture = (s, d) => {
  visualHeader(s, d, 'CAPTURE RÉELLE · macOS', C.orange, C.deep);
  const file = need(d.image), capH = 0.42, rowH = 1.0;
  const below = capH + 0.12 + (d.items ? rowH + 0.15 : 0);
  const box = visual(s, d, file, VIS_BOTTOM - VIS_TOP - below, 0.80 * W);
  text(s, d.caption, X0, box.y + box.h + 0.12, CW, capH, 14, C.muted, false, { italic: true, align: 'center' });
  if (d.items) itemRow(s, d.items, box.y + box.h + 0.12 + capH + 0.15, rowH);
};
L.cards = (s, d) => {
  header(s, d);
  const n = d.items.length, gap = 0.3, w = (CW - gap * (n - 1)) / n, h = d.note ? 3.75 : 4.4, y = 2.0;
  d.items.forEach((it, i) => {
    const x = X0 + i * (w + gap);
    rect(s, x, y, w, h, C.pale);
    circle(s, String(i + 1), x + 0.25, y + 0.28, 0.5, C.navy, 17);
    text(s, it.label, x + 0.25, y + 0.95, w - 0.5, 0.75, n > 3 ? 19 : 22, C.navy, true, { valign: 'top' });
    text(s, it.text, x + 0.25, y + 1.75, w - 0.5, h - 1.95, n > 3 ? 16 : 18, C.ink, false, { valign: 'top' });
  });
  if (d.note) note(s, d.note);
};
L.process = (s, d) => {
  header(s, d);
  const n = d.items.length, gap = 0.5, w = (CW - gap * (n - 1)) / n, h = d.note ? 3.4 : 4.0, y = 2.15;
  const fs1 = n >= 5 ? 17 : 19, fs2 = n >= 5 ? 15 : 17;
  d.items.forEach((it, i) => {
    const x = X0 + i * (w + gap), last = i === n - 1;
    rect(s, x, y, w, h, last ? C.navy : C.pale);
    circle(s, String(i + 1), x + 0.22, y + 0.25, 0.46, last ? C.orange : C.navy, 15, last ? C.deep : C.white);
    text(s, it.label, x + 0.22, y + 0.88, w - 0.44, 0.9, fs1, last ? C.white : C.navy, true, { valign: 'top' });
    text(s, it.text, x + 0.22, y + 1.8, w - 0.44, h - 1.95, fs2, last ? C.white : C.ink, false, { valign: 'top' });
    if (!last) arrow(s, x + w + 0.07, y + h / 2, x + w + gap - 0.07, y + h / 2);
  });
  if (d.note) note(s, d.note);
};
L.table = (s, d) => {
  header(s, d);
  const fsz = d.fontSize || 16, tw = d.widths.reduce((a, b) => a + b, 0);
  const colW = d.widths.map(v => CW * v / tw);
  const avail = (d.note ? 5.95 : 6.75) - 1.85, rowH = Math.min(0.78, avail / (d.rows.length + 1));
  const rows = [d.headers.map(h => ({ text: h, options: { bold: true, color: C.white, fill: { color: C.navy } } }))];
  d.rows.forEach((r, i) => rows.push(r.map((v, j) => ({ text: String(v), options: { color: j === 0 ? C.navy : C.ink, bold: j === 0, fill: { color: i % 2 ? C.white : C.pale } } }))));
  s.addTable(rows, { x: X0, y: 1.85, w: CW, colW, rowH, fontFace: 'Arial', fontSize: fsz, valign: 'middle', margin: [0.03, 0.1, 0.03, 0.1], border: { type: 'solid', color: C.line, pt: 0.75 } });
  manifest.push({ slide: slideNo, table: d.headers.join(' | '), rows: d.rows.length, rowH, size: fsz });
  if (d.note) note(s, d.note);
};
L.kpis = (s, d) => {
  header(s, d);
  const n = d.items.length, gap = 0.3, w = (CW - gap * (n - 1)) / n, y = 2.05, h = d.note ? 3.7 : 4.3;
  d.items.forEach((v, i) => {
    const x = X0 + i * (w + gap), hi = i === (d.highlight ?? 1);
    rect(s, x, y, w, h, hi ? C.navy : C.pale);
    const vs = v.value.length > 9 ? 30 : (v.value.length > 6 ? 36 : 44);
    text(s, v.value, x + 0.2, y + 0.45, w - 0.4, 1.1, vs, hi ? C.white : C.navy, true, { align: 'center' });
    text(s, v.label, x + 0.2, y + 1.8, w - 0.4, h - 2.0, 17, hi ? C.white : C.ink, false, { align: 'center', valign: 'top' });
  });
  if (d.note) note(s, d.note);
};
L.mail = (s, d) => {
  header(s, d);
  rect(s, X0, 1.85, 9.1, 4.85, C.pale, C.line, 0.08);
  [['De', d.sender], ['À', d.to], ['Objet', d.subject]].forEach((r, i) => {
    text(s, r[0], X0 + 0.3, 2.0 + i * 0.42, 0.9, 0.36, 14, C.muted, true);
    text(s, r[1], X0 + 1.2, 2.0 + i * 0.42, 7.6, 0.36, 15, C.ink, i === 2);
  });
  s.addShape(ST.line, { x: X0 + 0.3, y: 3.35, w: 8.5, h: 0, line: { color: C.line, width: 1 } });
  text(s, d.body, X0 + 0.3, 3.5, 8.5, 3.0, 21, C.navy, false, { valign: 'top', paraSpaceAfter: 8 });
  rect(s, 10.05, 1.85, X1 - 10.05, 4.85, C.deep);
  text(s, 'À NOTER', 10.3, 2.1, 2.2, 0.35, 14, C.orange, true, { charSpacing: 1 });
  text(s, d.aside, 10.3, 2.6, X1 - 10.55, 2.3, 20, C.white, true, { valign: 'top' });
  text(s, 'Personnages et entreprise fictifs.', 10.3, 5.85, X1 - 10.55, 0.6, 14, C.white, false, { valign: 'top' });
};
L.statement = (s, d) => {
  header(s, d);
  const dark = d.danger;
  const sy = d.chips ? 1.95 : 2.55;
  rect(s, X0, sy, CW, 2.75, dark ? C.redPale : C.pale, dark ? C.red : C.pale);
  text(s, d.big, X0 + 0.5, sy + 0.15, CW - 1.0, 1.75, dark ? 28 : 32, dark ? C.red : C.navy, true, { fontFace: dark ? 'Courier New' : 'Arial', align: 'center' });
  text(s, d.sub, X0 + 0.5, sy + 1.9, CW - 1.0, 0.7, 20, C.ink, false, { align: 'center' });
  if (d.chips) {
    const gap = 0.25, w = (CW - gap * (d.chips.length - 1)) / d.chips.length;
    d.chips.forEach((c, i) => { rect(s, X0 + i * (w + gap), 5.15, w, 0.95, C.navy); text(s, c, X0 + i * (w + gap) + 0.15, 5.15, w - 0.3, 0.95, 17, C.white, true, { align: 'center' }); });
  }
};
L.compare = (s, d) => {
  header(s, d);
  const h = d.note ? 3.85 : 4.6, w = 5.65, y = 1.95, xr = X1 - w;
  const lf = d.neutral ? C.pale : C.redPale, lc = d.neutral ? C.navy : C.red;
  rect(s, X0, y, w, h, lf); rect(s, xr, y, w, h, C.navy);
  text(s, d.leftLabel, X0 + 0.3, y + 0.25, w - 0.6, 0.4, 14, lc, true, { charSpacing: 1 });
  text(s, d.left, X0 + 0.3, y + 0.85, w - 0.6, h - 1.1, 20, C.ink, false, { valign: 'top', paraSpaceAfter: 6 });
  text(s, d.rightLabel, xr + 0.3, y + 0.25, w - 0.6, 0.4, 14, C.orange, true, { charSpacing: 1 });
  text(s, d.right, xr + 0.3, y + 0.85, w - 0.6, h - 1.1, 20, C.white, false, { valign: 'top', paraSpaceAfter: 6 });
  circle(s, d.arrow || '→', X0 + w + (xr - X0 - w) / 2 - 0.3, y + h / 2 - 0.3, 0.6, C.orange, 20, C.deep);
  if (d.note) note(s, d.note);
};
L.code = (s, d) => {
  header(s, d);
  text(s, d.caption, X0, 1.75, 7.6, 0.34, 14, C.muted, true);
  rect(s, X0, 2.15, 7.6, 3.75, C.deep, C.deep, 0.08);
  text(s, d.code, X0 + 0.3, 2.35, 7.0, 3.35, 19, C.white, false, { fontFace: 'Courier New', valign: 'top' });
  sideItems(s, d.items, 8.7, 2.25, X1 - 8.7, 17);
  if (d.note) note(s, d.note);
};
L.grid = (s, d) => {
  header(s, d);
  const cols = d.cols, rowsN = Math.ceil(d.items.length / cols), gap = 0.22;
  const top = 1.9, bottom = d.note ? 5.95 : 6.8, h = (bottom - top - gap * (rowsN - 1)) / rowsN, w = (CW - gap * (cols - 1)) / cols;
  const small = h < 1.6;
  d.items.forEach((it, i) => {
    const x = X0 + (i % cols) * (w + gap), y = top + Math.floor(i / cols) * (h + gap);
    rect(s, x, y, w, h, C.pale);
    circle(s, it.num, x + 0.18, y + 0.18, small ? 0.42 : 0.5, C.navy, small ? 14 : 16);
    text(s, it.label, x + (small ? 0.72 : 0.82), y + 0.16, w - (small ? 0.85 : 0.98), small ? 0.46 : 0.55, cols >= 5 ? 15 : (small ? 16 : 18), C.navy, true);
    text(s, it.text, x + 0.2, y + (small ? 0.72 : 0.9), w - 0.4, h - (small ? 0.8 : 1.0) - (it.tag ? 0.4 : 0), small ? 14 : 16, C.ink, false, { valign: 'top' });
    if (it.tag) pill(s, it.tag, x + 0.2, y + h - 0.52, C.orange, C.deep, Math.min(w - 0.4, pillW(it.tag)));
  });
  if (d.note) note(s, d.note);
};
L.effort = (s, d) => {
  header(s, d);
  const n = d.levels.length, gap = 0.3, w = (CW - gap * (n - 1)) / n, base = 5.3;
  d.levels.forEach((lv, i) => {
    const h = 1.2 + i * 0.62, x = X0 + i * (w + gap), on = i === d.start;
    rect(s, x, base - h, w, h, on ? C.orange : (i > d.start ? C.navy : C.pale), on ? C.orange : undefined, 0.08);
    text(s, lv, x + 0.15, base - h + 0.15, w - 0.3, 0.6, 24, on ? C.deep : (i > d.start ? C.white : C.navy), true, { align: 'center' });
    text(s, d.captions[i], x, base + 0.12, w, 0.45, 16, C.ink, on, { align: 'center' });
  });
  const x = X0 + d.start * (w + gap);
  pill(s, 'COMMENCER ICI', x + (w - 1.8) / 2, base - (1.2 + d.start * 0.62) - 0.5, C.deep, C.white, 1.8);
  text(s, 'GPT-6 Luna · Standard = vitesse, réglée par l\'offre', X0, 1.85, 7, 0.4, 15, C.muted, true);
  if (d.note) note(s, d.note);
};
L.grain = (s, d) => {
  header(s, d);
  text(s, 'UNE LIGNE DE fact_vente', X0, 1.9, CW, 0.45, 18, C.muted, true, { charSpacing: 1 });
  const n = d.tiles.length, gap = 0.3, w = (CW - gap * (n - 1)) / n;
  d.tiles.forEach((t, i) => { const x = X0 + i * (w + gap); rect(s, x, 2.5, w, 2.1, i === 3 ? C.navy : C.pale);
    text(s, t[0], x + 0.25, 2.7, w - 0.5, 0.4, 16, i === 3 ? C.orange : C.muted, true);
    text(s, t[1], x + 0.25, 3.3, w - 0.5, 0.9, t[1].length > 11 ? 22 : 28, i === 3 ? C.white : C.navy, true); });
  circle(s, 'ID', X0, 5.0, 0.6, C.orange, 16, C.deep);
  text(s, d.idline, X0 + 0.85, 5.0, CW - 0.85, 0.6, 21, C.ink, true);
};
L.loads = (s, d) => {
  header(s, d);
  const gap = 0.55, w = (CW - 2 * gap) / 3, y = 1.95, h = 3.65;
  d.panels.forEach((p, i) => {
    const x = X0 + i * (w + gap), dark = i === 1;
    rect(s, x, y, w, h, dark ? C.deep : (i === 2 ? C.white : C.pale), i === 2 ? C.navy : undefined);
    text(s, p.label, x + 0.3, y + 0.2, w - 0.6, 0.5, 20, dark ? C.white : C.navy, true);
    pill(s, p.tag, x + 0.3, y + 0.8, C.orange, C.deep);
    p.lines.forEach((l, j) => text(s, l, x + 0.3, y + 1.35 + j * 0.48, w - 0.6, 0.42, 17, dark ? C.white : C.ink));
    s.addShape(ST.line, { x: x + 0.3, y: y + 2.85, w: w - 0.6, h: 0, line: { color: C.orange, width: 1.5 } });
    text(s, p.total, x + 0.3, y + 2.97, w - 0.6, 0.5, 20, dark ? C.white : C.navy, true);
    if (i < 2) arrow(s, x + w + 0.08, y + h / 2, x + w + gap - 0.08, y + h / 2, C.navy);
  });
  text(s, d.formula, X0, 5.8, CW, 0.5, 20, C.navy, true, { align: 'center' });
  text(s, 'Compteurs = référence du générateur, pas des valeurs inventées.', X0, 6.35, CW, 0.4, 14, C.muted, false, { align: 'center' });
};
L.chart = (s, d) => {
  header(s, d);
  text(s, d.period, X0, 1.75, 8.6, 0.4, 15, C.muted);
  // Values stay in millimes (the warehouse unit); the label format prints them as TND
  // with a space and a comma whatever the viewer's locale: 40887210 -> "40 887,210".
  s.addChart(pptx.ChartType.bar, [{ name: 'Ventes nettes (millimes, affichées en TND)', labels: d.labels, values: d.millimes }], {
    x: X0, y: 2.2, w: 8.4, h: 4.5, barDir: 'bar', lang: 'fr-FR',
    catAxisLabelFontFace: 'Arial', catAxisLabelFontSize: 16, catAxisLabelColor: C.ink, catAxisOrientation: 'maxMin',
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 52000000, valAxisMajorUnit: 10000000,
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#\\ ###\\,###', dataLabelColor: C.navy, dataLabelFontSize: 15, dataLabelFontBold: true,
    showLegend: false, showTitle: false, chartColors: [C.navy], valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, barGapWidthPct: 55,
  });
  rect(s, 9.35, 2.2, X1 - 9.35, 4.5, C.pale);
  text(s, 'À RETENIR', 9.6, 2.4, 3, 0.35, 14, C.orange, true, { charSpacing: 1 });
  text(s, d.insight, 9.6, 2.85, X1 - 9.85, 0.9, 20, C.navy, true, { valign: 'top' });
  text(s, d.explanation, 9.6, 3.85, X1 - 9.85, 1.5, 16, C.ink, false, { valign: 'top' });
  text(s, 'Total : ' + d.total, 9.6, 5.6, X1 - 9.85, 0.8, 15, C.navy, true, { valign: 'top' });
};
L.session = (s, d) => {
  header(s, d);
  const total = d.segments.reduce((a, g) => a + g[1], 0);
  if (total !== 240) throw new Error('Séance ≠ 240 min : ' + d.title);
  const col = { e: C.navy, p: C.orange, m: C.mid, z: 'C9CDD8' }, tc = { e: C.white, p: C.deep, m: C.white, z: C.ink };
  let x = X0; const y = 1.85, h = 0.55;
  d.segments.forEach(g => { const w = CW * g[1] / 240; s.addShape(ST.rect, { x, y, w, h, fill: { color: col[g[2]] }, line: { color: C.white, width: 1.5 } });
    if (w > 0.5) text(s, String(g[1]), x, y, w, h, 14, tc[g[2]], true, { align: 'center' }); x += w; });
  const leg = [['e', 'explication'], ['m', 'explication + pratique'], ['p', 'pratique'], ['z', 'pause']];
  const lx = [0, 1.55, 4.1, 5.45];
  leg.forEach((l, i) => { s.addShape(ST.rect, { x: X0 + lx[i], y: 2.56, w: 0.22, h: 0.22, fill: { color: col[l[0]] }, line: { color: col[l[0]] } }); text(s, l[1], X0 + lx[i] + 0.3, 2.5, 2.4, 0.34, 14, C.muted); });
  text(s, d.split || '66 min d\'explications · 154 min de pratique · 2 pauses', X0 + 6.5, 2.5, CW - 6.5, 0.34, 14, C.navy, true, { align: 'right' });
  const per = Math.ceil(d.segments.length / 2), rowH = Math.min(0.56, 3.55 / per);
  d.segments.forEach((g, i) => { const cx = X0 + Math.floor(i / per) * 3.85, cy = 3.15 + (i % per) * rowH;
    s.addShape(ST.rect, { x: cx, y: cy + 0.1, w: 0.18, h: rowH - 0.2, fill: { color: col[g[2]] }, line: { color: col[g[2]] } });
    text(s, g[1] + ' min', cx + 0.3, cy, 0.9, rowH, 14, C.navy, true);
    text(s, g[0], cx + 1.2, cy, 2.55, rowH, 14, C.ink); });
  rect(s, 8.55, 3.1, X1 - 8.55, 3.65, C.deep);
  text(s, 'CE QUE VOUS PROUVEZ', 8.8, 3.3, 3.5, 0.35, 14, C.orange, true, { charSpacing: 1 });
  d.prove.forEach((p, i) => { circle(s, '✓', 8.8, 3.85 + i * 0.95, 0.36, C.orange, 14, C.deep); text(s, p, 9.3, 3.8 + i * 0.95, X1 - 9.5, 0.85, 16, C.white, false, { valign: 'top' }); });
};
L.sources = (s, d) => {
  header(s, d);
  // Titles only on the slide (each one is a link); full addresses are in the speaker notes.
  const per = Math.ceil(d.links.length / 2), w = (CW - 0.4) / 2, rowH = Math.min(0.95, 4.95 / per);
  d.links.forEach((l, i) => { const x = X0 + Math.floor(i / per) * (w + 0.4), y = 1.85 + (i % per) * rowH;
    rect(s, x, y, w, rowH - 0.12, i % 2 ? C.white : C.pale, C.line, 0.06);
    text(s, [{ text: l[0], options: { hyperlink: { url: l[1], tooltip: l[1] } } }], x + 0.25, y + 0.06, w - 0.5, 0.42, 18, C.navy, true);
    text(s, new URL(l[1]).host, x + 0.25, y + 0.44, w - 0.5, rowH - 0.6, 14, C.muted, false); });
  text(s, 'Adresses complètes dans les notes du présentateur et dans docs/setup/sources.json.', X0, 6.62, CW, 0.3, 14, C.muted, false, { italic: true });
};

// ---------- build ----------
fs.mkdirSync(OUT_DIR, { recursive: true });
spec.slides.forEach((d) => {
  if (!L[d.layout]) throw new Error('Mise en page inconnue : ' + d.layout);
  if (!d.notes) throw new Error('Notes manquantes : ' + d.id);
  slideNo += 1;
  const s = pptx.addSlide(['cover', 'divider', 'closing'].includes(d.layout) ? undefined : { masterName: 'SOLEN' });
  L[d.layout](s, d);
  s.addNotes(d.notes);
});
fs.writeFileSync(path.join(BASE, 'layout_manifest.json'), JSON.stringify(manifest, null, 1) + '\n');
const outFile = path.join(OUT_DIR, 'Solen_CODEX_BI_22h.pptx');
pptx.writeFile({ fileName: outFile }).then(() => console.log(`${spec.slides.length} diapositives → ${path.relative(path.resolve(BASE, '../..'), outFile)}`));
