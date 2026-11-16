"""Look and feel: dyslexia-friendly CSS, and small browser components
(read-aloud with word highlighting, tap-to-reveal diagrams, Symbol Snap, quiz clock,
reading ruler).

Components use ``st.components.v2`` and run inline in the page (no iframe), so the
global CSS below applies to what they draw.
"""
from __future__ import annotations

import streamlit as st

# --------------------------------------------------------------------------- settings
FONTS = {
    "Lexend": "'Lexend', Verdana, Arial, sans-serif",
    "Atkinson Hyperlegible": "'Atkinson Hyperlegible', Verdana, Arial, sans-serif",
    "Verdana": "Verdana, Arial, sans-serif",
}
SPACING = {  # line-height, letter-spacing, word-spacing
    "Normal": (1.5, "0.01em", "0.04em"),
    "Roomy": (1.75, "0.03em", "0.12em"),
    "Extra roomy": (2.0, "0.05em", "0.2em"),
}
TINTS = {  # light mode backgrounds: (page, panel, line)
    "Cream": ("#f6f1e4", "#fffaf0", "#d9cfb8"),
    "Soft blue": ("#e4edf6", "#f3f7fc", "#c4d3e3"),
    "Soft green": ("#e6f0e1", "#f4faf1", "#c6d8bd"),
    "Peach": ("#f7e7db", "#fdf4ee", "#e2cbb9"),
    "Light grey": ("#eceef0", "#f8f9fa", "#d0d4d9"),
}
DEFAULT_SETTINGS = {"font": "Lexend", "size": 19, "spacing": "Roomy", "tint": "Cream",
                    "rate": 0.9, "ruler": False}


def is_dark() -> bool:
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def palette(settings: dict) -> dict:
    if is_dark():
        return dict(bg="#11161d", panel="#1a212b", ink="#eef1f5", muted="#a3adbb", line="#2c3644",
                    acc="#f5b700", acc_ink="#11161d", acc_soft="#3a3218", key="#f5b700",
                    good="#4cc275", good_soft="#173322", bad="#ff6b5e", bad_soft="#3a1c1a",
                    qv="#5aa7ff", qi="#ff6b75", qr="#ffaa3b", qp="#58d68d", qf="#b493ff", qk="#3dd6d0",
                    ruler="rgba(245,183,0,.14)")
    bg, panel, line = TINTS.get(settings.get("tint"), TINTS["Cream"])
    return dict(bg=bg, panel=panel, ink="#1d2430", muted="#4f5866", line=line,
                acc="#c98a00", acc_ink="#1d2430", acc_soft="#f4e2b4", key="#8a5500",
                good="#2f8a4c", good_soft="#d7eedc", bad="#c0392b", bad_soft="#f6d9d5",
                qv="#1f6fd1", qi="#c62f3a", qr="#b86a00", qp="#2f8a4c", qf="#7a4fc4", qk="#0f8a8a",
                ruler="rgba(201,138,0,.16)")


def inject_css(settings: dict) -> None:
    p = palette(settings)
    font = FONTS.get(settings.get("font"), FONTS["Lexend"])
    lh, ls, ws = SPACING.get(settings.get("spacing"), SPACING["Roomy"])
    size = int(settings.get("size", 19))
    vars_ = ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in p.items())
    st.html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Barlow+Condensed:wght@600;700&family=Lexend:wght@400;500;600;700&display=swap');
:root{{{vars_};--font:{font};--lh:{lh};--display:"Barlow Condensed","Arial Narrow",Arial,sans-serif}}
/* Text size: Streamlit sizes most things in rem, so scaling the root scales the whole app. */
html{{font-size:{size}px !important}}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="stBottom"]>div{{background:var(--bg) !important}}
.stApp,.stApp p,.stApp li,.stApp label,.stApp button,.stApp input,.stApp textarea,.stApp select,
.stApp [data-testid="stMarkdownContainer"],.stApp [data-baseweb]{{font-family:var(--font) !important}}
.stApp{{color:var(--ink);letter-spacing:{ls};word-spacing:{ws}}}
.stApp p,.stApp li,.stApp label,[data-testid="stMarkdownContainer"]{{line-height:var(--lh)}}
.stApp h1,.stApp h2,.stApp h3{{font-family:var(--display) !important;letter-spacing:.02em;line-height:1.15}}
/* No italics (harder to read), no justified text, keep lines short */
.stApp em,.stApp i{{font-style:normal;font-weight:600}}
.stApp p,.stApp li{{text-align:left;max-width:65ch}}
.block-container{{max-width:780px !important;padding-top:3.5rem !important;padding-bottom:5rem !important}}
@media (max-width:640px){{.block-container{{padding-left:16px !important;padding-right:16px !important}}}}
/* Big, clear buttons */
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{{min-height:52px;border-radius:12px;font-weight:600;
  padding:.5rem 1rem;border-width:2px;text-align:left;line-height:1.4;white-space:normal}}
