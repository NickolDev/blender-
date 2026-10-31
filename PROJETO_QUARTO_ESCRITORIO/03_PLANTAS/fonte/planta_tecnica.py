"""Desenhos técnicos da versão para aprovação (Layout A, cenário Equilibrado).

Gera em 03_PLANTAS/:
  planta_mobiliada_cotada.svg   — vista superior com cotas de móveis, afastamentos e circulação
  iluminacao.svg                — pontos existentes + iluminação proposta (sem pontos elétricos novos)
  elevacoes/elevacao_parede_D.svg — ripado, mesa, prateleira, cama, LED e alturas
"""
from planta_v1 import (C_, CAMA_L, CAMA_W, D, DASH, E, GAP, RIP, ROOT, S, Svg, ambiente, cadeira, movel,
                       painel_base, zona, PE)

MESA_W, MESA_P = 1.70, 0.70
MX0 = D - MESA_W - 0.02            # 0,93
MY0 = RIP + GAP                    # 0,05
PRAT_P, PRAT_H = 0.25, 1.95        # prateleira: profundidade e altura da face inferior
LED_V_X = (CAMA_W + MX0) / 2       # perfil vertical no vão de 5 cm entre cama e mesa
ARAND_X, ARAND_H = 0.44, 1.10
# PC sobre o tampo, canto direito (gabinete com vidro frontal e lateral −x): 23 × 45 × 46 cm
PC_X0, PC_Y0, PC_W, PC_P, PC_H = 2.37, 0.12, 0.23, 0.45, 0.46
CPU_X0 = PC_X0
MON_CX = 1.72                      # centro dos monitores no braço (6 cm à esquerda do centro da mesa)
NB = (0.97, 0.42, 1.29, 0.66)      # notebook em suporte baixo, na frente à esquerda (x0, y0, x1, y1)
NICHOS_X0, NICHO_W, NICHO_H, NICHO_P, NICHO_Z0, NICHO_GAP = 0.06, 0.24, 0.26, 0.16, 1.55, 0.02
TOM_D = D / 2
CAMA_H = 0.62
TAP = (1.08, 0.78, 2.48, 2.78)     # tapete 1,40 × 2,00 (x0, y0, x1, y1) — 7 cm livres até o armário


