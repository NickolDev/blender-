"""Auditoria dimensional e de interferências do quarto_escritorio.blend.

Uso: blender -b quarto_escritorio.blend --python validar_cena.py
Escreve 07_DOCUMENTACAO/validacao_3d.json com o resultado de cada verificação.
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

PROJ = Path(bpy.data.filepath).resolve().parents[1]
sys.path.insert(0, str(PROJ / "03_PLANTAS" / "fonte"))
import planta_tecnica as PT  # noqa: E402
import planta_v1 as P        # noqa: E402

TOL = 0.002
R = []


def aabb(*nomes):
    """Caixa envolvente (mundo, com modificadores) de um ou mais objetos/prefixos."""
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    achou = False
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not any(ob.name == n or (n.endswith("*") and ob.name.startswith(n[:-1])) for n in nomes):
            continue
        achou = True
        ev = ob.evaluated_get(dg)
        for v in ev.to_mesh().vertices:
            w = ev.matrix_world @ v.co
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
        ev.to_mesh_clear()
    if not achou:
        raise KeyError(nomes)
    return lo, hi


def chk(nome, ok, detalhe):
    R.append({"verificacao": nome, "status": "OK" if ok else "FALHA", "detalhe": detalhe})


def dim(nome, obj, esperado):
    lo, hi = aabb(obj)
    d = tuple(round(h - l, 4) for l, h in zip(lo, hi))
    ok = all(abs(a - b) <= TOL for a, b in zip(d, esperado))
    chk(nome, ok, f"medido {d} m · esperado {esperado} m")
    return lo, hi


def sep(nome, a, b, minimo=0.0):
    """Distância mínima entre AABBs (0 = encostado; negativo = interseção)."""
    la, ha = aabb(*a)
    lb, hb = aabb(*b)
    gaps = [max(lb[i] - ha[i], la[i] - hb[i]) for i in range(3)]
    g = max(gaps)
    chk(nome, g >= minimo - 1e-4, f"folga {g*100:.1f} cm (mínimo {minimo*100:.1f} cm)")


# --- ambiente
dim("Piso do quarto 2,65 × 2,85", "Piso_Quarto", (P.D, P.E, 0.02))
lo, _ = aabb("Teto")
chk("Pé-direito 2,64 m", abs(lo.z - P.PE) <= TOL, f"face inferior do teto em z = {lo.z:.3f}")
lo, hi = aabb("Parede_E_peitoril")
chk("Peitoril da janela a 1,00 m", abs(hi.z - P.JAN_PEIT) <= TOL, f"topo do peitoril z = {hi.z:.3f}")
lo, _ = aabb("Parede_E_verga")
chk("Janela com 1,20 m de altura", abs(lo.z - P.JAN_PEIT - P.JAN_H) <= TOL, f"verga em z = {lo.z:.3f}")

# --- mobiliário (tabela de móveis)
lo, hi = dim("Tampo da mesa 170 × 70 × 2,5", "Mesa_Tampo_Freijo_170x70x2_5", (PT.MESA_W, PT.MESA_P, 0.025))
chk("Mesa na posição da planta", abs(lo.x - PT.MX0) <= TOL and abs(lo.y - PT.MY0) <= TOL,
    f"canto em ({lo.x:.3f}, {lo.y:.3f}) · planta ({PT.MX0:.3f}, {PT.MY0:.3f})")
chk("Altura do tampo (sentado) 0,73", abs(hi.z - 0.73) <= TOL, f"z = {hi.z:.3f}")
lo, hi = aabb("Cama_Box_base", "Cama_Colchao_88x188", "Cama_Box_rodape_preto")
d = (round(hi.x - lo.x, 3), round(hi.y - lo.y, 3), round(hi.z - lo.z, 3))
chk("Cama 88 × 188 × 62", abs(d[0] - 0.88) <= TOL and abs(d[1] - 1.88) <= TOL and abs(d[2] - 0.62) <= TOL, f"medido {d}")
lo, hi = dim("Prateleira 170 × 25 × 2,5", "Prateleira_Freijo_170x25", (PT.MESA_W, PT.PRAT_P, 0.025))
chk("Prateleira a 1,95 m", abs(lo.z - PT.PRAT_H) <= TOL, f"face inferior z = {lo.z:.3f}")
lo, hi = aabb("Ripado_Ripas_Freijo")
chk("Ripas dentro dos 2,65 m da Parede D", lo.x >= 0 and hi.x <= P.D, f"ripas de x = {lo.x:.4f} a {hi.x:.4f}")
dim("Fundo do ripado 2,65 × 2,64", "Ripado_Fundo_MDF_Preto", (P.D, 0.012, P.PE))
dim("Tapete 140 × 200", "Tapete_140x200", (1.40, 2.00, 0.008))

# --- interferências
sep("Mesa × ripado (mesa elétrica não pode raspar)", ["Mesa_Tampo_Freijo_170x70x2_5"], ["Ripado_Ripas_Freijo"], 0.019)
CAMA_RIGIDA = ["Cama_Box_base", "Cama_Colchao_88x188", "Cama_Box_rodape_preto"]
sep("Mesa × cama (partes rígidas; planta = 5 cm)", ["Mesa_Tampo_Freijo_170x70x2_5", "Mesa_Estrutura_*"], CAMA_RIGIDA, 0.049)
lo_e, hi_e = aabb("Cama_Edredom", "Cama_Manta_Caramelo")
chk("Roupa de cama abaixo do tampo na altura mínima (sem contato)", hi_e.z < 0.73 - 0.025,
    f"topo da roupa de cama {hi_e.z:.3f} m · face inferior do tampo ≥ {0.73-0.025:.3f} m")
sep("Mesa × Parede C", ["Mesa_Tampo_Freijo_170x70x2_5"], ["Parede_C"], 0.019)
sep("PC × perna direita da estrutura", ["PC_Gabinete_em_suporte_suspenso"], ["Mesa_Estrutura_coluna_dir"], 0.02)
sep("PC × perna esquerda da estrutura", ["PC_Gabinete_em_suporte_suspenso"], ["Mesa_Estrutura_coluna_esq"], 0.5)
sep("Cadeira × cama", ["Cadeira_*"], ["Cama_*"], 0.05)
sep("Cama × face das portas do armário (partes rígidas; planta = 0,94)", CAMA_RIGIDA, ["Armario_existente_porta_*"], 0.939)
sep("Cama × puxadores do armário (puxadores estimados, 1,5 cm)", CAMA_RIGIDA, ["Armario_existente_puxador_*"], 0.92)
sep("Roupa de cama × armário (circulação real)", ["Cama_*"], ["Armario_existente_*"], 0.85)
sep("Cama × Parede E", ["Cama_Box_base", "Cama_Colchao_88x188"], ["Parede_E_*"], 0.0)
sep("Ar-condicionado × prateleira", ["ArCondicionado_existente"], ["Prateleira_Freijo_170x25"], 0.10)
sep("Cadeira × armário (circulação atrás da cadeira)", ["Cadeira_*"], ["Armario_existente_*"], 1.0)
# monitores na altura máxima da mesa (+45 cm) × prateleira
lo, hi = aabb("Monitor_27_*")
chk("Monitores na altura da elevação (0,90–1,265 sentado)", abs(lo.z - 0.90) <= 0.01 and abs(hi.z - 1.265) <= 0.01,
    f"monitores de z = {lo.z:.3f} a {hi.z:.3f}")
chk("Monitores centrados na mesa", abs((lo.x + hi.x) / 2 - (PT.MX0 + PT.MESA_W / 2)) <= 0.02,
    f"centro x = {(lo.x + hi.x) / 2:.3f} · mesa {PT.MX0 + PT.MESA_W / 2:.3f}")
topo_max = hi.z + (1.18 - 0.73)
chk("Monitores × prateleira com a mesa no máximo (1,18)", topo_max < PT.PRAT_H,
    f"topo dos monitores no máximo = {topo_max:.3f} m · prateleira = {PT.PRAT_H} m")
lo, hi = aabb("Cama_*")
chk("Cama abaixo do peitoril (janela operável)", hi.z < P.JAN_PEIT, f"topo da cama+travesseiros = {hi.z:.3f} m")
# portas: nada no arco da porta de entrada nem na faixa do banheiro
for nome in ("Cama_*", "Mesa_Tampo_Freijo_170x70x2_5", "Cadeira_*", "Tapete_140x200"):
    lo, hi = aabb(nome)
    chk(f"{nome.rstrip('*_')} fora da faixa de entrada (x > 2,65, y 2,00–2,86)",
        hi.x <= P.D + 1e-4 or hi.y <= P.C + 1e-4, f"x máx {hi.x:.3f}, y máx {hi.y:.3f}")

# --- arquivo
faltando = [im.filepath for im in bpy.data.images if im.source == "FILE" and not Path(bpy.path.abspath(im.filepath)).exists()]
chk("Texturas e HDRIs encontrados (caminhos relativos)", not faltando, f"faltando: {faltando or 'nenhum'}")
chk("Arquivo .blend reaberto em processo novo", True, bpy.data.filepath)
cols = [c.name for c in bpy.data.collections]
chk("Coleções 01–08 presentes", all(any(c.startswith(f"0{i}_") for c in cols) for i in range(1, 9)), ", ".join(cols))

out = PROJ / "07_DOCUMENTACAO" / "validacao_3d.json"
out.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
print("VALIDACAO", sum(r["status"] == "OK" for r in R), "/", len(R))
for r in R:
    print(r["status"], "|", r["verificacao"], "|", r["detalhe"])
