"""Gera a entrega do projeto em partes .zip independentes (cada uma abre sozinha; extraia todas na mesma pasta).

Uso: python3 ENTREGA/gerar_zip.py
O GitHub não aceita arquivos acima de 100 MB, por isso o projeto (≈ 300 MB) é dividido em partes de até 90 MB.
Ficam de fora apenas arquivos regeneráveis ou temporários: backups .blend1, versões antigas em 05_BLENDER/versoes,
renders de teste (_teste), cache Python e arquivos de configuração do editor.
"""
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PROJ = RAIZ / "PROJETO_QUARTO_ESCRITORIO"
SAIDA = RAIZ / "ENTREGA"
LIMITE = 90 * 1024 * 1024
NOME = "Suite01_quarto_escritorio"

LEIAME = """SUÍTE 01 — PROJETO QUARTO + ESCRITÓRIO (entrega em {n} partes)

1. Baixe TODAS as partes ({nomes}).
2. Extraia todas na MESMA pasta (no Windows: botão direito > Extrair tudo, escolhendo a mesma pasta de destino).
   Cada parte é um .zip normal; juntas formam a pasta PROJETO_QUARTO_ESCRITORIO completa.
3. Abra:
   - PROJETO_QUARTO_ESCRITORIO/08_VISUALIZADOR_3D/index.html  → apresentação, modelo 3D e temas/layouts
   - PROJETO_QUARTO_ESCRITORIO/09_TOUR_360/index.html         → tour 360° (escolha o tema no canto superior)
   - PROJETO_QUARTO_ESCRITORIO/07_DOCUMENTACAO/               → resumo, lista de compras, temas, validações
   - PROJETO_QUARTO_ESCRITORIO/04_ORCAMENTO/orcamento_completo.xlsx
   - PROJETO_QUARTO_ESCRITORIO/05_BLENDER/quarto_escritorio_realista.blend (Blender 5.2)
   As páginas usam bibliotecas da internet (three.js, model-viewer): abra com internet. Alguns navegadores bloqueiam
   o modelo 3D aberto direto do disco; nesse caso use um servidor local: na pasta do projeto, "python -m http.server"
   e acesse http://localhost:8000/08_VISUALIZADOR_3D/
4. Renders na qualidade máxima (GPU): veja 07_DOCUMENTACAO/temas_e_layouts.md ("Como gerar qualquer combinação").
"""


def fora(p: Path) -> bool:
    r = p.relative_to(RAIZ).as_posix()
    return (p.suffix == ".blend1" or "/_teste/" in f"/{r}/" or "__pycache__" in r or "/05_BLENDER/versoes/" in f"/{r}"
            or ".impeccable" in r or p.name == ".directory")


def main():
    arquivos = sorted(f for f in PROJ.rglob("*") if f.is_file() and not fora(f))
    partes, atual, tam = [], [], 0
    for f in arquivos:
        s = f.stat().st_size
        if atual and tam + s > LIMITE:
            partes.append(atual)
            atual, tam = [], 0
        atual.append(f)
        tam += s
    partes.append(atual)
    for z in SAIDA.glob(f"{NOME}_parte*.zip"):
        z.unlink()
    nomes = [f"{NOME}_parte{i+1}_de_{len(partes)}.zip" for i in range(len(partes))]
    texto = LEIAME.format(n=len(partes), nomes=", ".join(nomes))
    (SAIDA / "LEIA-ME.txt").write_text(texto, encoding="utf-8")
    for i, (lista, nome) in enumerate(zip(partes, nomes)):
        with zipfile.ZipFile(SAIDA / nome, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            if i == 0:
                z.writestr("LEIA-ME.txt", texto)
            for f in lista:
                z.write(f, f.relative_to(RAIZ).as_posix())
        mb = (SAIDA / nome).stat().st_size / 1024 / 1024
        print(f"{nome}: {len(lista)} arquivos, {mb:.1f} MB")
    print("TOTAL", len(arquivos), "arquivos em", len(partes), "partes")


if __name__ == "__main__":
    main()