def mobiliada():
    s = Svg("Planta mobiliada cotada — Layout A · cenário Equilibrado",
            "Suíte 01 · versão para aprovação · medidas em metros (móveis em cm na tabela) · 30/10/2026")
    ambiente(s, cotas=False)
    s.rect(0, 0, D, RIP, "url(#rip)", "#5a3a1e", 1)
    s.rect(*TAP, "#2b2b2b", "#2b2b2b", 1, "est", op=0.12)
    movel(s, 0, RIP, CAMA_W, RIP + CAMA_L, C_["cama"], "CAMA (1)", "88 × 188", rot=-90)
    s.rect(0.06, RIP + 0.04, CAMA_W - 0.06, RIP + 0.40, "#d9d9d9", "#555", 1)
    movel(s, MX0, MY0, MX0 + MESA_W, MY0 + MESA_P, C_["mesa"], "MESA (2)", "170 × 70", dy=0.10)
    s.rect(MX0, RIP, MX0 + MESA_W, RIP + PRAT_P, "none", C_["marc"], 2, "calc")
    s.rect(PC_X0, PC_Y0, PC_X0 + PC_W, PC_Y0 + PC_P, "#2a2a2a", "#e0e0e0", 1.5)
    s.text(PC_X0 + PC_W / 2, PC_Y0 + PC_P / 2, "PC", 9, "#fff", bold=True)
    s.rect(*NB, "none", "#777", 1.0, "est")
    s.text((NB[0] + NB[2]) / 2, (NB[1] + NB[3]) / 2, "notebook", 8, "#777")
    for k in range(3):
        nx = NICHOS_X0 + k * (NICHO_W + NICHO_GAP)
        s.rect(nx, RIP, nx + NICHO_W, RIP + NICHO_P, "none", C_["marc"], 1.5, "calc")
    cadeira(s, MX0 + MESA_W / 2 - 0.10, MY0 + MESA_P + 0.38)
    zona(s, 0.0, RIP + CAMA_L, D, E, "")
    s.text(1.32, 2.55, "circulação / acesso ao armário", 10, C_["circ"], bold=True)
    # cotas horizontais (abaixo)
    s.cota_h(0, CAMA_W, -0.42, "0,88", C_["cama"])
    s.cota_h(CAMA_W, MX0, -0.42, "0,05", "#444", dy=14, size=10)
    s.cota_h(MX0, MX0 + MESA_W, -0.42, "1,70", C_["mesa"])
    s.cota_h(MX0 + MESA_W, D, -0.70, "0,02", "#444", dy=14, size=10)
    s.cota_h(0, D, -0.98, "2,65 (Parede D)", C_["d"])
    # cotas verticais
    s.cota_v(RIP, RIP + CAMA_L, -0.40, "1,88", C_["cama"])
    s.cota_v(RIP + CAMA_L, E, -0.40, "0,94", "#444")
    s.cota_v(0, RIP, -0.70, "", "#5a3a1e")
    s.cota_v(MY0, MY0 + MESA_P, 2.80, "0,70", C_["mesa"], dx=16)
    s.cota_v(0, MY0, 3.05, "0,05", "#444", dx=16, size=10)
    s.cota_v(MY0 + MESA_P, E, 2.42, "2,10", C_["circ"], "calc")
    s.cota_h(CAMA_W, D, 1.62, "1,77", C_["circ"], "calc")
    s.text(0.95, -0.25, "ripado 3 cm + folga 2 cm", 10, "#5a3a1e", anchor="start")
    painel = painel_base() + [
        ("h", "MOBILIÁRIO (L × P × A, cm)"),
        ("sw", (C_["cama"], "conf", "(1) Cama box solteiro 88 × 188 × 62")),
        ("sw", (C_["mesa"], "conf", "(2) Mesa regulável 170 × 70 × 73–118")),
        ("sw", ("#ffffff", "calc", "(3) Prateleira 170 × 25 · face inferior a 195")),
        ("sw", ("url(#rip)", "conf", "(4) Ripado 265 × 3 × 264 (piso → teto)")),
        ("sw", ("#3d3f44", "conf", "(5) Cadeira — base ~65 (est.)")),
        ("sw", ("#2a2a2a", "conf", "(6) PC sobre a mesa 23 × 45 × 46 (vidro)")),
        ("sw", ("#d8d8d8", "est", "(7) Tapete 140 × 200")),
        ("sw", ("#ffffff", "calc", "(8) 3 nichos 24 × 26 × 16 sobre a cabeceira")),
        ("h", "VERIFICAÇÕES"),
        ("t", "✓ Cadeira recua até ~1,50 m; 1,35 m livres até o armário"),
        ("t", "✓ 0,94 m entre o pé da cama e o armário"),
        ("t", "✓ Portas de entrada e do banheiro sem interferência"),
        ("t", "✓ A mesa sobe e desce sem tocar no ripado (folga de 2 cm)"),
        ("t", "✓ O PC fica longe da cabeceira (ruído/luz)"),
        ("t", "✓ PC no tampo: topo a 1,64 m com a mesa no máximo"),
        ("t", "   (< 1,95 da prateleira); carga ≈ 64 kg < 80 kg"),
        ("t", "✓ Notebook à frente: não cruza o monitor esquerdo"),
        ("warn", "⚠ Braço do monitor: fixar pelo FURO no tampo"),
        ("t", "   (a presilha de borda não cabe na folga de 2 cm)"),
    ]
    return s.save(ROOT / "planta_mobiliada_cotada.svg", painel)


