# Formato .qet: o que o simulador precisa

Notas a partir de `circuitos-qet/partida_direta.qet` (QElectroTech 0.100.0).

## Estrutura geral

O `.qet` é um XML com três blocos que interessam:

```
<project>
  <diagram>                 ← o desenho (folha)
    <elements>              ← cada símbolo colocado
    <conductors>            ← cada fio
  </diagram>
  <collection>              ← definições embutidas dos símbolos usados
</project>
```

## Elementos (`diagram/elements/element`)

- `uuid`: identificador único do elemento no desenho.
- `type`: caminho do símbolo (ex.: `.../01_coils/comm_electronique.elmt`).
- `elementInformations/elementInformation[@name="label"]`: o nome (S1, K1...).
- `links_uuids/link_uuid`: vínculo mestre/escravo. Existe **nos dois sentidos**:
  a bobina aponta para o contato e o contato aponta para a bobina.

## Definições (`collection/.../element/definition`)

- `link_type`:
  - `master`: bobina (com `kindInformations/type = coil`)
  - `slave`: contato (com `kindInformations/state = NO` ou `NC`)
  - `simple`: botoeiras, fonte etc.
- `terminal`: cada borne, com `uuid` e `name` (L, N, A1, A2, 13, 14, 21, 22).

## Fios (`diagram/conductors/conductor`)

Cada fio liga dois bornes:
`element1` + `terminal1` ↔ `element2` + `terminal2`.
Os `terminal*` são os uuid dos bornes da definição (não os `id` numéricos do elemento).

## O que está e o que não está no arquivo

| Necessidade | No `.qet`? |
|---|---|
| Ligação dos fios | Sim, por borne |
| Nome dos bornes | Sim |
| Bobina = mestre, contato = escravo | Sim (`link_type`) |
| Contato NA ou NF | Sim (`state`) |
| Contato pertence a qual bobina | Sim, **se vinculado** no QElectroTech |
| Botoeira NA ou NF | **Não**: deduzir pela numeração IEC (x3–x4 = NA, x1–x2 = NF) |

## Armadilhas encontradas

1. **Texto digitado não é vínculo.** Escrever "K1" sobre um contato só cria um
   texto livre (`text_from="UserText"`). O vínculo real é feito na aba de
   referência cruzada do contato e aparece como `link_uuid`.
2. **Mudança na tela ≠ arquivo salvo.** Conferir o asterisco na barra de título.
3. **Contato vinculado pode ter `label` vazio:** o nome vem da bobina mestre.
4. **Maiúsculas e minúsculas:** a bobina foi salva como `k1`. O simulador compara
   nomes sem diferenciar maiúsculas e minúsculas.

## Temporizadores

- A bobina do temporizador é uma bobina comum (`link_type="master"`, `type=coil`).
- O **tipo de temporização fica no contato** (`kindInformations/type`):
  `delayOn` = retardo na energização ("conta e liga"); `delayOff` = retardo na desenergização.
- **Não existe campo de tempo.** O simulador usa 5 s por padrão, aceita o comando `tempo KT1 3`
  e lê um valor como `5s` escrito em qualquer campo de texto da bobina.
- **Defeito na biblioteca do QElectroTech:** `con_simple_tmp_r.elmt` (`delayOff`) e
  `con_simple_tmp_t.elmt` (`delayOn`) têm o **mesmo nome em PT e EN**
  ("tempo retardado de ligado" / "switch-on delay timer"). Em FR e DE os nomes estão certos
  (*tempo repos* / *abfallverzögert* para o `_r`; *tempo travail* / *ansprechverzögert* para o `_t`).

## Mais armadilhas

5. **Elementos sobrepostos:** um contato colado exatamente sobre outro fica invisível na tela.
   O simulador avisa contatos sem vínculo.
6. **Editar o .qet com o QElectroTech aberto:** ao salvar, o programa grava por cima das alterações
   feitas fora dele.
