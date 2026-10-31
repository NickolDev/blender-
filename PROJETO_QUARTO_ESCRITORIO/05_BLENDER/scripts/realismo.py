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
- câmeras panorâmicas 360° para o tour virtual;
- detalhes do setup (31/10/2026): telas com conteúdo real (editor de código, planta do projeto, e-mail), headphone
  modelado, fans do PC com pás e anel de LED, cooler torre e memórias, samambaia pendente cheia e caindo pela borda, vaso cônico com terra,
  vidro nos quadros, cabos, caneca com café, relógio com dígitos, teclado/touchpad no notebook, cúpula aberta na
  luminária.
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
    """Apaga os objetos com esses prefixos e todos os seus filhos (filho órfão cairia na origem)."""
    alvo = [ob for ob in bpy.data.objects if ob.name.startswith(prefixos)]
    for ob in alvo:
        alvo += [c for c in ob.children_recursive if c not in alvo]
    for ob in alvo:
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
    # samambaia do vaso pendente: ver planta_pendente_cheia()
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


# ------------------------------------------------------------------ detalhes do setup (31/10/2026)
def malha_torus(nome, R, r, seg=48, seg_r=12):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    vs = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(seg_r):
            b = 2 * math.pi * j / seg_r
            row.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        vs.append(row)
    for i in range(seg):
        for j in range(seg_r):
            bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % seg_r], vs[i][(j + 1) % seg_r]))
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def malha_cone(nome, r0, r1, h, seg=48, tampa=True):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=tampa, segments=seg, radius1=r0, radius2=r1, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    bm.to_mesh(me)
    bm.free()
    return me


def filho_da_mesa(ob):
    mesa = bpy.data.objects["Mesa_Tampo_Freijo_170x70x2_5"]
    bpy.context.view_layer.update()
    ob.parent = mesa
    ob.matrix_parent_inverse = mesa.matrix_world.inverted()


