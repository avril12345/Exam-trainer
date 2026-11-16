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
                    "rate": 0.9, "ruler": False, "confetti": True}


def is_dark() -> bool:
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def palette(settings: dict) -> dict:
    if is_dark():
        return dict(bg="#11161d", panel="#1a212b", ink="#eef1f5", muted="#a3adbb", line="#2c3644",
                    acc="#f5b700", acc_ink="#11161d", acc_soft="#3a3218", key="#f5b700",
                    good="#5cc98a", good_soft="#1a3527", bad="#f08a6c", bad_soft="#3a2520",
                    qv="#5aa7ff", qi="#ff6b75", qr="#ffaa3b", qp="#58d68d", qf="#b493ff", qk="#3dd6d0",
                    ruler="rgba(245,183,0,.14)", shadow="0 1px 2px rgba(0,0,0,.25),0 6px 18px rgba(0,0,0,.18)",
                    hero="linear-gradient(135deg,#1f2a36,#1a212b)")
    bg, panel, line = TINTS.get(settings.get("tint"), TINTS["Cream"])
    # Calm and warm: sage green for success, soft terracotta (not alarm red) for "not yet".
    return dict(bg=bg, panel=panel, ink="#1d2430", muted="#4f5866", line=line,
                acc="#c98a00", acc_ink="#1d2430", acc_soft="#f6e7c1", key="#8a5500",
                good="#2e8b57", good_soft="#dcefe2", bad="#b5533a", bad_soft="#f8e4dc",
                qv="#1f6fd1", qi="#c62f3a", qr="#b86a00", qp="#2f8a4c", qf="#7a4fc4", qk="#0f8a8a",
                ruler="rgba(201,138,0,.16)", shadow="0 1px 2px rgba(60,45,10,.05),0 6px 18px rgba(60,45,10,.07)",
                hero=f"linear-gradient(135deg,{panel},#f6ead0)")


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
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px;margin:0 0 6px;box-shadow:var(--shadow)}}
.panel.focus{{border:2px solid var(--acc)}}
/* Soft, calm surfaces: gentle shadow, a little lift on hover */
[data-testid="stVerticalBlockBorderWrapper"]{{border-radius:16px !important;box-shadow:var(--shadow);background:var(--panel)}}
.stButton>button,[data-testid="stPageLink"] a{{transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease}}
.stButton>button:hover,[data-testid="stPageLink"] a:hover{{transform:translateY(-1px);box-shadow:var(--shadow)}}
.hero{{background:var(--hero);border:1px solid var(--line);border-radius:18px;padding:20px 20px 16px;box-shadow:var(--shadow);margin-bottom:6px}}
.hero h2{{margin:0 0 4px;font-size:2rem}}
.hero .lead{{margin:0;color:var(--muted)}}
.goal{{display:flex;gap:16px;align-items:center;margin-top:14px}}
.ring{{--p:0;flex:0 0 78px;width:78px;height:78px;border-radius:50%;display:grid;place-items:center;
  background:conic-gradient(var(--good) calc(var(--p)*1%),var(--line) 0)}}
.ring>span{{width:60px;height:60px;border-radius:50%;background:var(--panel);display:grid;place-items:center;
  font-family:var(--display);font-size:1.35rem;line-height:1}}
