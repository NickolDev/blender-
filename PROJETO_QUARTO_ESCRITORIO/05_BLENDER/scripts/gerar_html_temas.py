"""Injeta os dados de temas/layouts na página de apresentação e gera as miniaturas.

Uso: python3 gerar_html_temas.py   (depois de renderizar as variantes com variantes.py)
Lê temas_dados.py e 07_DOCUMENTACAO/validacao_layouts.json; escreve o bloco entre /*TEMAS-DADOS-INICIO*/ e
/*TEMAS-DADOS-FIM*/ em 08_VISUALIZADOR_3D/index.html e cria 08_VISUALIZADOR_3D/temas/mini/*.jpg (480 × 300).
"""
import json
import re
import subprocess
from pathlib import Path

from temas_dados import DESCARTADOS, LAYOUTS, TEMAS

PROJ = Path(__file__).resolve().parents[2]
HTML = PROJ / "08_VISUALIZADOR_3D" / "index.html"
TEMAS_DIR = PROJ / "08_VISUALIZADOR_3D" / "temas"
VALID = PROJ / "07_DOCUMENTACAO" / "validacao_layouts.json"
CAMPOS_T = ("nome", "resumo", "paleta", "materiais", "decoracao", "custo_extra")
CAMPOS_L = ("nome", "curto", "resumo", "pros", "contras")


def main():
    faltando = [f"{t}_{L}_{m}.jpg" for t in TEMAS for L in LAYOUTS for m in ("dia", "noite")
                if not (TEMAS_DIR / f"{t}_{L}_{m}.jpg").exists()]
    faltando += [f"planta_{L}.jpg" for L in LAYOUTS if not (TEMAS_DIR / f"planta_{L}.jpg").exists()]
    if faltando:
        print("AVISO: imagens faltando:", ", ".join(faltando))
    mini = TEMAS_DIR / "mini"
    mini.mkdir(exist_ok=True)
    for f in sorted(TEMAS_DIR.glob("*_*_*.jpg")):
        subprocess.run(["convert", str(f), "-resize", "480x300", "-quality", "78", str(mini / f.name)], check=True)
    dados = {
        "temas": {k: {c: v[c] for c in CAMPOS_T} for k, v in TEMAS.items()},
        "layouts": {k: {c: v[c] for c in CAMPOS_L} for k, v in LAYOUTS.items()},
        "descartados": DESCARTADOS,
        "validacao": json.loads(VALID.read_text(encoding="utf-8")) if VALID.exists() else {},
    }
    bloco = "/*TEMAS-DADOS-INICIO*/\nconst TD = " + json.dumps(dados, ensure_ascii=False) + ";\n/*TEMAS-DADOS-FIM*/"
    html = HTML.read_text(encoding="utf-8")
    novo, n = re.subn(r"/\*TEMAS-DADOS-INICIO\*/.*?/\*TEMAS-DADOS-FIM\*/", lambda m: bloco, html, flags=re.S)
    if n != 1:
        raise SystemExit("marcadores não encontrados no index.html")
    HTML.write_text(novo, encoding="utf-8")
    print("HTML OK", HTML, "miniaturas", len(list(mini.glob("*.jpg"))))
    escrever_md(dados)


def brl(v):
    return f"{v:,}".replace(",", ".")


def escrever_md(dados):
    L = ["# Temas, layouts e decoração", "",
         "Gerado por `05_BLENDER/scripts/gerar_html_temas.py` a partir de `temas_dados.py` e da validação de cada layout.",
         "As imagens ficam em `08_VISUALIZADOR_3D/temas/` e aparecem na página de apresentação (seção *Temas, layouts e decoração*).",
         "", "## Como gerar qualquer combinação",
         "", "```", "blender -b 05_BLENDER/quarto_escritorio_realista.blend --python 05_BLENDER/scripts/variantes.py -- \\",
         "    --tema japandi --layout C --render dia,noite,planta [--salvar]", "```",
         "`--salvar` grava um .blend editável em `05_BLENDER/temas/`. Sem GPU, use `--res 1280x800 --amostras 48`.",
         "", "## Temas", ""]
    for k, t in TEMAS.items():
        L += [f"### {t['nome']} (`{k}`)", "", t["resumo"], "",
              "Paleta: " + " · ".join(f"{n} `{c}`" for n, c in t["paleta"]), "",
              "Materiais: " + "; ".join(t["materiais"]) + ".", "",
              "Decoração: " + "; ".join(t["decoracao"]) + ".", "",
              f"Pacote de decoração (estimativa, fora a obra já orçada): R$ {brl(t['custo_extra'][0])} – "
              f"R$ {brl(t['custo_extra'][1])}", ""]
    L += ["## Layouts", ""]
    for k, l in LAYOUTS.items():
        V = dados["validacao"].get(k, [])
        n = {st: sum(r["status"] == st for r in V) for st in ("OK", "ATENÇÃO", "FALHA")}
        L += [f"### {l['nome']}", "", l["resumo"], "", "A favor:", *[f"- {x}" for x in l["pros"]], "", "Contra:",
              *[f"- {x}" for x in l["contras"]], "",
              f"Verificação no modelo 3D: **{n['OK']} OK, {n['ATENÇÃO']} atenção, {n['FALHA']} falha(s)**", "",
              "| Status | Verificação | Medição |", "|---|---|---|",
              *[f"| {r['status']} | {r['verificacao']} | {r['detalhe']} |" for r in V], ""]
    L += ["## Arranjos descartados", "", *[f"- **{n}:** {m}" for n, m in DESCARTADOS], ""]
    destino = PROJ / "07_DOCUMENTACAO" / "temas_e_layouts.md"
    destino.write_text("\n".join(L), encoding="utf-8")
    print("MD OK", destino)


if __name__ == "__main__":
    main()