.stButton>button p,.stFormSubmitButton>button p{{font-size:1rem;max-width:none}}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primaryFormSubmit"]{{background:var(--acc);border-color:var(--acc);color:var(--acc-ink)}}
.stButton>button[kind="primary"]:hover{{filter:brightness(1.06);color:var(--acc-ink)}}
[data-testid="stPageLink"] a{{min-height:52px;border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:.5rem .9rem}}
[data-testid="stPageLink"] a:hover{{border-color:var(--acc)}}
[data-testid="stPageLink"] p{{font-weight:600}}
input,textarea{{font-size:1.05rem !important}}
:focus-visible{{outline:3px solid var(--acc) !important;outline-offset:2px}}
@media (prefers-reduced-motion:reduce){{*{{transition:none !important;animation:none !important}}}}
/* ---- app blocks ---- */
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin:0 0 4px}}
.panel.focus{{border:2px solid var(--acc)}}
.muted{{color:var(--muted)}} .small{{font-size:.88rem}}
.row{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.chip{{display:inline-flex;align-items:center;gap:6px;padding:2px 12px;border-radius:999px;font-size:.82rem;border:1px solid var(--line);background:var(--bg);white-space:nowrap}}
.chip.t1{{border-color:var(--qv);color:var(--qv)}} .chip.t2{{border-color:var(--qp);color:var(--qp)}}
.chip.chk{{border-color:var(--acc);background:var(--acc-soft);color:var(--ink)}}
.qtext{{font-size:1.2rem;font-weight:500;line-height:var(--lh);max-width:60ch;margin:.4rem 0}}
.qtext b,.key{{color:var(--key);font-weight:700}}
.opt{{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:12px;border:2px solid var(--line);background:var(--panel);margin:0 0 10px;line-height:1.45}}
.opt .let{{flex:0 0 32px;height:32px;border-radius:8px;display:grid;place-items:center;background:var(--bg);border:1px solid var(--line);font-weight:700}}
.opt.right{{border-color:var(--good);background:var(--good-soft)}} .opt.wrong{{border-color:var(--bad);background:var(--bad-soft)}}
.opt.dim{{opacity:.55}}
.feedback{{border-left:6px solid var(--good);padding:12px 16px;border-radius:8px;background:var(--good-soft);margin:6px 0}}
.feedback.no{{border-color:var(--bad);background:var(--bad-soft)}}
.feedback .head{{font-family:var(--display);font-size:1.35rem;letter-spacing:.02em;display:block}}
.dots{{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 10px}}
.dots i{{width:14px;height:14px;border-radius:50%;background:var(--line)}}
.dots i.ok{{background:var(--good)}} .dots i.no{{background:var(--bad)}} .dots i.now{{background:var(--acc)}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}}
.stat{{text-align:center;padding:10px 6px;border-radius:12px;background:var(--bg);border:1px solid var(--line)}}
.stat b{{display:block;font-family:var(--display);font-size:1.9rem;line-height:1.1}}
.stat span{{font-size:.8rem;color:var(--muted)}}
.bar{{height:12px;border-radius:99px;background:var(--bg);border:1px solid var(--line);overflow:hidden;margin:8px 0}}
.bar>i{{display:block;height:100%;background:var(--acc);border-radius:99px}}
.big{{font-family:var(--display);font-size:3.2rem;line-height:1}}
.note{{border:2px dashed var(--acc);border-radius:10px;padding:10px 14px;font-size:.92rem;background:var(--acc-soft);margin:8px 0}}
.keypoints{{margin:.3rem 0;padding-left:1.3em}} .keypoints li{{margin:.35rem 0}} .keypoints li::marker{{color:var(--acc)}}
.ref{{font-size:.88rem;color:var(--muted)}}
.boxes{{display:flex;gap:6px;margin:6px 0}}
.boxes span{{flex:1;text-align:center;font-size:.78rem;padding:6px 2px;border-radius:8px;background:var(--bg);border:1px solid var(--line)}}
.boxes b{{display:block;font-family:var(--display);font-size:1.3rem}}
/* formula lab */
.q{{font-weight:700;font-style:normal}}
.q.v{{color:var(--qv)}} .q.i{{color:var(--qi)}} .q.r{{color:var(--qr)}} .q.p{{color:var(--qp)}} .q.f{{color:var(--qf)}} .q.k{{color:var(--qk)}}
.given{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin:8px 0}}
.gv{{padding:10px 12px;border-radius:10px;background:var(--bg);border:1px solid var(--line);border-left-width:6px}}
.gv.v{{border-left-color:var(--qv)}} .gv.i{{border-left-color:var(--qi)}} .gv.r{{border-left-color:var(--qr)}}
.gv.p{{border-left-color:var(--qp)}} .gv.f{{border-left-color:var(--qf)}} .gv.k{{border-left-color:var(--qk)}}
.gv small{{display:block;color:var(--muted);font-size:.75rem}}
.steps{{margin:0;padding-left:1.5em}} .steps li{{margin:.5rem 0;padding-left:4px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem}}
/* diagrams & symbols */
.dg{{width:100%;height:auto;display:block;background:var(--bg);border-radius:12px;border:1px solid var(--line)}}
.dg .s{{stroke:var(--ink);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.dg .a{{stroke:var(--acc);fill:none;stroke-width:2.5}}
.dg .fa{{fill:var(--acc)}} .dg .fi{{fill:var(--ink)}} .dg .fs{{fill:var(--acc-soft)}}
.dg .d{{stroke:var(--muted);stroke-width:1.5;fill:none;stroke-dasharray:4 4}}
.dg text{{fill:var(--ink);font-family:var(--font);font-size:12px;letter-spacing:0;word-spacing:0}}
.dg text.t{{font-weight:600}}
.dg .lab{{cursor:pointer}} .dg .cover{{display:none;fill:var(--acc)}}
.dg .qm{{display:none;fill:var(--acc-ink);font-weight:700;font-size:13px}}
.hidelabels .dg .lab:not(.shown) text:not(.qm){{opacity:0}}
.hidelabels .dg .lab:not(.shown) .cover,.hidelabels .dg .lab:not(.shown) .qm{{display:block}}
.sym{{width:100%;max-width:260px;margin:0 auto;display:block;color:var(--ink)}}
.sym *{{vector-effect:non-scaling-stroke}}
.symbox{{background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:16px;display:grid;place-items:center;min-height:120px}}
/* components */
.say{{border:2px solid var(--line);background:var(--panel);color:var(--ink);border-radius:10px;min-height:44px;padding:4px 14px;cursor:pointer;
  display:inline-flex;gap:8px;align-items:center;font:inherit;font-size:.9rem;font-weight:600}}
.say:hover{{border-color:var(--acc)}} .say.on{{background:var(--acc);border-color:var(--acc);color:var(--acc-ink)}}
.say svg{{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:2}}
.ra-body .w.hl{{background:var(--acc-soft);outline:2px solid var(--acc);border-radius:4px}}
.seg{{display:flex;border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:8px 0}}
.seg button{{flex:1;min-height:48px;border:0;background:var(--panel);color:var(--ink);cursor:pointer;padding:6px 10px;font:inherit;font-size:.92rem}}
.seg button.on{{background:var(--acc);color:var(--acc-ink);font-weight:700}}
.snap .opt{{width:100%;cursor:pointer;font:inherit;color:var(--ink);text-align:left;min-height:56px}}
.snap .opt:hover{{border-color:var(--acc)}}
.snap .top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}}
.timer{{font-family:var(--display);font-size:1.8rem;font-variant-numeric:tabular-nums}}
#sparky-ruler{{position:fixed;left:0;right:0;height:calc(var(--lh) * 1.25em);background:var(--ruler);pointer-events:none;z-index:999990;
  border-top:2px solid var(--acc);border-bottom:2px solid var(--acc);display:none}}
