# Temas, layouts e decoração

Gerado por `05_BLENDER/scripts/gerar_html_temas.py` a partir de `temas_dados.py` e da validação de cada layout.
As imagens ficam em `08_VISUALIZADOR_3D/temas/` e aparecem na página de apresentação (seção *Temas, layouts e decoração*).

## Como gerar qualquer combinação

```
blender -b 05_BLENDER/quarto_escritorio_realista.blend --python 05_BLENDER/scripts/variantes.py -- \
    --tema japandi --layout C --render dia,noite,planta [--salvar]
```
`--salvar` grava um .blend editável em `05_BLENDER/temas/`. Sem GPU, use `--res 1280x800 --amostras 48`.

## Temas

### Moderno Escuro Aconchegante (`escuro`)

O projeto aprovado: grafite, ripado de freijó e luz âmbar. Ambiente de foco à noite.

Paleta: Grafite `#3A3C40` · Freijó `#A87A4F` · Caramelo `#B5653A` · Cinza linho `#9EA2A8` · Preto `#151515`

Materiais: Parede grafite fosco; Ripado e marcenaria em freijó; Tampo freijó 25 mm; Roupa de cama cinza em espinha de peixe; Manta caramelo de tricô; Metais pretos.

Decoração: Persiana romana de linho grafite; Almofadas de veludo caramelo e linho grafite; Quadros P&B; Planta de chão no canto morto; Samambaia pendente; Nichos com vaso, elefante e baleia.

Pacote de decoração (estimativa, fora a obra já orçada): R$ 650 – R$ 1.100

### Escandinavo Claro (`escandinavo`)

Off-white quente, carvalho claro e linho. O quarto parece maior e mais iluminado de dia.

Paleta: Off-white quente `#E8E4DC` · Carvalho claro `#C9A77C` · Linho branco `#EEECE7` · Verde sálvia `#8E9C84` · Mostarda `#C49A45`

Materiais: Paredes off-white quente; Ripado e marcenaria em carvalho claro; Fundo do ripado off-white; Roupa de cama de linho branco; Manta waffle cinza; Metais brancos.

Decoração: Persiana romana de linho cru; Almofadas verde-sálvia (veludo) e mostarda; Arte em traço fino; Cesto de vime sob a mesa; Vaso alto de cerâmica branca na prateleira; Planta de chão; Tigela de madeira e suculenta nos nichos.

Pacote de decoração (estimativa, fora a obra já orçada): R$ 700 – R$ 1.200

### Japandi (`japandi`)

Greige com textura de cal, freixo claro, preto pontual e linho. Calmo e organizado.

Paleta: Greige `#D5CABB` · Freixo `#D7C3A3` · Linho areia `#D2C5B1` · Terracota suave `#A9765C` · Preto quente `#2B2A28`

Materiais: Paredes greige com efeito cal; Ripado e marcenaria em freixo; Fundo do ripado preto quente; Roupa de cama de linho areia; Tapete de juta; Metais pretos; LED 2700 K.

Decoração: Persiana romana de linho natural; Almofadas de linho preto e creme; Arte sumi-e (ensō); Cesto de vime sob a mesa; Tapete de juta; Planta de chão; Tigela e vaso de cerâmica nos nichos.

Pacote de decoração (estimativa, fora a obra já orçada): R$ 750 – R$ 1.300

### Industrial Urbano (`industrial`)

Cimento queimado, nogueira escura, couro conhaque e metal preto. Personalidade forte.

Paleta: Cimento queimado `#8E8D88` · Nogueira `#5C3F2A` · Chumbo `#55575B` · Conhaque `#8A4B2A` · Preto `#151515`

Materiais: Paredes com efeito cimento queimado; Ripado e marcenaria em nogueira; Fundo do ripado preto; Roupa de cama chumbo; Almofada de couro conhaque; Tapete espinha de peixe grafite; LED 2700 K.

