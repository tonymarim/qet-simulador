# qet-simulador

Simulador de comandos elétricos que lê arquivos `.qet` do [QElectroTech](https://qelectrotech.org).
*Electrical control-circuit simulator that reads QElectroTech `.qet` files.*

> **Status:** protótipo (prova de conceito). / *Prototype (proof of concept).*

## O que faz / What it does

Lê um diagrama de comando desenhado no QElectroTech e simula, no terminal, o
comportamento de botoeiras, bobinas e contatos: selo, intertravamento, desligamento
e temporizadores (retardo na energização e na desenergização).

*Reads a control diagram drawn in QElectroTech and simulates push buttons, coils and
contacts in the terminal (self-holding, interlocking, stop, on-delay and off-delay timers).*

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
partida temporizada, estrela-triângulo / *DOL, reversing, timed start, star-delta*.

## Como usar / How to use

Requer Python 3.8+ (sem bibliotecas extras). / *Requires Python 3.8+ (no extra libraries).*

```
cd simulador
python simulador.py ../circuitos-qet/reversao.qet
```

Comandos / *Commands*: `S1` pulso / *pulse* · `+S1` mantém / *hold* · `-S1` solta / *release* ·
`t 5` avança 5 s / *advance 5 s* · `tempo KT1 3` ajusta KT1 para 3 s / *set KT1 to 3 s* · `sair` / *quit*

## Regras para o desenho / Drawing rules

1. **Vincule cada contato à sua bobina** pela referência cruzada do QElectroTech
   (texto digitado não vale). / *Link each contact to its coil via cross-reference.*
2. **Botoeiras:** numeração IEC define o tipo: 13–14 = NA, 21–22 = NF.
   / *Push buttons: IEC terminal numbers define type: x3–x4 = NO, x1–x2 = NC.*
3. **Dê nome a todas as botoeiras** (S0, S1...). / *Name every push button.*
4. **Temporizadores:** o tipo vem do contato (`delayOn` / `delayOff`). O QElectroTech não tem campo de
   tempo: o padrão é 5 s, ou escreva o valor (ex.: `5s`) em um campo de texto da bobina.
   / *Timer type comes from the contact; default time is 5 s, or write e.g. `5s` in a coil text field.*
   ⚠️ Em PT/EN, os contatos `con_simple_tmp_r` e `con_simple_tmp_t` têm o mesmo nome na biblioteca;
   o de "conta e liga" é o `_t` (FR: *tempo travail*). / *In PT/EN both share the same name; on-delay is `_t`.*

Detalhes do formato: [`notas/formato-qet.md`](notas/formato-qet.md)

## Limitações atuais / Current limitations

- Uma folha por projeto / *single sheet*
- Sem circuito de força / *no power circuit*
- Cargas em série não suportadas / *series loads not supported*

## Licença / License

GPL-3.0
