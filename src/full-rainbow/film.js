// "A rainbow is a full circle" — Impasto palette-knife short, 1080x1920.
import { Impasto, Strokes, KNIFE, DAB, hex } from './engine/impasto.js';
import { Ref, paintRef, strokePath } from './engine/plate.js';
import { P, E as EL, lin, rad, lerp, clamp, ss, seg } from './common.js';

const W = 1080, H = 1920, DUR = 17;
const HZ = 1180, CA = [540, HZ], RA = 450;                     // meadow plate: horizon + rainbow centre/radius
const CB = [540, 1260], RB = 400;                              // above-the-clouds plate
const BANDS = ['#e2453c', '#f08a33', '#f4cf4b', '#6cbd5c', '#4f86d4', '#7656b4'];
const T = { aIn: 0, title1: 1.6, cross: 6.6, ringIn: 8.0, ringDur: 2.6, title2: 11.0, back: 15.1 };

function rainbow(st, c, r, a0, a1, appFn) {
  BANDS.forEach((col, i) => {
    const rr = r - i * 24, pts = [];
    for (let k = 0; k <= 160; k++) { const a = lerp(a0, a1, k / 160); pts.push([c[0] + Math.cos(a) * rr, c[1] + Math.sin(a) * rr]); }
    const n0 = st.n; strokePath(st, pts, { wid: 26, c: hex(col), type: KNIFE, step: 9 });
    for (let j = n0; j < st.n; j++) st.a[j * 20 + 15] = .82;
    if (appFn) for (let j = n0; j < st.n; j++) { const b = st.a, o = j * 20; const ang = Math.atan2(b[o + 1] - c[1], b[o] - c[0]); b[o + 14] = appFn(ang); }
  });
}

function buildMeadow() {
  const R = new Ref(W, H, 1);
  R.fill(P([[0, 0], [W, 0], [W, HZ + 30], [0, HZ + 30]]), lin(0, 0, 0, HZ, [[0, '#2f4f86'], [.4, '#5f78ab'], [.75, '#d9a07e'], [1, '#f6d7a0']]), { dir: -8, fallback: -8, group: 'sky', maxR: 46, jit: .07, detail: 2.2, aj: .3 });
  const cloud = (x, y, w, h, col, und) => R.fill(c => { c.ellipse(x, y, w, h, 0, 0, 7); c.ellipse(x - w * .55, y + h * .25, w * .6, h * .7, 0, 0, 7); c.ellipse(x + w * .6, y + h * .3, w * .55, h * .6, 0, 0, 7); }, lin(0, y - h, 0, y + h, [[0, col], [.7, col], [1, und]]), { dir: -4, fallback: -4, group: 'sky', maxR: 30, detail: 1.6, aj: .3 });
  cloud(200, 760, 260, 70, '#565a80', '#c9887a'); cloud(900, 690, 300, 80, '#4e5280', '#cf8c7c'); cloud(620, 900, 220, 40, '#8e7f9c', '#efb282');
  R.fill(P([[0, HZ - 10], [W, HZ - 25], [W, HZ + 60], [0, HZ + 60]]), '#4c6a4a', { dir: 0, group: 'hills', maxR: 14 });
  [[120, 60], [260, 40], [820, 70], [960, 50]].forEach(([x, h], i) => R.fill(EL(x, HZ - h * .6, h * .55, h * .75), '#2f4a36', { dir: 90, maxR: 8, group: 'tree' + i }));
  const gcol = lin(0, HZ, 0, H, [[0, '#9aa35a'], [.25, '#b8a04c'], [.6, '#8a6e36'], [1, '#5a4528']]);
  [[HZ + 40, HZ + 160, 10], [HZ + 160, HZ + 360, 18], [HZ + 360, H, 30]].forEach(([y0, y1, r]) => R.fill(P([[0, y0], [W, y0], [W, y1], [0, y1]]), gcol, { dir: 0, fallback: 0, group: 'ground', maxR: r, aj: .3, jit: .09 }));
  // a wet path that mirrors the bright horizon
  { const c0 = R.ctx; c0.save(); c0.filter = 'blur(30px)'; c0.globalCompositeOperation = 'source-atop'; c0.beginPath(); P([[500, HZ + 50], [580, HZ + 50], [820, H + 40], [260, H + 40]])(c0); c0.fillStyle = 'rgba(250,214,160,.55)'; c0.fill(); c0.restore(); }
  const st = paintRef(R, { R: [46, 23, 11, 5.5, 3], T: 13, seed: 3, app: (x, y, lv) => (1 - y / H) * 0 + (y / H) * .9 + lv * .05 });
  rainbow(st, CA, RA, Math.PI, 2 * Math.PI, a => 1.0 + ((a + Math.PI * 2) % (Math.PI * 2) - Math.PI) / Math.PI * .5);
  return { st, R };
}