def mat_tela(nome, imagem, dia=1.6, noite=0.9):
    """Tela ligada: imagem emissiva. U = 1 − X da coordenada Generated, porque a face da tela aponta para +y e quem
    olha da cadeira vê +x à esquerda (sem isso o texto sairia espelhado)."""
    m = bpy.data.materials.new(nome)
    nt = m.node_tree
    b = principled(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(str(ASSETS / "textures" / imagem), check_existing=True)
    im.extension = "EXTEND"
    nt.links.new(tc.outputs["Generated"], sp.inputs["Vector"])
    nt.links.new(sp.outputs["X"], inv.inputs[1])
    nt.links.new(inv.outputs["Value"], cb.inputs["X"])
    nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
    nt.links.new(cb.outputs["Vector"], im.inputs["Vector"])
    nt.links.new(im.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Emission Strength"].default_value = noite
    m["emissao_noite"], m["emissao_dia"] = noite, dia
    return m


def telas():
    # Monitor_27_2 (x maior, junto do PC) fica à esquerda de quem está sentado
    for ob_nome, img in (("Monitor_27_2_tela", "tela_monitor_codigo.jpg"), ("Monitor_27_1_tela", "tela_monitor_planta.jpg"),
                         ("Notebook_tela", "tela_notebook_email.jpg")):
        ob = bpy.data.objects[ob_nome]
        ob.data = ob.data.copy()
        ob.data.materials.clear()
        ob.data.materials.append(mat_tela(f"Tela_{ob_nome}", img))


def headphone():
    M = bpy.data.materials
    remover(("Headphone_",))
    hx, hy, z = 2.50, 0.67, MESA_Z
    R, zc = 0.085, z + 0.265 + 0.006 - 0.085
    cu = bpy.data.curves.new("Headphone_arco", "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", 0.006, 4
    sp = cu.splines.new("POLY")
    n = 24
    sp.points.add(n)
    for i in range(n + 1):
        a = math.pi * i / n
        sp.points[i].co = (hx + R * math.cos(a), hy, zc + R * math.sin(a), 1)
    arco = novo_obj("Headphone_arco", cu, "03_MOBILIARIO", M["Preto_Fosco"])
    # almofada do arco (couro sintético)
    cu2 = cu.copy()
    cu2.bevel_depth = 0.009
    almo = novo_obj("Headphone_arco_almofada", cu2, "03_MOBILIARIO", M["Tecido_Cadeira"])
    almo.location = (0, 0, -0.008)
    pecas = [arco, almo]
    for s_ in (-1, 1):
        lado = "esq" if s_ < 0 else "dir"
        cx = hx + s_ * R
        concha = novo_obj(f"Headphone_concha_{lado}", malha_cone(f"Headphone_concha_{lado}", 0.045, 0.040, 0.028),
                          "03_MOBILIARIO", M["Preto_Fosco"])
        concha.location = (cx, hy, zc - 0.035)
        concha.rotation_euler = (0, -s_ * math.pi / 2, 0)    # eixo da concha apontando para dentro (±x)
        suave(concha, 0)
        b = concha.modifiers.new("Chanfro", "BEVEL")
        b.width, b.segments = 0.006, 3
        coxim = novo_obj(f"Headphone_coxim_{lado}", malha_torus(f"Headphone_coxim_{lado}", 0.032, 0.011), "03_MOBILIARIO",
                         M["Tecido_Cadeira"])
        coxim.location = (cx - s_ * 0.034, hy, zc - 0.035)       # almofada na face interna da concha
        coxim.rotation_euler = (0, math.pi / 2, 0)
        pecas += [concha, coxim]
    for o in pecas:
        filho_da_mesa(o)


def fans_pc():
    M = bpy.data.materials
    remover(("PC_Fan_",))
    x = PT.PC_X0 + PT.PC_W / 2
    y = PT.PC_Y0 + PT.PC_P - 0.030
    from mathutils import Matrix
    pas = bpy.data.materials.new("Plastico_Pas_Fan")
    pb = principled(pas)
    pb.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1)
    pb.inputs["Roughness"].default_value = 0.35
    pecas = []
    for i in range(3):
        fz = MESA_Z + 0.17 + i * 0.125
        anel = novo_obj(f"PC_Fan_{i+1}_anel_LED", malha_torus(f"PC_Fan_{i+1}_anel_LED", 0.056, 0.0035, 64, 8),
                        "03_MOBILIARIO", M["LED_PC_3000K"])
        anel.location, anel.rotation_euler = (x, y + 0.004, fz), (math.pi / 2, 0, 0)
        moldura = novo_obj(f"PC_Fan_{i+1}_moldura", malha_torus(f"PC_Fan_{i+1}_moldura", 0.058, 0.007, 64, 8),
                           "03_MOBILIARIO", M["Preto_Fosco"])
        moldura.location, moldura.rotation_euler = (x, y - 0.006, fz), (math.pi / 2, 0, 0)
        moldura.scale = (1, 1, 1.8)
        hub = novo_obj(f"PC_Fan_{i+1}_hub", malha_cone(f"PC_Fan_{i+1}_hub", 0.019, 0.019, 0.012), "03_MOBILIARIO", pas)
        hub.location, hub.rotation_euler = (x, y + 0.001, fz), (math.pi / 2, 0, 0)
        pecas += [anel, moldura, hub]
        for k in range(7):
            me = bpy.data.meshes.new(f"PC_Fan_{i+1}_pa_{k+1}")
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts:
                u = v.co.x + 0.5                          # 0 → raiz, 1 → ponta
                v.co.x = 0.019 + u * 0.033
                v.co.y *= 0.016 + 0.010 * u               # pá mais larga na ponta
                v.co.z *= 0.0015
            bm.to_mesh(me)
            bm.free()
            pa = novo_obj(f"PC_Fan_{i+1}_pa_{k+1}", me, "03_MOBILIARIO", pas)
            # pá no plano XY → plano XZ (eixo da fan = y), com 25° de passo, distribuída em volta do eixo
            pa.matrix_world = (Matrix.Translation((x, y - 0.004, fz)) @ Matrix.Rotation(k * 2 * math.pi / 7, 4, "Y")
                               @ Matrix.Rotation(math.radians(90 + 25), 4, "X"))
            pecas.append(pa)
    for o in pecas:
        filho_da_mesa(o)


def planta_pendente_cheia():
    """Vaso cônico com terra e samambaia de 6 touceiras caindo pela borda (a do modelo é uma touceira só, achatada)."""
    M = bpy.data.materials
    px, py, pz = 0.30, 2.25, 1.95
    remover(("Planta_pendente_vaso", "Planta_pendente_samambaia"))
    vaso = novo_obj("Planta_pendente_vaso", malha_cone("Planta_pendente_vaso", 0.068, 0.09, 0.16), "06_DECORACAO",
                    M["Ceramica_Preta_Fosca"])
    vaso.location = (px, py, pz)
    b = vaso.modifiers.new("Chanfro", "BEVEL")
    b.width, b.segments = 0.004, 3
    borda = novo_obj("Planta_pendente_vaso_borda", malha_torus("Planta_pendente_vaso_borda", 0.088, 0.006), "06_DECORACAO",
                     M["Ceramica_Preta_Fosca"])
    borda.location = (px, py, pz + 0.16)
    terra = bpy.data.materials.new("Terra_Vaso")
    principled(terra).inputs["Base Color"].default_value = (0.035, 0.025, 0.018, 1)
    principled(terra).inputs["Roughness"].default_value = 1.0
    t = novo_obj("Planta_pendente_terra", malha_cone("Planta_pendente_terra", 0.084, 0.084, 0.004), "06_DECORACAO", terra)
    t.location = (px, py, pz + 0.145)
    raiz0, novos = importar_gltf(MODELS / "fern_02" / "fern_02.gltf", "06_DECORACAO", "Planta_pendente_samambaia_1")
    filhos = [o for o in novos if o.parent == raiz0]
    from mathutils import Matrix
    topo = Vector((px, py, pz + 0.15))
    rnd = random.Random(7)
    for k in range(6):
        if k == 0:
            r = raiz0
        else:
            r = bpy.data.objects.new(f"Planta_pendente_samambaia_{k+1}", None)
            col("06_DECORACAO").objects.link(r)
            for f in filhos:
                c = f.copy()                                  # malha compartilhada (instância leve)
                col("06_DECORACAO").objects.link(c)
                c.parent = r
                c.matrix_parent_inverse = f.matrix_parent_inverse.copy()
        esc = 0.17 + 0.04 * rnd.random()
        inc = math.radians(24 + 10 * rnd.random())          # quanto a touceira tomba para fora do vaso
        az = k * 2 * math.pi / 6 + rnd.uniform(-0.25, 0.25)
        # as frondes do modelo se espalham para (+x, −y): gira 44° para alinhá-las a +x, tomba em y, distribui em z
        r.matrix_world = (Matrix.Translation(topo) @ Matrix.Rotation(az, 4, "Z") @ Matrix.Rotation(inc, 4, "Y")
                          @ Matrix.Rotation(math.radians(44), 4, "Z") @ Matrix.Scale(esc, 4))
    bpy.context.view_layer.update()
    lo = min((o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.name.startswith("fern") and o.type == "MESH"
             for c in o.bound_box) if any(o.name.startswith("fern") for o in bpy.data.objects) else None
    print("SAMAMBAIA ponto mais baixo z =", lo)


def quadros_vidro():
    for m in bpy.data.materials:
        if m.name.startswith("Arte_PB_"):
            b = principled(m)
            b.inputs["Coat Weight"].default_value = 1.0      # vidro do quadro: reflexo nítido por cima da impressão
            b.inputs["Coat Roughness"].default_value = 0.03


def cabo(nome, pts, raio=0.0028, mesa=False):
    cu = bpy.data.curves.new(nome, "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", raio, 3
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    sp.order_u, sp.use_endpoint_u = 3, True
    ob = novo_obj(nome, cu, "03_MOBILIARIO", bpy.data.materials["Preto_Fosco"])
    if mesa:
        filho_da_mesa(ob)
    return ob


def cabos():
    td = P.D / 2                                              # tomada da Parede D (x = 1,325; z ≈ 0,30)
    mx = PT.MON_CX
    # monitores → coluna do braço → passa-cabo no tampo
    for i, sx in enumerate((-0.312, 0.312)):
        cabo(f"Cabo_monitor_{i+1}", [(mx + sx, MY0 + 0.22, MESA_Z + 0.30), (mx + sx * 0.5, MY0 + 0.10, MESA_Z + 0.33),
                                     (mx + 0.022, MY0 + 0.075, MESA_Z + 0.30), (mx + 0.022, MY0 + 0.075, MESA_Z + 0.02)],
             mesa=True)
    # feixe sob o tampo até a tomada (pende no vão entre a mesa e o ripado)
    cabo("Cabo_feixe_tomada", [(mx, MY0 + 0.06, MESA_Z - 0.03), (mx - 0.10, 0.045, 0.55), (td + 0.08, 0.040, 0.34),
                               (td, RIP + 0.012, 0.30)], raio=0.006)
    pcx = PT.PC_X0 + 0.15
    cabo("Cabo_PC_energia", [(pcx, PT.PC_Y0 + 0.002, MESA_Z + 0.07), (pcx, PT.PC_Y0 - 0.03, MESA_Z + 0.05),
                             (pcx, 0.040, MESA_Z + 0.02),
                             (pcx - 0.05, 0.045, 0.60), (td + 0.25, 0.040, 0.36), (td + 0.02, RIP + 0.012, 0.30)], raio=0.004)
    lx = 1.01
    cabo("Cabo_luminaria", [(lx + 0.05, 0.12, MESA_Z + 0.003), (lx + 0.03, MY0 + 0.012, MESA_Z + 0.003),
                            (lx + 0.03, 0.044, MESA_Z),
                            (lx + 0.04, 0.042, MESA_Z - 0.10), (td - 0.10, 0.040, 0.40), (td - 0.02, RIP + 0.012, 0.30)],
         raio=0.0022)


def caneca_relogio_notebook_luminaria():
    M = bpy.data.materials
    # caneca: alça em anel e café
    remover(("Caneca_alca",))
    z = MESA_Z
    alca = novo_obj("Caneca_alca", malha_torus("Caneca_alca", 0.022, 0.0055), "06_DECORACAO", M["Ceramica_Caneca"])
    alca.location, alca.rotation_euler = (2.338, 0.66, z + 0.05), (math.pi / 2, 0, 0)
    alca.scale = (0.8, 1, 1)
    cafe = bpy.data.materials.new("Cafe")
    b = principled(cafe)
    b.inputs["Base Color"].default_value = (0.03, 0.012, 0.004, 1)
    b.inputs["Roughness"].default_value = 0.05
    c = novo_obj("Caneca_cafe", malha_cone("Caneca_cafe", 0.034, 0.034, 0.0006), "06_DECORACAO", cafe)
    c.location = (2.30, 0.66, z + 0.095)
    filho_da_mesa(alca)
    filho_da_mesa(c)
    # relógio: visor escuro + dígitos (acendem à noite com o LED 3000 K)
    disp = bpy.data.objects["Relogio_LED_display"]
    disp.data.materials.clear()
    disp.data.materials.append(M["Preto_Fosco"])
    zp = PT.PRAT_H + 0.025
    tx = bpy.data.curves.new("Relogio_LED_digitos", "FONT")
    tx.body, tx.size, tx.align_x, tx.align_y = "22:41", 0.026, "CENTER", "CENTER"
    tx.extrude = 0.0004
    d = novo_obj("Relogio_LED_digitos", tx, "06_DECORACAO", M["LED_3000K"])
    d.location = (2.08, RIP + 0.1425, zp + 0.030)
    d.rotation_euler = (math.pi / 2, 0, math.pi)
    # notebook: teclado e touchpad
    nb = bpy.data.objects["Notebook_base"]
    lo = Vector([min(v.co[i] for v in nb.data.vertices) for i in range(3)]) + nb.location
    hi = Vector([max(v.co[i] for v in nb.data.vertices) for i in range(3)]) + nb.location
    for nome, (ya, yb, xa, xb, cor) in {"Notebook_teclado": (0.025, 0.125, 0.02, 0.02, (0.02, 0.02, 0.022, 1)),
                                        "Notebook_touchpad": (0.145, 0.205, 0.105, 0.105, (0.33, 0.34, 0.36, 1))}.items():
        m = bpy.data.materials.new(nome)
        principled(m).inputs["Base Color"].default_value = cor
        principled(m).inputs["Roughness"].default_value = 0.45
        me = bpy.data.meshes.new(nome)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(me)
        bm.free()
        ob = novo_obj(nome, me, "03_MOBILIARIO", m)
        ob.scale = (hi.x - lo.x - xa - xb, yb - ya, 0.001)
        ob.location = ((lo.x + xa + hi.x - xb) / 2, lo.y + (ya + yb) / 2, hi.z + 0.0004)
        filho_da_mesa(ob)
    # luminária: cúpula cônica aberta com lâmpada dentro
    cup = bpy.data.objects["Luminaria_mesa_cupula"]
    loc, rot = cup.matrix_world.translation.copy(), cup.matrix_world.to_euler()
    bpy.data.objects.remove(cup, do_unlink=True)
    me = malha_cone("Luminaria_mesa_cupula", 0.045, 0.022, 0.075, 48, tampa=False)
    nova = novo_obj("Luminaria_mesa_cupula", me, "06_DECORACAO", M["Preto_Fosco"])
    so = nova.modifiers.new("Espessura", "SOLIDIFY")
    so.thickness = 0.0015
    nova.location, nova.rotation_euler = loc, rot
    bulbo = bpy.data.meshes.new("Luminaria_mesa_lampada")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.018)
    bm.to_mesh(bulbo)
    bm.free()
    bl = novo_obj("Luminaria_mesa_lampada", bulbo, "06_DECORACAO", M["Lampada_3000K"])
    bl.location = loc + rot.to_matrix() @ Vector((0, 0, 0.03))
    filho_da_mesa(nova)
    filho_da_mesa(bl)


def caixa(nome, x0, y0, z0, x1, y1, z1, mat, cname="03_MOBILIARIO", chanfro=0.0):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))
    bm.to_mesh(me)
    bm.free()
    ob = novo_obj(nome, me, cname, mat)
    if chanfro:
        m = ob.modifiers.new("Chanfro", "BEVEL")
        m.width, m.segments = chanfro, 2
    return ob


def interior_pc():
    """Cooler torre em alumínio escuro (o cilindro cromado refletia os anéis de LED como um disco branco) e 2 pentes
    de memória ao lado."""
    M = bpy.data.materials
    remover(("PC_Cooler_CPU",))
    x1 = PT.PC_X0 + PT.PC_W - 0.010                         # face da placa-mãe
    y0, z0 = PT.PC_Y0, MESA_Z
    alu = bpy.data.materials.new("Aluminio_Anodizado_Escuro")
    b = principled(alu)
    b.inputs["Base Color"].default_value = (0.05, 0.05, 0.055, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.45
    pecas = [caixa("PC_Cooler_CPU_dissipador", x1 - 0.105, y0 + 0.12, z0 + 0.30, x1 - 0.045, y0 + 0.24, z0 + 0.42, alu,
                   chanfro=0.003),
             caixa("PC_Cooler_CPU_fan", x1 - 0.105, y0 + 0.24, z0 + 0.30, x1 - 0.045, y0 + 0.265, z0 + 0.42,
                   M["Preto_Fosco"], chanfro=0.004),
             caixa("PC_Cooler_CPU_base", x1 - 0.045, y0 + 0.15, z0 + 0.33, x1, y0 + 0.21, z0 + 0.39, alu)]
    for k in range(2):
        pecas.append(caixa(f"PC_Memoria_RAM_{k+1}", x1 - 0.034, y0 + 0.285 + k * 0.012, z0 + 0.28, x1,
                           y0 + 0.292 + k * 0.012, z0 + 0.42, M["Preto_Fosco"]))
    for o in pecas:
        filho_da_mesa(o)
    em = next(n for n in M["LED_PC_3000K"].node_tree.nodes if n.type == "EMISSION")
    em.inputs["Strength"].default_value = 6.0                # anéis das fans com brilho de LED de verdade


def luzes_invisiveis_na_camera():
    """No Cycles a luz pontual/spot/área aparece como disco para a câmera; quem deve aparecer são as peças emissivas
    (fitas, lâmpadas, anéis das fans). Mantém a luz no ambiente e nos reflexos difusos."""
    for ob in bpy.data.objects:
        if ob.type == "LIGHT" and ob.data.type != "SUN" and not ob.name.startswith("Portal"):
            ob.visible_camera = False
            ob.visible_glossy = False


def detalhes_setup():
    luzes_invisiveis_na_camera()
    interior_pc()
    telas()
    headphone()
    fans_pc()
    planta_pendente_cheia()
    quadros_vidro()
    cabos()
    caneca_relogio_notebook_luminaria()


def main():
    materiais()
    chanfros()
    cama()
    cadeira()
    teclado()
    n = modelos()
    detalhes_setup()
    cameras_360()
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA), relative_remap=True)
    print("REALISMO OK", SAIDA, "livros", n)


main()
