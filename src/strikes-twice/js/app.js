// Chalkboard short (1080x1920): "Lightning never strikes twice?" -> wipe -> "~23 times a year" (Empire State Building, NOAA).
import { clamp, lerp } from '/core/lib.js';
import { bake, drawStroke, poly, line, zigzag } from './chalk.js';
import { installDeposit } from './r2d.js';
import { loadSvgFont, writeLatin, latinWidth } from './hand.js';
import { bakeSlate } from './stage.js';

const W = innerWidth, H = innerHeight, cv = document.getElementById('c'); cv.width = W; cv.height = H;
const ctx = cv.getContext('2d');
await loadSvgFont('fonts/Hershey.svg');
installDeposit();
const LOGO = new Image(); LOGO.src = 'logo.png'; await LOGO.decode();
const DUR = 18, EV = [], S = [];
const add = (list, group, ev = true) => { for (const s of list) { s.group = group; S.push(s); if (ev) EV.push({ t: s.t0, type: 'chalk', d: s.t1 - s.t0, len: s.len }); } return list; };
const timed = (s, t0, d) => { s.t0 = t0; s.t1 = t0 + d; return s; };
const center = (txt, cap) => W / 2 - latinWidth(txt, cap) / 2;

// 1. the saying
let r = writeLatin('LIGHTNING', center('LIGHTNING', 110), 420, 110, 0.0, { lspeed: 55, seed: 3 }); add(r, 'keep');
r = writeLatin('NEVER STRIKES TWICE?', center('NEVER STRIKES TWICE?', 54), 545, 54, r.end + 0.05, { lspeed: 60, seed: 4 }); add(r, 'myth');
// 2. the building
const Lp = [[390,1250],[390,1060],[425,1060],[425,960],[455,960],[455,880],[485,880],[485,810],[510,810],[510,760],[528,760],[532,705],[540,640]];
const SC = ([x, y]) => [540 + (x - 540) * 1.35, 1520 + (y - 1250) * 1.35];
Lp.splice(0, Lp.length, ...Lp.map(SC));
const Rp = Lp.map(([x, y]) => [W - x, y]).reverse();
let t = 2.25;
const bld = [poly(Lp, { w: 6, wob: .8 }), poly(Rp, { w: 6, wob: .8 }), line(300, 1522, 780, 1522, { w: 6 })];
timed(bld[0], t, .55); timed(bld[1], t + .55, .55); timed(bld[2], t + 1.1, .3);
for (const [i, x] of [445, 492, 540, 588, 635].entries()) bld.push(timed(line(x, 1060, x, 1508, { w: 3.2, press: .8 }), t + 1.45 + i * .08, .12));
add(bld, 'keep');
r = writeLatin('EMPIRE STATE BUILDING', center('EMPIRE STATE BUILDING', 34), 1585, 34, 3.0, { lspeed: 120, seed: 6 }); add(r, 'keep');
// 3. strikes (accent) + tallies
const bolt = (x0, y0, x1, y1, t0, seed) => {
  const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = (x1 - x0), dy = (y1 - y0);
  const s = poly([[x0, y0], [lerp(x0, x1, .45) - 30, lerp(y0, y1, .35)], [lerp(x0, x1, .4) + 25, lerp(y0, y1, .55)], [x1, y1]], { w: 7, color: 'orange', wob: .3, seed });
  EV.push({ t: t0, type: 'bolt' }); return timed(s, t0, .16);
};
add([bolt(410, 600, 536, 690, 4.15, 11)], 'keep', false);
add([bolt(680, 605, 545, 690, 6.35, 12)], 'keep', false);
const TALLY = [];
const tallyAt = i => { const g = Math.floor(i / 5), k = i % 5, gx = 310 + g * 100, y0 = 1625, y1 = 1700;
  return k < 4 ? line(gx + k * 20, y0, gx + k * 20 + 3, y1, { w: 5, color: 'orange' }) : line(gx - 12, y1 - 8, gx + 72, y0 + 8, { w: 5, color: 'orange' }); };
const tt = [4.4, 6.6]; for (let i = 2; i < 23; i++) tt.push(7.1 + 5.2 * Math.pow((i - 2) / 20, .8));
tt.forEach((t0, i) => { const s = timed(tallyAt(i), t0, .1); TALLY.push(s); EV.push({ t: t0, type: 'tick', n: i + 1 }); });
add(TALLY, 'keep', false);
// 4. the truth, written where the myth was wiped
const WIPE1 = { t0: 5.0, t1: 5.8, w: 120, path: [[100, 518], [W - 100, 512]] };
EV.push({ t: WIPE1.t0, type: 'wipe', d: WIPE1.t1 - WIPE1.t0 });
{ const a = 'HITS IT ~', b = '23', c = ' TIMES A YEAR', cap = 50, x = center(a + b + c, cap);
  let q = writeLatin(a, x, 545, cap, 12.7, { lspeed: 60, seed: 7 }); add(q, 'keep');
  let q2 = writeLatin(b, q.x, 545, cap, q.end, { lspeed: 50, seed: 8, color: 'orange' }); add(q2, 'keep');
  add(writeLatin(c, q2.x, 545, cap, q2.end, { lspeed: 60, seed: 9 }), 'keep'); }