</style>""")


# --------------------------------------------------------------------------- HTML helpers
def html(s: str) -> None:
    st.html(s)


def chip(text: str, cls: str = "") -> str:
    return f'<span class="chip {cls}">{text}</span>'


def paper_chip(p: str) -> str:
    return chip(p, p.lower())


def dots(states: list[str]) -> str:
    return '<div class="dots">' + "".join(f'<i class="{s}"></i>' for s in states) + "</div>"


def feedback(head: str, body: str = "", ok: bool = True) -> str:
    return f'<div class="feedback {"" if ok else "no"}"><span class="head">{head}</span>{body}</div>'


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


# --------------------------------------------------------------------------- components
_SAY_ICON = ('<svg viewBox="0 0 24 24"><path d="M4 9v6h4l5 4V5L8 9z"/>'
             '<path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/></svg>')

_READ_JS = r"""
const CLEAN = [[/Ω/g,' ohms'],[/µF/g,' microfarads'],[/mm²/g,' square millimetres'],[/m²/g,' square metres'],
  [/²/g,' squared'],[/√3/g,'root 3'],[/√/g,'root '],[/π/g,'pi'],[/→/g,', '],[/≥/g,'at least '],[/≤/g,'no more than '],
  [/×/g,' times '],[/÷/g,' divided by '],[/±/g,' plus or minus '],[/η/g,'efficiency'],[/Φ/g,'flux'],[/τ/g,'tau'],[/·/g,', ']];
