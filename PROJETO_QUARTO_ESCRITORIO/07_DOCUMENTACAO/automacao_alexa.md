# Integração do quarto com a Alexa

O plano usa o Echo que você já tem. Todos os aparelhos são **Wi-Fi 2,4 GHz e dispensam hub**, então funcionam com
qualquer modelo de Echo. Depois de configurados, você comanda tudo pelo app da Alexa, por voz ou por rotinas
automáticas. As posições valem para o layout aprovado (A) e foram conferidas no modelo 3D. A planta de iluminação
(`03_PLANTAS/iluminacao.pdf`) mostra o Echo (A), o controle do ar (IR) e os sensores (S e T).

Preços da busca web de 04/11/2026: conferir no link antes de comprar. Os itens já estão no orçamento
(`04_ORCAMENTO/orcamento_completo.xlsx`, categoria *Automação (Alexa)*).

## O que a Alexa controla

| Nome na Alexa | O que é | Como entra na Alexa | Cenários |
|---|---|---|---|
| **Luz da mesa** | Fita sob a prateleira + perfil vertical no ripado (L1 + L2) | Controle Wi-Fi 1 da fita (dimmer) | todos |
| **Nichos** | Fita dos 3 nichos da cabeceira (L5) | Controle Wi-Fi 2 da fita (dimmer) | todos |
| **Luminária** | Luminária de mesa (L6) | Lâmpada Wi-Fi, branco 2700–6500 K | todos |
| **Arandela** | Arandela da cama (L4) | Tomada Wi-Fi (liga/desliga) | todos |
| **Luz do teto** | Luz do ventilador | Econômico: lâmpada Wi-Fi · Equilibrado/Premium: interruptor Wi-Fi | todos |
| **Ventilador** | Ventilador de teto (liga, desliga, velocidade) | Interruptor Wi-Fi do ventilador | Equilibrado, Premium |
| **Ar** | Ar-condicionado (liga, desliga, temperatura, modo) | Controle IR Wi-Fi (aparece como termostato) | todos |
| **Sensor da entrada** | Sensor de presença | WEG Home (dispara rotinas) | Equilibrado, Premium |
| **Temperatura do quarto** | Sensor de temperatura e umidade | Tuya/Smart Life (dispara rotinas) | Equilibrado, Premium |
| **Porta do quarto** | Sensor de abertura na porta de entrada | WEG Home (dispara rotinas) | Premium |
| **Persiana** | Persiana externa com motor | Motor tubular Wi-Fi | Premium |

Crie o grupo **Quarto** no app da Alexa com todas as luzes e o próprio Echo. Com isso, "Alexa, apagar a luz" falado
no quarto apaga só as luzes daqui.

**Ficam de fora, de propósito:**
- **Barra de luz do monitor (L3):** é alimentada pela USB e liga junto com o monitor. A BenQ do Premium tem sensor de
  presença próprio.
- **PC:** não ligue o PC numa tomada Wi-Fi para "ligar por voz". Cortar a energia com ele ligado pode corromper dados.
- **Mesa elétrica:** não tem Wi-Fi.
- **Relógio LED:** fica sempre aceso.

## Zonas de luz (fita 24 V)

A fonte de 24 V sob o tampo alimenta **dois controles Wi-Fi ligados em paralelo**, um por zona. Assim a mesa e a
cabeceira acendem e mudam de intensidade separadas.

| Zona | Trechos | Carga (fita de 16 W/m) | Controle |
|---|---|---|---|
| Mesa | L1 1,70 m + L2 2,40 m | ≈ 66 W · 2,7 A | Controle 1 (aguentar ≥ 3 A) |
| Cabeceira | L5 3 × 0,24 m | ≈ 12 W · 0,5 A | Controle 2 |
| Mesa no Premium | L1 1,70 m + 2 × L2 2,40 m | ≈ 104 W · 4,3 A | Controle de ≥ 5 A, na fonte própria (o Premium tem 2 fontes) |