.goal b{{font-family:var(--display);font-size:1.25rem;letter-spacing:.02em}}
.next{{border-left:6px solid var(--acc)}}
.encourage{{color:var(--muted);font-size:.92rem;margin-top:6px}}
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
.feedback{{border-left:6px solid var(--good);padding:14px 18px;border-radius:12px;background:var(--good-soft);margin:8px 0}}
.feedback .tail{{display:block;margin-top:6px;font-size:.88rem;color:var(--muted)}}
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
.bar>i{{display:block;height:100%;background:linear-gradient(90deg,var(--acc),var(--good));border-radius:99px}}
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
/* Block Drop: one falling block, styled as a labelled DIN-rail module */
.block-container:has(.bdrop){{padding-bottom:.5rem !important}}
.bdrop{{-webkit-user-select:none;user-select:none}}
.bd-top{{display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:48px;margin-bottom:6px}}
.bd-score{{font-family:var(--display);font-size:1.7rem;line-height:1;font-variant-numeric:tabular-nums}}
.bd-score small{{display:block;font-family:var(--font);font-size:.7rem;color:var(--muted)}}
.bd-mid{{display:flex;flex-direction:column;align-items:center;gap:4px}}
.bd-lives{{display:flex;gap:5px;align-items:center;font-size:.75rem;color:var(--muted)}}
.bd-lives i{{width:12px;height:22px;border-radius:3px;border:2px solid var(--ink);background:var(--good)}}
.bd-lives i.off{{background:transparent;opacity:.35}}
.bd-top .say{{min-width:96px;justify-content:center}}
.bd-play{{position:relative;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:var(--bg)}}
.bd-rail{{position:absolute;left:0;right:0;bottom:0;height:12px;border-top:2px solid var(--muted);
  background:repeating-linear-gradient(90deg,var(--line) 0 18px,var(--bg) 18px 26px)}}
.bd-bar{{position:absolute;left:0;top:0;height:8px;width:100%;background:var(--acc);transform-origin:left center}}
.bd-block{{position:absolute;left:10px;right:10px;top:0;will-change:transform;background:var(--panel);
  border:2px solid var(--ink);border-radius:8px;overflow:hidden}}
.bd-tag{{display:flex;justify-content:space-between;gap:8px;background:var(--acc);color:var(--acc-ink);
  font-weight:700;font-size:.78rem;padding:4px 10px;line-height:1.3}}
.bd-body{{padding:10px 12px 8px}}
.bd-body .qtext{{font-size:1.05rem;margin:0;line-height:1.45}}
.bd-sym{{display:grid;place-items:center;padding:2px 0}} .bd-sym .sym{{max-width:200px;max-height:100px}}
.bd-term{{height:14px;border-top:1px solid var(--line);
  background:radial-gradient(circle,var(--muted) 0 3px,transparent 3.5px) 0 50%/28px 14px repeat-x}}
.bd-block.ok{{border-color:var(--good);background:var(--good-soft)}} .bd-block.ok .bd-tag{{background:var(--good);color:var(--panel)}}
.bd-block.bad{{border-color:var(--bad);background:var(--bad-soft)}} .bd-block.bad .bd-tag{{background:var(--bad);color:var(--panel)}}
.bd-over{{position:absolute;inset:0;display:grid;place-items:center;padding:12px;z-index:3;background:color-mix(in srgb,var(--bg) 82%,transparent)}}
.bd-over .panel{{max-width:320px;width:100%;text-align:center}}
.bd-over .head{{font-family:var(--display);font-size:1.4rem;display:block;margin-bottom:4px}}
.bd-over button{{width:100%;justify-content:center;margin-top:8px}}
.bd-ans{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}}
.bd-ans .opt{{margin:0;min-height:56px;cursor:pointer;font:inherit;font-size:.86rem;color:var(--ink);text-align:left;
  padding:8px 10px;gap:8px;align-items:center;line-height:1.3;overflow-wrap:anywhere}}
.bd-ans .opt .let{{flex:0 0 28px;height:28px}}
.bd-ans .opt:hover{{border-color:var(--acc)}}
.bd-ans .opt:disabled{{cursor:default}}
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


def feedback(head: str, body: str = "", ok: bool = True, tail: str = "") -> str:
    tail_html = f'<span class="tail">{tail}</span>' if tail else ""
    return f'<div class="feedback {"" if ok else "no"}"><span class="head">{head}</span>{body}{tail_html}</div>'


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


# --------------------------------------------------------------------------- components
_SAY_ICON = ('<svg viewBox="0 0 24 24"><path d="M4 9v6h4l5 4V5L8 9z"/>'
             '<path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/></svg>')

