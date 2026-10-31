"""Gera as artes dos quadros de cada tema (SVG com textura de papel) e rasteriza no Chromium (Playwright).

Uso: python3 gerar_artes_temas.py   (precisa de node + playwright)
Saída: assets/arte_temas/*.svg e assets/textures/<id>.jpg (A 40×55, B e C 36×26, D 20×25, E 15×20 — proporções reais)
"""
import os
import subprocess
from pathlib import Path

A = Path(__file__).resolve().parents[1] / "assets"
SVG, JPG = A / "arte_temas", A / "textures"
TAM = {"A": (400, 550), "B": (360, 260), "C": (360, 260), "D": (200, 250), "E": (150, 200)}


def papel(fundo, grao=0.06):
    return (f'<defs><filter id="p"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="4"/>'
            f'<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {grao} 0"/></filter>'
            f'<filter id="tinta"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="9"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="6"/></filter></defs>'
            f'<rect width="100%" height="100%" fill="{fundo}"/>')


def folha(cx, cy, l, w, ang, cor, nerv="#00000033"):
    return (f'<g transform="translate({cx},{cy}) rotate({ang})"><path d="M0,0 C{w},{-l*0.25} {w*0.8},{-l*0.8} 0,{-l} '
            f'C{-w*0.8},{-l*0.8} {-w},{-l*0.25} 0,0Z" fill="{cor}"/><path d="M0,0 L0,{-l*0.95}" stroke="{nerv}" stroke-width="1.5"/></g>')


