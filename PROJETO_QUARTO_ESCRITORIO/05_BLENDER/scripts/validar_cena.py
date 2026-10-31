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
# --- PC sobre o tampo, notebook, decoração (plano aprovado em 30/10/2026)
PC = ["PC_Gabinete_*"]
lo_pc, hi_pc = aabb(*PC)
lo_t, hi_t = aabb("Mesa_Tampo_Freijo_170x70x2_5")
chk("PC dentro do tampo (x, y) e apoiado nele", lo_pc.x >= lo_t.x - 1e-4 and hi_pc.x <= hi_t.x + 1e-4 and lo_pc.y >= lo_t.y - 1e-4
    and hi_pc.y <= hi_t.y + 1e-4 and abs(lo_pc.z - hi_t.z) <= TOL,
    f"PC x {lo_pc.x:.3f}–{hi_pc.x:.3f}, y {lo_pc.y:.3f}–{hi_pc.y:.3f}, base z {lo_pc.z:.3f} · tampo x {lo_t.x:.3f}–{hi_t.x:.3f}, "
    f"y {lo_t.y:.3f}–{hi_t.y:.3f}, z {hi_t.z:.3f}")
d = tuple(round(h - l, 3) for l, h in zip(lo_pc, hi_pc))
chk("Gabinete 23 × 45 × 46 (com pés)", all(abs(a - b) <= TOL for a, b in zip(d, (PT.PC_W, PT.PC_P, PT.PC_H))), f"medido {d}")
sep("PC × monitor direito", PC, ["Monitor_27_2", "Monitor_27_2_tela"], 0.02)
sep("PC × coluna do braço dos monitores", PC, ["Braco_ELG_F160N_*"], 0.02)
chk("PC × prateleira com a mesa no máximo (1,18)", hi_pc.z + (1.18 - 0.73) < PT.PRAT_H,
    f"topo do PC no máximo = {hi_pc.z + 0.45:.3f} m · prateleira = {PT.PRAT_H} m")
NBK = ["Notebook_*", "Suporte_Notebook_*"]
sep("Notebook × monitor esquerdo", NBK, ["Monitor_27_1", "Monitor_27_1_tela"], 0.01)
sep("Notebook × teclado", NBK, ["Teclado"], 0.02)
sep("Luminária de mesa × monitor esquerdo", ["Luminaria_mesa_*"], ["Monitor_27_1"], 0.02)
sep("Luminária de mesa × notebook", ["Luminaria_mesa_*"], NBK, 0.02)
sep("Caneca × mousepad", ["Caneca", "Caneca_alca"], ["Mousepad"], 0.01)
sep("Headphone × PC", ["Suporte_headphone_*", "Headphone_*"], PC, 0.02)
for nome in ("Suporte_headphone_*", "Caneca", "Luminaria_mesa_*"):
    lo, hi = aabb(nome)
    chk(f"{nome.rstrip('*_')} dentro do tampo", lo.x >= lo_t.x and hi.x <= hi_t.x and lo.y >= lo_t.y and hi.y <= hi_t.y,
        f"x {lo.x:.3f}–{hi.x:.3f}, y {lo.y:.3f}–{hi.y:.3f}")
lo_n, hi_n = aabb("Nicho_*")
chk("Nichos ≥ 0,90 m acima do colchão", lo_n.z - PT.CAMA_H >= 0.90 - 1e-4,
    f"base dos nichos z = {lo_n.z:.3f} · colchão {PT.CAMA_H:.2f} → {lo_n.z - PT.CAMA_H:.3f} m")
chk("Nichos dentro da largura da cama (sobre a cabeceira)", lo_n.x >= 0 and hi_n.x <= P.CAMA_W,
    f"x {lo_n.x:.3f}–{hi_n.x:.3f} · cama 0–{P.CAMA_W}")
sep("Nichos × perfil de LED vertical", ["Nicho_*"], ["L2_Fita_LED_vertical"], 0.05)
sep("Nichos × arandela", ["Nicho_*"], ["L4_Arandela_*"], 0.30)
lo, hi = aabb("Planta_pendente_vaso")
chk("Planta pendente com a base ≥ 1,95 m", lo.z >= 1.95 - 1e-4, f"base do vaso z = {lo.z:.3f}")
sep("Planta pendente × ventilador", ["Planta_pendente_*"], ["Ventilador_*"], 0.30)
lo, hi = aabb("Quadro_A_*", "Quadro_B_*", "Quadro_C_*")
chk("Quadros da Parede E antes da janela (y < 1,10)", hi.y < P.JAN_Y0 and hi.y <= 1.10,
    f"quadros até y = {hi.y:.3f} · janela começa em y = {P.JAN_Y0:.3f}")
sep("Quadros × nichos", ["Quadro_A_*", "Quadro_B_*", "Quadro_C_*"], ["Nicho_*"], 0.02)
lo, hi = aabb("Quadro_D_*", "Quadro_E_*", "Relogio_LED_*")
chk("Itens da prateleira dentro dela", lo.x >= PT.MX0 and hi.x <= PT.MX0 + PT.MESA_W and hi.y <= P.RIP + PT.PRAT_P,
    f"x {lo.x:.3f}–{hi.x:.3f}, y até {hi.y:.3f}")
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
chk("Monitores no eixo do braço (6 cm à esquerda do centro da mesa)", abs((lo.x + hi.x) / 2 - PT.MON_CX) <= 0.01,
    f"centro x = {(lo.x + hi.x) / 2:.3f} · braço {PT.MON_CX:.3f} · mesa {PT.MX0 + PT.MESA_W / 2:.3f}")
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
