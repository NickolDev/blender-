"""Planta v1 da Suíte 01 (geometria com respostas do levantamento) + alternativas de layout.

Gera, em 03_PLANTAS/:
  planta_arquitetonica_v1.svg   — ambiente sem mobiliário
  layouts/layout_A.svg          — cama sob a janela (Parede E), mesa na Parede D
  layouts/layout_B.svg          — cama na Parede C (sob o ar), mesa na Parede D

Coordenadas em metros: origem no canto interno Parede E × Parede D; x → direita da
planta original, y → para cima da planta original (em direção ao armário).
Linha contínua = confirmada; tracejada = calculada; pontilhada = estimada.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- geometria
D, E, C = 2.65, 2.85, 2.00            # confirmadas
LARG = 4.60                           # armário parede a parede (confirmado)
FAIXA = 0.86                          # frente do armário → banheiro (confirmado)
PE = 2.64                             # pé-direito (confirmado)
EE, ED = 1.10, 0.30                   # trechos da Parede E (confirmados)
JAN_Y0, JAN_Y1 = EE, E - ED           # janela: largura 1,45 calculada
JAN_PEIT, JAN_H = 1.00, 1.20          # peitoril confirmado; 1,20 = altura (interpretação)
BLD, PBWC = 0.30, 0.73                # banheiro: trecho + porta c/ batente (conf.)
T = 0.12                              # espessura de parede — ESTIMADA (desconhecida)
TC = 0.10                             # Parede C (drywall/alvenaria fina) — ESTIMADA
PROF_ARM = 0.60                       # armário existente — profundidade ESTIMADA
PENT = 0.80                           # porta de entrada c/ batente (conf.), folha 0,75
AC_W, AC_Y = 0.85, C / 2              # ar-condicionado no meio da Parede C (largura est.)

C_ = {"armario": "#e3263a", "ble": "#f08a1c", "bld": "#1f5fe0", "c": "#0f9a9a",
      "d": "#18a52b", "e": "#8a3b12", "ee": "#a12de0", "ed": "#e8b400",
      "txt": "#1c1c1c", "pend": "#c0392b", "jan": "#3a7bd5", "wall": "#3b3b3b",
      "ripado": "#b07a4a", "mesa": "#1f1f1f", "cama": "#6b6e73", "marc": "#c58c55",
      "eletr": "#d4a017", "circ": "#2e9e5b"}
DASH = {"conf": "", "calc": 'stroke-dasharray="10 6"', "est": 'stroke-dasharray="2 5"'}

S, X0, Y0 = 140, -1.05, -1.15          # px/m e origem do desenho (m)
XMAX, YMAX = 5.45, 4.15
PANEL = 470                            # largura do painel lateral (px)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, title, subtitle):
        self.el, self.title, self.subtitle = [], title, subtitle

    def X(self, x): return 30 + (x - X0) * S
    def Y(self, y): return 110 + (YMAX - y) * S

    def add(self, s): self.el.append(s)

    def rect(self, x0, y0, x1, y1, fill, stroke="none", w=1, st="conf", op=1):
        self.add(f'<rect x="{self.X(x0):.1f}" y="{self.Y(y1):.1f}" width="{(x1-x0)*S:.1f}" '
                 f'height="{(y1-y0)*S:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
                 f'stroke-width="{w}" {DASH[st]}/>')

    def line(self, x1, y1, x2, y2, cor, w=2, st="conf"):
        self.add(f'<line x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" x2="{self.X(x2):.1f}" '
                 f'y2="{self.Y(y2):.1f}" stroke="{cor}" stroke-width="{w}" {DASH[st]}/>')

    def text(self, x, y, s, size=12, cor=None, anchor="middle", bold=False, rot=0, px=False):
        tx, ty = (x, y) if px else (self.X(x), self.Y(y))
        s = esc(s)
        tr = f' transform="rotate({rot} {tx:.1f} {ty:.1f})"' if rot else ""
        fw = ' font-weight="bold"' if bold else ""
        self.add(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{size}" fill="{cor or C_["txt"]}" '
                 f'text-anchor="{anchor}"{fw}{tr}>{s}</text>')

    def arc(self, hx, hy, r, a0, a1, cor="#333"):
        """Arco de giro de porta: centro (hx,hy), de a0 a a1 graus (anti-horário)."""
        import math
        p0 = (hx + r * math.cos(math.radians(a0)), hy + r * math.sin(math.radians(a0)))
        p1 = (hx + r * math.cos(math.radians(a1)), hy + r * math.sin(math.radians(a1)))
        sweep = 0 if a1 > a0 else 1   # y invertido no SVG
        self.add(f'<path d="M {self.X(p0[0]):.1f} {self.Y(p0[1]):.1f} A {r*S:.1f} {r*S:.1f} 0 0 {sweep} '
                 f'{self.X(p1[0]):.1f} {self.Y(p1[1]):.1f}" fill="none" stroke="{cor}" stroke-width="1.2" '
                 f'stroke-dasharray="6 4"/>')
        self.line(hx, hy, *p1, cor, 2)

    def cota_h(self, x1, x2, y, label, cor="#444", st="conf", dy=-6, size=12):
        yy = self.Y(y)
        self.add(f'<line x1="{self.X(x1):.1f}" y1="{yy:.1f}" x2="{self.X(x2):.1f}" y2="{yy:.1f}" '
                 f'stroke="{cor}" stroke-width="1.3" marker-start="url(#a)" marker-end="url(#a)" {DASH[st]}/>')
        for xx in (x1, x2):
            self.add(f'<line x1="{self.X(xx):.1f}" y1="{yy-7:.1f}" x2="{self.X(xx):.1f}" y2="{yy+7:.1f}" stroke="{cor}"/>')
        self.text(self.X((x1 + x2) / 2), yy + dy, label, size, cor, bold=True, px=True)

    def cota_v(self, y1, y2, x, label, cor="#444", st="conf", dx=-6, size=12):
        xx = self.X(x)
        self.add(f'<line x1="{xx:.1f}" y1="{self.Y(y1):.1f}" x2="{xx:.1f}" y2="{self.Y(y2):.1f}" '
                 f'stroke="{cor}" stroke-width="1.3" marker-start="url(#a)" marker-end="url(#a)" {DASH[st]}/>')
        for yy in (y1, y2):
            self.add(f'<line x1="{xx-7:.1f}" y1="{self.Y(yy):.1f}" x2="{xx+7:.1f}" y2="{self.Y(yy):.1f}" stroke="{cor}"/>')
        self.text(xx + dx, self.Y((y1 + y2) / 2), label, size, cor, bold=True, rot=-90, px=True)

    def save(self, path, panel_lines):
        W = int(self.X(XMAX) + PANEL)
        H = int(self.Y(Y0) + 30)
        px0 = self.X(XMAX) + 10
        body = []
        yy = 130
        for kind, txt in panel_lines:
            if kind == "h":
                yy += 10
                body.append(f'<text x="{px0}" y="{yy}" font-size="15" font-weight="bold">{esc(txt)}</text>')
                yy += 22
            elif kind == "sw":   # swatch: (cor, estilo, rótulo)
                cor, st, lab = txt
                body.append(f'<rect x="{px0}" y="{yy-11}" width="26" height="13" fill="{cor}" stroke="#333" {DASH[st]}/>'
                            f'<text x="{px0+34}" y="{yy}" font-size="12">{esc(lab)}</text>')
                yy += 20
            elif kind == "ln":
                st, lab = txt
                body.append(f'<line x1="{px0}" y1="{yy-4}" x2="{px0+26}" y2="{yy-4}" stroke="#333" stroke-width="2.5" {DASH[st]}/>'
                            f'<text x="{px0+34}" y="{yy}" font-size="12">{esc(lab)}</text>')
                yy += 20
            elif kind == "warn":
                body.append(f'<text x="{px0}" y="{yy}" font-size="12" fill="{C_["pend"]}" font-weight="bold">{esc(txt)}</text>')
                yy += 18
            else:
                body.append(f'<text x="{px0}" y="{yy}" font-size="12" fill="#333">{esc(txt)}</text>')
                yy += 18
        # escala gráfica
        sx, sy = px0, max(yy + 20, H - 70)
        body.append(f'<rect x="{sx}" y="{sy}" width="{S/2}" height="8" fill="#000"/>'
                    f'<rect x="{sx+S/2}" y="{sy}" width="{S/2}" height="8" fill="#fff" stroke="#000"/>'
                    f'<text x="{sx}" y="{sy+24}" font-size="11" text-anchor="middle">0</text>'
                    f'<text x="{sx+S/2}" y="{sy+24}" font-size="11" text-anchor="middle">0,5</text>'
                    f'<text x="{sx+S}" y="{sy+24}" font-size="11" text-anchor="middle">1 m</text>'
                    f'<text x="{sx+S+20}" y="{sy+9}" font-size="11">escala gráfica (1 m = {S} px)</text>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{max(H, sy+50)}" viewBox="0 0 {W} {max(H, sy+50)}" font-family="DejaVu Sans, Arial, sans-serif">
<defs>
<marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="context-stroke"/></marker>
<pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="9" height="9" fill="#ececec"/><line x1="0" y1="0" x2="0" y2="9" stroke="#cfcfcf" stroke-width="3"/></pattern>
<pattern id="rip" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="{C_["ripado"]}"/><line x1="0" y1="0" x2="0" y2="6" stroke="#7a5230" stroke-width="2"/></pattern>
<pattern id="wood" width="40" height="14" patternUnits="userSpaceOnUse"><rect width="40" height="14" fill="#efe6da"/><line x1="0" y1="13.5" x2="40" y2="13.5" stroke="#e2d4c2" stroke-width="1"/><line x1="20" y1="0" x2="20" y2="14" stroke="#e2d4c2" stroke-width="0.6"/></pattern>
</defs>
<rect width="100%" height="100%" fill="#fff"/>
<text x="30" y="42" font-size="22" font-weight="bold">{self.title}</text>
<text x="30" y="66" font-size="13" fill="#555">{self.subtitle}</text>
{chr(10).join(self.el)}
{chr(10).join(body)}
</svg>'''
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8")
        return path


# ---------------------------------------------------------------- ambiente
def ambiente(s: Svg, cotas=True):
    # piso de madeira (novo, colante)
    s.add('<g>')
    pts = [(0, 0), (D, 0), (D, C), (LARG, C), (LARG, E), (0, E)]
    s.add('<polygon points="' + " ".join(f"{s.X(a):.1f},{s.Y(b):.1f}" for a, b in pts) +
          '" fill="url(#wood)"/>')
    s.add('</g>')
    # banheiro (fora do escopo)
    s.rect(D + TC, -T, LARG + T, C - T, "url(#hatch)")
    s.text((D + TC + LARG) / 2, 1.05, "BANHO", 17, bold=True)
    s.text((D + TC + LARG) / 2, 0.86, "fora do escopo", 11, "#666")
    # armário existente
    s.rect(0, E, LARG, E + PROF_ARM, "#e3263a", C_["armario"], 1.5, "est", op=0.18)
    s.line(0, E, LARG, E, C_["armario"], 4)
    s.text(LARG / 2, E + 0.36, "ARMÁRIO EXISTENTE — 4,60 m (parede a parede)", 13, C_["armario"], bold=True)
    s.text(LARG / 2, E + 0.17, "profundidade estimada 0,60 — não interfere no layout", 11, C_["armario"])
    # paredes (espessura estimada)
    W = C_["wall"]
    s.rect(-T, -T, D + TC, 0, W)                         # Parede D
    s.rect(-T, -T, 0, JAN_Y0, W)                         # Parede E E
    s.rect(-T, JAN_Y1, 0, E + PROF_ARM + T, W)           # Parede E D + atrás do armário
    s.rect(D, 0, D + TC, C, W)                           # Parede C
    s.rect(D, C - T, D + TC + BLD, C, W)                 # banheiro L D
    s.rect(D + TC + BLD + PBWC, C - T, LARG, C, W)       # banheiro L E (até a parede leste)
    s.rect(LARG, C - T, LARG + T, C + (FAIXA - PENT) / 2, W)
    s.rect(LARG, C + (FAIXA + PENT) / 2, LARG + T, E + PROF_ARM + T, W)
    s.rect(-T, E + PROF_ARM, LARG + T, E + PROF_ARM + T, W)
    # faixas coloridas como na planta original
    s.line(0, 0.02, D, 0.02, C_["d"], 4)
    s.line(D - 0.02, 0, D - 0.02, C, C_["c"], 4)
    s.line(0.02, 0, 0.02, EE, C_["ee"], 4)
    s.line(0.02, JAN_Y1, 0.02, E, C_["ed"], 4)
    s.line(D, C + 0.02, D + TC + BLD, C + 0.02, C_["bld"], 4)
    s.line(D + TC + BLD + PBWC, C + 0.02, LARG, C + 0.02, C_["ble"], 4, "calc")
    # janela de correr 2 folhas
    for dx in (-T + 0.02, -T / 2, -0.02):
        s.line(dx, JAN_Y0, dx, JAN_Y1, C_["jan"], 1.4)
    s.line(-T / 2 - 0.02, JAN_Y0, -T / 2 - 0.02, (JAN_Y0 + JAN_Y1) / 2 + 0.1, C_["jan"], 3)
    s.line(-T / 2 + 0.02, (JAN_Y0 + JAN_Y1) / 2 - 0.1, -T / 2 + 0.02, JAN_Y1, C_["jan"], 3)
    # porta do banheiro (folha 0,60, abre para dentro do banho, dobradiça à esquerda)
    hx = D + TC + BLD + (PBWC - 0.60) / 2
    s.arc(hx, C - T, 0.60, 0, -90)
    # porta de entrada (folha 0,75) — parede leste, abre para dentro, dobradiça junto ao armário (est.)
    hy = C + (FAIXA + PENT) / 2 - 0.025
    s.arc(LARG, hy, 0.75, 270, 180)
    s.text(LARG + 0.30, C + FAIXA / 2 + 0.02, "ENTRADA", 11, "#333", bold=True, rot=-90)
    # ar-condicionado (Parede C, meio)
    s.rect(D - 0.22, AC_Y - AC_W / 2, D, AC_Y + AC_W / 2, "#cfe6ff", "#3a7bd5", 1.5, "est", op=0.8)
    s.text(D - 0.11, AC_Y, "AR-COND.", 10, "#1d4f91", bold=True, rot=-90)
    # pontos elétricos existentes
    tom = [(D / 2, 0.06), (0.06, (0 + E) / 2)]
    for (x, y) in tom:
        s.add(f'<circle cx="{s.X(x):.1f}" cy="{s.Y(y):.1f}" r="7" fill="#fff" stroke="#000" stroke-width="1.5"/>'
              f'<line x1="{s.X(x)-3:.1f}" y1="{s.Y(y)-3:.1f}" x2="{s.X(x)-3:.1f}" y2="{s.Y(y)+3:.1f}" stroke="#000"/>'
              f'<line x1="{s.X(x)+3:.1f}" y1="{s.Y(y)-3:.1f}" x2="{s.X(x)+3:.1f}" y2="{s.Y(y)+3:.1f}" stroke="#000"/>')
    # ventilador + luz (centro) e luz frente ao banheiro
    fx, fy = D / 2, E / 2
    s.add(f'<circle cx="{s.X(fx):.1f}" cy="{s.Y(fy):.1f}" r="{0.53*S:.1f}" fill="none" stroke="#888" stroke-dasharray="3 4"/>'
          f'<circle cx="{s.X(fx):.1f}" cy="{s.Y(fy):.1f}" r="9" fill="{C_["eletr"]}" stroke="#000"/>')
    s.text(fx, fy - 0.17, "ventilador + luz", 10, "#555")
    lx, ly = D + TC + BLD + PBWC / 2, C + FAIXA / 2
    s.add(f'<circle cx="{s.X(lx):.1f}" cy="{s.Y(ly):.1f}" r="9" fill="{C_["eletr"]}" stroke="#000"/>')
    # norte (Parede D voltada ao norte → norte para baixo no desenho)
    nx, ny = s.X(-0.65), s.Y(-0.55)
    s.add(f'<g transform="translate({nx:.1f},{ny:.1f})"><circle r="24" fill="#fff" stroke="#333"/>'
          f'<polygon points="0,22 -8,-10 0,-4 8,-10" fill="#222"/>'
          f'<text y="40" font-size="13" text-anchor="middle" font-weight="bold">N</text></g>')

    if cotas:
        s.cota_h(0, D, -0.42, "Parede D 2,65 m", C_["d"])
        s.cota_h(0, LARG, E + PROF_ARM + 0.33, "4,60 m (armário parede a parede)", C_["armario"])
        s.cota_v(0, E, -0.40, "Parede E 2,85 m", C_["e"])
        s.cota_v(0, EE, -0.78, "1,10", C_["ee"])
        s.cota_v(JAN_Y0, JAN_Y1, -0.78, "janela 1,45 (calc.)", C_["jan"], "calc")
        s.cota_v(JAN_Y1, E, -0.78, "0,30", C_["ed"])
        s.cota_v(C, E, LARG + 0.55, "0,86", "#444", dx=16)
        s.cota_v(0, C, LARG + 0.55, "Parede C 2,00 m", C_["c"], dx=16)
        s.cota_h(D + TC, D + TC + BLD, C + 0.17, "0,30", C_["bld"], size=11)
        s.cota_h(D + TC + BLD, D + TC + BLD + PBWC, C + 0.17, "0,73", "#444", size=11)


def painel_base():
    return [
        ("h", "LEGENDA"),
        ("ln", ("conf", "Confirmada")),
        ("ln", ("calc", "Calculada")),
        ("ln", ("est", "Estimada")),
        ("sw", (C_["wall"], "conf", "Parede (espessura estimada 12 cm)")),
        ("sw", ("#cfe6ff", "est", "Ar-condicionado existente (larg. est.)")),
        ("sw", (C_["eletr"], "conf", "Ponto de luz existente")),
        ("t", "○ ‖  Tomada existente (meio da Parede D e E)"),
    ]


# ---------------------------------------------------------------- mobiliário
def movel(s, x0, y0, x1, y1, fill, label, sub=None, txt="#fff", st="conf", rot=0, size=12, dy=0.0):
    s.rect(x0, y0, x1, y1, fill, "#111", 1.4, st)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + dy
    s.text(cx, cy + (0.04 if sub else -0.03), label, size, txt, bold=True, rot=rot)
    if sub:
        if rot:
            s.text(cx + 0.14, cy, sub, 10, txt, rot=rot)
        else:
            s.text(cx, cy - 0.13, sub, 10, txt)


def cadeira(s, cx, cy):
    r = 0.30
    s.add(f'<circle cx="{s.X(cx):.1f}" cy="{s.Y(cy):.1f}" r="{r*S:.1f}" fill="none" stroke="#666" stroke-dasharray="4 3"/>')
    s.rect(cx - 0.25, cy - 0.25, cx + 0.25, cy + 0.22, "#3d3f44", "#111", 1.2)
    s.rect(cx - 0.22, cy + 0.20, cx + 0.22, cy + 0.30, "#26282c", "#111", 1)
    s.text(cx, cy - 0.06, "cadeira", 10, "#fff")


def zona(s, x0, y0, x1, y1, label):
    s.rect(x0, y0, x1, y1, C_["circ"], C_["circ"], 1.2, "calc", op=0.10)
    s.text((x0 + x1) / 2, (y0 + y1) / 2, label, 10, C_["circ"], bold=True)


RIP = 0.03          # espessura do painel ripado
GAP = 0.02          # folga mesa ↔ painel (mesa elétrica não pode raspar)
MESA_W, MESA_P = 1.70, 0.70
CAMA_W, CAMA_L = 0.88, 1.88   # solteiro padrão (colchão 88 × 188)


def layout_A():
    s = Svg("Layout A — cama sob a janela · mesa na Parede D  (RECOMENDADO)",
            "Suíte 01 · planta mobiliada preliminar · medidas em metros · v1 (30/10/2026)")
    ambiente(s, cotas=False)
    y_rip = RIP
    # painel ripado em toda a Parede D (fundo da mesa + cabeceira)
    s.rect(0, 0, D, y_rip, "url(#rip)", "#5a3a1e", 1)
    # cama sob a janela
    cx0, cy0 = 0.0, y_rip
    movel(s, cx0, cy0, cx0 + CAMA_W, cy0 + CAMA_L, C_["cama"], "CAMA SOLTEIRO", "88 × 188", rot=-90)
    s.rect(cx0 + 0.06, cy0 + 0.04, cx0 + CAMA_W - 0.06, cy0 + 0.40, "#d9d9d9", "#555", 1)
    # mesa elétrica
    mx0 = D - MESA_W - 0.02
    my0 = y_rip + GAP
    movel(s, mx0, my0, mx0 + MESA_W, my0 + MESA_P, C_["mesa"], "MESA REGULÁVEL", "170 × 70 (alt. 62–127)", dy=0.10)
    # prateleira suspensa (projeção, tracejada)
    s.rect(mx0, y_rip, mx0 + MESA_W, y_rip + 0.25, "none", C_["marc"], 2, "calc")
    s.text(mx0 + MESA_W / 2, y_rip + 0.10 + MESA_P - 0.02, "", 9)
    cadeira(s, mx0 + MESA_W / 2 - 0.15, my0 + MESA_P + 0.38)
    # tapete
    s.rect(1.00, 0.95, 2.45, 2.45, "#2b2b2b", "#2b2b2b", 1, "est", op=0.12)
    zona(s, 0.0, cy0 + CAMA_L, D, E, "")
    s.text(1.32, 2.55, "circulação / acesso ao armário", 10, C_["circ"], bold=True)

    # cotas
    s.cota_h(0, CAMA_W, -0.42, "0,88", C_["cama"])
    s.cota_h(CAMA_W, mx0, -0.42, "0,05", "#444", dy=14, size=10)
    s.cota_h(mx0, mx0 + MESA_W, -0.42, "1,70", C_["mesa"])
    s.cota_h(D - 0.02, D, -0.70, "0,02", "#444", dy=14, size=10)
    s.cota_v(cy0, cy0 + CAMA_L, -0.40, "1,88 (cama)", C_["cama"])
    s.cota_v(cy0 + CAMA_L, E, -0.40, "0,94", "#444")
    s.cota_v(my0, my0 + MESA_P, 2.80, "0,70", C_["mesa"], dx=16)
    s.cota_v(my0 + MESA_P, E, 2.42, "2,10", C_["circ"], "calc", dx=-6)
    s.cota_h(CAMA_W, D, 1.62, "1,77", C_["circ"], "calc")
    s.text(2.25, -0.25, "ripado 3 cm + folga 2 cm", 10, "#5a3a1e")

    painel = painel_base() + [
        ("h", "MÓVEIS (L × P × A, cm)"),
        ("sw", (C_["mesa"], "conf", "Mesa regulável 170 × 70 × 62–127 (a definir)")),
        ("sw", (C_["cama"], "conf", "Cama solteiro 88 × 188 × ~45")),
        ("sw", ("url(#rip)", "conf", "Painel ripado 265 × 3 × 264 (marcenaria)")),
        ("sw", ("#ffffff", "calc", "Prateleira 170 × 25 c/ LED a ~170 cm")),
        ("sw", ("#3d3f44", "conf", "Cadeira ergonômica ~65 × 65")),
        ("sw", ("#d8d8d8", "est", "Tapete 1,50 × 2,00 (opcional)")),
        ("h", "VERIFICAÇÕES"),
        ("t", "✓ Cadeira recua até 1,45 m sem tocar a cama"),
        ("t", "✓ 0,94 m livres entre o pé da cama e o armário"),
        ("t", "✓ Portas de entrada e banheiro livres"),
        ("t", "✓ Tomada da Parede E fica junto à cama"),
        ("t", "✓ Tomada da Parede D fica atrás da mesa"),
        ("t", "✓ Luz natural pela direita de quem está na mesa"),
        ("warn", "⚠ O ar-condicionado sopra em direção à cama:"),
        ("t", "   direcionar as aletas para o centro/teto"),
        ("warn", "⚠ Para abrir a janela é preciso se debruçar na cama"),
        ("warn", "⚠ Recorte no ripado para a tomada da Parede D"),
    ]
    return s.save(ROOT / "layouts" / "layout_A.svg", painel)


def layout_B():
    s = Svg("Layout B — cama na Parede C (sob o ar-condicionado) · mesa na Parede D",
            "Suíte 01 · planta mobiliada preliminar · medidas em metros · v1 (30/10/2026)")
    ambiente(s, cotas=False)
    s.rect(0, 0, D, RIP, "url(#rip)", "#5a3a1e", 1)
    bx0 = D - CAMA_W
    movel(s, bx0, RIP, D, RIP + CAMA_L, C_["cama"], "CAMA SOLTEIRO", "88 × 188", rot=-90)
    s.rect(bx0 + 0.06, RIP + 0.04, D - 0.06, RIP + 0.40, "#d9d9d9", "#555", 1)
    mx0, my0 = 0.02, RIP + GAP
    movel(s, mx0, my0, mx0 + MESA_W, my0 + MESA_P, C_["mesa"], "MESA REGULÁVEL", "170 × 70 (alt. 62–127)", dy=0.10)
    s.rect(mx0, RIP, mx0 + MESA_W, RIP + 0.25, "none", C_["marc"], 2, "calc")
    cadeira(s, mx0 + MESA_W / 2 + 0.10, my0 + MESA_P + 0.38)
    s.rect(0.15, 1.00, 1.70, 2.50, "#2b2b2b", "#2b2b2b", 1, "est", op=0.12)
    zona(s, 0.0, RIP + CAMA_L, D, E, "")
    s.text(1.32, 2.55, "circulação / acesso ao armário", 10, C_["circ"], bold=True)

    s.cota_h(0, mx0, -0.70, "0,02", "#444", dy=14, size=10)
    s.cota_h(mx0, mx0 + MESA_W, -0.42, "1,70", C_["mesa"])
    s.cota_h(mx0 + MESA_W, bx0, -0.42, "0,05", "#444", dy=14, size=10)
    s.cota_h(bx0, D, -0.42, "0,88", C_["cama"])
    s.cota_v(my0, my0 + MESA_P, -0.40, "0,70", C_["mesa"])
    s.cota_v(my0 + MESA_P, E, -0.40, "2,10", C_["circ"], "calc")
    s.cota_v(RIP + CAMA_L, E, 2.45, "0,94", "#444", dx=-6)

    painel = painel_base() + [
        ("h", "MÓVEIS (L × P × A, cm)"),
        ("sw", (C_["mesa"], "conf", "Mesa regulável 170 × 70 × 62–127 (a definir)")),
        ("sw", (C_["cama"], "conf", "Cama solteiro 88 × 188 × ~45")),
        ("sw", ("url(#rip)", "conf", "Painel ripado 265 × 3 × 264 (marcenaria)")),
        ("h", "VERIFICAÇÕES"),
        ("t", "✓ Mesa colada na janela: luz lateral bem próxima"),
        ("t", "✓ Área livre maior junto à janela"),
        ("t", "✓ Quem dorme não fica no jato do ar-condicionado"),
        ("warn", "⚠ O ar-condicionado sopra em quem está na mesa"),
        ("warn", "⚠ Não há tomada junto à cama:"),
        ("t", "   exige extensão ou um ponto elétrico novo"),
        ("warn", "⚠ Manutenção e dreno do ar ficam sobre a cama"),
        ("warn", "⚠ Ao entrar, a cama é a primeira coisa vista"),
    ]
    return s.save(ROOT / "layouts" / "layout_B.svg", painel)


def arquitetonica():
    s = Svg("Suíte 01 — Planta arquitetônica v1 (sem mobiliário)",
            "Geometria atualizada com o levantamento de 30/10/2026 · medidas em metros · pé-direito 2,64 m")
    ambiente(s, cotas=True)
    s.text(D / 2, 1.85, "SUÍTE 01", 22, bold=True)
    s.text(D / 2, 1.68, "área livre principal 2,65 × 2,85 = 7,55 m²", 11, "#444")
    s.text((D + LARG) / 2 + 0.05, C + 0.72, "faixa de entrada ≈ 1,66 m²", 10, "#444")
    painel = painel_base() + [
        ("h", "DADOS DO LEVANTAMENTO"),
        ("t", "Pé-direito: 2,64 m (conf.)"),
        ("t", "Janela: correr, 2 folhas · peitoril 1,00 m"),
        ("t", "   altura 1,20 m · largura 1,45 m (calc.)"),
        ("t", "   persiana de enrolar metálica externa"),
        ("t", "Porta de entrada: 0,80 c/ batente · folha 0,75"),
        ("t", "Porta do banheiro: 0,73 c/ batente · folha 0,60"),
        ("t", "Norte: a Parede D está voltada ao norte"),
        ("t", "   → a janela da Parede E fica a LESTE (sol da manhã)"),
        ("t", "Piso: madeira colante nova (fora do orçamento)"),
        ("h", "PENDÊNCIAS / INCONSISTÊNCIAS"),
        ("warn", "⚠ 2,65 + parede + 0,30 + 0,73 + 1,10 = 4,78 + parede"),
        ("t", "   ultrapassa os 4,60 m. O trecho 1,10 foi desenhado"),
        ("t", "   até 4,60. Não afeta a área mobiliável."),
        ("warn", "⚠ Espessura das paredes: estimada"),
        ("warn", "⚠ Sentido de abertura da porta de entrada: estimado"),
        ("warn", "⚠ Largura do ar-condicionado: estimada (0,85)"),
        ("t", "Parede E 2,85 × (2,00 + 0,86 = 2,86): 1 cm de"),
        ("t", "   diferença, dentro da tolerância"),
    ]
    return s.save(ROOT / "planta_arquitetonica_v1.svg", painel)


if __name__ == "__main__":
    for f in (arquitetonica(), layout_A(), layout_B()):
        print(f)