Decoração: Persiana romana de linho chumbo; Almofadas de couro conhaque e linho; Arte gráfica P&B; Coleção de livros de capa dura na prateleira; Planta de chão; Tapete espinha de peixe.

Pacote de decoração (estimativa, fora a obra já orçada): R$ 900 – R$ 1.700

### Botânico Verde (`botanico`)

Verde musgo, nogueira e latão, com muitas plantas. Aconchegante e vivo.

Paleta: Verde musgo `#5B6B55` · Nogueira `#7A5536` · Off-white `#E5E0D5` · Mostarda `#B88A3B` · Latão `#B08D57`

Materiais: Paredes verde musgo; Ripado e marcenaria em nogueira; Roupa de cama off-white; Almofada de veludo verde; Metais em latão; Tapete creme.

Decoração: Persiana romana de linho cru; Almofadas de veludo verde e linho terracota; Gravuras botânicas; Planta de chão; Vaso de barro com planta na prateleira; Suculenta no nicho; Cesto de vime sob a mesa; Samambaia pendente.

Pacote de decoração (estimativa, fora a obra já orçada): R$ 850 – R$ 1.500

### Terracota Mediterrâneo (`terracota`)

Reboco terracota, carvalho, linho cru e fibras naturais. Quente e ensolarado.

Paleta: Terracota `#B87458` · Carvalho `#C9A77C` · Linho cru `#E7DDCC` · Ferrugem `#9C4F2E` · Oliva `#6E6B3E`

Materiais: Paredes em reboco terracota; Ripado e marcenaria em carvalho; Fundo do ripado marrom café; Roupa de cama de linho cru; Manta ferrugem; Luminárias em fibra natural; LED 2700 K.

Decoração: Persiana romana de linho cru; Almofada estampada + almofada de linho oliva; Arte com arcos e sol; Tapete listrado de algodão; Cesto de vime sob a mesa; Vaso de barro na prateleira; Planta de chão.

Pacote de decoração (estimativa, fora a obra já orçada): R$ 800 – R$ 1.400

## Layouts

### A — cama na Parede E, mesa na Parede D (aprovado)

Cama encostada na parede da janela com a cabeceira no ripado; mesa de 1,70 m no ripado.

A favor:
- Usa a tomada existente junto à cama (sem elétrica nova)
- Entrada e circulação até o armário livres
- Luz natural lateral na mesa, sem ofuscar os monitores
- Ripado contínuo: fundo da mesa e cabeceira

Contra:
- Cama sob a janela: a persiana precisa ser operada por cima da cama
- Planta pendente fica no arco das portas do armário se elas forem de abrir

Verificação no modelo 3D: **21 OK, 1 atenção, 0 falha(s)**

| Status | Verificação | Medição |
|---|---|---|
| OK | Mesa × cama (partes rígidas) | folga 5.0 cm (mínimo 4.0 cm) |
| OK | Mesa × ripado / Parede E / Parede C | folga 2.0 cm (mínimo 1.9 cm) |
| OK | Mesa × portas do armário | folga 210.0 cm (mínimo 15.0 cm) |
| OK | Cama × portas do armário (circulação) | folga 94.0 cm (mínimo 60.0 cm) |
| OK | Cadeira × cama | folga 46.3 cm (mínimo 5.0 cm) |
| OK | Cadeira × armário (recuo + passagem) | folga 136.0 cm (mínimo 60.0 cm) |
| OK | PC longe da cabeceira (ruído e LED) | folga 159.0 cm (mínimo 90.0 cm) |
| OK | Monitores × prateleira com a mesa no máximo | topo 1.715 m · prateleira 1.95 m |
| OK | Janela: frente livre acima do peitoril | nada acima do peitoril |
| OK | Ar-condicionado: ninguém no jato direto | nada a menos de 0,6 m do aparelho |
| OK | Faixa de entrada e porta do banheiro livres | livres |
| ATENÇÃO | Arco das portas do armário (se forem de abrir) | no arco: planta pendente (até y = 2.34) — ok se as portas forem de correr |
| OK | Nichos ≥ 0,90 m acima do colchão | folga 93.0 cm (mínimo 90.0 cm) |
| OK | Planta pendente: folhas acima de 1,90 m | folga 3.9 cm (mínimo 0.0 cm) |
| OK | Planta pendente × ventilador | folga 19.0 cm (mínimo 10.0 cm) |
| OK | Planta de chão × cadeira | folga 8.7 cm (mínimo 5.0 cm) |
| OK | Planta de chão × mesa e cama | folga 11.1 cm (mínimo 0.0 cm) |
| OK | Planta de chão dentro do quarto | x 2.11–2.55, y 0.86–1.38 |
| OK | Tapete dentro do quarto | x 1.08–2.48, y 0.78–2.78 |
| OK | Luminária de braço × monitores | folga 2.7 cm (mínimo 1.5 cm) |
| OK | Luminária de braço × ripado/paredes | folga 1.0 cm (mínimo 0.5 cm) |
| OK | Tomada usada pela mesa (Parede D) | cabos descem até (1.32, 0.04, 0.30) |