const clean = s => CLEAN.reduce((a,[r,t]) => a.replace(r,t), s);
function pickVoice(){
  const vs = window.speechSynthesis.getVoices();
  return vs.find(v=>/en-IE/i.test(v.lang)) || vs.find(v=>/en-GB/i.test(v.lang)) || vs.find(v=>/^en/i.test(v.lang));
}
function wrapWords(body){
  if (body.dataset.wrapped) return;
  const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
  const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const n of nodes) {
    if (n.parentElement && n.parentElement.closest('svg')) continue;
    const parts = n.textContent.split(/(\s+)/); const frag = document.createDocumentFragment();
    for (const p of parts) {
      if (!p) continue;
      if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); continue; }
      const s = document.createElement('span'); s.className = 'w'; s.textContent = p; frag.appendChild(s);
    }
    n.replaceWith(frag);
  }
  body.dataset.wrapped = '1';
}
export default function({ parentElement, data }) {
  const root = parentElement;
  root.innerHTML = '';
  const box = document.createElement('div'); box.className = 'ra ' + (data.cls || '');
  const body = document.createElement('div'); body.className = 'ra-body';
  body.innerHTML = data.html || '';
  const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'say';
  btn.setAttribute('aria-label', 'Read aloud');
  const label = data.label || 'Read aloud';
  btn.innerHTML = data.icon + '<span>' + label + '</span>';
  if (data.html) box.appendChild(body);
  box.appendChild(btn); root.appendChild(box);
  const stopAll = () => { try { speechSynthesis.cancel(); } catch(e){}
    document.querySelectorAll('.say.on').forEach(b => { b.classList.remove('on'); b.lastChild.textContent = b.dataset.label || 'Read aloud'; });
    document.querySelectorAll('.ra-body .w.hl').forEach(w => w.classList.remove('hl')); };
  btn.dataset.label = label;
  btn.onclick = () => {
    const synth = window.speechSynthesis;
    if (!synth) { btn.lastChild.textContent = 'Not supported in this browser'; return; }
    if (btn.classList.contains('on')) { stopAll(); return; }
    stopAll();
    let text = '', marks = [];
    if (data.html && !data.speak) {
      wrapWords(body);
      const words = [...body.querySelectorAll('.w')];
      for (const w of words) { marks.push([text.length, w]); text += clean(w.textContent) + ' '; }
    } else { text = clean(data.speak || body.textContent || ''); }
    const u = new SpeechSynthesisUtterance(text); u.rate = data.rate || 0.9;
    const v = pickVoice(); if (v) u.voice = v;
    let last = null;
    u.onboundary = e => {
      if (!marks.length || e.name === 'sentence') return;
      let m = null; for (const mk of marks) { if (mk[0] <= e.charIndex) m = mk[1]; else break; }
      if (last) last.classList.remove('hl'); if (m) { m.classList.add('hl'); last = m; }
    };
    u.onend = u.onerror = () => { if (last) last.classList.remove('hl'); btn.classList.remove('on'); btn.lastChild.textContent = label; };
    btn.classList.add('on'); btn.lastChild.textContent = 'Stop';
    synth.speak(u);
  };
}
"""
_read_aloud = st.components.v2.component("sparky_read_aloud", js=_READ_JS, isolate_styles=False)


def read_aloud(key: str, html_text: str = "", speak: str | None = None, cls: str = "",
               label: str = "Read aloud") -> None:
    """Show ``html_text`` with a read-aloud button that highlights each word as it is spoken.

    If ``speak`` is given, that text is read instead (without word highlighting).
    """
    rate = st.session_state.get("S", {}).get("settings", {}).get("rate", 0.9)
    _read_aloud(key=key, data={"html": html_text, "speak": speak, "cls": cls, "rate": rate,
                               "label": label, "icon": _SAY_ICON})


_RAW_JS = r"""
export default function({ parentElement, data }) {
  if (parentElement._html === data.html) return;
  parentElement._html = data.html;
  parentElement.innerHTML = data.html;
}
"""
_raw = st.components.v2.component("sparky_raw_html", js=_RAW_JS, isolate_styles=False)


def drawing(key: str, markup: str) -> None:
    """Show the app's own SVG drawings. ``st.html`` sanitises SVG away, so drawings
    go through this component instead. Only use with trusted, app-made markup."""
    _raw(key=key, data={"html": markup})


_DIAG_JS = r"""
function addCovers(svg){
  const ns = 'http://www.w3.org/2000/svg';
  svg.querySelectorAll('.lab').forEach(g => {
    if (g.querySelector('.cover')) return;
    const t = g.querySelector('text'); let bb; try { bb = t.getBBox(); } catch(e) { return; }
    if (!bb.width) return;
    const r = document.createElementNS(ns,'rect');
    r.setAttribute('x',bb.x-4); r.setAttribute('y',bb.y-2); r.setAttribute('width',bb.width+8); r.setAttribute('height',bb.height+4);
    r.setAttribute('class','cover'); r.setAttribute('rx','5');
    const q = document.createElementNS(ns,'text');
    q.setAttribute('x',bb.x+bb.width/2); q.setAttribute('y',bb.y+bb.height/2+4); q.setAttribute('text-anchor','middle');
    q.setAttribute('class','qm'); q.textContent='?';
    g.insertBefore(r,t); g.appendChild(q);
  });
}
export default function({ parentElement, data }) {
  const root = parentElement; root.innerHTML = '';
  const seg = document.createElement('div'); seg.className = 'seg';
  seg.innerHTML = '<button type="button" class="on" data-k="show">Show labels</button><button type="button" data-k="hide">Test me (hide labels)</button>';
  const wrap = document.createElement('div'); wrap.style.overflowX = 'auto'; wrap.innerHTML = data.svg;
  const note = document.createElement('p'); note.className = 'small muted';
  const SHOW = 'Practise drawing this on paper, then compare.';
  const HIDE = 'Say what each orange box is, then tap it to check.';
  note.textContent = SHOW;
  root.append(seg, wrap, note);
  const svg = wrap.querySelector('svg');
  const ready = () => { if (svg) addCovers(svg); };
  requestAnimationFrame(ready);
  seg.onclick = e => {
    const b = e.target.closest('button'); if (!b) return;
    seg.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
    const hide = b.dataset.k === 'hide'; ready();
    wrap.classList.toggle('hidelabels', hide);
    wrap.querySelectorAll('.lab').forEach(l => l.classList.remove('shown'));
    note.textContent = hide ? HIDE : SHOW;
  };
  wrap.onclick = e => { const l = e.target.closest('.lab'); if (l && wrap.classList.contains('hidelabels')) l.classList.add('shown'); };
}
"""
_diagram = st.components.v2.component("sparky_diagram", js=_DIAG_JS, isolate_styles=False)


def diagram_reveal(key: str, svg: str) -> None:
    _diagram(key=key, data={"svg": svg})


_SNAP_JS = r"""
export default function({ parentElement, data, setTriggerValue }) {
  const root = parentElement;
  if (root.dataset.round === String(data.round)) return;   // already running this round
  root.dataset.round = String(data.round);
  if (root._timer) clearInterval(root._timer);
  const S = data.symbols; let left = data.seconds, score = 0, wrong = 0, last = -1, busy = false, done = false;
  root.innerHTML = '<div class="snap"><div class="top"><span class="timer"></span><span class="chip chk"></span></div>' +
    '<div class="symbox"></div><div class="opts" style="margin-top:12px"></div>' +
    '<button type="button" class="say stop" style="width:100%;justify-content:center;margin-top:6px">Stop and see my score</button></div>';
  const tEl = root.querySelector('.timer'), sEl = root.querySelector('.chip'), box = root.querySelector('.symbox'), opts = root.querySelector('.opts');
  const shuffle = a => { a = a.slice(); for (let i = a.length-1; i > 0; i--) { const j = Math.floor(Math.random()*(i+1)); [a[i],a[j]] = [a[j],a[i]]; } return a; };
  const paint = () => { tEl.textContent = Math.max(0,left) + 's'; sEl.textContent = 'Score ' + score; };
  const finish = (stopped) => {
    if (done) return; done = true; clearInterval(root._timer);
    setTriggerValue('done', {score, wrong, stopped: !!stopped, used: data.seconds - Math.max(0, left), round: data.round});
  };
  root.querySelector('.stop').onclick = () => finish(true);
  function next(){
    let i; do { i = Math.floor(Math.random()*S.length); } while (i === last && S.length > 1); last = i;
    const choice = shuffle([i, ...shuffle(S.map((_,k)=>k).filter(k=>k!==i)).slice(0,3)]);
    box.innerHTML = S[i].s;
    opts.innerHTML = choice.map(k => '<button type="button" class="opt" data-k="'+k+'">'+S[k].n+'</button>').join('');
    busy = false;
    opts.onclick = e => {
      const b = e.target.closest('.opt'); if (!b || busy || done) return; busy = true;
      const k = +b.dataset.k;
      opts.querySelectorAll('.opt').forEach(x => { if (+x.dataset.k === i) x.classList.add('right'); else if (x === b) x.classList.add('wrong'); else x.classList.add('dim'); });
      if (k === i) score++; else { wrong++; left = Math.max(0, left - 3); }
      paint(); if (left <= 0) return finish();
      setTimeout(() => { if (!done) next(); }, k === i ? 400 : 1200);
    };
  }
  paint(); next();
  root._timer = setInterval(() => { left--; paint(); if (left <= 0) finish(); }, 1000);
}
"""
_snap = st.components.v2.component("sparky_snap", js=_SNAP_JS, isolate_styles=False)


def snap_game(round_id: int, symbols: list[dict], seconds: int = 60):
    return _snap(key=f"snap_{round_id}", data={"round": round_id, "symbols": symbols, "seconds": seconds},
                 on_done_change=lambda: None)


_CLOCK_JS = r"""
export default function({ parentElement, data, setTriggerValue }) {
  const root = parentElement;
  if (root._timer) clearInterval(root._timer);
  root.innerHTML = '<span class="timer" role="timer"></span>';
  const el = root.firstChild; let fired = false;
  const tick = () => {
    const s = Math.max(0, Math.round((data.deadline - Date.now()) / 1000));
    el.textContent = Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    if (s <= 0 && !fired) { fired = true; clearInterval(root._timer); setTriggerValue('timeout', data.deadline); }
  };
  tick(); root._timer = setInterval(tick, 500);
}
"""
_clock = st.components.v2.component("sparky_clock", js=_CLOCK_JS, isolate_styles=False)


def countdown(key: str, deadline_epoch: float):
    return _clock(key=key, data={"deadline": int(deadline_epoch * 1000)}, on_timeout_change=lambda: None)


_RULER_JS = r"""
export default function({ data }) {
  let el = document.getElementById('sparky-ruler');
  if (!el) {
    el = document.createElement('div'); el.id = 'sparky-ruler'; document.body.appendChild(el);
    window.addEventListener('pointermove', e => {
      const r = document.getElementById('sparky-ruler');
      if (r && r.dataset.on === '1' && e.pointerType === 'mouse') { r.style.display = 'block'; r.style.top = (e.clientY - r.offsetHeight / 2) + 'px'; }
    }, { passive: true });
  }
  el.dataset.on = data.on ? '1' : '0';
  if (!data.on) el.style.display = 'none';
}
"""
_ruler = st.components.v2.component("sparky_ruler", js=_RULER_JS, isolate_styles=False)


def reading_ruler(on: bool) -> None:
    _ruler(key="ruler", data={"on": bool(on)}, height=0)

