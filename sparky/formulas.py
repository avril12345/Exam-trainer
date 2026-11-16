"""Formula Lab generators, ported from the original JavaScript.

Each generator's ``make()`` returns a dict with:
  given: list of (symbol_key, value, unit)
  ask:   the question
  ans:   the exact answer (float)
  unit:  answer unit
  steps: list of HTML strings. ``{key}`` is replaced with a colour-coded symbol.

Inside the f-strings below, ``{{key}}`` produces a literal ``{key}`` symbol marker.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable

TAU = 2 * math.pi
R3 = math.sqrt(3)
pick = random.choice


def n3(x: float) -> str:
    """Three decimal places, as the exam asks for."""
    return f"{x:.3f}"


def js(x) -> str:
    """Format a number the way JavaScript template strings do (1500, not 1500.0)."""
    if isinstance(x, float):
        if x.is_integer():
            return str(int(x))
        return repr(round(x, 10))
    return str(x)


def G(k, val, unit):
    return (k, val, unit)


@dataclass
class Gen:
    id: str
    p: str  # paper: T1 / T2
    t: str  # topic
    n: str  # name
    make: Callable[[], dict]


# ---------------------------------------------------------------- T1 / shared
def _sync():
    P = pick([2, 4, 6, 8])
    ns = 120 * 50 / P
    nr = pick({2: [2850, 2880, 2900, 2940], 4: [1420, 1440, 1450, 1460, 1470],
               6: [940, 950, 960, 970], 8: [705, 720, 730]}[P])
    s = (ns - nr) / ns * 100
    return dict(given=[G('p', P, ''), G('f', 50, 'Hz'), G('nr', nr, 'rpm')],
                ask='Find the percentage slip', ans=s, unit='%', steps=[
        f"{{ns}} = 120 × {{f}} ÷ poles = 120 × 50 ÷ {P} = {js(ns)} rpm",
        "{s} = ({ns} − {nr}) ÷ {ns} × 100",
        f"= ({js(ns)} − {nr}) ÷ {js(ns)} × 100 = <b>{n3(s)} %</b>"])


def _rotor():
    P = pick([4, 6, 8]); s = pick([3, 4, 4.5, 5, 6]); ns = 6000 / P; nr = ns * (1 - s / 100)
    return dict(given=[G('p', P, ''), G('f', 50, 'Hz'), G('s', s, '%')],
                ask='Find the rotor speed', ans=nr, unit='rpm', steps=[
        f"{{ns}} = 120 × {{f}} ÷ poles = 120 × 50 ÷ {P} = {js(ns)} rpm",
        "{nr} = {ns} × (1 − {s} ÷ 100)",
        f"= {js(ns)} × (1 − {js(s / 100)}) = <b>{n3(nr)} rpm</b>"])


def _torque():
    P = pick([5.5, 7.5, 10.5, 15, 22]); n = pick([1420, 1440, 1450, 960, 2900])
    w = TAU * n / 60; T = P * 1000 / w
    return dict(given=[G('Pout', P, 'kW'), G('n', n, 'rpm')],
                ask='Find the torque developed', ans=T, unit='Nm', steps=[
        "{T} = {P} ÷ ω, and ω = 2π × {n} ÷ 60",
        f"ω = 2π × {n} ÷ 60 = {n3(w)} rad/s",
        f"{{T}} = {js(P * 1000)} ÷ {n3(w)} = <b>{n3(T)} Nm</b>"])


def _motor3():
    Po = pick([5.5, 7.5, 11, 15, 22, 30]); e = pick([0.8, 0.82, 0.85, 0.88, 0.9])
    pf = pick([0.73, 0.78, 0.8, 0.85]); Pi = Po * 1000 / e; IL = Pi / (R3 * 400 * pf); Ip = IL / R3
    return dict(given=[G('Pout', Po, 'kW'), G('eta', js(e * 100), '%'), G('pf', pf, 'lag'), G('VL', 400, 'V')],
                ask='Motor is in DELTA. Find the phase current in the windings', ans=Ip, unit='A', steps=[
        f"{{Pin}} = {{Pout}} ÷ {{eta}} = {js(Po * 1000)} ÷ {e} = {n3(Pi)} W",
        f"{{IL}} = {{Pin}} ÷ (√3 × {{VL}} × {{pf}}) = {n3(Pi)} ÷ (1.732 × 400 × {pf}) = {n3(IL)} A",
        f"Delta: {{Iph}} = {{IL}} ÷ √3 = {n3(IL)} ÷ 1.732 = <b>{n3(Ip)} A</b>"])


def _delta():
    Ip = pick([5.5, 6.2, 8.5, 10, 12.4]); pf = pick([0.7, 0.75, 0.8, 0.85, 0.9])
    IL = R3 * Ip; P = R3 * 400 * IL * pf
    return dict(given=[G('VL', 400, 'V'), G('Iph', Ip, 'A'), G('pf', pf, 'lag')],
                ask='Balanced DELTA load. Find the total power', ans=P, unit='W', steps=[
        f"Delta: {{IL}} = √3 × {{Iph}} = 1.732 × {Ip} = {n3(IL)} A",
        "{P} = √3 × {VL} × {IL} × {pf}",
        f"= 1.732 × 400 × {n3(IL)} × {pf} = <b>{n3(P)} W</b>"])


def _star():
    R = pick([20, 22.5, 30, 35, 40]); X = pick([15, 25, 30, 50])
    Vp = 400 / R3; Z = math.hypot(R, X); I = Vp / Z; P = 3 * I * I * R
    return dict(given=[G('VL', 400, 'V'), G('R', R, 'Ω'), G('XL', X, 'Ω')],
                ask='Balanced STAR load, R and X in each phase. Find the total power', ans=P, unit='W', steps=[
        f"Star: {{Vph}} = {{VL}} ÷ √3 = 400 ÷ 1.732 = {n3(Vp)} V",
        f"{{Z}} = √({{R}}² + {{XL}}²) = √({R}² + {X}²) = {n3(Z)} Ω",
        f"{{Iph}} = {{Vph}} ÷ {{Z}} = {n3(Vp)} ÷ {n3(Z)} = {n3(I)} A",
        f"{{pf}} = {{R}} ÷ {{Z}} = {n3(R / Z)}",
        f"{{P}} = 3 × {{Iph}}² × {{R}} = 3 × {n3(I)}² × {R} = <b>{n3(P)} W</b>"])


def _rl():
    R = pick([30, 47, 68, 100, 150, 220, 380]); L = pick([0.1, 0.15, 0.2, 0.3, 0.4, 0.6])
    XL = TAU * 50 * L; Z = math.hypot(R, XL); I = 230 / Z
    return dict(given=[G('R', R, 'Ω'), G('L', L, 'H'), G('V', 230, 'V'), G('f', 50, 'Hz')],
                ask='Find the supply current', ans=I, unit='A', steps=[
        f"{{XL}} = 2π{{f}}{{L}} = 2π × 50 × {L} = {n3(XL)} Ω",
        f"{{Z}} = √({{R}}² + {{XL}}²) = √({R}² + {n3(XL)}²) = {n3(Z)} Ω",
        f"{{I}} = {{V}} ÷ {{Z}} = 230 ÷ {n3(Z)} = <b>{n3(I)} A</b>"])


def _rlpf():
    R = pick([100, 200, 250, 380]); L = pick([0.3, 0.5, 0.6, 0.8])
    XL = TAU * 50 * L; Z = math.hypot(R, XL)
    return dict(given=[G('R', R, 'Ω'), G('L', L, 'H'), G('V', 230, 'V'), G('f', 50, 'Hz')],
                ask='Find the power factor (and say leading or lagging)', ans=R / Z, unit='', steps=[
        f"{{XL}} = 2π × 50 × {L} = {n3(XL)} Ω",
        f"{{Z}} = √({R}² + {n3(XL)}²) = {n3(Z)} Ω",
        f"{{pf}} = {{R}} ÷ {{Z}} = {R} ÷ {n3(Z)} = <b>{n3(R / Z)} lagging</b> (inductive)"])


def _rcpf():
    R = pick([20, 35, 47, 60]); C = pick([100, 150, 200, 300])
    XC = 1 / (TAU * 50 * C * 1e-6); Z = math.hypot(R, XC)
    return dict(given=[G('R', R, 'Ω'), G('C', C, 'µF'), G('V', 200, 'V'), G('f', 50, 'Hz')],
                ask='Find the power factor (and say leading or lagging)', ans=R / Z, unit='', steps=[
        f"{{XC}} = 1 ÷ (2π{{f}}{{C}}) = 1 ÷ (2π × 50 × {C}×10⁻⁶) = {n3(XC)} Ω",
        f"{{Z}} = √({{R}}² + {{XC}}²) = √({R}² + {n3(XC)}²) = {n3(Z)} Ω",
        f"{{pf}} = {{R}} ÷ {{Z}} = <b>{n3(R / Z)} leading</b> (capacitive)"])


def _res():
    L = pick([0.1, 0.2, 0.3, 0.398, 0.5]); C = pick([6.37, 10, 22, 47, 100])
    LC = L * C * 1e-6; f = 1 / (TAU * math.sqrt(LC))
    return dict(given=[G('L', L, 'H'), G('C', C, 'µF')],
                ask='Find the resonant frequency', ans=f, unit='Hz', steps=[
        "{f0} = 1 ÷ (2π√({L} × {C}))",
        f"{{L}} × {{C}} = {L} × {C}×10⁻⁶ = {LC:.4e}",
        f"√ = {math.sqrt(LC):.4e}",
        f"{{f0}} = 1 ÷ (2π × {math.sqrt(LC):.4e}) = <b>{n3(f)} Hz</b>"])


def _par():
    IR = pick([5, 8, 9.2, 12, 15]); IL = pick([6, 11.5, 15, 18.5, 20]); IC = pick([3, 8, 15.33, 26.5, 10])
    if IC == IL:
        IC += 2
    I = math.hypot(IR, IC - IL); lead = IC > IL
    return dict(given=[G('IR', IR, 'A'), G('IL', IL, 'A'), G('IC', IC, 'A')],
                ask='Find the supply current', ans=I, unit='A', steps=[
        f"{{IC}} and {{IL}} are opposite, so subtract: {IC} − {IL} = {n3(IC - IL)} A",
        f"{{I}} = √({{IR}}² + ({{IC}} − {{IL}})²) = √({IR}² + {n3(IC - IL)}²)",
        f"= <b>{n3(I)} A</b>",
        f"{{pf}} = {{IR}} ÷ {{I}} = {n3(IR / I)} "
        + ('leading (I<sub>C</sub> bigger)' if lead else 'lagging (I<sub>L</sub> bigger)')])


def _tau():
    C = pick([5, 10, 22, 47, 68, 100]); R = pick([10, 22, 47, 100, 470]); t = C * 1e-6 * R * 1e3
    return dict(given=[G('C', C, 'µF'), G('R', R, 'kΩ')],
                ask='Find the time constant', ans=t, unit='s', steps=[
        "{tau} = {R} × {C}",
        f"= {R}×10³ × {C}×10⁻⁶",
        f"= <b>{n3(t)} s</b> (fully charged after about 5{{tau}} = {n3(5 * t)} s)"])


def _i0():
    R = pick([10, 22, 47, 100, 500]); V = pick([12, 24, 48, 100]); I = V / (R * 1e3) * 1000
    return dict(given=[G('V', V, 'V'), G('R', R, 'kΩ')],
                ask='Find the initial charging current', ans=I, unit='mA', steps=[
        "At switch-on the capacitor acts like a short, so {I0} = {V} ÷ {R}",
        f"= {V} ÷ {R * 1000} = {V / (R * 1e3):.6f} A",
        f"= <b>{n3(I)} mA</b>"])


def _flux_density():
    F = pick([0.005, 0.01, 0.015, 0.02, 0.03]); A = pick([100, 120, 150, 200, 250]); B = F / (A / 1e4)
    return dict(given=[G('Phi', F, 'Wb'), G('A', A, 'cm²')],
                ask='Find the flux density', ans=B, unit='T', steps=[
        f"Convert area: {A} cm² ÷ 10,000 = {js(A / 1e4)} m²",
        f"{{B}} = {{Phi}} ÷ {{A}} = {F} ÷ {js(A / 1e4)}",
        f"= <b>{n3(B)} T</b>"])


def _vd():
    c = pick([(1.5, 29), (2.5, 18), (4, 11), (6, 7.3), (10, 4.4), (16, 2.8)])
    I = pick([14, 18, 25, 32, 38, 40]); L = pick([12, 20, 25, 30, 40, 50])
    vd = c[1] * I * L / 1000; ok = vd <= 9.2
    return dict(given=[G('mV', c[1], f'({c[0]} mm²)'), G('I', I, 'A'), G('len', L, 'm')],
                ask='Find the volt drop. Is it within 4 % of 230 V?', ans=vd, unit='V', steps=[
        "{Vd} = {mV} × {I} × length ÷ 1000",
        f"= {c[1]} × {I} × {L} ÷ 1000 = <b>{n3(vd)} V</b>",
        "4 % of 230 V = 9.2 V → " + ('<b>OK</b>, within the limit' if ok else '<b>Too high</b> — use a bigger cable'),
        '<span class="muted">In the exam take the mV/A/m value from the ET101 table for the right installation method.</span>'])


def _led():
    Vs = pick([12, 24, 48]); Vf = pick([1.8, 2, 2.2, 3.2]); If = pick([10, 15, 20, 25])
    R = (Vs - Vf) / (If / 1000)
    return dict(given=[G('Vs', Vs, 'V'), G('Vf', Vf, 'V'), G('If', If, 'mA')],
                ask='Find the series resistor value', ans=R, unit='Ω', steps=[
        f"Voltage across the resistor = {{Vs}} − {{Vf}} = {Vs} − {Vf} = {n3(Vs - Vf)} V",
        f"{{R}} = {n3(Vs - Vf)} ÷ {js(If / 1000)} = <b>{n3(R)} Ω</b>",
        f"Resistor power {{P}} = {{If}}² × {{R}} = {n3((If / 1000) ** 2 * R)} W → pick a resistor rated above this"])


def _cells():
    N = pick([6, 8, 10, 12]); E = pick([1.2, 1.5, 2]); r = pick([0.1, 0.2, 0.25]); R = pick([3, 4, 5, 10])
    I = N * E / (N * r + R)
    return dict(given=[G('N', N, ''), G('E', E, 'V each'), G('r', r, 'Ω each'), G('R', R, 'Ω load')],
                ask='Find the current in the load', ans=I, unit='A', steps=[
        f"Total EMF = {N} × {E} = {n3(N * E)} V",
        f"Total resistance = {N} × {r} + {R} = {n3(N * r + R)} Ω",
        f"{{I}} = {n3(N * E)} ÷ {n3(N * r + R)} = <b>{n3(I)} A</b>"])


# ---------------------------------------------------------------- T2 extras
def _lux():
    F = pick([8400, 10500, 12000, 15000, 24000]); d = pick([(5, 7), (6, 8), (7, 12), (8, 10), (8, 16)])
    A = d[0] * d[1]; E = F / A
    return dict(given=[G('Fl', F, 'lm'), G('room', f"{d[0]} m × {d[1]}", 'm')],
                ask='Find the average illuminance on the floor', ans=E, unit='lux', steps=[
        f"Area = {d[0]} × {d[1]} = {A} m²", f"E = F ÷ A = {F} ÷ {A}", f"= <b>{n3(E)} lux</b>"])


def _flux_needed():
    E = pick([300, 400, 450, 500]); d = pick([(7, 12), (7.5, 15), (8, 16), (6, 9), (10, 12)])
    A = d[0] * d[1]; F = E * A
    return dict(given=[G('Ex', E, 'lux'), G('room', f"{d[0]} m × {d[1]}", 'm')],
                ask='Find the total luminous flux', ans=F, unit='lm', steps=[
        f"Area = {d[0]} × {d[1]} = {js(A)} m²", f"F = E × A = {E} × {js(A)}", f"= <b>{n3(F)} lumens</b>"])


def _lumen():
    E = pick([300, 400, 500]); d = pick([(8, 14), (10, 12), (6, 9), (12, 15)])
    lm = pick([2800, 3600, 4000, 5000]); n = pick([1, 2]); UF = pick([0.6, 0.65, 0.7, 0.75]); MF = pick([0.8, 0.85])
    A = d[0] * d[1]; F = E * A; N = F / (n * lm * UF * MF)
    return dict(given=[G('Ex', E, 'lux'), G('room', f"{d[0]} m × {d[1]}", 'm'), G('nl', n, 'lamp(s) per fitting'),
                       G('lmp', lm, 'lm'), G('UF', UF, ''), G('MF', MF, '')],
                ask='How many luminaires? (give the exact figure, then round up)', ans=N, unit='', steps=[
        f"F = E × A = {E} × {A} = {F} lm",
        "N = F ÷ (n × lamp lm × UF × MF)",
        f"= {F} ÷ ({n} × {lm} × {UF} × {MF}) = <b>{n3(N)}</b>",
        f"Round UP → <b>{math.ceil(N - 1e-9)} luminaires</b>"])


def _conduit():
    while True:
        a = pick([1, 2, 3, 4]); b = pick([1, 2, 3, 4]); cpc = random.random() < 0.6
        per = 2 if cpc else 3; tot = a * per * 30 + b * per * 22
        if tot <= 529:
            break
    fit = '25 mm (factor 292)' if tot <= 292 else '32 mm (factor 529)'
    return dict(given=[G('cir', a, '× 2.5 mm²'), G('cir', b, '× 1.5 mm²'), G('run', 8, 'm, 2 bends'),
                       G('cpc', 'YES' if cpc else 'NO', '')],
                ask='Find the total cable factor (stranded PVC single-core, steel conduit)', ans=tot, unit='', steps=[
        f"Conduit {'IS' if cpc else 'is NOT'} the CPC → {per} cables per circuit ({'L + N' if cpc else 'L + N + CPC'})",
        f"2.5 mm²: {a} × {per} = {a * per} cables × 30 = {a * per * 30}",
        f"1.5 mm²: {b} × {per} = {b * per} cables × 22 = {b * per * 22}",
        f"Total cable factor = <b>{tot}</b>",
        f"Smallest conduit with factor ≥ {tot}: <b>{fit}</b>",
        '<span class="muted">Factors from your model answers (Tables 52J.3/52J.4). Check them in ET101.</span>'])


def _ol1():
    P = pick([0.75, 1.5, 2.2, 3]); pf = pick([0.7, 0.72, 0.8, 0.85]); I = P * 1000 / (230 * pf)
    return dict(given=[G('Pout', P, 'kW'), G('V', 230, 'V'), G('pf', pf, '')],
                ask='Find the full-load current to set the overload', ans=I, unit='A', steps=[
        "{I} = {P} ÷ ({V} × {pf})", f"= {js(P * 1000)} ÷ (230 × {pf}) = <b>{n3(I)} A</b>",
        "Set the overload at the motor full-load current"])


def _olsd():
    F = pick([10, 18, 24, 30, 42]); s = F / R3
    return dict(given=[G('FLC', F, 'A (line)')],
                ask='Overload is in the delta loop (phase windings). Find the setting', ans=s, unit='A', steps=[
        "In delta, phase current = line current ÷ √3",
        f"Setting = {F} ÷ 1.732 = <b>{n3(s)} A</b> (about 58 % of FLC)"])


GENS: list[Gen] = [
    Gen('sync', 'T1', 'Motors', 'Synchronous speed & slip', _sync),
    Gen('rotor', 'T1', 'Motors', 'Rotor speed from slip', _rotor),
    Gen('torque', 'T1', 'Motors', 'Motor torque', _torque),
    Gen('motor3', 'T1', 'Three-phase', 'Motor input & phase current (delta)', _motor3),
    Gen('delta', 'T1', 'Three-phase', 'Delta load: total power', _delta),
    Gen('star', 'T1', 'Three-phase', 'Star load with R and X: total power', _star),
    Gen('rl', 'T1', 'AC circuits', 'Series R–L: supply current', _rl),
    Gen('rlpf', 'T1', 'AC circuits', 'Series R–L: power factor', _rlpf),
    Gen('rcpf', 'T1', 'AC circuits', 'Series R–C: power factor', _rcpf),
    Gen('res', 'T1', 'AC circuits', 'Resonant frequency', _res),
    Gen('par', 'T1', 'AC circuits', 'Parallel R–L–C: supply current', _par),
    Gen('tau', 'T1', 'DC & capacitors', 'Capacitor time constant', _tau),
    Gen('i0', 'T1', 'DC & capacitors', 'Initial charging current', _i0),
    Gen('fluxB', 'T1', 'Magnetism', 'Flux density', _flux_density),
    Gen('vd', 'T2', 'Cables', 'Volt drop (T2)', _vd),
    Gen('led', 'T1', 'Electronics', 'LED series resistor', _led),
    Gen('cells', 'T2', 'Batteries', 'Cells in series with a load', _cells),
    Gen('lux', 'T2', 'Lighting (T2 Q17)', 'Illuminance from flux (E = F ÷ A)', _lux),
    Gen('flux', 'T2', 'Lighting (T2 Q17)', 'Luminous flux needed (F = E × A)', _flux_needed),
    Gen('lumen', 'T2', 'Lighting (T2 Q18)', 'Number of luminaires (lumen method)', _lumen),
    Gen('conduit', 'T2', 'Conduit (T2 Q9)', 'Conduit cable factors (8 m, 2 bends)', _conduit),
    Gen('ol1', 'T2', 'Motor control', 'Overload setting: single-phase motor', _ol1),
    Gen('olsd', 'T2', 'Motor control', 'Overload setting: star-delta (in the phase windings)', _olsd),
]
GEN_BY_ID = {g.id: g for g in GENS}


def is_correct(value: float, answer: float) -> bool:
    return abs(value - answer) <= max(0.0015, abs(answer) * 0.005)