### B — cama na Parede C, mesa na Parede D junto à janela

Cama sob o ar-condicionado com a cabeceira no ripado; mesa no ripado, colada na janela.

A favor:
- Mesa recebe a luz da janela pela esquerda (ideal para destros)
- Área livre maior junto à janela
- PC fica longe da cabeceira (na ponta da mesa junto à janela)

Contra:
- Ar-condicionado sobre a cama (jato de ar, dreno e manutenção sobre quem dorme)
- Sem tomada junto à cama: extensão ou ponto novo para a arandela
- Ao entrar no quarto a cama é a primeira coisa vista

Verificação no modelo 3D: **20 OK, 2 atenção, 0 falha(s)**

| Status | Verificação | Medição |
|---|---|---|
| OK | Mesa × cama (partes rígidas) | folga 5.0 cm (mínimo 4.0 cm) |
| OK | Mesa × ripado / Parede E / Parede C | folga 2.0 cm (mínimo 1.9 cm) |
| OK | Mesa × portas do armário | folga 210.0 cm (mínimo 15.0 cm) |
| OK | Cama × portas do armário (circulação) | folga 94.0 cm (mínimo 60.0 cm) |
| OK | Cadeira × cama | folga 42.3 cm (mínimo 5.0 cm) |
| OK | Cadeira × armário (recuo + passagem) | folga 136.0 cm (mínimo 60.0 cm) |
| OK | PC longe da cabeceira (ruído e LED) | folga 159.0 cm (mínimo 90.0 cm) |
| OK | Monitores × prateleira com a mesa no máximo | topo 1.715 m · prateleira 1.95 m |
| OK | Janela: frente livre acima do peitoril | nada acima do peitoril |
| ATENÇÃO | Ar-condicionado: ninguém no jato direto | a menos de 0,6 m do aparelho: cama — direcionar as aletas para o centro do quarto |
| OK | Faixa de entrada e porta do banheiro livres | livres |
| ATENÇÃO | Arco das portas do armário (se forem de abrir) | no arco: planta pendente (até y = 2.34) — ok se as portas forem de correr |
| OK | Nichos ≥ 0,90 m acima do colchão | folga 93.0 cm (mínimo 90.0 cm) |
| OK | Planta pendente: folhas acima de 1,90 m | folga 3.9 cm (mínimo 0.0 cm) |
| OK | Planta pendente × ventilador | folga 19.0 cm (mínimo 10.0 cm) |
| OK | Planta de chão × cadeira | folga 17.5 cm (mínimo 5.0 cm) |
| OK | Planta de chão × mesa e cama | folga 12.3 cm (mínimo 0.0 cm) |
| OK | Planta de chão dentro do quarto | x 0.10–0.50, y 0.87–1.33 |
| OK | Tapete dentro do quarto | x 0.17–1.57, y 0.78–2.78 |
| OK | Luminária de braço × monitores | folga 2.7 cm (mínimo 1.5 cm) |
| OK | Luminária de braço × ripado/paredes | folga 1.0 cm (mínimo 0.5 cm) |
| OK | Tomada usada pela mesa (Parede D) | cabos descem até (1.32, 0.04, 0.30) |

