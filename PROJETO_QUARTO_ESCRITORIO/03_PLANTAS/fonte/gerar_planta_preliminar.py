"""Gera a planta preliminar (v0) da Suíte 01 em SVG, sem dependências externas.

Sistema de coordenadas (metros): origem no canto interno entre Parede E (oeste da
imagem) e Parede D (sul da imagem); x para a direita, y para cima.
Estilo das linhas = status da medida: contínua = confirmada, tracejada = calculada,
pontilhada = estimada.
"""
from pathlib import Path

S = 150          # px por metro
MX, MY = 170, 150
H = 3.55         # altura útil do desenho em metros (inclui armário)
OUT = Path(__file__).resolve().parents[1] / "planta_preliminar_v0.svg"

COR = {
    "armario": "#e3263a", "ble": "#f08a1c", "bld": "#1f5fe0", "c": "#0f9a9a",
    "d": "#18a52b", "e": "#8a3b12", "ee": "#a12de0", "ed": "#e8b400",
    "txt": "#1c1c1c", "cota": "#444", "pend": "#c0392b",
}
DASH = {"conf": "", "calc": 'stroke-dasharray="10 6"', "est": 'stroke-dasharray="2 5"'}


def X(x): return MX + x * S
def Y(y): return MY + (H - y) * S


el = []


def line(x1, y1, x2, y2, cor, w=6, st="conf", cap="butt"):
    el.append(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" '
              f'stroke="{cor}" stroke-width="{w}" stroke-linecap="{cap}" {DASH[st]}/>')


def text(x, y, s, size=14, cor=None, anchor="middle", weight="normal", rot=0, px=False):
    tx, ty = (x, y) if px else (X(x), Y(y))
    tr = f' transform="rotate({rot} {tx:.1f} {ty:.1f})"' if rot else ""
    el.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{size}" fill="{cor or COR["txt"]}" '
              f'text-anchor="{anchor}" font-weight="{weight}"{tr}>{s}</text>')


def cota_h(x1, x2, y, label, cor, st="conf", off=0):
    """Cota horizontal em y (m); off desloca o texto em px."""
    yy = Y(y)
    el.append(f'<line x1="{X(x1):.1f}" y1="{yy:.1f}" x2="{X(x2):.1f}" y2="{yy:.1f}" stroke="{cor}" '
              f'stroke-width="1.6" marker-start="url(#a)" marker-end="url(#a)" {DASH[st]}/>')
    for xx in (x1, x2):
        el.append(f'<line x1="{X(xx):.1f}" y1="{yy-8:.1f}" x2="{X(xx):.1f}" y2="{yy+8:.1f}" stroke="{cor}" stroke-width="1"/>')
    text(X((x1 + x2) / 2), yy - 6 + off, label, 13, cor, weight="bold", px=True)


def cota_v(y1, y2, x, label, cor, st="conf", side=-1):
    xx = X(x)
    el.append(f'<line x1="{xx:.1f}" y1="{Y(y1):.1f}" x2="{xx:.1f}" y2="{Y(y2):.1f}" stroke="{cor}" '
              f'stroke-width="1.6" marker-start="url(#a)" marker-end="url(#a)" {DASH[st]}/>')
    for yy in (y1, y2):
        el.append(f'<line x1="{xx-8:.1f}" y1="{Y(yy):.1f}" x2="{xx+8:.1f}" y2="{Y(yy):.1f}" stroke="{cor}" stroke-width="1"/>')
    tx = xx + side * 8
    ty = Y((y1 + y2) / 2)
    text(tx, ty, label, 13, cor, weight="bold", rot=-90, px=True)


# ---------------- geometria (metros) ----------------
D, E, C = 2.65, 2.85, 2.00          # confirmadas
ARM, BLD, BLE, EE, ED = 4.60, 0.30, 1.10, 1.10, 0.30
JAN = E - EE - ED                   # calculada = 1,45 (hipótese: segmentos somam a Parede E)
PORTA_BWC = ARM - D - BLD - BLE     # calculada = 0,55 (hipótese: armário = largura interna total)
PROF_ARM = 0.60                     # estimada (padrão de mercado) — PENDENTE

# piso útil do quarto
pts = [(0, 0), (D, 0), (D, C), (ARM, C), (ARM, E), (0, E)]
el.append('<polygon points="' + " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in pts) +
          '" fill="#f3f1ec" stroke="none"/>')