ARTES = {
    # Escandinavo: traço fino, sálvia e mostarda sobre off-white
    "esc_A": lambda w, h: papel("#F1EEE8") + '<circle cx="230" cy="210" r="110" fill="#A9B5A0"/>'
             '<path d="M70,470 C120,300 210,420 250,260 S360,180 330,90" fill="none" stroke="#1E1E1E" stroke-width="3"/>'
             '<circle cx="140" cy="380" r="34" fill="#C9A24A"/>',
    "esc_B": lambda w, h: papel("#F1EEE8") + '<circle cx="150" cy="130" r="70" fill="#A9B5A0"/><circle cx="215" cy="130" r="70" fill="#C9A24A" opacity=".85"/>',
    "esc_C": lambda w, h: papel("#F1EEE8") + '<path d="M20,200 Q100,90 180,170 T340,140" fill="none" stroke="#1E1E1E" stroke-width="2.5"/>'
             '<path d="M20,215 Q110,130 190,190 T340,170" fill="none" stroke="#8E9C84" stroke-width="2"/>',
    "esc_D": lambda w, h: papel("#F1EEE8") + folha(100, 210, 150, 45, 0, "none") + '<path d="M100,210 C150,160 140,90 100,60 C60,90 50,160 100,210Z" fill="none" stroke="#1E1E1E" stroke-width="2.5"/>',
    "esc_E": lambda w, h: papel("#F1EEE8") + '<path d="M35,170 L35,90 A40,40 0 0 1 115,90 L115,170Z" fill="#A9B5A0"/>',
    # Japandi: tinta sumi sobre papel de arroz, carimbo vermelho
    "jap_A": lambda w, h: papel("#EFE8DC", .08) + '<g filter="url(#tinta)"><path d="M200,120 A120,120 0 1 1 112,158" fill="none" stroke="#1C1B19" stroke-width="26" stroke-linecap="round"/></g>'
             '<rect x="300" y="450" width="28" height="28" fill="#A8382B"/>',
    "jap_B": lambda w, h: papel("#EFE8DC", .08) + '<g filter="url(#tinta)"><path d="M40,140 C120,120 220,150 320,128" fill="none" stroke="#1C1B19" stroke-width="18" stroke-linecap="round"/></g>',
    "jap_C": lambda w, h: papel("#EFE8DC", .08) + '<ellipse cx="130" cy="180" rx="60" ry="30" fill="#2B2A28"/><ellipse cx="215" cy="190" rx="40" ry="20" fill="#5A5650"/>'
             '<ellipse cx="270" cy="196" rx="24" ry="12" fill="#8A847A"/>',
    "jap_D": lambda w, h: papel("#EFE8DC", .08) + '<g filter="url(#tinta)"><path d="M100,230 L100,30 M100,120 C130,100 150,95 170,100 M100,80 C70,60 50,55 35,60" fill="none" stroke="#1C1B19" stroke-width="7" stroke-linecap="round"/></g>',
    "jap_E": lambda w, h: papel("#EFE8DC", .08) + '<g filter="url(#tinta)"><circle cx="75" cy="95" r="45" fill="none" stroke="#1C1B19" stroke-width="10"/></g>',
    # Industrial: gráfico P&B, concreto e malha
    "ind_A": lambda w, h: papel("#E9E9E7", .1) + ''.join(f'<rect x="{30+i*48}" y="{550-hh}" width="40" height="{hh}" fill="{c}"/>'
             for i, (hh, c) in enumerate([(220, "#1A1A1A"), (360, "#3A3A3A"), (280, "#1A1A1A"), (420, "#555"), (300, "#2A2A2A"),
                                         (240, "#1A1A1A"), (330, "#444")])) + '<line x1="0" y1="120" x2="400" y2="120" stroke="#1A1A1A" stroke-width="2"/>',
    "ind_B": lambda w, h: papel("#E9E9E7", .1) + '<rect x="40" y="40" width="130" height="180" fill="#1A1A1A"/><rect x="190" y="40" width="130" height="85" fill="#8A8A86"/>'
             '<rect x="190" y="135" width="130" height="85" fill="none" stroke="#1A1A1A" stroke-width="4"/>',
    "ind_C": lambda w, h: papel("#E9E9E7", .1) + ''.join(f'<line x1="{20+i*16}" y1="40" x2="{20+i*16}" y2="220" stroke="#1A1A1A" stroke-width="{1+(i%4)}"/>' for i in range(21)),
    "ind_D": lambda w, h: papel("#E9E9E7", .1) + '<circle cx="100" cy="125" r="62" fill="none" stroke="#1A1A1A" stroke-width="10"/><rect x="38" y="63" width="124" height="124" fill="none" stroke="#1A1A1A" stroke-width="3"/>',
    "ind_E": lambda w, h: papel("#E9E9E7", .1) + '<rect x="25" y="30" width="100" height="140" fill="#2A2A2A"/><rect x="45" y="50" width="60" height="100" fill="#8A8A86"/>',
    # Botânico: gravuras de folhas sobre creme
    "bot_A": lambda w, h: papel("#EEE8DA") + folha(200, 500, 420, 150, 0, "#3F5A3C", "#EEE8DA") + folha(200, 470, 260, 90, -38, "#5E7A55", "#EEE8DA")
             + folha(205, 470, 260, 90, 38, "#5E7A55", "#EEE8DA"),
    "bot_B": lambda w, h: papel("#EEE8DA") + ''.join(folha(60 + i * 40, 230 - i * 6, 90, 22, 30 - i * 3, "#4C6646") for i in range(7)),
    "bot_C": lambda w, h: papel("#EEE8DA") + '<path d="M30,200 C120,150 220,140 330,80" fill="none" stroke="#4C3B2A" stroke-width="3"/>'
             + ''.join(f'<ellipse cx="{60+i*45}" cy="{185-i*16}" rx="16" ry="11" fill="#7D9B8A"/>' for i in range(6)),
    "bot_D": lambda w, h: papel("#EEE8DA") + folha(100, 225, 190, 60, 0, "#3F5A3C", "#EEE8DA"),
    "bot_E": lambda w, h: papel("#EEE8DA") + folha(75, 175, 140, 40, 10, "#6E8B5E", "#EEE8DA"),
    # Terracota: arcos e sol
    "ter_A": lambda w, h: papel("#EFE3D0") + '<path d="M80,550 L80,260 A120,120 0 0 1 320,260 L320,550Z" fill="#B87458"/>'
             '<circle cx="200" cy="300" r="55" fill="#E3B062"/><path d="M80,550 L80,450 Q200,390 320,450 L320,550Z" fill="#6E6B3E"/>',
    "ter_B": lambda w, h: papel("#EFE3D0") + '<circle cx="180" cy="150" r="60" fill="#D9934E"/><path d="M0,260 L0,190 Q90,140 180,185 T360,170 L360,260Z" fill="#9C4F2E"/>',
    "ter_C": lambda w, h: papel("#EFE3D0") + ''.join(f'<path d="M{40+i*75},220 L{40+i*75},120 A30,30 0 0 1 {100+i*75},120 L{100+i*75},220Z" fill="{c}"/>'
             for i, c in enumerate(["#B87458", "#6E6B3E", "#D9934E", "#9C4F2E"])),
    "ter_D": lambda w, h: papel("#EFE3D0") + '<path d="M30,200 A70,70 0 0 1 170,200Z" fill="#B87458"/><line x1="20" y1="215" x2="180" y2="215" stroke="#4A3022" stroke-width="3"/>',
    "ter_E": lambda w, h: papel("#EFE3D0") + '<path d="M30,180 L30,90 A45,45 0 0 1 120,90 L120,180Z" fill="#6E6B3E"/><circle cx="75" cy="95" r="18" fill="#E3B062"/>',
}


def main():
    SVG.mkdir(parents=True, exist_ok=True)
    tarefas = []
    for nome, f in ARTES.items():
        w, h = TAM[nome[-1]]
        corpo = f(w, h) + '<rect width="100%" height="100%" filter="url(#p)"/>'
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{corpo}</svg>'
        (SVG / f"{nome}.svg").write_text(svg, encoding="utf-8")
        tarefas.append((str(SVG / f"{nome}.svg"), str(JPG / f"{nome}.png"), w, h))
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();for(const [s,o,w,h] of "
          + str(tarefas).replace("(", "[").replace(")", "]") + "){const p=await b.newPage({viewport:{width:w,height:h},"
          "deviceScaleFactor:2});await p.goto('file://'+s);await p.screenshot({path:o});await p.close();}await b.close();})();")
    raiz = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["node", "-e", js], check=True, env={**os.environ, "NODE_PATH": raiz})
    for _, png, _, _ in tarefas:
        subprocess.run(["convert", png, "-quality", "90", png[:-4] + ".jpg"], check=True)
        Path(png).unlink()
    print("ARTES", len(tarefas))


if __name__ == "__main__":
    main()