### C — mesa sob a janela, cama na Parede D

Mesa de frente para a janela; cama com a lateral no ripado e a cabeceira na Parede E.

A favor:
- Centro do quarto mais livre (1,9 m entre a cama e o armário)
- Vista para fora enquanto trabalha
- Cama fora do caminho e longe do ar-condicionado

Contra:
- Monitores na frente da janela: contraluz e ofuscamento de dia (persiana necessária)
- A ponta da mesa fica a 20 cm do armário: a 1ª porta só abre se for de correr
- Sem prateleira sobre a mesa (ela vai para cima da cama)

Verificação no modelo 3D: **20 OK, 2 atenção, 0 falha(s)**

| Status | Verificação | Medição |
|---|---|---|
| OK | Mesa × cama (partes rígidas) | folga 4.0 cm (mínimo 4.0 cm) |
| OK | Mesa × ripado / Parede E / Parede C | folga 2.0 cm (mínimo 1.9 cm) |
| OK | Mesa × portas do armário | folga 20.0 cm (mínimo 15.0 cm) |
| OK | Cama × portas do armário (circulação) | folga 194.0 cm (mínimo 60.0 cm) |
| OK | Cadeira × cama | folga 41.3 cm (mínimo 5.0 cm) |
| OK | Cadeira × armário (recuo + passagem) | folga 83.5 cm (mínimo 60.0 cm) |
| OK | PC longe da cabeceira (ruído e LED) | folga 158.0 cm (mínimo 90.0 cm) |
| OK | Prateleira fora da mesa | a prateleira não fica sobre a mesa neste layout |
| ATENÇÃO | Janela: frente livre acima do peitoril | na frente da janela: monitores (topo 1.26 m), PC (topo 1.19 m) |
| OK | Ar-condicionado: ninguém no jato direto | nada a menos de 0,6 m do aparelho |
| OK | Faixa de entrada e porta do banheiro livres | livres |
| ATENÇÃO | Arco das portas do armário (se forem de abrir) | no arco: mesa (até y = 2.65) — ok se as portas forem de correr |
| OK | Nichos ≥ 0,90 m acima do colchão | folga 93.0 cm (mínimo 90.0 cm) |
| OK | Planta pendente: folhas acima de 1,90 m | folga 3.9 cm (mínimo 0.0 cm) |
| OK | Planta pendente × ventilador | folga 13.5 cm (mínimo 10.0 cm) |
| OK | Planta de chão × cadeira | folga 65.1 cm (mínimo 5.0 cm) |
| OK | Planta de chão × mesa e cama | folga 19.7 cm (mínimo 0.0 cm) |
| OK | Planta de chão dentro do quarto | x 2.08–2.52, y 0.19–0.71 |
| OK | Tapete dentro do quarto | x 0.62–2.62, y 1.05–2.45 |
| OK | Luminária de braço × monitores | folga 2.7 cm (mínimo 1.5 cm) |
| OK | Luminária de braço × ripado/paredes | folga 1.0 cm (mínimo 0.5 cm) |
| OK | Tomada usada pela mesa (Parede E) | cabos descem até (0.01, 1.43, 0.33) |

## Arranjos descartados

- **Mesa na Parede C:** O ar-condicionado ficaria sobre os monitores e a janela atrás de quem usa a mesa (reflexo na tela).
- **Cama no centro do ripado:** Sobram menos de 0,90 m de cada lado; a mesa de 1,70 m não cabe mais na Parede D.
- **Cama atravessada sob a janela (cabeceira na Parede E) e mesa na D:** A cama ocuparia a faixa atrás da cadeira: a cadeira não teria onde recuar ao levantar.