# banheiro (fora da área útil)
el.append(f'<rect x="{X(D):.1f}" y="{Y(C):.1f}" width="{(ARM-D)*S:.1f}" height="{C*S:.1f}" fill="url(#hatch)" stroke="#999"/>')
text((D + ARM) / 2, C / 2 + 0.08, "BANHO", 18, weight="bold")
text((D + ARM) / 2, C / 2 - 0.12, "fora da área útil", 12, "#555")
# armário
el.append(f'<rect x="{X(0):.1f}" y="{Y(E+PROF_ARM):.1f}" width="{ARM*S:.1f}" height="{PROF_ARM*S:.1f}" '
          f'fill="#e3263a22" stroke="{COR["armario"]}" stroke-width="2" stroke-dasharray="2 5"/>')
text(ARM / 2, E + PROF_ARM / 2 + 0.03, "ARMÁRIO — trecho 4,60 m (confirmado)", 14, COR["armario"], weight="bold")
text(ARM / 2, E + PROF_ARM / 2 - 0.15, "profundidade PENDENTE (desenhado 0,60 estimado)", 12, COR["pend"])

# paredes do quarto
line(0, 0, D, 0, COR["d"])                       # Parede D
line(D, 0, D, C, COR["c"])                       # Parede C
line(0, 0, 0, EE, COR["ee"])                     # Parede E E
line(0, E - ED, 0, E, COR["ed"])                 # Parede E D
line(D, C, D + BLD, C, COR["bld"])               # Banheiro L D
line(D + BLD + PORTA_BWC, C, ARM, C, COR["ble"])  # Banheiro L E
line(ARM, 0, ARM, C, "#777", 6, "est")           # parede leste do banho (estimada)
line(D, 0, ARM, 0, "#777", 6, "est")             # parede sul do banho

# janela na Parede E
for dx in (-0.05, 0, 0.05):
    line(dx, EE, dx, EE + JAN, "#3a7bd5", 1.5, "calc")
text(0.22, EE + JAN / 2, "JANELA", 13, "#3a7bd5", weight="bold", rot=-90)

# porta do banheiro (abre para dentro do banho, dobradiça à esquerda — conforme imagem)
hx, hy = D + BLD, C
line(hx, hy, hx, hy - PORTA_BWC, "#333", 2, "calc")
el.append(f'<path d="M {X(hx):.1f} {Y(hy-PORTA_BWC):.1f} A {PORTA_BWC*S:.1f} {PORTA_BWC*S:.1f} 0 0 0 '
          f'{X(hx+PORTA_BWC):.1f} {Y(hy):.1f}" fill="none" stroke="#333" stroke-width="1.2" stroke-dasharray="10 6"/>')

# porta de entrada — parede leste, faixa entre banho e armário (pendente)
line(ARM, C, ARM, E, COR["pend"], 3, "est")
text(ARM + 0.62, (C + E) / 2 + 0.05, "PORTA DE ENTRADA?", 12, COR["pend"], anchor="start", weight="bold")
text(ARM + 0.62, (C + E) / 2 - 0.10, "largura / sentido pendentes", 11, COR["pend"], anchor="start")

# basculante do banho (estimado)
line(D + 0.55, -0.0, D + 1.20, 0, "#3a7bd5", 3, "est")
text(D + 0.88, -0.14, "basculante (est.)", 11, "#3a7bd5")

# pontos elétricos identificados na parede D (posição estimada)
el.append(f'<circle cx="{X(0.70):.1f}" cy="{Y(0.12):.1f}" r="9" fill="none" stroke="#000" stroke-width="2"/>')
el.append(f'<path d="M {X(0.70):.1f} {Y(0.12)-9:.1f} A 9 9 0 0 1 {X(0.70):.1f} {Y(0.12)+9:.1f} Z" fill="#000"/>')
el.append(f'<polygon points="{X(0.90)-9:.1f},{Y(0.18):.1f} {X(0.90)+9:.1f},{Y(0.18):.1f} {X(0.90):.1f},{Y(0.04):.1f}" fill="{COR["d"]}" stroke="#000"/>')
text(0.80, 0.28, "pontos elétricos? (est.)", 11, "#555")

# pilares (estimados) — blocos cinzas da imagem
for (px_, py_) in [(-0.35, -0.30), (-0.35, E + PROF_ARM - 0.25), (ARM, E + PROF_ARM - 0.25)]:
    el.append(f'<rect x="{X(px_):.1f}" y="{Y(py_+0.25):.1f}" width="{0.35*S:.1f}" height="{0.25*S:.1f}" fill="#9a9a9a" stroke="#555"/>')

