"""Camada de realismo sobre o modelo aprovado (não altera nenhuma medida aprovada).

Uso: blender -b quarto_escritorio.blend --python realismo.py
Lê o modelo base e salva 05_BLENDER/quarto_escritorio_realista.blend (o base continua intacto).

O que faz:
- chanfros em móveis, ripas e esquadrias (as quinas pegam luz como na realidade);
- roupa de cama com caimento (edredom e manta caem pela lateral e pelos pés), travesseiro e almofada estofados;
- cadeira com assento/encosto estofados e encosto em tela;
- teclado com teclas, monitores com papel de parede;
- materiais: brilho de tecido (sheen), verniz leve no piso, variação de rugosidade nas paredes;
- modelos CC0 do Poly Haven: ventilador de teto, vasos, livros, porta-lápis, objetos dos nichos e samambaia;
- câmeras panorâmicas 360° para o tour virtual.
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

PROJ = Path(bpy.data.filepath).resolve().parents[1]
sys.path.insert(0, str(PROJ / "03_PLANTAS" / "fonte"))
import planta_tecnica as PT  # noqa: E402
import planta_v1 as P        # noqa: E402

ASSETS = PROJ / "05_BLENDER" / "assets"
MODELS = ASSETS / "models"
SAIDA = PROJ / "05_BLENDER" / "quarto_escritorio_realista.blend"
random.seed(4)

RIP, CAMA_W, CAMA_L, CAMA_H = P.RIP, P.CAMA_W, P.CAMA_L, PT.CAMA_H
MX0, MY0, MESA_W, MESA_P = PT.MX0, PT.MY0, PT.MESA_W, PT.MESA_P
MESA_Z = 0.73


def col(nome):
    return bpy.data.collections[nome]


def remover(prefixos):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefixos):
            bpy.data.objects.remove(ob, do_unlink=True)


def novo_obj(nome, me, cname, mat=None):
    ob = bpy.data.objects.new(nome, me)
    col(cname).objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


def suave(ob, sub=2):
    for p in ob.data.polygons:
        p.use_smooth = True
    if sub:
        m = ob.modifiers.new("Subdiv", "SUBSURF")
        m.levels = m.render_levels = sub


# ------------------------------------------------------------------ materiais
def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def materiais():
    M = bpy.data.materials
    for nome, sheen in (("Tecido_Edredom_poly_wool", 0.8), ("Tecido_Manta_caramelo", 0.9), ("Tecido_Box_Grafite", 0.6),
                        ("Tecido_Colchao", 0.5), ("Tecido_Fronha", 0.7), ("Tecido_Almofada_Caramelo", 0.8),
                        ("Tecido_Cadeira", 0.12), ("Tapete_Cinza_Escuro", 1.0)):
        b = principled(M[nome])
        b.inputs["Sheen Weight"].default_value = sheen
        b.inputs["Sheen Roughness"].default_value = 0.4
    # tapete: textura de fio (ruído fino no relevo)
    nt = M["Tapete_Cinza_Escuro"].node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 900.0
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], principled(M["Tapete_Cinza_Escuro"]).inputs["Normal"])
    # piso: verniz acetinado
    b = principled(M["Piso_Madeira_wood_floor"])
    b.inputs["Coat Weight"].default_value = 0.35
    b.inputs["Coat Roughness"].default_value = 0.22
    # madeira do mobiliário: verniz fosco
    for nome in ("Madeira_Freijo_angli_veneer", "Madeira_Freijo_vertical"):
        b = principled(M[nome])
        b.inputs["Coat Weight"].default_value = 0.12
        b.inputs["Coat Roughness"].default_value = 0.35
    # paredes: variação sutil de rugosidade (marcas de rolo)
    for nome, base in (("Tinta_Grafite_3A3C40", 0.80), ("Tinta_Teto_ECE8E1", 0.88)):
        nt = M[nome].node_tree
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 6.0
        nz.inputs["Detail"].default_value = 6.0
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = base - 0.08, base + 0.06
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], principled(M[nome]).inputs["Roughness"])
    principled(M["Metal_Preto"]).inputs["Roughness"].default_value = 0.42
    # telas: papel de parede (coordenadas geradas X/Z da caixa fina)
    tela = M["Tela_Monitor"]
    nt = tela.node_tree
    for n in list(nt.nodes):
        if n.type not in ("BSDF_PRINCIPLED", "OUTPUT_MATERIAL"):
            nt.nodes.remove(n)
    b = principled(tela)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(ASSETS / "textures" / "wallpaper_monitor.jpg"), check_existing=True)
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["X"], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], img.inputs["Vector"])
    nt.links.new(img.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Emission Strength"].default_value = 0.9
    tela["emissao_noite"] = 0.9
    tela["emissao_dia"] = 1.6


# ------------------------------------------------------------------ chanfros
def chanfros():
    alvo = ("03_MOBILIARIO", "04_MARCENARIA", "02_PORTAS_JANELAS")
    pular = ("Monitor_27_", "Barra_Luz", "Mousepad", "Notebook_tela", "Janela_Folha", "PC_Gabinete_vidro", "PC_Fan_")
    for c in alvo:
        for ob in col(c).all_objects:
            if ob.type != "MESH" or ob.name.startswith(pular) or any(m.type == "BEVEL" for m in ob.modifiers):
                continue
            larg = 0.0012 if ob.name.startswith("Ripado_Ripas") else 0.0025
            m = ob.modifiers.new("Chanfro", "BEVEL")
            m.width, m.segments, m.limit_method, m.angle_limit = larg, 2, "ANGLE", math.radians(40)
            # o chanfro precisa vir antes do array (ripa a ripa)
            idx = list(ob.modifiers).index(m)
            if idx > 0:
                try:
                    ob.modifiers.move(idx, 0)
                except Exception:
                    pass


# ------------------------------------------------------------------ roupa de cama
def tecido_caimento(nome, x0, x1, y0, y1, ztopo, queda_x, queda_y, esp, mat, ruido, cname="03_MOBILIARIO"):
    """Malha de tecido: plano no topo que cai pela lateral (x1) e pelo pé (y1)."""
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    nu, nv = 36, 64
    vs = []
    for i in range(nu + 1):
        s = x0 + (x1 - x0 + queda_x) * i / nu
        row = []
        for j in range(nv + 1):
            r = y0 + (y1 - y0 + queda_y) * j / nv
            dx, dy = max(0.0, s - x1), max(0.0, r - y1)
            x = min(s, x1) + 0.035 * (1 - math.exp(-dx / 0.04)) if dx else s
            y = min(r, y1) + 0.035 * (1 - math.exp(-dy / 0.04)) if dy else r
            z = ztopo - max(dx, dy)
            # leve abaulado no topo (enchimento)
            if not dx and not dy:
                u, v = (s - x0) / (x1 - x0), (r - y0) / (y1 - y0)
                z += 0.012 * math.sin(math.pi * u) * math.sin(math.pi * min(1, v))
            row.append(bm.verts.new((x, y, z)))
        vs.append(row)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    bm.to_mesh(me)
    bm.free()
    ob = novo_obj(nome, me, cname, mat)
    so = ob.modifiers.new("Espessura", "SOLIDIFY")
    so.thickness, so.offset = esp, -1
    tex = bpy.data.textures.new(nome + "_rugas", "CLOUDS")
    tex.noise_scale, tex.noise_depth = 0.09, 2
    dp = ob.modifiers.new("Rugas", "DISPLACE")
    dp.texture, dp.strength, dp.mid_level = tex, ruido, 0.5
    suave(ob, 1)
    return ob


def almofada(nome, sx, sy, sz, mat, loc, rot=(0, 0, 0), cname="03_MOBILIARIO"):
    """Forma de travesseiro: caixa subdividida que afina nas bordas."""
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=10, use_grid_fill=True)
    for v in bm.verts:
        nx, ny = 2 * v.co.x, 2 * v.co.y
        f = max(0.18, (1 - abs(nx) ** 5) * (1 - abs(ny) ** 5))
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz * f))
    bm.to_mesh(me)
    bm.free()
    ob = novo_obj(nome, me, cname, mat)
    ob.location, ob.rotation_euler = loc, rot
    suave(ob, 1)
    return ob


def cama():
    M = bpy.data.materials
    remover(("Cama_Edredom", "Cama_Manta", "Cama_Travesseiro", "Cama_Almofada"))
    y0 = RIP
    tecido_caimento("Cama_Edredom", 0.0, CAMA_W, y0 + 0.40, y0 + CAMA_L, CAMA_H + 0.045, 0.24, 0.22, 0.04,
                    M["Tecido_Edredom_poly_wool"], 0.010)
    # dobra do edredom na cabeceira
    dob = tecido_caimento("Cama_Edredom_dobra", 0.0, CAMA_W, y0 + 0.36, y0 + 0.56, CAMA_H + 0.075, 0.20, 0.0, 0.035,
                          M["Tecido_Edredom_poly_wool"], 0.006)
    tecido_caimento("Cama_Manta_Caramelo", 0.0, CAMA_W, y0 + 1.38, y0 + 1.78, CAMA_H + 0.09, 0.30, 0.0, 0.018,
                    M["Tecido_Manta_caramelo"], 0.012)
    almofada("Cama_Travesseiro", 0.68, 0.44, 0.16, M["Tecido_Fronha"], (CAMA_W / 2, y0 + 0.25, CAMA_H + 0.085),
             (math.radians(-6), 0, 0))
    almofada("Cama_Almofada_Caramelo", 0.44, 0.44, 0.15, M["Tecido_Almofada_Caramelo"],
             (CAMA_W / 2 + 0.06, y0 + 0.22, CAMA_H + 0.27), (math.radians(-72), 0, math.radians(4)))
    del dob


# ------------------------------------------------------------------ cadeira
def cadeira():
    M = bpy.data.materials
    raiz = bpy.data.objects["Cadeira_DT3_Elin"]
    chx, chy = raiz.location.x, raiz.location.y
    remover(("Cadeira_assento", "Cadeira_encosto", "Cadeira_apoio_cabeca"))
    # encosto em tela: padrão de trama
    tela = bpy.data.materials.new("Tela_Encosto_Cadeira")
    nt = tela.node_tree
    b = principled(tela)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 260.0
    br.inputs["Color1"].default_value = (0.02, 0.02, 0.022, 1)
    br.inputs["Color2"].default_value = (0.035, 0.035, 0.04, 1)
    br.inputs["Mortar"].default_value = (0.006, 0.006, 0.007, 1)
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.6
    b.inputs["Sheen Weight"].default_value = 0.08
    partes = [
        almofada("Cadeira_assento", 0.50, 0.48, 0.09, M["Tecido_Cadeira"], (chx, chy - 0.01, 0.49)),
        # encosto e apoio de cabeça: modelados "deitados" (espessura no eixo z) e girados para a vertical
        almofada("Cadeira_encosto", 0.47, 0.62, 0.06, tela, (chx, chy + 0.24, 0.90), (math.radians(90 - 8), 0, 0)),
        almofada("Cadeira_apoio_cabeca", 0.27, 0.14, 0.06, M["Tecido_Cadeira"], (chx, chy + 0.31, 1.31),
                 (math.radians(90 - 12), 0, 0)),
    ]
    for p in partes:
        p.data.polygons.foreach_set("use_smooth", [True] * len(p.data.polygons))
        p.parent = raiz
        p.matrix_parent_inverse = raiz.matrix_world.inverted()


# ------------------------------------------------------------------ teclado
def teclado():
    kb = bpy.data.objects["Teclado"]
    lo = Vector([min(v.co[i] for v in kb.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in kb.data.vertices) for i in range(3)])
    me = bpy.data.meshes.new("Teclado_teclas")
    bm = bmesh.new()
    cap = 0.0155
    for r in range(5):
        for c in range(20):
            x = lo.x + 0.012 + c * 0.0172
            y = lo.y + 0.012 + r * 0.021
            if x + cap > hi.x - 0.01:
                continue
            bmesh.ops.create_cube(bm, size=1.0, matrix=__import__("mathutils").Matrix.LocRotScale(
                Vector((x + cap / 2, y + cap / 2, hi.z + 0.004)), None, Vector((cap, cap, 0.008))))
    bm.to_mesh(me)
    bm.free()
    ob = novo_obj("Teclado_teclas", me, "03_MOBILIARIO", bpy.data.materials["Plastico_Teclado"])
    ob.location = kb.location
    ob.parent = kb.parent
    ob.matrix_parent_inverse = kb.matrix_parent_inverse.copy()
    m = ob.modifiers.new("Chanfro", "BEVEL")
    m.width, m.segments = 0.0015, 2


# ------------------------------------------------------------------ modelos Poly Haven
def importar_gltf(caminho, cname, nome_raiz):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(caminho))
    novos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new(nome_raiz, None)
    col(cname).objects.link(raiz)
    for o in novos:
        for c in o.users_collection:
            c.objects.unlink(o)
        col(cname).objects.link(o)
        if o.parent is None:
            o.parent = raiz
    return raiz, novos


def modelos():
    remover(("Ventilador_", "Vaso_planta", "Planta_folhagem", "Livro_"))
    # ventilador de teto (existente; tamanho real não informado → Ø ~1,10 m)
    fan, _ = importar_gltf(MODELS / "ceiling_fan" / "ceiling_fan.gltf", "05_ILUMINACAO", "Ventilador_teto_existente")
    fan.location, fan.scale = (P.D / 2, P.E / 2, P.PE), (0.75, 0.75, 0.75)
    fan["status"] = "existente; modelo Poly Haven 'ceiling_fan' (CC0) em escala estimada"
    luz = bpy.data.objects["Luz_Ventilador_3000K"]
    luz.location.z = P.PE - 0.516 * 0.75 - 0.03
    # vaso pequeno na prateleira (ponta esquerda)
    pl, _ = importar_gltf(MODELS / "potted_plant_04" / "potted_plant_04.gltf", "06_DECORACAO", "Vaso_suculenta_prateleira")
    pl.location = (MX0 + 0.16, RIP + 0.13, PT.PRAT_H + 0.025)
    # planta média em escala reduzida na prateleira (x 1,25–1,50); o canto da mesa ficou com a luminária
    pl2, _ = importar_gltf(MODELS / "potted_plant_02" / "potted_plant_02.gltf", "06_DECORACAO", "Vaso_planta_prateleira")
    pl2.scale = (0.36, 0.36, 0.36)
    assentar(pl2, (1.375, RIP + 0.125), PT.PRAT_H + 0.025)
    # porta-lápis e papelaria (canto direito da mesa)
    st, _ = importar_gltf(MODELS / "stationery_supplies" / "stationery_supplies.gltf", "06_DECORACAO", "Papelaria_mesa")
    st.location, st.rotation_euler = (MX0 + MESA_W - 0.20, MY0 + 0.12, MESA_Z + 0.074), (0, 0, math.radians(-90))
    # objetos dos nichos (centro interno: y = RIP + 0,085; piso interno a 1,565)
    zi = PT.NICHO_Z0 + 0.015
    yc = RIP + 0.006 + (PT.NICHO_P - 0.006) / 2
    cx = [PT.NICHOS_X0 + k * (PT.NICHO_W + PT.NICHO_GAP) + PT.NICHO_W / 2 for k in range(3)]
    for k, (modelo, esc, rot) in enumerate((("ceramic_vase_02", 0.6, 0), ("carved_wooden_elephant", 1.5, 20),
                                            ("bronze_whale_statue", 0.14, 90))):
        r, _ = importar_gltf(MODELS / modelo / f"{modelo}.gltf", "06_DECORACAO", f"Nicho_{k+1}_objeto_{modelo}")
        r.scale, r.rotation_euler = (esc,) * 3, (0, 0, math.radians(rot))
        assentar(r, (cx[k], yc), zi)
    # samambaia no vaso pendente (base do vaso a 1,95 m; vaso de 16 cm)
    fe, _ = importar_gltf(MODELS / "fern_02" / "fern_02.gltf", "06_DECORACAO", "Planta_pendente_samambaia")
    fe.scale = (0.22, 0.22, 0.22)
    assentar(fe, (0.30, 2.25), 1.95 + 0.16 - 0.025)
    # livros: trecho do conjunto do Poly Haven (só os de até 24 cm de profundidade)
    blend = MODELS / "decorative_book_set_01" / "decorative_book_set_01.blend"
    with bpy.data.libraries.load(str(blend), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    livros = [o for o in dst.objects if o and o.type == "MESH" and not o.name.startswith("magazine")]
    for o in livros:                       # precisa estar na cena para matrix_world valer
        col("06_DECORACAO").objects.link(o)
    bpy.context.view_layer.update()

    def ext(o):
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return (min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs), min(c.z for c in cs))
    livros = sorted(livros, key=lambda o: ext(o)[0])
    x_ini = ext(livros[0])[0]
    escolhidos = [o for o in livros if ext(o)[1] - x_ini <= 0.36 and ext(o)[3] - ext(o)[2] <= 0.24]
    y_min = min(ext(o)[2] for o in escolhidos)
    z_min = min(ext(o)[4] for o in escolhidos)
    for o in livros:
        if o not in escolhidos:
            bpy.data.objects.remove(o, do_unlink=True)
    raiz = bpy.data.objects.new("Livros_prateleira", None)
    col("06_DECORACAO").objects.link(raiz)
    raiz.location = (MX0 + MESA_W - 0.42 - x_ini, RIP + 0.03 - y_min, PT.PRAT_H + 0.025 - z_min)
    for o in escolhidos:
        o.parent = raiz
    for o in list(dst.objects):            # objetos da biblioteca que sobraram sem uso
        try:
            if o and o.users == 0:
                bpy.data.objects.remove(o)
        except ReferenceError:              # já removido acima
            pass
    return len(escolhidos)


def caixa_mundo(raiz):
    bpy.context.view_layer.update()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in raiz.children_recursive:
        if o.type == "MESH":
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
    return lo, hi


def assentar(raiz, centro_xy, z_base):
    """Move a raiz para que a caixa real do modelo fique centrada em centro_xy com a base em z_base."""
    lo, hi = caixa_mundo(raiz)
    raiz.location += Vector((centro_xy[0] - (lo.x + hi.x) / 2, centro_xy[1] - (lo.y + hi.y) / 2, z_base - lo.z))
    lo, hi = caixa_mundo(raiz)
    raiz["dimensoes_reais_cm"] = " × ".join(f"{(h - l) * 100:.1f}" for l, h in zip(lo, hi))
    print("ASSENTADO", raiz.name, raiz["dimensoes_reais_cm"], tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))


def Matrix_id():
    from mathutils import Matrix
    return Matrix.Identity(4)


# ------------------------------------------------------------------ câmeras 360°
PANOS = {
    # nome: (x, y, z) — z = altura dos olhos (em pé 1,60; sentado 1,18; sentado na cama 1,05)
    "PANO_entrada": (2.40, 2.42, 1.60),
    "PANO_centro": (1.30, 1.72, 1.60),
    "PANO_mesa": (PT.MX0 + PT.MESA_W / 2 - 0.10, PT.MY0 + PT.MESA_P + 0.42, 1.18),
    "PANO_cama": (0.48, 1.40, 1.05),
}


def cameras_360():
    for nome, loc in PANOS.items():
        cd = bpy.data.cameras.new(nome)
        cd.type = "PANO"
        cd.panorama_type = "EQUIRECTANGULAR"
        cd.clip_start = 0.02
        ob = bpy.data.objects.new(nome, cd)
        ob.location = loc
        ob.rotation_euler = (math.radians(90), 0, 0)    # centro da imagem = +y (em direção ao armário)
        col("07_CAMERAS").objects.link(ob)


def main():
    materiais()
    chanfros()
    cama()
    cadeira()
    teclado()
    n = modelos()
    cameras_360()
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA), relative_remap=True)
    print("REALISMO OK", SAIDA, "livros", n)


main()