Confira a corrente máxima no anúncio do controle antes de comprar. Se for menor que a da zona, use um controle maior.

## Onde fica cada aparelho (conferido no modelo 3D)

- **Echo (A):** no tampo, canto esquerdo, entre a base da luminária (y 0,06–0,18 m) e o suporte do notebook
  (y 0,44–0,65 m), centro em x 1,02 m · y 0,31 m. O vão livre tem 15 × 26 cm, onde cabe um Echo Dot ou Echo Pop
  (Ø 10 cm); um Echo Show 5 cabe de lado. Fica a uns 25 cm do travesseiro, então dá para tocar nele da cama e da cadeira.
  O cabo desce junto com o da luminária até o filtro sob o tampo. Ele sobe e desce com a mesa sem problema.
- **Controle IR do ar (IR):** em cima da prateleira (1,97 m), perto da ponta esquerda (x ≈ 1,29 m), virado para o
  ar-condicionado da Parede C. Fica a ≈ 1,9 m do ar, na mesma altura e dentro do ângulo do receptor. O cabo USB segue o
  caminho do fio da fita L1 até o filtro.
- **Sensor de presença (S):** no canto da Parede C com a faixa de entrada (x 2,60 m · y 1,95 m), a 2,10 m de altura,
  apontado para a cama e a faixa. Vê quem levanta da cama e quem entra. Bateria recarregável (≈ 3 meses), fixa com
  dupla-face.
- **Sensor de temperatura (T):** no nicho da esquerda (x 0,06–0,30 m), ao lado do vaso. Mede a temperatura onde você
  dorme, longe do PC (canto direito da mesa) e do sopro do ar.
- **Interruptor do ventilador (Equilibrado e Premium):** substitui o interruptor atual do ventilador, na mesma caixa.
  Precisa de fio **neutro** na caixa, e o eletricista confere isso antes da compra. Sem neutro, use a solução do
  Econômico: lâmpada Wi-Fi na luz e a velocidade no controle atual.
- **Sensor de porta (Premium):** na porta de entrada, do lado de dentro, com o ímã no batente.
- **Persiana (Premium):** motor tubular dentro do eixo da persiana externa. Precisa de energia na caixa da persiana.
  Confirme o tipo (de enrolar, com fita) antes de comprar; o valor é estimado.

## Rotinas

Para criar, abra o app Alexa → Mais → Rotinas → "+". Os nomes entre aspas são o que você fala.

| Rotina | Quando dispara | O que faz |
|---|---|---|
| **Bom dia** | Despertador dos dias úteis ou "Alexa, bom dia" | Nichos em 20%; espera 5 min; nichos em 60% e luz do teto acesa; desliga o ar; fala a previsão do tempo. Premium: abre a persiana |
| **Hora de trabalhar** | "Alexa, hora de trabalhar" | Luz da mesa 100%; luminária 100% em 4000 K (luz neutra para concentrar); nichos apagados; ventilador na velocidade 2 |
| **Reunião** | "Alexa, modo reunião" | Luminária 80% em 3000 K (luz no rosto); luz da mesa 60%; ventilador desligado (sem ruído no microfone) |
| **Relaxar** | "Alexa, relaxar" | Luz do teto apagada; luz da mesa 30%; nichos 50%; luminária apagada |
| **Jogo ou filme** | "Alexa, modo jogo" | Luz da mesa 10%; nichos 15%; o resto apagado |
| **Leitura** | "Alexa, hora de ler" | Arandela acesa; nichos 20%; o resto apagado |
| **Boa noite** | "Alexa, boa noite" | Apaga o grupo Quarto e deixa os nichos em 5% por 5 min; ar em 23 °C; ventilador na 1. Premium: fecha a persiana |
| **Saindo** | "Alexa, estou saindo" | Apaga tudo; desliga o ar e o ventilador |
| **Pôr do sol** | Automático, no pôr do sol | Nichos 40% e luz da mesa 30% |
| **Luz de passagem** | Automático: movimento no sensor entre 23 h e 6 h | Luz da mesa em 5% por 3 min (o perfil vertical ilumina o chão sem acordar) |
| **Calor** | Automático: temperatura acima de 27 °C entre 12 h e 23 h | Liga o ar em 24 °C. Ative só nos meses quentes |
| **Chegada** (Premium) | Automático: porta abre depois das 18 h | Luz da mesa 40% e nichos 40% |