text(1.32, 1.45, "SUÍTE 01", 26, weight="bold")
text(1.32, 1.22, "área livre principal ≈ 7,55 m² (calc.)", 13, "#555")

# ---------------- cotas ----------------
cota_h(0, D, -0.45, "Parede D 2,65 m (conf.)", COR["d"])
cota_h(0, ARM, E + PROF_ARM + 0.30, "Armário 4,60 m (conf.)", COR["armario"])
cota_v(0, E, 0.45, "Parede E 2,85 m (conf.)", COR["e"], side=-1)
cota_v(0, EE, -0.55, "E E 1,10 (conf.)", COR["ee"])
cota_v(EE, EE + JAN, -0.55, "janela 1,45 (calc.)", "#3a7bd5", "calc")
cota_v(E - ED, E, -0.55, "0,30", COR["ed"])
cota_v(0, C, D - 0.30, "Parede C 2,00 m (conf.)", COR["c"])
cota_v(C, E, ARM + 0.40, "0,85 (calc.)", "#555", "calc", side=1)
cota_h(D, D + BLD, C + 0.20, "0,30", COR["bld"])
cota_h(D + BLD, D + BLD + PORTA_BWC, C + 0.20, "0,55?", "#555", "calc")
cota_h(D + BLD + PORTA_BWC, ARM, C + 0.20, "1,10 (conf.)", COR["ble"])

# ---------------- legenda ----------------
LX, LY = MX + 6.75 * S, MY + 20
leg = [("contínua", "conf", "Confirmada (indicada na planta)"),
       ("tracejada", "calc", "Calculada (depende de hipótese)"),
       ("pontilhada", "est", "Estimada (inferida da imagem)")]
text(LX, LY, "LEGENDA", 15, anchor="start", weight="bold", px=True)
for i, (_, st, lab) in enumerate(leg):
    yy = LY + 26 + i * 24
    el.append(f'<line x1="{LX}" y1="{yy-4}" x2="{LX+40}" y2="{yy-4}" stroke="#333" stroke-width="3" {DASH[st]}/>')
    text(LX + 50, yy, lab, 13, anchor="start", px=True)
notas = [
    "PLANTA PRELIMINAR v0 — NÃO USAR PARA EXECUÇÃO",
    "• A imagem original NÃO está em escala: as escalas",
    "  medidas em pixels variam de 171 a 297 px/m.",
    "• Hipótese A: armário 4,60 = largura interna total.",
    "• Hipótese B: 0,30 + janela + 1,10 = Parede E.",
    "• Espessura de paredes, pé-direito, portas e",
    "  profundidade do armário: PENDENTES.",
    "• Norte: indefinido (ver pendências).",
    "Escala do desenho: 1 m = 150 px",
]
for i, n in enumerate(notas):
    text(LX, LY + 120 + i * 20, n, 12, COR["pend"] if i == 0 else "#333", anchor="start",
         weight="bold" if i == 0 else "normal", px=True)
# escala gráfica 1 m
sx, sy = LX, LY + 120 + len(notas) * 20 + 20
el.append(f'<rect x="{sx}" y="{sy}" width="{S/2}" height="8" fill="#000"/><rect x="{sx+S/2}" y="{sy}" width="{S/2}" height="8" fill="#fff" stroke="#000"/>')
text(sx, sy + 24, "0", 11, anchor="middle", px=True)
text(sx + S, sy + 24, "1 m", 11, anchor="middle", px=True)

W = int(LX + 380)
Hpx = int(Y(-0.75) + 40)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hpx}" viewBox="0 0 {W} {Hpx}" font-family="DejaVu Sans, Arial, sans-serif">
<defs>
<marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="context-stroke"/></marker>
<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#e6e6e6"/><line x1="0" y1="0" x2="0" y2="10" stroke="#c4c4c4" stroke-width="3"/></pattern>
</defs>
<rect width="100%" height="100%" fill="#fff"/>
<text x="{MX}" y="40" font-size="22" font-weight="bold">Suíte 01 — Planta reconstruída preliminar (v0)</text>
<text x="{MX}" y="64" font-size="13" fill="#555">Reconstrução a partir da planta fornecida · medidas em metros · status por estilo de linha</text>
{chr(10).join(el)}
</svg>'''
OUT.write_text(svg, encoding="utf-8")
print(OUT, f"janela={JAN:.2f} porta_bwc={PORTA_BWC:.2f} area={D*E:.2f}")
