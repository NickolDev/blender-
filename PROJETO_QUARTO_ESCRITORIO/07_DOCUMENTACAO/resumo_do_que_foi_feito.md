# O que foi feito até agora — Fases A, B e C

Atualizado em 30/10/2026. Projeto: Suíte 01 (quarto + escritório).

## Fase A — Levantamento da planta

1. **Ferramentas verificadas.** O Blender não está conectado (precisa estar aberto com o add-on MCP para a
   Fase D). Poly Haven e Sketchfab não têm integração MCP, mas as APIs públicas respondem. Para PDF/PNG
   usei `rsvg-convert` e `magick`, que já estavam instalados. Para planilha e gráficos criei um ambiente
   Python isolado (fora da pasta do projeto) com `openpyxl` e `matplotlib`.
2. **Planta original analisada.** A imagem **não está em escala** (cada cota dá uma escala diferente),
   então só valem as medidas escritas. Reconstruí a planta em 2D com as medidas classificadas em
   confirmadas, calculadas e estimadas.
3. **Suas respostas incorporadas:** pé-direito de 2,64 m, armário existente de parede a parede, janela de
   correr com peitoril de 1,00 m, portas, faixa de 0,86 m, pontos de luz e tomadas, ar-condicionado no meio
   da Parede C e Parede D voltada ao norte (a janela fica a leste e recebe sol da manhã).

## Fase B — Conceito e layout

1. **Leitura das 8 referências** → conceito **"Moderno Escuro Aconchegante"**: paredes grafite, ripado de
   freijó, tampo de madeira sobre estrutura preta e LED âmbar de 3000 K. Moodboard em
   `02_ANALISE/moodboard.png`.
2. **Layouts comparados.** No A, a cama fica sob a janela e a mesa na Parede D. No B, a cama fica sob o
   ar-condicionado. Uma terceira opção, com a mesa na Parede C, foi descartada: o ar ficaria sobre os
   monitores e a janela atrás de quem usa a mesa.
3. **Recomendado: Layout A.** Usa a tomada existente junto à cama (sem elétrica nova), deixa a área da
   entrada livre e aproveita o blackout da persiana.

## Fase C — Projeto técnico e orçamento

> Como você pediu para seguir, adotei as opções recomendadas: **Layout A, cama de solteiro, paredes
> grafite, tapete incluído, sem gaveteiro**. Tudo isso pode ser trocado antes da modelagem 3D.

### Desenhos (`03_PLANTAS/`)
- `planta_arquitetonica.pdf` — ambiente sem móveis.
- `planta_mobiliada_cotada.pdf/.png` — cada móvel com largura, profundidade, afastamentos e circulação.
- `iluminacao.pdf` — pontos existentes + iluminação nova, **sem nenhum ponto elétrico novo**.
- `elevacoes/elevacao_parede_D.pdf` — ripado, mesa (73 e 118 cm), prateleira a 1,95 m, cama e arandela.

**Ajuste técnico feito no caminho:** a prateleira subiu para **1,95 m**. Na altura de 1,70 m, ela bateria
nos monitores com a mesa regulável no ponto máximo.

### Pesquisa de produtos (`04_ORCAMENTO/produtos_e_fornecedores.csv`)
Preços consultados em 30/10/2026 na Pichau e na Amazon Brasil, com link de cada item. O Mercado Livre
pediu verificação de conta e não foi usado. Cada preço está marcado como:
- **Pesquisado (página do produto)** — preço e ficha técnica conferidos.
- **Pesquisado (listagem)** — preço conferido na busca da loja.
- **Estimativa** — marcenaria e mão de obra, com base em faixas de mercado citadas na planilha.

### Orçamento (`04_ORCAMENTO/orcamento_completo.xlsx`)
| Cenário | Itens | Reserva 10% | **Total** | Parte estimada |
|---|---:|---:|---:|---:|
| Econômico | R$ 6.609 | R$ 661 | **R$ 7.270** | R$ 2.565 |
| Equilibrado | R$ 10.563 | R$ 1.056 | **R$ 11.620** | R$ 5.357 |
| Premium | R$ 18.258 | R$ 1.826 | **R$ 20.083** | R$ 8.371 |

A planilha tem fórmulas: mude quantidades e preços (em azul) e os totais se recalculam. A aba
**Quantitativos** calcula áreas, galões de tinta, metros de LED e barras de perfil. Os totais foram
conferidos recalculando as fórmulas de forma independente.

**Quantitativos principais:** 15,0 m² de paredes grafite (3 demãos → 2 galões), 9,2 m² de teto
(2 demãos → 1 galão), 7,0 m² de ripado e 4,5 m de fita LED (1 rolo; o Premium usa 7,2 m, 2 rolos).

## O que precisa de profissional habilitado
- Conferir o circuito e a bitola da tomada da Parede D (PC + monitores + LED).
- Recorte do ripado na tomada e instalação do prolongador de caixa.
- Fixação da prateleira e do ripado: verificar o tipo de parede (alvenaria ou drywall) antes de furar.

## Fase D — Modelo 3D no Blender

- **Integração:** o Blender MCP não conectou (o Blender não estava aberto e o servidor não conhece o
  caminho do executável). Usei o **mesmo Blender 5.2.3** de `~/Downloads` em modo background, com scripts
  Python `bpy`. O resultado é o mesmo `.blend` editável. A renderização usa a GPU **AMD RX 6750 XT (HIP)**.
- **Cenário modelado:** Layout A, cenário Equilibrado. As medidas são importadas dos mesmos scripts das
  plantas 2D.
- **Arquivo:** `05_BLENDER/quarto_escritorio.blend`, com as coleções 01_ESTRUTURA a 08_COTAS_REFERENCIAS,
  objetos nomeados em português e cada móvel selecionável. Versões intermediárias ficam em `05_BLENDER/versoes/`.
- **Scripts:** `construir_cena.py` (gera a cena), `renderizar.py` (vistas dia/noite) e `validar_cena.py` (auditoria).
- **Materiais:** Poly Haven CC0 (freijó, piso, tecidos) + tintas procedurais. HDRIs de dia e de noite vistos pela janela.
- **Sketchfab:** não usado (exige token). Todos os móveis foram modelados com as medidas reais.
- **Validação:** 35 de 35 verificações OK depois de duas correções reais (posição do PC e comprimento do tapete),
  aplicadas também na planta 2D. Detalhes em `07_DOCUMENTACAO/validacao_tecnica.md`.
