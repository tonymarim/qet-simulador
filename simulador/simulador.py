"""
Protótipo do simulador de comandos elétricos (Passo 2).

Lê um arquivo .qet do QElectroTech e simula o circuito de comando
no terminal. Sem interface gráfica: o objetivo é validar o modelo.

Uso:
    python simulador.py ..\\circuitos-qet\\partida_direta.qet
Depois digite os comandos (ex.: S1, +S1, -S1, t 5, sair).
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, deque


# ---------------------------------------------------------------
# 1. LEITURA DO ARQUIVO .qet
# ---------------------------------------------------------------
def ler_definicoes(raiz):
    """Lê a 'biblioteca' embutida no .qet: o que cada símbolo é."""
    defs = {}
    for el in raiz.find("collection").iter("element"):
        d = el.find("definition")
        if d is None:
            continue
        kind = {}
        ki = d.find("kindInformations")
        if ki is not None:
            for k in ki:
                kind[k.attrib.get("name")] = (k.text or "").strip()
        bornes = {t.attrib["uuid"]: t.attrib.get("name", "")
                  for t in d.iter("terminal")}
        defs[el.attrib["name"]] = {
            "link_type": d.attrib.get("link_type", "simple"),
            "kind": kind,
            "bornes": bornes,
        }
    return defs


def classificar(nome_arquivo, definicao):
    """Decide o papel do elemento no simulador."""
    lt, kind = definicao["link_type"], definicao["kind"]
    nomes = set(definicao["bornes"].values())
    if {"L", "N"} <= nomes:
        return "fonte", None
    if lt == "master" and kind.get("type") == "coil":
        return "bobina", None
    if lt == "slave":
        return "contato", kind.get("state", "NO")       # NO ou NC
    # Botoeira: deduz NA/NF pela numeração IEC (x3-x4 = NA, x1-x2 = NF)
    finais = {n[-1:] for n in nomes if n}
    if finais == {"3", "4"}:
        return "botoeira", "NO"
    if finais == {"1", "2"}:
        return "botoeira", "NC"
    return "desconhecido", None


def ler_circuito(caminho):
    raiz = ET.parse(caminho).getroot()
    defs = ler_definicoes(raiz)
    diagrama = raiz.find("diagram")

    elementos = {}
    for e in diagrama.find("elements"):
        arquivo = e.attrib["type"].split("/")[-1]
        d = defs[arquivo]
        info = {}
        ei = e.find("elementInformations")
        if ei is not None:
            info = {i.attrib.get("name"): (i.text or "").strip() for i in ei}
        papel, estado = classificar(arquivo, d)
        elementos[e.attrib["uuid"]] = {
            "papel": papel,
            "estado_normal": estado,
            "nome": info.get("label", ""),
            "bornes": d["bornes"],          # uuid do borne -> nome (A1, 13...)
            "vinculos": [l.attrib["uuid"] for l in e.iter("link_uuid")],
            "tipo_contato": d["kind"].get("type", "simple"),  # simple, delayOn, delayOff
            "info": info,
        }

    # Contato sem nome herda o nome da bobina vinculada
    for el in elementos.values():
        if el["papel"] == "contato" and not el["nome"] and el["vinculos"]:
            el["nome"] = elementos[el["vinculos"][0]]["nome"]

    fios = [((c.attrib["element1"], c.attrib["terminal1"]),
             (c.attrib["element2"], c.attrib["terminal2"]))
            for c in diagrama.find("conductors")]
    return elementos, fios


# ---------------------------------------------------------------
# 2. MOTOR DE SIMULAÇÃO
# ---------------------------------------------------------------
class Simulador:
    def __init__(self, elementos, fios):
        self.el = elementos
        self.fios = fios
        self.pressionado = {u: False for u, e in elementos.items()
                            if e["papel"] == "botoeira"}
        self.energizada = {u: False for u, e in elementos.items()
                           if e["papel"] == "bobina"}
        # Temporização: tempo ajustado (s) e cronômetros de cada bobina
        self.relogio = 0.0
        self.t_ajuste = {u: tempo_do_desenho(elementos[u])
                         for u in self.energizada if self.e_temporizador(u)}
        self.t_ligada = {u: 0.0 for u in self.energizada}            # há quanto tempo energizada
        self.t_desligada = {u: float("inf") for u in self.energizada} # há quanto tempo desligada

    def e_temporizador(self, bobina):
        """Uma bobina é temporizador se algum contato dela for retardado."""
        return any(e["papel"] == "contato" and bobina in e["vinculos"]
                   and e["tipo_contato"] != "simple"
                   for e in self.el.values())

    # --- estado de cada chave/contato ---------------------------
    def fechado(self, uuid):
        e = self.el[uuid]
        if e["papel"] == "botoeira":
            atuado = self.pressionado[uuid]
        elif e["papel"] == "contato":
            atuado = any(self.contato_atuado(e["tipo_contato"], m)
                         for m in e["vinculos"] if m in self.energizada)
        else:
            return False
        return atuado if e["estado_normal"] == "NO" else not atuado

    def contato_atuado(self, tipo, bobina):
        ligada = self.energizada[bobina]
        T = self.t_ajuste.get(bobina, 0.0)
        if tipo == "delayOn":     # retardo na energização
            return ligada and self.t_ligada[bobina] >= T - 1e-9
        if tipo == "delayOff":    # retardo na desenergização
            return ligada or self.t_desligada[bobina] < T - 1e-9
        return ligada             # contato comum

    # --- quais bornes estão "vivos" a partir de L ou de N --------
    def alcancaveis(self, nome_origem):
        viz = defaultdict(set)
        for a, b in self.fios:                      # fios sempre conduzem
            viz[a].add(b); viz[b].add(a)
        for u, e in self.el.items():                # chaves fechadas conduzem
            if e["papel"] in ("botoeira", "contato") and self.fechado(u):
                t1, t2 = list(e["bornes"])
                viz[(u, t1)].add((u, t2)); viz[(u, t2)].add((u, t1))
        origem = [(u, t) for u, e in self.el.items() if e["papel"] == "fonte"
                  for t, n in e["bornes"].items() if n == nome_origem]
        vistos, fila = set(origem), deque(origem)
        while fila:
            n = fila.popleft()
            for m in viz[n] - vistos:
                vistos.add(m); fila.append(m)
        return vistos

    # --- resolve até estabilizar ---------------------------------
    def resolver(self, max_iter=50):
        for _ in range(max_iter):
            vL, vN = self.alcancaveis("L"), self.alcancaveis("N")
            mudou = False
            for u in self.energizada:
                a, b = [(u, t) for t in self.el[u]["bornes"]]
                novo = (a in vL and b in vN) or (b in vL and a in vN)
                if novo != self.energizada[u]:
                    self.energizada[u] = novo
                    if novo:
                        self.t_ligada[u] = 0.0
                    else:
                        self.t_desligada[u] = 0.0
                    mudou = True
            if not mudou:
                return "estável"
        return "OSCILANDO"

    # --- interação ----------------------------------------------
    def uuid_de(self, nome):
        for u, e in self.el.items():
            if e["nome"].lower() == nome.lower() and e["papel"] == "botoeira":
                return u
        raise KeyError(f"Botoeira '{nome}' não encontrada")

    def estado(self):
        return ", ".join(
            f"{self.el[u]['nome']}={'ENERGIZADA' if v else 'desligada'}"
            for u, v in self.energizada.items())

    def acao(self, nome, pressionar):
        self.pressionado[self.uuid_de(nome)] = pressionar
        situacao = self.resolver()
        verbo = "pressiona" if pressionar else "solta    "
        print(f"  t={self.relogio:5.1f}s {verbo} {nome:<4} -> {self.estado()}   [{situacao}]")

    def avancar(self, segundos, dt=0.1):
        """Avança o tempo simulado em passos de dt, mostrando só o que muda."""
        passos = int(round(segundos / dt))
        anterior = self.estado()
        for _ in range(passos):
            self.relogio += dt
            for u in self.energizada:
                if self.energizada[u]:
                    self.t_ligada[u] += dt
                else:
                    self.t_desligada[u] += dt
            situacao = self.resolver()
            atual = self.estado()
            if atual != anterior:
                print(f"  t={self.relogio:5.1f}s           -> {atual}   [{situacao}]")
                anterior = atual
        print(f"  t={self.relogio:5.1f}s (fim)      -> {self.estado()}")

    def ajustar_tempo(self, nome, segundos):
        for u in self.t_ajuste:
            if self.el[u]["nome"].lower() == nome.lower():
                self.t_ajuste[u] = segundos
                print(f"  {self.el[u]['nome']} ajustado para {segundos:g} s")
                return
        raise KeyError(f"Temporizador '{nome}' não encontrado")


def tempo_do_desenho(elemento, padrao=5.0):
    """Procura um tempo escrito em qualquer campo do elemento (ex.: '5s', 't=2,5 s').
    O QElectroTech não tem campo de tempo; se nada for encontrado, usa o padrão."""
    for valor in elemento["info"].values():
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*s\b", valor)
        if m:
            return float(m.group(1).replace(",", "."))
    return padrao


# ---------------------------------------------------------------
# 3. EXECUÇÃO
# ---------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    elementos, fios = ler_circuito(sys.argv[1])

    print("Elementos encontrados:")
    for e in elementos.values():
        extra = f" ({e['estado_normal']})" if e["estado_normal"] else ""
        print(f"  {e['papel']:<9} {e['nome'] or '-'}{extra}")
    print(f"Fios: {len(fios)}")
    sem_nome = [e for e in elementos.values()
                if e["papel"] == "botoeira" and not e["nome"]]
    if sem_nome:
        print(f"\nATENÇÃO: {len(sem_nome)} botoeira(s) sem nome no desenho. "
              "Elas não podem ser acionadas. Dê nome a elas no QElectroTech.")

    soltos = [e for e in elementos.values()
              if e["papel"] == "contato" and not e["vinculos"]]
    if soltos:
        print(f"ATENÇÃO: {len(soltos)} contato(s) sem vínculo com bobina. "
              "Eles nunca vão atuar.")

    sim = Simulador(elementos, fios)
    nomes_tipo = {"delayOn": "retardo na energização",
                  "delayOff": "retardo na desenergização"}
    for u, T in sim.t_ajuste.items():
        tipos = {e["tipo_contato"] for e in elementos.values()
                 if u in e["vinculos"] and e["tipo_contato"] != "simple"}
        desc = ", ".join(nomes_tipo.get(t, t) for t in tipos)
        print(f"Temporizador {elementos[u]['nome']}: {T:g} s ({desc})")
    print("\nEstado inicial:", sim.resolver())
    print("""
Comandos:
  S1          pulso (pressiona e solta)
  +S1         mantém pressionada
  -S1         solta
  t 5         avança 5 segundos
  tempo KT1 3 ajusta o temporizador KT1 para 3 s
  sair        encerra
""")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        if cmd.lower() in ("sair", "q"):
            break
        partes = cmd.split()
        try:
            if partes[0].lower() == "t" and len(partes) == 2:
                sim.avancar(float(partes[1].replace(",", ".")))
            elif partes[0].lower() == "tempo" and len(partes) == 3:
                sim.ajustar_tempo(partes[1], float(partes[2].replace(",", ".")))
            elif cmd[0] == "+":
                sim.acao(cmd[1:], True)
            elif cmd[0] == "-":
                sim.acao(cmd[1:], False)
            else:
                sim.acao(cmd, True)
                sim.acao(cmd, False)
        except KeyError as erro:
            print(" ", erro.args[0])
        except ValueError:
            print("  Valor inválido. Exemplo: t 5")


if __name__ == "__main__":
    main()