No Econômico não há sensores. As rotinas automáticas dele são só as de horário (pôr do sol, despertador).

## Configuração, passo a passo

1. **Wi-Fi:** confira se o sinal de 2,4 GHz é bom junto da mesa (teste no celular). Se o roteador junta 2,4 e 5 GHz num
   nome só e o pareamento falhar, separe as redes durante a configuração.
2. **Apps:** cada aparelho usa o app do fabricante:
   - **Smart Life:** controles da fita (confira no manual), controle IR, sensor de temperatura e interruptor do ventilador.
   - **Positivo Casa Inteligente:** lâmpadas e tomada.
   - **WEG Home:** sensores de presença e de porta.

   Pareie cada aparelho no app dele.
3. **Skills:** no app Alexa, ative as skills Smart Life, Positivo Casa Inteligente e WEG Home e toque em
   "Descobrir dispositivos".
4. **Nomes:** renomeie com os nomes da tabela acima. Use nomes curtos e diferentes entre si. Crie o grupo Quarto com o Echo.
5. **Ar-condicionado:** no Smart Life, escolha a marca do ar no controle IR e teste ligar, desligar e mudar a
   temperatura. Na Alexa ele aparece como termostato: "Alexa, ar em 23 graus".
6. **Lâmpada da luminária:** deixe em 2700 K como padrão, para combinar com o resto (as rotinas mudam quando precisa).
7. **Rotinas:** crie as da tabela.

## Compras por cenário

Os valores incluem os 2 controles Wi-Fi da fita, que no orçamento ficam em *Iluminação*.