// 5. clean board for the loop
const WIPE2 = { t0: 16.5, t1: 17.6, w: 330, path: [] };
for (let k = 0; k <= 7; k++) WIPE2.path.push([k % 2 ? W + 80 : -80, 150 + k * 250]);
EV.push({ t: WIPE2.t0, type: 'wipe', d: WIPE2.t1 - WIPE2.t0 });
for (const s of S) bake(s, 2);

const SLATE = bakeSlate(W, H, 61);
const LA = new OffscreenCanvas(W, H), la = LA.getContext('2d');
const LB = new OffscreenCanvas(W, H), lb = LB.getContext('2d');
function wipe(c, w, t) {
  if (t <= w.t0) return;
  const P = w.path, u = clamp((t - w.t0) / (w.t1 - w.t0)), segs = P.length - 1, f = u * segs, n = Math.floor(f);
  const p = new Path2D(); p.moveTo(...P[0]);
  for (let i = 1; i <= Math.min(n, segs); i++) p.lineTo(...P[i]);
  if (n < segs) p.lineTo(lerp(P[n][0], P[n + 1][0], f - n), lerp(P[n][1], P[n + 1][1], f - n));
  c.globalCompositeOperation = 'destination-out'; c.filter = 'blur(14px)'; c.lineCap = 'round'; c.lineJoin = 'round'; c.lineWidth = w.w; c.strokeStyle = '#000';
  c.stroke(p); c.filter = 'none'; c.globalCompositeOperation = 'source-over';
}
function brand(c) {
  c.save(); c.fillStyle = 'rgba(8,16,12,.55)'; c.beginPath(); c.roundRect(48, 70, 400, 96, 48); c.fill();
  c.beginPath(); c.arc(96, 118, 44, 0, 6.29); c.fillStyle = '#f2efe6'; c.fill();
  c.save(); c.beginPath(); c.arc(96, 118, 40, 0, 6.29); c.clip(); c.drawImage(LOGO, 56, 78, 80, 80); c.restore();
  c.font = '600 34px Inter, sans-serif'; c.fillStyle = 'rgba(242,239,230,.92)'; c.textBaseline = 'middle'; c.fillText('@Visual.Brainer', 156, 120); c.restore();
}
window.render = t => {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'source-over';
  ctx.drawImage(SLATE.cv, 0, 0, W, H);
  la.clearRect(0, 0, W, H); lb.clearRect(0, 0, W, H);
  for (const s of S) if (t > s.t0) drawStroke(s.group === 'myth' ? la : lb, s, t);
  wipe(la, WIPE1, t);
  if (t > WIPE1.t1) { la.clearRect(0, 0, W, H); la.globalAlpha = .03; for (const s of S) if (s.group === 'myth') drawStroke(la, s, t); la.globalAlpha = 1; }
  wipe(la, WIPE2, t); wipe(lb, WIPE2, t);
  ctx.drawImage(LA, 0, 0); ctx.drawImage(LB, 0, 0);
  const g = ctx.createRadialGradient(W / 2, H * .45, H * .25, W / 2, H * .5, H * .8);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.45)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  brand(ctx);
};
window.TEXTS = t => {
  const out = [];
  if (t > 0.3 && t < 16.5) out.push({ id: 'l1', text: 'LIGHTNING', x0: 300, y0: 300, x1: 900, y1: 425 });
  if (t > 1.0 && t < 5.0) out.push({ id: 'myth', text: 'NEVER STRIKES TWICE?', x0: 150, y0: 480, x1: 960, y1: 550 });
  if (t > 13.0 && t < 16.5) out.push({ id: 'truth', text: 'HITS IT ~23 TIMES A YEAR', x0: 120, y0: 480, x1: 980, y1: 550 });
  if (t > 3.2 && t < 16.5) out.push({ id: 'esb', text: 'EMPIRE STATE BUILDING', x0: 330, y0: 1550, x1: 790, y1: 1590, pass: true });
  return out;
};
window.DUR = DUR; window.EV = EV.sort((a, b) => a.t - b.t); window.READY = true;
