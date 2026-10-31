# Plano: decoração + PC na mesa (aprovado pelo usuário em 30/10/2026, NÃO IMPLEMENTADO ainda)

Escolhas do usuário: PC sobre a mesa com gabinete de vidro; quadros P&B, nichos iluminados, plantas e
acessórios de setup.

## Problema encontrado (corrigir junto)
- Notebook + 2 monitores + PC lado a lado precisam de ~1,76 m; a mesa tem 1,70 m.
- **Interferência real no modelo atual:** o notebook no suporte (x 0,98–1,30, tela até z ≈ 1,04) cruza o monitor
  esquerdo (x 1,16–1,78, z 0,90–1,265). A validação não testava isso.

## Solução de layout (construir_cena.py + planta_tecnica.py)
- Monitores deslocados 6 cm para a esquerda no braço (centro x = 1,72).
- Notebook na frente à esquerda, em suporte baixo: x 0,97–1,29, y 0,42–0,66; dobradiça em y 0,43, tela inclinada 15° para trás.
- PC sobre a mesa: x 2,37–2,60, y 0,12–0,57, z 0,73–1,19 (0,23 × 0,45 × 0,46). Vidro na frente e no lado −x,
  3 fans com anel LED 3000 K. Com a mesa a 1,18 m, o topo fica a 1,64 m < 1,95 m da prateleira. Carga total ≈ 64 kg < 80 kg.
- Remover o suporte suspenso do PC (e do orçamento, nos 3 cenários).

## Decoração (realismo.py)
- Nichos: 3 de 24 × 26 × 16 cm sobre a cabeceira (Parede D), x 0,06–0,82, z 1,55–1,81, LED 3000 K.
  Conteúdo: ceramic_vase_02 (escala 0,6), carved_wooden_elephant e bronze_whale_statue (escala ~0,14).
  Os modelos já foram baixados em `05_BLENDER/assets/models/`.
- Quadros P&B (arte gerada com ImageMagick) na Parede E, trecho y 0–1,10:
  - A: 40 × 55, y 0,10–0,50, z 1,20–1,75;
  - B: 36 × 26, y 0,58–0,94, z 1,49–1,75;
  - C: 36 × 26, y 0,58–0,94, z 1,20–1,46;
  - mais 2 pequenos apoiados na prateleira (20 × 25 e 15 × 20).
  Remove o quadro Poly Haven atual.
- Planta pendente do teto em (0,30, 2,25), sobre a circulação, com a base a 1,95 m (fern_02 em escala ~0,22 num vaso suspenso).
- Acessórios: suporte de headphone em (2,50, 0,67), caneca em (2,30, 0,66), luminária de mesa em (1,01, 0,12)
  com spot 2700 K, relógio LED na prateleira.

## Orçamento
- Remover "Suporte de gabinete".
- Adicionar marcenaria: "Nichos iluminados 3×", estimativa R$ 300 / 450 / 700.
- Somar 0,72 m de LED dos nichos → rolos passam a 2 no Equilibrado.
- Nova categoria "Decoração (opcional)": preços ainda não pesquisados (a busca na Amazon falhou nesta sessão).

## Validação a acrescentar
PC × monitor; PC dentro do tampo; notebook × monitor; nichos ≥ 0,90 m acima do colchão; planta pendente ≥ 1,95 m;
quadros dentro do trecho y < 1,10 (sem invadir a janela).

## Depois
Rodar construir_cena → validar → realismo → renderizar_360 → copiar para `09_TOUR_360/pano` (+ prev) →
republicar o tour (mesmo arquivo index.html).
