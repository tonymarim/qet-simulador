# qet-simulador

Simulador de comandos elétricos que lê arquivos `.qet` do [QElectroTech](https://qelectrotech.org).
*Electrical control-circuit simulator that reads QElectroTech `.qet` files.*

> **Status:** protótipo (prova de conceito). / *Prototype (proof of concept).*

## O que faz / What it does

Lê um diagrama de comando desenhado no QElectroTech e simula, no terminal, o
comportamento de botoeiras, bobinas e contatos: selo, intertravamento, desligamento
e temporizadores (retardo na energização e na desenergização). No circuito de força, mostra se o
motor gira, o sentido de rotação, falta de fase e curto-circuito, com disjuntor e relé térmico
(o disjuntor dispara sozinho em curto-circuito entre fases).

*Reads a control diagram drawn in QElectroTech and simulates push buttons, coils and
contacts in the terminal (self-holding, interlocking, stop, on-delay and off-delay timers). In the
power circuit it shows motor running, direction of rotation, missing phase and short circuits, with
circuit breaker and thermal overload relay.*

Exemplo (reversão com intertravamento) / *Example (reversing starter with interlock):*

```
> S1
  pressiona S1   -> K1=ENERGIZADA, K2=desligada   [estável]
> S2
  pressiona S2   -> K1=ENERGIZADA, K2=desligada   [estável]   <- intertravamento / interlock
> S0
  pressiona S0   -> K1=desligada, K2=desligada   [estável]
> S2
  pressiona S2   -> K1=desligada, K2=ENERGIZADA   [estável]
```

Exemplos incluídos / *Included examples* (`circuitos-qet/`): partida direta, reversão com intertravamento,
partida temporizada, estrela-triângulo (comando), partida direta e reversão com força / *DOL,
reversing, timed start, star-delta (control), DOL and reversing with power circuit*.

## Versão gráfica / *Graphical version*

**Online:** https://tonymarim.github.io/qet-simulador/ (com circuitos de exemplo / *with example circuits*)

Abra `web/index.html` no navegador (duplo clique) e escolha um arquivo `.qet`. O diagrama aparece como
no QElectroTech e pode ser simulado: **clique e segure** uma botoeira para pressioná-la (**Shift+clique**
mantém pressionada), clique no **disjuntor** para ligar/desligar e no **relé térmico** para simular
sobrecarga. Fios energizados ficam vermelhos (fase) ou azuis (neutro), bobinas energizadas e contatos
atuados ficam realçados, o motor mostra o sentido de giro e os temporizadores correm em tempo real.
Funciona sem internet; `index.html` e `motor.js` precisam ficar na mesma pasta.

*Open `web/index.html` in a browser and pick a `.qet` file. Press and hold push buttons (Shift+click
latches), click the breaker or the thermal relay. Works offline; keep `index.html` and `motor.js`
together.*

### Instalar como aplicativo / *Install as an app*

No **Chrome** ou no **Edge**, abra o site e clique em **Instalar** (ícone na barra de endereço).
O simulador ganha ícone no menu, abre em janela própria, **funciona sem internet** e passa a aparecer
no **botão direito sobre um arquivo `.qet` > Abrir com > qet-simulador** (o QElectroTech continua sendo
o programa padrão do duplo clique). Para outros PCs basta passar o link: não precisa de instalador
nem de administrador. No Firefox o site funciona, mas não instala.

*In Chrome or Edge, click **Install** in the address bar: the simulator works offline and shows up in
"Open with" for `.qet` files.*

**Testes de paridade / *Parity tests*:** `python tests/paridade.py` e `node tests/paridade.js`
(requer `npm i @xmldom/xmldom`) devem produzir a mesma saída. / *must produce identical output.*

## Como usar / How to use

Requer Python 3.8+ (sem bibliotecas extras). / *Requires Python 3.8+ (no extra libraries).*

```
cd simulador
python simulador.py ../circuitos-qet/reversao.qet
```

Comandos / *Commands*: `S1` pulso / *pulse* · `+S1` mantém / *hold* · `-S1` solta / *release* ·
`t 5` avança 5 s / *advance 5 s* · `tempo KT1 3` ajusta KT1 para 3 s / *set KT1 to 3 s* ·
`Q1` liga/desliga disjuntor / *breaker on/off* · `F1` sobrecarga no térmico / *thermal overload trip/reset* · `sair` / *quit*

## Formato e instalação do QElectroTech / *QElectroTech file format and install*

- O simulador lê arquivos **`.qet`**. O QElectroTech 0.200 também salva **`.qetz`** (zip + banco SQLite),
  que **não** é lido: use *Salvar como* e escolha o tipo `.qet`.
  / *The simulator reads `.qet`. QElectroTech 0.200 can also save `.qetz` (zip + SQLite), which is not
  read: use Save As and pick `.qet`.*
- **Ubuntu:** a versão **Snap** do QElectroTech pode falhar ao salvar (erro em `/run/user/1000/doc/...`).
  Use a versão **Flatpak** ou AppImage. / *On Ubuntu the Snap build may fail to save; use Flatpak or AppImage.*
- Testado no Windows (QElectroTech 0.100) e no Ubuntu (QElectroTech 0.200, Flatpak), no navegador.
  / *Tested on Windows and Ubuntu.*

## Regras para o desenho / Drawing rules

1. **Vincule cada contato à sua bobina** pela referência cruzada do QElectroTech
   (texto digitado não vale). / *Link each contact to its coil via cross-reference.*
2. **Botoeiras:** o tipo NA/NF é deduzido, em ordem, pela numeração IEC dos bornes
   (13–14 = NA, 21–22 = NF), pelo nome do arquivo do símbolo (`_no`, `_nf`...) e pelo nome do
   elemento na biblioteca. Se nada servir, o simulador avisa. Botões de pressão "mestres"
   (`poussoir`, tipo `commutator`) também são aceitos, e contatos vinculados a eles seguem o botão.
   / *Push-button NO/NC type is inferred from IEC terminal numbers, then the symbol file name,
   then the element name; a warning is shown if none works. Master push buttons (`commutator`)
   are supported, and contacts linked to them follow the button.*
3. **Dê nome a todas as botoeiras** (S0, S1...). / *Name every push button.*
4. **Temporizadores:** o tipo vem do contato (`delayOn` / `delayOff`). O QElectroTech não tem campo de
   tempo: o padrão é 5 s, ou escreva o valor (ex.: `5s`) em um campo de texto da bobina.
   / *Timer type comes from the contact; default time is 5 s, or write e.g. `5s` in a coil text field.*
   ⚠️ Em PT/EN, os contatos `con_simple_tmp_r` e `con_simple_tmp_t` têm o mesmo nome na biblioteca;
   o de "conta e liga" é o `_t` (FR: *tempo travail*). / *In PT/EN both share the same name; on-delay is `_t`.*

Detalhes do formato: [`notas/formato-qet.md`](notas/formato-qet.md)

## Limitações atuais / Current limitations

- Várias folhas: todas são desenhadas e simuladas juntas; contatos vinculados entre folhas funcionam.
  Fios que passam de uma folha a outra pela referência de página (*renvoi de folio*: Seta de saída /
  Seta de entrada, vinculadas) também / *multi-sheet projects and folio reports supported*
- Sensor de 3 fios (PNP, NA ou NF; indutivo, capacitivo, magnético, ótico): bornes 1 (+), 3 (-), 4 (saída),
  ou bornes sem nome com as cores (BN/BR, BU/BL, BK) ou números escritos no símbolo. Só dá saída se estiver alimentado; um clique simula a peça /
  *3-wire PNP sensors (1/3/4 or BN/BU/BK); output only when powered; click to place a part*
- Comando alimentado pela fonte trifásica (uma fase + N) ou por fonte retificadora 24 Vcc
  ("Alterna monofásica > Contínua", bornes L, N, L+, L-: com L e N na entrada, L+ vale como fase e L- como
  neutro). Comando entre duas fases (ex.: 380 V) ainda não; a tensão das bobinas não é conferida /
  *control fed by phase + N, or by an AC/DC supply (L, N, L+, L-); phase-to-phase control not yet;
  coil voltage is not checked*
- Força: motores de 3 bornes e de 6 bornes (U1-V1-W1 / U2-V2-W2: identifica estrela, triângulo,
  enrolamentos abertos e ligação incorreta) / *3- and 6-terminal motors (star, delta, open windings,
  wrong connection)*
- Também entende fontes separadas de fase (L) e neutro (N), fusíveis, parada de emergência (trava ao
  acionar) e lâmpadas de sinalização (acendem na cor do símbolo) / *also separate phase/neutral sources,
  fuses, latching emergency stops and signaling lamps*
- Cargas em série não suportadas / *series loads not supported*

## Licença / License

GPL-3.0