def iluminacao():
    s = Svg("Planta de iluminação e pontos elétricos — proposta",
            "Suíte 01 · usa apenas os pontos existentes · fitas de LED 24 V em baixa tensão · 30/10/2026")
    ambiente(s, cotas=False)
    s.rect(0, 0, D, RIP, "url(#rip)", "#5a3a1e", 1)
    s.rect(0, RIP, CAMA_W, RIP + CAMA_L, "#eeeeee", "#aaa", 1, "est")
    s.rect(MX0, MY0, MX0 + MESA_W, MY0 + MESA_P, "#f4f4f4", "#aaa", 1, "est")
    s.text(MX0 + 0.20, MY0 + 0.60, "mesa", 10, "#999")
    s.text(CAMA_W / 2, 1.2, "cama", 10, "#999", rot=-90)
    amb = "#e08a00"
    # LED sob a prateleira
    s.line(MX0 + 0.03, RIP + 0.20, MX0 + MESA_W - 0.03, RIP + 0.20, amb, 5)
    s.text(MX0 + MESA_W - 0.10, RIP + 0.27, "L1", 12, amb, bold=True)
    # LED vertical
    s.add(f'<circle cx="{s.X(LED_V_X):.1f}" cy="{s.Y(RIP/2):.1f}" r="7" fill="{amb}" stroke="#000"/>')
    s.text(LED_V_X + 0.02, -0.30, "L2 · perfil vertical 2,40 m", 10, amb, bold=True, anchor="middle")
    # light bar
    s.line(MX0 + 0.45, MY0 + 0.42, MX0 + 1.25, MY0 + 0.42, "#6250d6", 4)
    s.text(MX0 + 0.85, MY0 + 0.48, "L3", 12, "#6250d6", bold=True)
    # arandela
    s.add(f'<circle cx="{s.X(ARAND_X):.1f}" cy="{s.Y(0.08):.1f}" r="8" fill="#fff" stroke="{amb}" stroke-width="3"/>')
    s.text(ARAND_X, 0.62, "L4 · arandela h 1,10", 10, amb, bold=True, rot=-90)
    # fonte/filtro
    fx, fy = TOM_D + 0.25, MY0 + 0.10
    s.rect(fx - 0.10, fy - 0.04, fx + 0.12, fy + 0.04, "#333", "#000", 1)
    s.text(fx + 0.20, fy - 0.02, "F", 12, "#333", bold=True)
    # fiação
    def fio(pts, cor="#555"):
        d = " ".join(f"{'M' if i == 0 else 'L'} {s.X(x):.1f} {s.Y(y):.1f}" for i, (x, y) in enumerate(pts))
        s.add(f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    fio([(TOM_D, 0.06), (fx - 0.10, fy)])
    fio([(fx, fy), (fx, RIP + 0.20)])
    fio([(fx - 0.10, fy - 0.02), (LED_V_X, MY0 + 0.05), (LED_V_X, RIP / 2)])
    fio([(0.06, E / 2), (0.30, E / 2), (0.30, 0.12), (ARAND_X, 0.08)], "#999")
    painel = painel_base() + [
        ("h", "ILUMINAÇÃO PROPOSTA (tudo em 3000 K)"),
        ("t", "Geral: ventilador c/ luz existente → lâmpada LED 3000 K"),
        ("t", "L1  Fita COB 24 V sob a prateleira — tarefa/ambiente"),
        ("t", "L2  Fita COB em perfil vertical no ripado — decorativa"),
        ("t", "L3  Barra de luz no monitor — tarefa, sem reflexo na tela"),
        ("t", "L4  Arandela articulada na cabeceira — leitura"),
        ("t", "F   Filtro c/ DPS + fonte 24 V presos sob o tampo"),
        ("t", "L1 + L2 dimerizáveis por controle Wi-Fi (cena “noite”)"),
        ("h", "ALIMENTAÇÃO (sem pontos novos)"),
        ("t", "Tomada Parede D → filtro c/ DPS → PC, monitores, fonte LED"),
        ("t", "Tomada Parede E → arandela + carregador da cama"),
        ("t", "Tomada D recebe prolongador de caixa (ripado de 3 cm)"),
        ("warn", "⚠ Conferir com eletricista: circuito e bitola da"),
        ("t", "   tomada D (PC + 2 monitores + LED ≈ 600–900 W)"),
        ("warn", "⚠ Fonte 24 V sempre ventilada e acessível"),
    ]
    return s.save(ROOT / "iluminacao.svg", painel)


def elevacao_D():
    """Elevação da Parede D vista de dentro do quarto (de frente para o norte)."""
    from planta_v1 import PANEL
    import planta_v1 as pv
    s = Svg("Elevação da Parede D (vista de dentro do quarto)",
            "Ripado piso → teto · mesa na altura sentada (73 cm) e máxima (118 cm) · medidas em metros")
    # reaproveita a classe Svg mudando os limites do desenho: x = largura da parede, y = altura
    pv.X0, pv.Y0, pv.XMAX, pv.YMAX = -0.95, -0.55, 3.55, 2.95
    # parede invertida: na vista de dentro, a Parede E (x=0) fica à DIREITA? Não — olhando para o norte
    # (Parede D), a Parede E (leste) fica à direita. Espelha x para manter a leitura real.
    W = D
    xm = lambda x: W - x
    s.rect(-0.12, -0.10, W + 0.12, 0, "#3b3b3b")                       # piso (laje)
    s.rect(-0.12, PE, W + 0.12, PE + 0.08, "#3b3b3b")                   # teto
    s.rect(-0.12, 0, 0, PE, "#3b3b3b")
    s.rect(W, 0, W + 0.12, PE, "#3b3b3b")
    s.rect(0, 0, W, PE, "url(#rip)", "#5a3a1e", 1)
    # LED vertical
    s.rect(xm(LED_V_X) - 0.012, 0.10, xm(LED_V_X) + 0.012, 2.50, "#ffb46b", "#e08a00", 1)
    # cama (vista lateral da cabeceira: largura 0,88)
    s.rect(xm(CAMA_W), 0, xm(0), CAMA_H, C_["cama"], "#111", 1.4)
    s.rect(xm(CAMA_W) + 0.06, CAMA_H, xm(0) - 0.06, CAMA_H + 0.16, "#d9d9d9", "#555", 1)
    s.text(xm(CAMA_W / 2), 0.30, "CAMA 0,88", 11, "#fff", bold=True)
    # arandela
    s.add(f'<circle cx="{s.X(xm(ARAND_X)):.1f}" cy="{s.Y(ARAND_H):.1f}" r="9" fill="#fff" stroke="#e08a00" stroke-width="3"/>')
    # tomada D
    s.rect(xm(TOM_D) - 0.05, 0.27, xm(TOM_D) + 0.05, 0.33, "#fff", "#000", 1.2, "est")
    s.text(xm(TOM_D), 0.38, "tomada", 9, "#fff", bold=True)
    # mesa sentada
    x0, x1 = xm(MX0 + MESA_W), xm(MX0)
    s.rect(x0, 0.705, x1, 0.73, "#b8875a", "#5a3a1e", 1.2)
    for lx in (x0 + 0.25, x1 - 0.25):
        s.rect(lx - 0.03, 0, lx + 0.03, 0.705, "#1a1a1a")
    s.rect(x0, 1.155, x1, 1.18, "none", "#5a3a1e", 1.2, "calc")
    # monitores (2 × 27" ≈ 61 × 36 cm) em braço, altura sentada
    for cx in (xm(MON_CX) - 0.32, xm(MON_CX) + 0.32):
        s.rect(cx - 0.305, 0.90, cx + 0.305, 1.26, "#222", "#000", 1)
    s.text(xm(MON_CX), 1.30, "2 × 27\" (posição sentada)", 10, "#222")
    # PC sobre o tampo (posição sentada) e contorno na altura máxima
    s.rect(xm(PC_X0 + PC_W), 0.73, xm(PC_X0), 0.73 + PC_H, "#2a2a2a", "#000", 1.2)
    s.text(xm(PC_X0 + PC_W / 2), 0.73 + PC_H / 2, "PC", 10, "#fff", bold=True)
    s.rect(xm(PC_X0 + PC_W), 1.18, xm(PC_X0), 1.18 + PC_H, "none", "#666", 1.0, "calc")
    # nichos iluminados sobre a cabeceira
    for k in range(3):
        nx = NICHOS_X0 + k * (NICHO_W + NICHO_GAP)
        s.rect(xm(nx + NICHO_W), NICHO_Z0, xm(nx), NICHO_Z0 + NICHO_H, "#1a1a1a", C_["marc"], 1.4)
        s.line(xm(nx + NICHO_W) + 0.02, NICHO_Z0 + NICHO_H - 0.015, xm(nx) - 0.02, NICHO_Z0 + NICHO_H - 0.015, "#ffb46b", 3)
    # prateleira + LED
    s.rect(x0, PRAT_H, x1, PRAT_H + 0.025, "#b8875a", "#5a3a1e", 1.2)
    s.line(x0 + 0.03, PRAT_H - 0.01, x1 - 0.03, PRAT_H - 0.01, "#ffb46b", 4)
    # cotas
    s.cota_h(0, W, -0.30, "2,65", C_["d"])
    s.cota_h(x0, x1, PE + 0.22, "mesa / prateleira 1,70", C_["mesa"])
    s.cota_h(xm(CAMA_W), xm(0), PE + 0.22, "0,88", C_["cama"])
    s.cota_v(0, PE, -0.78, "pé-direito 2,64", "#333")
    s.cota_v(0, 0.73, -0.14, "0,73", "#5a3a1e")
    s.cota_v(0, 1.18, -0.34, "1,18 máx.", "#5a3a1e", "calc")
    s.cota_v(0, PRAT_H, -0.56, "1,95 prateleira", C_["marc"])
    s.cota_v(0, CAMA_H, W + 0.30, "0,62", C_["cama"], dx=16)
    s.cota_v(0, ARAND_H, W + 0.55, "1,10 arandela", "#e08a00", dx=16)
    s.text(0.0, -0.50, "← Parede C (ar-condicionado)", 11, "#555", anchor="start")
    s.text(W, -0.50, "Parede E (janela) →", 11, "#555", anchor="end")
    painel = [
        ("h", "ELEMENTOS"),
        ("sw", ("url(#rip)", "conf", "Ripado freijó 2,65 × 2,64, fundo preto")),
        ("sw", ("#ffb46b", "conf", "LED 3000 K: vertical + sob a prateleira")),
        ("sw", ("#b8875a", "conf", "Tampo 170 × 70 × 2,5 / prateleira 170 × 25")),
        ("sw", (C_["cama"], "conf", "Cama box 88 × 188 × 62")),
        ("ln", ("calc", "Tampo na altura máxima (1,18)")),
        ("h", "VERIFICAÇÕES DE ALTURA"),
        ("t", "✓ Mesa no máximo (118) + monitor (~51 acima do"),
        ("t", "   tampo) = ~1,69 < 1,95 da prateleira"),
        ("t", "✓ Prateleira acima da cabeça de quem está em pé"),
        ("t", "   junto à mesa (padrão 1,80–1,85)"),
        ("t", "✓ Arandela a 1,10: ~45 cm acima do colchão"),
        ("t", "✓ O ar-condicionado (Parede C) não toca a prateleira"),
        ("t", "✓ PC no máximo: topo 1,64 < 1,95 da prateleira"),
        ("t", "✓ Nichos 1,55–1,81: 0,93 m acima do colchão"),
        ("warn", "⚠ Altura da tomada: medir antes de cortar o ripado"),
        ("warn", "⚠ Monitores desenhados como referência (27\" ≈ 61 × 36)"),
    ]
    p = s.save(ROOT / "elevacoes" / "elevacao_parede_D.svg", painel)
    pv.X0, pv.Y0, pv.XMAX, pv.YMAX = -1.05, -1.15, 5.45, 4.15
    return p


if __name__ == "__main__":
    for f in (mobiliada(), iluminacao(), elevacao_D()):
        print(f)