function buildClouds() {
  const R = new Ref(W, H, 1);
  R.fill(P([[0, 0], [W, 0], [W, 1000], [0, 1000]]), lin(0, 0, 0, 1000, [[0, '#1f3570'], [.55, '#4f73b4'], [1, '#bcd2ea']]), { dir: -6, fallback: -6, group: 'sky', maxR: 46, jit: .07, detail: 2.2 });
  R.fill(P([[0, 960], [W, 940], [W, H], [0, H]]), lin(0, 940, 0, H, [[0, '#f4ead8'], [.4, '#e9d6cf'], [1, '#b8a6c4']]), { dir: 0, group: 'sea', maxR: 34, jit: .1, aj: .35 });
  for (let row = 0; row < 7; row++) {                      // rows of cloud heaps, smaller toward the horizon
    const y = 990 + row * row * 22 + row * 40, s = .45 + row * .2;
    for (let i = -1; i < 9; i++) { const x = i * 150 * s + (row % 2) * 70 * s; 
      R.fill(c => { c.ellipse(x, y, 90 * s, 40 * s, 0, 0, 7); c.ellipse(x + 50 * s, y - 22 * s, 60 * s, 34 * s, 0, 0, 7); }, lin(0, y - 60 * s, 0, y + 40 * s, [[0, '#fff8ec'], [.6, '#f1e2dc'], [1, '#c4b2cc']]), { dir: 0, group: 'heap' + row + (i & 1), maxR: 12 + row * 3, aj: .3 }); } }
  R.fill(EL(CB[0], CB[1], 26, 16), 'rgba(70,60,90,.85)', { dir: 0, group: 'shadow', maxR: 4 });
  const st = paintRef(R, { R: [46, 23, 11, 5.5, 3], T: 13, seed: 5, app: (x, y, lv) => (x / W) * .8 + lv * .05 });
  // full ring: top half lands first, the bottom half is knifed in afterwards (clockwise from the left)
  rainbow(st, CB, RB, -Math.PI, Math.PI, a => ((a + Math.PI) / (2 * Math.PI)) * T.ringDur);
  return { st, R };
}

function buildTitle(text, size, col) {
  const R = new Ref(1000, 220, 1);
  R.text(text, 500, 150, `italic 700 ${size}px Georgia, serif`, col, { dir: 0, maxR: 6, group: 'title' });
  const st = paintRef(R, { R: [12, 6, 3], T: 10, seed: 9, app: (x, y, lv) => x / 1000 * .9 + lv * .02 });
  return { st, R };
}

let E, A, B, T1, T2;
const up = (b, w, h) => ({ b: E.batch(b.st.data()), tex: E.texture(b.R.ctx.canvas), w, h });
function plate(pl, o) { E.under(pl.tex, pl.w, pl.h, { ...o, appear: undefined }); E.draw(pl.b, o); }

E = new Impasto(document.getElementById('c'), { W, H, ss: +(new URLSearchParams(location.search).get('ss') || 1) });
A = up(buildMeadow(), W, H); B = up(buildClouds(), W, H);
T1 = up(buildTitle('Half a circle?', 118, '#fbf1dc'), 1000, 220); T2 = up(buildTitle("It's a full circle.", 104, '#fbf1dc'), 1000, 220);

const POST = { expo: 1.03, sat: 1.06, contrast: 1.05, vig: .28, spec: .28, shin: 26 };
window.render = t => {
  E.begin();
  const inB = t >= T.cross && t < T.back + .6;
  if (!inB) {
    const tA = t >= T.back ? t - T.back : t;                 // plate A again for the loop
    const cam = { x: 540, y: lerp(1000, 940, ss(tA / 6)), zoom: lerp(1.10, 1.02, ss(tA / 6)) };
    plate(A, { t: tA, cam, appear: 0, appDur: .14, grey: 0 });
  } else {
    const tb = t - T.cross;
    const cam = { x: 540, y: lerp(990, 960, ss(tb / 8)), zoom: lerp(1.04, 1.09, ss(tb / 8)) };
    plate(B, { t: tb, cam, appear: 0, appDur: .14, grey: 0 });
    // ring strokes keep their own later timing via per-stroke app (offset by ringIn)
  }
  // titles laid in with the knife, then scraped off by the next sweep
  const M1 = [1, 0, 0, 1, 40, 300], cam0 = { x: W / 2, y: H / 2, zoom: 1 };
  if (t > T.title1 && t < T.cross) E.draw(T1.b, { t: t - T.title1, M: M1, cam: cam0, appear: 0, appDur: .12, grey: 0 });
  if (t > T.title2 && t < T.back) E.draw(T2.b, { t: t - T.title2, M: M1, cam: cam0, appear: 0, appDur: .12, grey: 0 });
  E.finish(POST);
};
window.DUR = DUR;
window.EV = [{ t: 0, type: 'sweep', d: 1.2 }, { t: T.title1, type: 'title' }, { t: T.cross, type: 'sweep', d: 1.0 },
  { t: T.cross + 1.4, type: 'ring', d: T.ringDur }, { t: T.title2, type: 'title' }, { t: T.back, type: 'sweep', d: 1.2 }];
window.TEXTS = t => (t > T.title1 + .9 && t < T.cross) ? [{ id: 't1', text: 'Half a circle?', x0: 120, y0: 330, x1: 960, y1: 500 }]
  : (t > T.title2 + .9 && t < T.back) ? [{ id: 't2', text: "It's a full circle.", x0: 120, y0: 330, x1: 960, y1: 500 }] : [];
await document.querySelector('#brand img').decode();
window.render(0); window.READY = true;
