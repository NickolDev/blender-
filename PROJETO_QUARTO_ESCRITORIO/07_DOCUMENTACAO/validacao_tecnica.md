# Validação técnica — modelo 3D × planta × orçamento

Executada em 31/10/2026 pelo script `05_BLENDER/scripts/validar_cena.py`, que **reabre o .blend em um processo novo** e mede os objetos (caixas envolventes com modificadores aplicados). Resultado: **58 de 58 verificações OK**.

Esta rodada inclui as verificações do plano "decoração + PC na mesa": PC dentro do tampo, PC × monitor, PC × prateleira com a mesa no máximo, notebook × monitor, nichos acima do colchão, planta pendente, quadros fora da janela e acessórios dentro do tampo. (Rodada feita na sessão em nuvem, com o mesmo Blender 5.2.3 instalado como módulo `bpy`; por isso o caminho do arquivo abaixo é o do servidor.)

## Verificações automáticas

| Status | Verificação | Medição |
|---|---|---|
| ✅ OK | Piso do quarto 2,65 × 2,85 | medido (2.65, 2.85, 0.02) m · esperado (2.65, 2.85, 0.02) m |
| ✅ OK | Pé-direito 2,64 m | face inferior do teto em z = 2.640 |
| ✅ OK | Peitoril da janela a 1,00 m | topo do peitoril z = 1.000 |
| ✅ OK | Janela com 1,20 m de altura | verga em z = 2.200 |
| ✅ OK | Tampo da mesa 170 × 70 × 2,5 | medido (1.7, 0.7, 0.025) m · esperado (1.7, 0.7, 0.025) m |
| ✅ OK | Mesa na posição da planta | canto em (0.930, 0.050) · planta (0.930, 0.050) |
| ✅ OK | Altura do tampo (sentado) 0,73 | z = 0.730 |
| ✅ OK | Cama 88 × 188 × 62 | medido (0.88, 1.88, 0.62) |
| ✅ OK | Prateleira 170 × 25 × 2,5 | medido (1.7, 0.25, 0.025) m · esperado (1.7, 0.25, 0.025) m |
| ✅ OK | Prateleira a 1,95 m | face inferior z = 1.950 |
| ✅ OK | Ripas dentro dos 2,65 m da Parede D | ripas de x = 0.0075 a 2.6175 |
| ✅ OK | Fundo do ripado 2,65 × 2,64 | medido (2.65, 0.012, 2.64) m · esperado (2.65, 0.012, 2.64) m |
| ✅ OK | Tapete 140 × 200 | medido (1.4, 2.0, 0.008) m · esperado (1.4, 2.0, 0.008) m |
| ✅ OK | Mesa × ripado (mesa elétrica não pode raspar) | folga 2.0 cm (mínimo 1.9 cm) |
| ✅ OK | Mesa × cama (partes rígidas; planta = 5 cm) | folga 5.0 cm (mínimo 4.9 cm) |
| ✅ OK | Roupa de cama abaixo do tampo na altura mínima (sem contato) | topo da roupa de cama 0.685 m · face inferior do tampo ≥ 0.705 m |
| ✅ OK | Mesa × Parede C | folga 2.0 cm (mínimo 1.9 cm) |
| ✅ OK | PC dentro do tampo (x, y) e apoiado nele | PC x 2.370–2.600, y 0.120–0.570, base z 0.730 · tampo x 0.930–2.630, y 0.050–0.750, z 0.730 |
| ✅ OK | Gabinete 23 × 45 × 46 (com pés) | medido (0.23, 0.45, 0.46) |
| ✅ OK | PC × monitor direito | folga 2.8 cm (mínimo 2.0 cm) |
| ✅ OK | PC × coluna do braço dos monitores | folga 33.8 cm (mínimo 2.0 cm) |
| ✅ OK | PC × prateleira com a mesa no máximo (1,18) | topo do PC no máximo = 1.640 m · prateleira = 1.95 m |
| ✅ OK | Notebook × monitor esquerdo | folga 2.5 cm (mínimo 1.0 cm) |
| ✅ OK | Notebook × teclado | folga 23.0 cm (mínimo 2.0 cm) |
| ✅ OK | Luminária de mesa × monitor esquerdo | folga 2.8 cm (mínimo 2.0 cm) |
| ✅ OK | Luminária de mesa × notebook | folga 2.6 cm (mínimo 2.0 cm) |
| ✅ OK | Caneca × mousepad | folga 3.0 cm (mínimo 1.0 cm) |
| ✅ OK | Headphone × PC | folga 5.0 cm (mínimo 2.0 cm) |
| ✅ OK | Suporte_headphone dentro do tampo | x 2.450–2.550, y 0.620–0.720 |
| ✅ OK | Caneca dentro do tampo | x 2.260–2.340, y 0.620–0.700 |
| ✅ OK | Luminaria_mesa dentro do tampo | x 0.950–1.070, y 0.060–0.336 |
| ✅ OK | Nichos ≥ 0,90 m acima do colchão | base dos nichos z = 1.550 · colchão 0.62 → 0.930 m |
| ✅ OK | Nichos dentro da largura da cama (sobre a cabeceira) | x 0.060–0.820 · cama 0–0.88 |
| ✅ OK | Nichos × perfil de LED vertical | folga 8.4 cm (mínimo 5.0 cm) |
| ✅ OK | Nichos × arandela | folga 34.7 cm (mínimo 30.0 cm) |
| ✅ OK | Planta pendente com a base ≥ 1,95 m | base do vaso z = 1.950 |
| ✅ OK | Planta pendente × ventilador | folga 61.8 cm (mínimo 30.0 cm) |
| ✅ OK | Quadros da Parede E antes da janela (y < 1,10) | quadros até y = 0.940 · janela começa em y = 1.100 |
| ✅ OK | Quadros × nichos | folga 3.5 cm (mínimo 2.0 cm) |
| ✅ OK | Itens da prateleira dentro dela | x 1.580–2.140, y até 0.171 |
| ✅ OK | Cadeira × cama | folga 46.5 cm (mínimo 5.0 cm) |
| ✅ OK | Cama × face das portas do armário (partes rígidas; planta = 0,94) | folga 94.0 cm (mínimo 93.9 cm) |
| ✅ OK | Cama × puxadores do armário (puxadores estimados, 1,5 cm) | folga 92.5 cm (mínimo 92.0 cm) |
| ✅ OK | Roupa de cama × armário (circulação real) | folga 89.5 cm (mínimo 85.0 cm) |
| ✅ OK | Cama × Parede E | folga 0.0 cm (mínimo 0.0 cm) |
| ✅ OK | Ar-condicionado × prateleira | folga 29.5 cm (mínimo 10.0 cm) |
| ✅ OK | Cadeira × armário (circulação atrás da cadeira) | folga 137.3 cm (mínimo 100.0 cm) |
| ✅ OK | Monitores na altura da elevação (0,90–1,265 sentado) | monitores de z = 0.900 a 1.265 |
| ✅ OK | Monitores no eixo do braço (6 cm à esquerda do centro da mesa) | centro x = 1.720 · braço 1.720 · mesa 1.780 |
| ✅ OK | Monitores × prateleira com a mesa no máximo (1,18) | topo dos monitores no máximo = 1.715 m · prateleira = 1.95 m |
| ✅ OK | Cama abaixo do peitoril (janela operável) | topo da cama+travesseiros = 0.999 m |
| ✅ OK | Cama fora da faixa de entrada (x > 2,65, y 2,00–2,86) | x máx 0.915, y máx 1.940 |
| ✅ OK | Mesa_Tampo_Freijo_170x70x2_5 fora da faixa de entrada (x > 2,65, y 2,00–2,86) | x máx 2.630, y máx 0.750 |
| ✅ OK | Cadeira fora da faixa de entrada (x > 2,65, y 2,00–2,86) | x máx 2.020, y máx 1.462 |
| ✅ OK | Tapete_140x200 fora da faixa de entrada (x > 2,65, y 2,00–2,86) | x máx 2.480, y máx 2.780 |
| ✅ OK | Texturas e HDRIs encontrados (caminhos relativos) | faltando: nenhum |
| ✅ OK | Arquivo .blend reaberto em processo novo | /home/user/blender-/PROJETO_QUARTO_ESCRITORIO/05_BLENDER/quarto_escritorio.blend |
| ✅ OK | Coleções 01–08 presentes | 01_ESTRUTURA, 02_PORTAS_JANELAS, 03_MOBILIARIO, 04_MARCENARIA, 05_ILUMINACAO, 06_DECORACAO, 07_CAMERAS, 08_COTAS_REFERENCIAS |

