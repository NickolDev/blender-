"""Gera as cópias em .js que deixam as páginas funcionarem abertas direto do disco (file://).

Aberto do disco, o navegador bloqueia (CORS) o que as páginas leem com WebGL ou fetch: os panoramas do
tour 360° e o modelo 3D da apresentação. Scripts ele aceita. Então cada arquivo ganha uma cópia .js com o
conteúdo embutido em base64, e as páginas só usam essas cópias quando estão em file://. Num servidor
(http/https) elas continuam lendo os .jpg e o quarto.json.

  09_TOUR_360/pano/<caminho>.jpg  ->  09_TOUR_360/pano/js/<caminho>.js
  08_VISUALIZADOR_3D/quarto.glb   ->  08_VISUALIZADOR_3D/quarto_modelo.js

Uso: python3 gerar_arquivos_offline.py   (rode de novo depois de renderizar panoramas ou exportar o modelo)
"""
import base64
from pathlib import Path

PROJ = Path(__file__).resolve().parent
PANO = PROJ / "09_TOUR_360" / "pano"
PANO_JS = PANO / "js"
GLB = PROJ / "08_VISUALIZADOR_3D" / "quarto.glb"
MODELO_JS = PROJ / "08_VISUALIZADOR_3D" / "quarto_modelo.js"


def b64(arquivo):
    return base64.b64encode(arquivo.read_bytes()).decode("ascii")


def gravar(destino, conteudo):
    if not destino.exists() or destino.read_text(encoding="ascii") != conteudo:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudo, encoding="ascii")


def panoramas():
    feitos = set()
    for jpg in sorted(PANO.rglob("*.jpg")):
        rel = jpg.relative_to(PANO)
        if rel.parts[0] == "js":
            continue
        js = PANO_JS / rel.with_suffix(".js")
        gravar(js, f'window.__PANO && window.__PANO("pano/{rel.as_posix()}", "data:image/jpeg;base64,{b64(jpg)}");\n')
        feitos.add(js)
    orfaos = [f for f in PANO_JS.rglob("*.js") if f not in feitos]
    for f in orfaos:
        f.unlink()
    print(f"tour: {len(feitos)} panoramas em {PANO_JS} ({len(orfaos)} órfãos removidos)")


def modelo():
    gravar(MODELO_JS, f'window.__MODELO_GLB = "{b64(GLB)}";\n')
    print(f"apresentação: modelo em {MODELO_JS} ({MODELO_JS.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    panoramas()
    modelo()