# Shared by the read-aloud button and Block Drop: tidy symbols for speech, pick an Irish/UK voice.
_SPEECH_JS = r"""
const CLEAN = [[/Ω/g,' ohms'],[/µF/g,' microfarads'],[/mm²/g,' square millimetres'],[/m²/g,' square metres'],
  [/²/g,' squared'],[/√3/g,'root 3'],[/√/g,'root '],[/π/g,'pi'],[/→/g,', '],[/≥/g,'at least '],[/≤/g,'no more than '],
  [/×/g,' times '],[/÷/g,' divided by '],[/±/g,' plus or minus '],[/η/g,'efficiency'],[/Φ/g,'flux'],[/τ/g,'tau'],[/·/g,', ']];
const clean = s => CLEAN.reduce((a,[r,t]) => a.replace(r,t), s);
function pickVoice(){
  const vs = window.speechSynthesis.getVoices();
  return vs.find(v=>/en-IE/i.test(v.lang)) || vs.find(v=>/en-GB/i.test(v.lang)) || vs.find(v=>/^en/i.test(v.lang));
}
"""

_READ_JS = _SPEECH_JS + r"""
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


_DROP_JS = _SPEECH_JS + r"""
export default function({ parentElement, data, setTriggerValue }) {
  const root = parentElement;
  // Streamlit calls this again on every rerun. Keep the running game, and always hand back
  // the cleanup: Streamlit only runs the last one it was given, when the component unmounts.
  if (root._game === data.game && root._cleanup) return root._cleanup;
  if (root._cleanup) root._cleanup();
  root._game = data.game;

  const B = data.blocks, N = B.length, LET = 'ABCD';
  const RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  let idx = -1, cur = null, score = 0, lives = 3, streak = 0, bestStreak = 0, correct = 0, results = [];
  let state = 'idle', paused = false, holding = false, elapsed = 0, T = 1, showLeft = 0, travel = 0;
  let last = performance.now(), raf = 0, dead = false, holdTimer = 0, reveal = '';

  root.innerHTML = '<div class="bdrop">' +
    '<div class="bd-top"><div class="bd-score" aria-live="polite"></div>' +
    '<div class="bd-mid"><div class="bd-lives" aria-label="Lives"></div><span class="chip chk bd-streak" hidden></span></div>' +
    '<button type="button" class="say bd-pause">Pause</button></div>' +
    '<div class="bd-play"><div class="bd-bar" hidden></div><div class="bd-block"></div><div class="bd-rail"></div><div class="bd-over" hidden></div></div>' +
    '<div class="bd-ans"></div></div>';
  const $ = s => root.querySelector(s);
  const scoreEl = $('.bd-score'), livesEl = $('.bd-lives'), streakEl = $('.bd-streak'), pauseBtn = $('.bd-pause');
  const play = $('.bd-play'), bar = $('.bd-bar'), blk = $('.bd-block'), over = $('.bd-over'), ans = $('.bd-ans'), top = $('.bd-top');
  bar.hidden = !RM;

  const paint = () => {
    scoreEl.innerHTML = score + '<small>points</small>';
    livesEl.innerHTML = 'Lives ' + [0,1,2].map(k => '<i class="' + (k < lives ? '' : 'off') + '"></i>').join('');
    streakEl.hidden = streak < 3; streakEl.textContent = 'Streak ' + streak;
  };
  const hush = () => { try { window.speechSynthesis && speechSynthesis.cancel(); } catch (e) {} };
  const endHold = () => { clearTimeout(holdTimer); if (holding) { holding = false; last = performance.now(); } };

  // Fit the play area plus answers into the screen, so the page never has to scroll.
  // Streamlit scrolls an inner container, not the window.
  function scroller() {
    for (let e = root.parentElement; e && e !== document.body; e = e.parentElement) {
      const o = getComputedStyle(e).overflowY;
      if ((o === 'auto' || o === 'scroll') && e.scrollHeight > e.clientHeight) return e;
    }
    return document.scrollingElement || document.documentElement;
  }
  function fit() {
    const sc = scroller();
    const docTop = root.getBoundingClientRect().top + sc.scrollTop;
    const h = window.innerHeight - docTop - top.offsetHeight - ans.offsetHeight - 22;
    play.style.height = Math.max(180, Math.round(h)) + 'px';
    travel = RM ? 0 : Math.max(0, play.clientHeight - blk.offsetHeight - 14);
    place();
  }
  function place() {
    const p = Math.min(1, elapsed / T);
    if (RM) bar.style.transform = 'scaleX(' + (1 - p) + ')';
    else blk.style.transform = 'translateY(' + (p * travel).toFixed(1) + 'px)';
  }
  function fallTime(b) {
    // Questions: 15 s plus 0.25 s per word, kept between 15 and 25 s (speeding up never goes below 15 s).
    // Symbols: 8 s, speeding up to no less than 4 s.
    const f = data.steady ? 1 : Math.pow(0.95, Math.floor(correct / 5));
    if (b.k === 's') return Math.max(4, 8 * f);
    return Math.max(15, Math.min(25, 15 + 0.25 * (b.words || 0)) * f);
  }
  function next() {
    if (lives <= 0 || idx + 1 >= N) return finish(false);
    cur = B[++idx]; elapsed = 0; T = fallTime(cur) * 1000;  // the clock counts milliseconds
    blk.className = 'bd-block';
    blk.innerHTML = '<div class="bd-tag"><span>' + cur.label + '</span><span>' + (idx + 1) + ' / ' + N + '</span></div>' +
      '<div class="bd-body">' + cur.html + '</div><div class="bd-term"></div>';
    ans.innerHTML = cur.opts.map((o, k) => '<button type="button" class="opt" data-k="' + k + '"><span class="let">' + LET[k] +
      '</span><span>' + o + '</span></button>').join('');
    reveal = ''; over.hidden = true; state = 'fall'; paint(); fit();
    if (data.read && window.speechSynthesis) {
      holding = true; hush();
      const u = new SpeechSynthesisUtterance(clean(cur.say)); u.rate = data.rate || 0.9;
      const v = pickVoice(); if (v) u.voice = v;
      u.onend = u.onerror = endHold;
      // Safety net in case the browser never reports the end of speech.
      holdTimer = setTimeout(endHold, 4000 + cur.say.split(/\s+/).length * 900 / (data.rate || 0.9));
      speechSynthesis.speak(u);
    }
    last = performance.now();
  }
  function mark(picked) {
    ans.querySelectorAll('.opt').forEach(b => {
      const k = +b.dataset.k; b.disabled = true;
      b.classList.add(k === cur.a ? 'right' : k === picked ? 'wrong' : 'dim');
    });
  }
  function answer(k) {
    if (state !== 'fall' || paused || k < 0 || k >= cur.opts.length) return;
    endHold(); hush();
    if (k === cur.a) {
      const bonus = Math.max(0, Math.min(10, Math.round(10 * (1 - elapsed / T))));
      score += 10 + bonus; streak++; correct++; bestStreak = Math.max(bestStreak, streak);
      results.push({ k: cur.k, i: cur.i, ok: true });
      blk.classList.add('ok'); mark(k); state = 'show'; showLeft = 450; paint();
    } else miss(k);
  }
  function miss(picked) {
    endHold(); hush();
    lives--; streak = 0; results.push({ k: cur.k, i: cur.i, ok: false });
    blk.classList.add('bad'); mark(picked); paint();
    reveal = '<div class="panel"><span class="head">' + (picked < 0 ? 'Out of time' : 'Not quite') + '</span>' +
      '<div class="small muted">Correct answer</div><div><b>' + LET[cur.a] + '.</b> ' + cur.opts[cur.a] + '</div></div>';
    over.innerHTML = reveal; over.hidden = false; state = 'show'; showLeft = 1500;
  }
  function finish(stopped) {
    if (state === 'over') return;
    state = 'over'; stop();
    ans.querySelectorAll('.opt').forEach(b => b.disabled = true);
    over.innerHTML = '<div class="panel"><span class="head">' + (stopped ? 'Game ended' : lives > 0 ? 'Deck cleared' : 'Game over') +
      '</span><div class="small muted">Adding up your score…</div></div>';
    over.hidden = false; pauseBtn.disabled = true;
    setTriggerValue('done', { game: data.game, score, results, bestStreak, stopped: !!stopped, cleared: !stopped && lives > 0 });
  }
  function pause() {
    if (paused || state === 'over' || state === 'idle') return;
    paused = true; hush(); endHold(); pauseBtn.textContent = 'Resume';
    over.innerHTML = '<div class="panel"><span class="head">Paused</span>' +
      '<button type="button" class="say on bd-resume">Resume</button><button type="button" class="say bd-end">End game</button></div>';
    over.hidden = false;
    over.querySelector('.bd-resume').onclick = resume;
    over.querySelector('.bd-end').onclick = () => finish(true);
  }
  function resume() {
    if (!paused) return;
    paused = false; pauseBtn.textContent = 'Pause'; last = performance.now();
    over.innerHTML = reveal; over.hidden = !reveal;   // bring back the answer card if one was showing
  }
  function frame(now) {
    if (dead) return;
    if (!root.isConnected) { stop(); return; }
    const dt = Math.min(100, now - last); last = now;
    if (!paused) {
      if (state === 'fall' && !holding) { elapsed += dt; if (elapsed >= T) { elapsed = T; place(); miss(-1); } else place(); }
      else if (state === 'show') { showLeft -= dt; if (showLeft <= 0) next(); }
    }
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    dead = true; cancelAnimationFrame(raf); clearTimeout(holdTimer); hush();
    document.removeEventListener('keydown', onKey); document.removeEventListener('visibilitychange', onVis);
    window.removeEventListener('resize', fit);
  }
  function onKey(e) {
    if (e.ctrlKey || e.metaKey || e.altKey || e.target.closest && e.target.closest('input,textarea,select,[contenteditable]')) return;
    const k = '1234'.indexOf(e.key) >= 0 ? '1234'.indexOf(e.key) : 'abcd'.indexOf((e.key || '').toLowerCase());
    if (k >= 0 && e.key.length === 1) { e.preventDefault(); answer(k); }
  }
  function onVis() { if (document.hidden) pause(); }

  ans.onclick = e => { const b = e.target.closest('.opt'); if (b) answer(+b.dataset.k); };
  pauseBtn.onclick = () => paused ? resume() : pause();
  document.addEventListener('keydown', onKey);
  document.addEventListener('visibilitychange', onVis);
  window.addEventListener('resize', fit);
  try { scroller().scrollTop = 0; } catch (e) {}  // he may have scrolled down to tap Start
  paint(); next();
  raf = requestAnimationFrame(frame);
  root._cleanup = () => { stop(); root._cleanup = null; root._game = null; };
  return root._cleanup;
}
"""
_drop = st.components.v2.component("sparky_drop", js=_DROP_JS, isolate_styles=False)


def drop_game(game_id: int, blocks: list[dict], steady: bool, read: bool, on_done):
    """Block Drop. ``blocks`` come from ``pages._drop_blocks``; the game reports
    ``done`` = {game, score, results: [{k, i, ok}], bestStreak, stopped, cleared}."""
    rate = st.session_state.get("S", {}).get("settings", {}).get("rate", 0.9)
    return _drop(key=f"drop_{game_id}", data={"game": game_id, "blocks": blocks, "steady": steady,
                                              "read": read, "rate": rate}, on_done_change=on_done)


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



# --------------------------------------------------------------------------- encouragement
PRAISE = ["Correct", "Spot on", "That's it", "Nailed it", "Right first time", "Good work"]
NOT_YET = ["Not quite", "Not this time", "Close — have a look", "Not yet"]


def praise() -> str:
    import random
    return random.choice(PRAISE)


def not_yet() -> str:
    import random
    return random.choice(NOT_YET)


# --------------------------------------------------------------------------- confetti
# Wire-colour confetti (brown, black, grey, blue, green/yellow) for a correct answer or a
# finished set. Short, falls out of the way, never blocks a tap, off for reduced motion.
_CONFETTI_JS = r"""
export default function({ data }) {
  if (!data || !data.id) return;
  window.__sparkyCheers = window.__sparkyCheers || new Set();
  if (window.__sparkyCheers.has(data.id)) return;          // each celebration plays once
  window.__sparkyCheers.add(data.id);
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const big = data.size === 'big';
  const cv = document.createElement('canvas');
  cv.setAttribute('aria-hidden', 'true');
  Object.assign(cv.style, {position:'fixed', inset:'0', width:'100vw', height:'100vh', pointerEvents:'none', zIndex: 999995});
  document.body.appendChild(cv);
  const dpr = window.devicePixelRatio || 1, W = innerWidth, H = innerHeight;
  cv.width = W * dpr; cv.height = H * dpr;
  const ctx = cv.getContext('2d'); ctx.scale(dpr, dpr);
  const COL = ['#8b5a2b', '#22262c', '#8a8f98', '#1f6fd1', '#3a9a3a', '#f5b700', '#c98a00'];
  const n = big ? 150 : 45, life = big ? 2600 : 1300;
  const P = [];
  for (let i = 0; i < n; i++) {
    const fromSide = big && i % 2;
    P.push({
      x: big ? (fromSide ? (i % 4 === 1 ? 0 : W) : W * Math.random()) : W / 2 + (Math.random() - .5) * 80,
      y: big ? (fromSide ? H * .55 : -10) : H * .45,
      vx: big ? (fromSide ? (i % 4 === 1 ? 1 : -1) * (3 + Math.random() * 5) : (Math.random() - .5) * 2) : (Math.random() - .5) * 9,
      vy: big ? (fromSide ? -(6 + Math.random() * 6) : 1 + Math.random() * 2) : -(4 + Math.random() * 6),
      w: 5 + Math.random() * 5, h: 8 + Math.random() * 8, r: Math.random() * 6, vr: (Math.random() - .5) * .3,
      c: COL[i % COL.length], stripe: i % 7 === 4
    });
  }
  const t0 = performance.now();
  function frame(t) {
    const k = (t - t0) / life;
    ctx.clearRect(0, 0, W, H);
    if (k >= 1) { cv.remove(); return; }
    ctx.globalAlpha = k > .7 ? (1 - k) / .3 : 1;
    for (const p of P) {
      p.vy += .22; p.vx *= .99; p.x += p.vx; p.y += p.vy; p.r += p.vr;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r);
      ctx.fillStyle = p.c; ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      if (p.stripe) { ctx.fillStyle = '#f5d000'; ctx.fillRect(-p.w / 2, -p.h / 6, p.w, p.h / 3); }  // green/yellow earth
      ctx.restore();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
"""
_confetti = st.components.v2.component("sparky_confetti", js=_CONFETTI_JS, isolate_styles=False)


def cheer(event_id: str | None = None, size: str = "small") -> None:
    """Queue a confetti burst for this run. ``event_id`` must be unique per event:
    the same id never plays twice, so it is safe to call from screens that redraw."""
    import uuid
    st.session_state["_cheer"] = {"id": str(event_id or uuid.uuid4()), "size": size}


def play_cheer() -> None:
    """Mount the confetti layer once, at the end of the script."""
    S = st.session_state.get("S", {})
    ev = st.session_state.pop("_cheer", None)
    if not S.get("settings", {}).get("confetti", True):
        ev = None
    _confetti(key="confetti", data=ev or {}, height=0)


# --------------------------------------------------------------------------- electric buzz
# Shown each time the level progress bar crosses another 10 %. An arc jumps between two
# terminals for under two seconds, then fades. Never blocks a tap. Static badge for reduced motion.
_BUZZ_JS = r"""
export default function({ data }) {
  if (!data || !data.id) return;
  window.__sparkyBuzz = window.__sparkyBuzz || new Set();
  if (window.__sparkyBuzz.has(data.id)) return;
  window.__sparkyBuzz.add(data.id);
  const RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const NS = 'http://www.w3.org/2000/svg', W = 300, H = 90, Y = 40;
  const wrap = document.createElement('div');
  wrap.setAttribute('role', 'status');
  Object.assign(wrap.style, {position:'fixed', left:'50%', top:'72px', transform:'translateX(-50%)', width:'min(340px,92vw)',
    pointerEvents:'none', zIndex:999996, background:'#1d2430', color:'#fff', borderRadius:'16px', padding:'8px 10px 10px',
    boxShadow:'0 8px 28px rgba(0,0,0,.35)', textAlign:'center', fontFamily:'var(--font, sans-serif)', transition:'opacity .4s'});
  wrap.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" aria-hidden="true">' +
    '<defs><filter id="bzglow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>' +
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>' +
    '<rect x="6" y="' + (Y - 14) + '" width="26" height="28" rx="5" fill="#8a8f98"/><rect x="' + (W - 32) + '" y="' + (Y - 14) + '" width="26" height="28" rx="5" fill="#8a8f98"/>' +
    '<circle cx="19" cy="' + Y + '" r="5" fill="#f5d000"/><circle cx="' + (W - 19) + '" cy="' + Y + '" r="5" fill="#f5d000"/>' +
    '<g filter="url(#bzglow)"><polyline class="a1" fill="none" stroke="#f5b700" stroke-width="5" stroke-linejoin="round"/>' +
    '<polyline class="a2" fill="none" stroke="#fff8d0" stroke-width="2" stroke-linejoin="round"/>' +
    '<polyline class="a3" fill="none" stroke="#7fc8ff" stroke-width="1.5" stroke-linejoin="round" opacity=".8"/></g>' +
    '<text x="' + (W / 2) + '" y="' + (H - 4) + '" text-anchor="middle" fill="#fff" font-size="15" font-weight="700">' + '</text></svg>';
  wrap.querySelector('text').textContent = data.label || '';
  document.body.appendChild(wrap);
  const a1 = wrap.querySelector('.a1'), a2 = wrap.querySelector('.a2'), a3 = wrap.querySelector('.a3');
  const arc = (amp) => {
    const pts = [[24, Y]], n = 14;
    for (let i = 1; i < n; i++) pts.push([24 + (W - 48) * i / n, Y + (Math.random() - .5) * amp]);
    pts.push([W - 24, Y]);
    return pts.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ');
  };
  const draw = () => { const p = arc(26); a1.setAttribute('points', p); a2.setAttribute('points', p); a3.setAttribute('points', arc(40)); };
  draw();
  const life = RM ? 2200 : 1900;
  let timer = 0;
  if (!RM) timer = setInterval(() => { draw(); wrap.style.opacity = Math.random() < .12 ? '.75' : '1'; }, 60);
  setTimeout(() => { clearInterval(timer); wrap.style.opacity = '0'; }, life);
  setTimeout(() => wrap.remove(), life + 450);
}
"""
_buzz = st.components.v2.component("sparky_buzz", js=_BUZZ_JS, isolate_styles=False)


def buzz(label: str) -> None:
    import uuid
    st.session_state["_buzz"] = {"id": str(uuid.uuid4()), "label": label}


def play_buzz() -> None:
    ev = st.session_state.pop("_buzz", None)
    _buzz(key="buzz", data=ev or {}, height=0)