## Correções feitas durante a validação

1. **PC × perna da mesa (interferência real).** O suporte do PC desenhado em x = 2,33 m colidia com a perna direita da estrutura (x ≈ 2,38). O PC foi movido para entre as pernas (x = 2,08); sobram 0,88 m para os joelhos. A planta 2D foi corrigida junto.
2. **Tapete.** Estava desenhado com 1,98 m, mas o produto tem 2,00 m. Corrigido na planta e no 3D; ficam 7 cm até o armário.
3. **Notebook × monitor esquerdo (31/10/2026, interferência real).** No modelo anterior o notebook no suporte (x 0,98–1,30, tela até z ≈ 1,04) cruzava o monitor esquerdo (x 1,16–1,78, z 0,90–1,265); a validação antiga não testava isso. Os monitores foram deslocados 6 cm para a esquerda no braço (eixo x = 1,72) e o notebook foi para a frente, num suporte baixo (y 0,42–0,66). Folga atual: 2,5 cm.
4. **PC sobre a mesa (31/10/2026).** O suporte suspenso saiu do projeto e do orçamento. O gabinete (23 × 45 × 46) fica no canto direito do tampo, a 2,8 cm do monitor direito; com a mesa no máximo, o topo fica a 1,64 m (prateleira a 1,95 m).
5. **Cama × armário.** A cota da planta (0,94 m) é medida até a face das portas. Os puxadores (estimados) reduzem para 0,925 m e a roupa de cama, para 0,895 m. A circulação continua confortável.

