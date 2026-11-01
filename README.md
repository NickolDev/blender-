# Suíte 01 — projeto de quarto + escritório

Projeto de interiores completo para transformar um quarto de 2,65 × 2,85 m (pé-direito 2,64 m) em quarto e
escritório: planta e medidas, layout, marcenaria, iluminação, orçamento, lista de compras, modelo 3D no Blender,
renders, tour 360° e 6 temas de decoração × 3 layouts.

## Por onde começar

| O quê | Onde |
|---|---|
| Apresentação (modelo 3D, renders, temas e layouts, lista de compras) | `PROJETO_QUARTO_ESCRITORIO/08_VISUALIZADOR_3D/index.html` |
| Tour 360° (escolha o tema no canto superior) | `PROJETO_QUARTO_ESCRITORIO/09_TOUR_360/index.html` |
| Resumo de tudo o que foi feito | `PROJETO_QUARTO_ESCRITORIO/07_DOCUMENTACAO/resumo_do_que_foi_feito.md` |
| Lista de compras (cenário Equilibrado) | `PROJETO_QUARTO_ESCRITORIO/07_DOCUMENTACAO/lista_compras.md` |
| Temas, layouts, validações e compras por tema | `PROJETO_QUARTO_ESCRITORIO/07_DOCUMENTACAO/temas_e_layouts.md` |
| Orçamento com fórmulas (3 cenários) | `PROJETO_QUARTO_ESCRITORIO/04_ORCAMENTO/orcamento_completo.xlsx` |
| Plantas e elevação (PDF/PNG) | `PROJETO_QUARTO_ESCRITORIO/03_PLANTAS/` |
| Cena do Blender 5.2 | `PROJETO_QUARTO_ESCRITORIO/05_BLENDER/quarto_escritorio_realista.blend` |

As páginas usam three.js e model-viewer da internet. Alguns navegadores não carregam o modelo 3D aberto direto do
disco: nesse caso, rode `python -m http.server` dentro de `PROJETO_QUARTO_ESCRITORIO` e abra
`http://localhost:8000/08_VISUALIZADOR_3D/`.

## Baixar tudo

- **Pelo GitHub:** botão *Code → Download ZIP* (um arquivo só).
- **Pela pasta `ENTREGA/`:** o projeto em partes `.zip` de até 90 MB (o GitHub não aceita arquivos maiores). Cada
  parte abre sozinha; extraia todas na mesma pasta. Instruções em `ENTREGA/LEIA-ME.txt`.

## Gerar de novo

Tudo é gerado por scripts a partir das mesmas medidas (`03_PLANTAS/fonte/`):

- `05_BLENDER/scripts/construir_cena.py` → cena base; `validar_cena.py` → auditoria dimensional (58 itens)
- `05_BLENDER/scripts/realismo.py` → camada de realismo; `renderizar.py` / `renderizar_360.py` → renders
- `05_BLENDER/scripts/variantes.py` → qualquer tema × layout (ex.: `-- --tema japandi --layout C --render dia,noite`)
- `04_ORCAMENTO/fonte/gerar_orcamento.py` → planilha, CSV e gráficos; `gerar_lista_compras.py` → lista de compras
- `05_BLENDER/scripts/gerar_html_temas.py` → dados da página e documento de temas

Os renders deste repositório foram feitos em CPU. Na GPU do desktop, rode os scripts sem `--amostras`/`--res` para a
qualidade máxima.
