# O que foi feito até agora — Fases A a F

Atualizado em 31/10/2026. Projeto: Suíte 01 (quarto + escritório).

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
| Econômico | R$ 7.708 | R$ 771 | **R$ 8.479** | R$ 3.621 |
| Equilibrado | R$ 12.095 | R$ 1.209 | **R$ 13.304** | R$ 6.887 |
| Premium | R$ 20.486 | R$ 2.049 | **R$ 22.535** | R$ 10.799 |

*Valores atualizados em 31/10/2026 (Fase E). Incluem a categoria "Decoração (opcional)", com preços estimados:
R$ 756 / R$ 1.080 / R$ 1.728. Sem ela, o Equilibrado fica em ≈ R$ 12.117 com a reserva.*

A planilha tem fórmulas: mude quantidades e preços (em azul) e os totais se recalculam. A aba
**Quantitativos** calcula áreas, galões de tinta, metros de LED e barras de perfil. Os totais foram
conferidos recalculando as fórmulas de forma independente.

**Quantitativos principais:** 15,0 m² de paredes grafite (3 demãos → 2 galões), 9,2 m² de teto
(2 demãos → 1 galão), 7,0 m² de ripado e 5,3 m de fita LED com os nichos (2 rolos; o Premium usa 7,9 m, também 2 rolos).

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
- **Validação (Fase D):** 35 de 35 verificações OK depois de duas correções reais (posição do PC e comprimento do tapete),
  aplicadas também na planta 2D. Detalhes em `07_DOCUMENTACAO/validacao_tecnica.md`.

## Fase E — Decoração e PC sobre a mesa (31/10/2026)

Plano aprovado em 30/10 (`plano_decoracao_pc.md`), implementado nesta sessão (em nuvem, com o mesmo Blender 5.2.3
instalado como módulo Python `bpy`; o Blender MCP não está disponível aqui).

- **Interferência corrigida:** o notebook cruzava o monitor esquerdo. Os monitores foram 6 cm para a esquerda no braço
  e o notebook foi para a frente, num suporte baixo (folga de 2,5 cm).
- **PC sobre a mesa:** gabinete 23 × 45 × 46 cm com vidro na frente e na lateral e 3 fans com anel de LED 3000 K, no
  canto direito do tampo. Com a mesa no máximo, o topo fica a 1,64 m (prateleira a 1,95 m). O suporte suspenso saiu do
  modelo e do orçamento.
- **Marcenaria:** 3 nichos iluminados de 24 × 26 × 16 cm sobre a cabeceira (base a 1,55 m, 0,93 m acima do colchão),
  com vaso, elefante de madeira e escultura de baleia (Poly Haven, escalados pelas medidas reais).
- **Decoração:** 3 quadros P&B na Parede E (antes da janela) e 2 pequenos na prateleira; samambaia em vaso pendente
  (base a 1,95 m) sobre a circulação; luminária de mesa 2700 K, suporte de headphone, caneca, relógio LED e a planta
  média movida para a prateleira.
- **Validação:** 58 de 58 verificações OK, incluindo as novas (`validacao_tecnica.md`).
- **Atualizados:** plantas 2D (mobiliada, iluminação, elevação da Parede D), orçamento (XLSX, CSV, gráficos), lista de
  compras (agora gerada por `04_ORCAMENTO/fonte/gerar_lista_compras.py`), planta de iluminação (L5 nichos,
  L6 luminária de mesa), renders, panoramas do tour 360°, modelo do
  visualizador 3D e créditos.
- **Renders desta rodada:** feitos em CPU (sem GPU na nuvem), com qualidade reduzida: vistas com 96 amostras e
  panoramas 360° com 2048 × 1024 px e 64 amostras. Para a qualidade final, rode no desktop (GPU RX 6750 XT) sem as
  opções `--amostras`/`--largura`: os padrões dos scripts continuam 256 amostras e 4096 px.
- **Passe de realismo (31/10/2026, a pedido):** telas com conteúdo real renderizado no Chromium (editor de código,
  planta do projeto num visualizador de PDF, e-mail no notebook) com orientação corrigida (sem espelhamento);
  headphone modelado (arco, conchas e almofadas); fans do PC com 7 pás, moldura e anel de LED; cooler torre e
  memórias dentro do gabinete; samambaia pendente com 6 touceiras caindo pela borda de um vaso cônico com terra
  (ponta mais baixa das folhas a 1,92 m; o vaso continua com a base a 1,95 m); vidro com reflexo nos quadros; cabos
  dos monitores, do PC e da luminária descendo até a tomada; caneca com café e alça; relógio com dígitos sempre acesos; teclado e touchpad no notebook; cúpula aberta com lâmpada na luminária.
  Três defeitos achados nos testes e corrigidos: luminárias apagadas apareciam pretas de dia (agora mostram o
  difusor branco leitoso); a luz pontual dentro do PC estourava as peças em branco
  (removida) e as luzes apareciam como discos para a câmera (agora só as peças emissivas aparecem).
- **Preços da decoração:** estimados. A Amazon não está liberada na rede desta sessão; pesquisar antes de comprar.

## Fase F — Temas, layouts e decoração (31/10/2026)

- **6 temas** sobre o mesmo quarto e as mesmas medidas: Moderno Escuro Aconchegante (o aprovado), Escandinavo
  Claro, Japandi, Industrial Urbano, Botânico Verde e Terracota Mediterrâneo. Cada um troca paredes (com textura real
  de reboco pintado, cal, cimento queimado ou argila), madeira do ripado e da marcenaria (freijó, carvalho, freixo,
  nogueira), roupa de cama, almofadas, tapete, persiana, acabamento das luminárias, temperatura do LED, quadros e os
  objetos dos nichos.
- **3 layouts** que cabem de verdade: A (aprovado), B (cama na Parede C, mesa junto à janela) e C (mesa de frente para a
  janela, cama ao longo do ripado). Três outros arranjos foram descartados com motivo (página e
  `temas_e_layouts.md`). Na troca de layout a mesa é rearranjada para o PC ficar longe da cabeceira, e cabos, planta de
  chão e planta pendente vão para posições válidas do layout.
- **Decoração nova em todos os temas:** persiana romana de linho (recolhida de dia, baixada à noite), duas almofadas,
  planta de chão no "canto morto" de cada layout, luminária de braço articulado (modelo real) e, conforme o tema,
  cesto de vime sob a mesa, vaso alto, livros de capa dura ou planta na prateleira.
- **Validação por layout** (`validacao_layouts.json`), com folgas medidas no modelo: mesa × cama, mesa × paredes,
  circulação até o armário, recuo da cadeira, PC × cabeceira, janela, ar-condicionado, faixa de entrada, arco das
  portas do armário, nichos, plantas, tapete, luminária e tomada usada. Os pontos de atenção estão na página.
- **Realismo:** texturas na escala real da amostra (dado da API do Poly Haven); cor final das paredes e tecidos igual ao
  hex da paleta (a textura vira só relevo/variação); exposição ajustada por tema (paredes claras refletem mais).
- **Página de apresentação:** nova seção *Temas, layouts e decoração* em `08_VISUALIZADOR_3D/index.html`, com escolha de
  tema, layout e dia/noite, paleta com códigos, materiais, decoração, custo estimado do pacote, prós e contras, planta
  vista de cima e a verificação completa do layout.
- **Correção achada no caminho:** o porta-lápis da mesa ficava dentro do gabinete do PC (sobra de antes de o PC ir para
  o tampo). Foi removido.