## Consistência entre planta, orçamento e 3D

- As medidas do 3D são **importadas dos mesmos módulos Python** que desenham as plantas (`03_PLANTAS/fonte/planta_v1.py` e `planta_tecnica.py`), então as duas fontes não divergem.
- Todos os itens do cenário **Equilibrado** que aparecem no 3D estão no orçamento: mesa (estrutura + tampo), cadeira, cama, braço ELG, ripado, prateleira, nichos, fita LED + perfis, barra de luz, arandela, tapete, suporte de notebook e filtro de linha (sob o tampo, não modelado).
- Itens no 3D que **não** estão no orçamento: armário (existente), ar-condicionado (existente), piso e rodapé (fora do escopo, por combinação), monitores/PC/notebook (do usuário) e livros/papelaria (ilustrativos). A decoração escolhida entra no orçamento como "Decoração (opcional)", com preço estimado.

## Não verificado / limitações (não classificar como verificado)

- **Abertura das portas do armário:** o tipo de porta (correr ou abrir) não foi informado. Com portas de abrir de cerca de 77 cm, a folha invade a área da cama e da cadeira quando aberta: **verificar no local**.
- **Altura real das tomadas, espessura das paredes, largura do ar-condicionado e sentido da porta de entrada:** continuam estimados.
- **Cadeira:** o fabricante não declara as dimensões; foi usado o volume de uma cadeira ergonômica típica (base com raio de 32 cm).
- **Modelos 3D simplificados:** volumes e acabamentos representam os produtos, mas não são os modelos oficiais dos fabricantes.
- **Renders:** a fidelidade de cor é aproximada (texturas Poly Haven com ajuste de tom); conferir as amostras físicas de freijó e grafite antes da compra.
- **Carga da mesa:** o peso do PC (~12 kg) é estimado; somado a tampo, monitores e braço dá ≈ 64 kg (limite da Starlift: 80 kg). Pesar o gabinete real.
- **Fixação dos nichos e do gancho da planta:** depende do tipo de parede/laje; verificar antes de furar.
- **Elétrica:** a carga da tomada da Parede D não foi medida. Precisa de eletricista habilitado.