### Econômico — R$ 279,74
| Item | Produto | Onde | Qtd | Preço | Status |
|---|---|---|---|---|---|
| Controle Wi-Fi da fita (2 zonas) | Controlador Wi-Fi c/ dimmer (Alexa/Google) | [Amazon](https://www.amazon.com.br/dp/B0FS91PKKL) | 2 | R$ 86,04 | listagem da loja |
| Lâmpadas Wi-Fi (luz do ventilador + luminária) | Positivo Smart Lâmpada 9W 806 lm, branco 2700–6500 K + RGB (kit 2) | [Amazon](https://www.amazon.com.br/dp/B09GBHTCTN) | 1 | R$ 99,00 | busca web — conferir no link |
| Tomada Wi-Fi da arandela (L4) | Positivo Smart Plug 10A/1000W (mede consumo) | [Amazon](https://www.amazon.com.br/dp/B07S14JHF2) | 1 | R$ 51,70 | busca web — conferir no link |
| Controle IR Wi-Fi do ar-condicionado | Novadigital SRW-004 (Tuya/Smart Life, IR 360°, 8 m) | [Amazon](https://www.amazon.com.br/dp/B0CLQ1NNJQ) | 1 | R$ 43,00 | busca web — conferir no link |

No Econômico, a lâmpada Wi-Fi do ventilador só funciona com o interruptor da luz sempre ligado. Se o ventilador tiver
mais de um soquete, compre uma lâmpada para cada um.

### Equilibrado — R$ 687,27
| Item | Produto | Onde | Qtd | Preço | Status |
|---|---|---|---|---|---|
| Controle Wi-Fi da fita (2 zonas) | Controlador Wi-Fi c/ dimmer (Alexa/Google) | [Amazon](https://www.amazon.com.br/dp/B0FS91PKKL) | 2 | R$ 86,04 | listagem da loja |
| Lâmpada Wi-Fi da luminária de mesa (L6) | Positivo Smart Lâmpada 9W 806 lm, branco 2700–6500 K + RGB | [Amazon](https://www.amazon.com.br/dp/B082FTRR76) | 1 | R$ 79,90 | busca web — conferir no link |
| Tomada Wi-Fi da arandela (L4) | Positivo Smart Plug 10A/1000W (mede consumo) | [Amazon](https://www.amazon.com.br/dp/B07S14JHF2) | 1 | R$ 51,70 | busca web — conferir no link |
| Controle IR Wi-Fi do ar-condicionado | Novadigital SRW-004 (Tuya/Smart Life, IR 360°, 8 m) | [Amazon](https://www.amazon.com.br/dp/B0CLQ1NNJQ) | 1 | R$ 43,00 | busca web — conferir no link |
| Interruptor Wi-Fi do ventilador (luz + velocidades) | Painel touch Wi-Fi Tuya p/ ventilador, 10 A (precisa de neutro) | [Casas Bahia](https://www.casasbahia.com.br/painel-de-interruptor-inteligente-coibeu-para-ventilador-funcao-wifi-24ghz-touch-app-tuya/p/1581529833) | 1 | R$ 120,00 | estimativa (anúncio sem preço; similar a R$ 104,50) |
| Sensor de presença | WEG Home sensor de presença Wi-Fi, bateria recarregável, 6 m / 115° | [Amazon](https://www.amazon.com.br/dp/B098PJWQB6) | 1 | R$ 96,73 | busca web — conferir no link |
| Sensor de temperatura e umidade | HONP Tuya Wi-Fi c/ display LCD (pilhas à parte) | [Amazon](https://www.amazon.com.br/dp/B0BK1J96H7) | 1 | R$ 59,90 | busca web — conferir no link |
| Instalação do interruptor do ventilador | Eletricista: troca do interruptor e teste do neutro | Profissional local | 1 | R$ 150,00 | estimativa |

### Premium — R$ 1.680,76
Tudo do Equilibrado, mais:

| Item | Produto | Onde | Qtd | Preço | Status |
|---|---|---|---|---|---|
| Sensor de porta | WEG Home sensor de abertura Wi-Fi, bateria recarregável | [Pichau](https://www.pichau.com.br/sensor-porta-ou-janela-weg-home-wi-fi-branco-15718937) | 1 | R$ 93,49 | listagem da loja (PIX) |
| Motor Wi-Fi na persiana externa + instalação | Motor tubular Wi-Fi (Tuya) no eixo da persiana de enrolar | Profissional local | 1 | R$ 900,00 | estimativa — confirmar o tipo da persiana |

No Premium, o controle da zona da mesa precisa aguentar 5 A ou mais (veja *Zonas de luz*).

**Efeito no orçamento total (com a reserva de 10%):**

| Cenário | Antes | Agora |
|---|---|---|
| Econômico | R$ 10.115 | **R$ 10.388** |
| Equilibrado | R$ 14.584 | **R$ 15.292** |
| Premium | R$ 23.101 | **R$ 24.856** |

## Se o seu Echo for…

- **Echo Dot de 5ª geração ou Echo de 4ª geração:** ele tem sensor de temperatura próprio. Dá para usar na rotina *Calor* e dispensar o
  sensor HONP (economia de R$ 59,90). O sensor do Echo fica na mesa, a 1,4 m do PC, e mede menos fiel que o do nicho.
- **Echo com hub Zigbee** (Echo 4ª geração, Echo Show 10, Echo Hub): os sensores podem ser Zigbee, que são mais baratos
  e têm pilha mais duradoura. Não é necessário: os Wi-Fi acima funcionam igual.
- **Echo Show:** mostra os controles na tela e serve de despertador visual na mesa.

## Cuidados

- Tomada Wi-Fi de 10 A / 1000 W: só para a arandela. Nunca use no ar-condicionado nem em aquecedor.
- Fonte de 24 V e controles sempre ventilados e acessíveis sob o tampo.
- O interruptor do ventilador mexe na instalação de 127/220 V. Quem instala é o eletricista.
