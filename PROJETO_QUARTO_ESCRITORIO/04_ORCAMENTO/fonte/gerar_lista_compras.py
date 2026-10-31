"""Gera 07_DOCUMENTACAO/lista_compras.md a partir do cenário Equilibrado (mesma fonte do orçamento)."""
from pathlib import Path

from dados_orcamento import CAT, CENARIOS, DATA
from gerar_orcamento import qtd, totais

OUT = Path(__file__).resolve().parents[2] / "07_DOCUMENTACAO" / "lista_compras.md"
CEN = "Equilibrado"

ORDEM = """## Ordem sugerida de execução

1. Eletricista: conferir a tomada da Parede D e instalar o prolongador de caixa.
2. Pintura (paredes e teto) **antes** do ripado e dos móveis.
3. Piso de madeira e rodapé (fora deste orçamento).
4. Marceneiro: ripado (com recorte da tomada e vão do LED a x ≈ 0,91 m), prateleira a 1,95 m, 3 nichos sobre a
   cabeceira (base a 1,55 m, x 0,06–0,82) e tampo com furo para o braço (eixo dos monitores 6 cm à esquerda do centro).
5. Montar a estrutura da mesa com o tampo novo, depois a fita LED, a fonte e o controlador.
6. Cama, cadeira, tapete, braço dos monitores, PC sobre o tampo (canto direito) e acessórios.
7. Decoração: quadros na Parede E (y 0,10–0,94; z 1,20–1,75), gancho de teto da planta pendente em (0,30; 2,25),
   objetos dos nichos, plantas e relógio na prateleira.
"""


def main():
    t = totais()[CEN]
    L = [f"# Lista de compras — cenário {CEN}", "",
         f"Preços consultados em {DATA} (reconfirmar antes de comprar). Total com reserva de 10%: "
         f"**R$ {t['total']:,.0f}**".replace(",", ".") + ". Detalhes e fórmulas em `04_ORCAMENTO/orcamento_completo.xlsx`.",
         "", "Itens marcados *estimativa* não têm cotação: pedir orçamento ou pesquisar o preço antes de comprar.", ""]
    for cat in CAT:
        itens = [i for i in CENARIOS[CEN] if i[0] == cat]
        if not itens:
            continue
        L += ["", f"## {cat}", ""]
        for _, item, prod, loja, link, _, _, st, q, pu, un in itens:
            q = qtd(q)
            qs = f"{q:g}"
            desc = f"[{prod}]({link})" if link.startswith("http") and st != "EST" else prod
            nota = {"EST": " *(estimativa — pedir orçamento)*", "BUSCA": " *(preço da busca web — conferir no link)*"}.get(st, "")
            L.append(f"- [ ] **{item}** — {desc} · {qs} {un} × R$ {pu:.2f} = **R$ {q * pu:.2f}**{nota}")
    L += ["", ORDEM]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
