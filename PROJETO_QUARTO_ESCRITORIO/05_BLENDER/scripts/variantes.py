"""Temas e layouts da Suíte 01 sobre o modelo realista (não altera o .blend salvo, a não ser com --salvar).

Uso:
    blender -b quarto_escritorio_realista.blend --python variantes.py -- --tema japandi --layout C \\
        [--render dia,noite,planta] [--amostras 64] [--res 1440x900] [--salvar] [--teste]

Ordem: 1) decoração/materiais do tema no layout A (coordenadas do projeto aprovado); 2) rearranjo da mesa e
transformação dos grupos para o layout; 3) cabos, planta de chão e planta pendente na posição do layout;
4) validação dimensional do layout (07_DOCUMENTACAO/validacao_layouts.json); 5) renders em
08_VISUALIZADOR_3D/temas/<tema>_<layout>_<modo>.jpg.
Temas e layouts: temas_dados.py (mesma fonte da página de apresentação).
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

PROJ = Path(bpy.data.filepath).resolve().parents[1]
SCRIPTS = PROJ / "05_BLENDER" / "scripts"
sys.path.insert(0, str(PROJ / "03_PLANTAS" / "fonte"))
sys.path.insert(0, str(SCRIPTS))
import planta_tecnica as PT   # noqa: E402
import planta_v1 as P         # noqa: E402
from temas_dados import LAYOUTS, TEMAS  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(nome, padrao=None):
    return ARGS[ARGS.index(nome) + 1] if nome in ARGS else padrao


TEMA = arg("--tema", "escuro")
LAYOUT = arg("--layout", "A")
RENDER = [m for m in arg("--render", "").split(",") if m]
AMOSTRAS = int(arg("--amostras", "64"))
RES = tuple(int(v) for v in arg("--res", "1440x900").split("x"))
TESTE = "--teste" in ARGS
ASSETS = PROJ / "05_BLENDER" / "assets"
TEX, MODELS = ASSETS / "textures", ASSETS / "models"
OUT = PROJ / "08_VISUALIZADOR_3D" / "temas" / ("_teste" if TESTE else "")
VALID = PROJ / "07_DOCUMENTACAO" / "validacao_layouts.json"

D, E, C, PE, RIP = P.D, P.E, P.C, P.PE, P.RIP
JAN_Y0, JAN_Y1, JAN_PEIT, JAN_H = P.JAN_Y0, P.JAN_Y1, P.JAN_PEIT, P.JAN_H
MX0, MY0, MESA_W, MESA_P = PT.MX0, PT.MY0, PT.MESA_W, PT.MESA_P
MESA_Z, CAMA_W, CAMA_L, CAMA_H = 0.73, P.CAMA_W, P.CAMA_L, PT.CAMA_H
CX_MESA = MX0 + MESA_W / 2
VAO0, PASSO = 0.035, 0.035                    # centros dos vãos do ripado: 0,035 + 0,035·i


# ------------------------------------------------------------------ utilidades
def srgb_lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def kelvin(k):
    t = k / 100
    r = 255 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    rgb = [max(0, min(255, v)) / 255 for v in (r, g, b)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)


def col(nome):
    return bpy.data.collections[nome]


def bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def com_prefixo(prefixos):
    return [o for o in bpy.data.objects if o.name.startswith(tuple(prefixos))]


def raizes(prefixos):
    """Objetos do grupo cujo ancestral não está no grupo (transformar só estes; os filhos acompanham)."""
    s = set(com_prefixo(prefixos))
    out = []
    for o in s:
        p, dentro = o.parent, False
        while p:
            if p in s:
                dentro = True
                break
            p = p.parent
        if not dentro:
            out.append(o)
    return out


def transformar(prefixos, M):
    bpy.context.view_layer.update()
    for o in raizes(prefixos):
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()


def remover(prefixos):
    alvo = com_prefixo(prefixos)
    for o in list(alvo):
        alvo += [c for c in o.children_recursive if c not in alvo]
    for o in alvo:
        bpy.data.objects.remove(o, do_unlink=True)


def caixa_mundo(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in objs:
        if o.type not in ("MESH", "CURVE", "FONT"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            w = ev.matrix_world @ v.co
            lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
        ev.to_mesh_clear()
    return lo, hi


def caixa(prefixos, filhos=True):
    objs = com_prefixo(prefixos)
    if filhos:
        for o in list(objs):
            objs += [c for c in o.children_recursive if c not in objs]
    return caixa_mundo(objs)


def novo_obj(nome, me, cname, mat=None):
    ob = bpy.data.objects.new(nome, me)
    col(cname).objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


def malha_caixa(nome, x0, y0, z0, x1, y1, z1):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))
    bm.to_mesh(me)
    bm.free()
    return me


def importar(nome_modelo, cname, nome_raiz):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(MODELS / nome_modelo / f"{nome_modelo}.gltf"))
    novos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new(nome_raiz, None)
    col(cname).objects.link(raiz)
    for o in novos:
        for c in o.users_collection:
            c.objects.unlink(o)
        col(cname).objects.link(o)
        if o.parent is None:
            o.parent = raiz
    return raiz


def assentar(raiz, xy, z, caber=None, rot=0.0, esc=1.0):
    """Centra a caixa real do modelo em xy com a base em z. caber=(w, d, h): reduz a escala até caber."""
    raiz.rotation_euler = (0, 0, math.radians(rot))
    raiz.scale = (esc,) * 3
    bpy.context.view_layer.update()
    lo, hi = caixa_mundo(raiz.children_recursive)
    if caber:
        f = min(1.0, *(c / (h - l) for c, l, h in zip(caber, lo, hi)))
        raiz.scale = (esc * f,) * 3
        bpy.context.view_layer.update()
        lo, hi = caixa_mundo(raiz.children_recursive)
    raiz.location += Vector((xy[0] - (lo.x + hi.x) / 2, xy[1] - (lo.y + hi.y) / 2, z - lo.z))
    bpy.context.view_layer.update()
    return raiz


# ------------------------------------------------------------------ materiais do tema
def stats(img):
    """Média e desvio da luminância da textura (para a cor final bater com o hex do tema)."""
    import array
    px = array.array("f", [0.0]) * (img.size[0] * img.size[1] * 4)
    img.pixels.foreach_get(px)
    n = len(px) // 4
    passo = max(1, n // 40000)
    lum = [0.2126 * px[i * 4] + 0.7152 * px[i * 4 + 1] + 0.0722 * px[i * 4 + 2] for i in range(0, n, passo)]
    m = sum(lum) / len(lum)
    dp = (sum((v - m) ** 2 for v in lum) / len(lum)) ** 0.5
    return m, max(dp, 1e-3)


def mat_textura(nome, base, tile, cor=None, var=0.06, nor=0.5, rough=(0.6, 0.9), rot90=False, sheen=0.0, ext="1k",
                metal=0.0, coat=0.0, translucido=0.0):
    """PBR com projeção em caixa. cor=None: cor original da textura; cor=hex: textura vira detalhe em torno de 1,0
    (±var) multiplicado pela cor, para o tom final ser o da paleta."""
    m = bpy.data.materials.new(nome)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = bsdf(m)
    tc, mp = N.new("ShaderNodeTexCoord"), N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / tile,) * 3
    if rot90:
        mp.inputs["Rotation"].default_value = (0, 0, math.pi / 2)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])

    def img(tipo, nc):
        n = N.new("ShaderNodeTexImage")
        caminho = TEX / f"{base}_{tipo}_{ext}.jpg"
        n.image = bpy.data.images.load(str(caminho), check_existing=True)
        if nc:
            n.image.colorspace_settings.name = "Non-Color"
        n.projection, n.projection_blend = "BOX", 0.25
        L.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    dif = img("diff", False)
    if cor:
        m_, dp = stats(dif.image)
        bw = N.new("ShaderNodeRGBToBW")
        L.new(dif.outputs["Color"], bw.inputs["Color"])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = m_ - 2 * dp, m_ + 2 * dp
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1 - var, 1 + var
        L.new(bw.outputs["Val"], mr.inputs["Value"])
        mix = N.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs["A"].default_value = srgb_lin(cor)
        L.new(mr.outputs["Result"], mix.inputs["B"])
        L.new(mix.outputs["Result"], b.inputs["Base Color"])
    else:
        L.new(dif.outputs["Color"], b.inputs["Base Color"])
    try:
        ru = img("rough", True)
        r = N.new("ShaderNodeMapRange")
        r.inputs["To Min"].default_value, r.inputs["To Max"].default_value = rough
        L.new(ru.outputs["Color"], r.inputs["Value"])
        L.new(r.outputs["Result"], b.inputs["Roughness"])
    except RuntimeError:
        b.inputs["Roughness"].default_value = sum(rough) / 2
    no = img("nor", True)
    nm = N.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = nor
    L.new(no.outputs["Color"], nm.inputs["Color"])
    L.new(nm.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Metallic"].default_value = metal
    if sheen:
        b.inputs["Sheen Weight"].default_value, b.inputs["Sheen Roughness"].default_value = sheen, 0.4
    if coat:
        b.inputs["Coat Weight"].default_value, b.inputs["Coat Roughness"].default_value = coat, 0.35
    if translucido:
        tr = N.new("ShaderNodeBsdfTranslucent")
        tr.inputs["Color"].default_value = srgb_lin(cor) if cor else (0.8, 0.8, 0.8, 1)
        mx = N.new("ShaderNodeMixShader")
        mx.inputs["Fac"].default_value = translucido
        out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
        L.new(b.outputs["BSDF"], mx.inputs[1])
        L.new(tr.outputs["BSDF"], mx.inputs[2])
        L.new(mx.outputs["Shader"], out.inputs["Surface"])
    return m


def mat_simples(nome, cor, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(nome)
    b = bsdf(m)
    b.inputs["Base Color"].default_value = srgb_lin(cor)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


TECIDOS = {   # textura, tile (m), variação, normal, sheen, ext
    "linho": ("rough_linen", 0.30, 0.10, 0.6, 0.5, "1k"),
    "waffle": ("waffle_pique_cotton", 0.18, 0.12, 0.8, 0.4, "1k"),
    "veludo": ("velour_velvet", 0.35, 0.10, 0.4, 0.9, "1k"),
    "espinha": ("poly_wool_herringbone", 0.27, 0.10, 0.8, 0.6, "2k"),
    "trico": ("knitted_fleece", 0.27, 0.12, 0.9, 0.7, "2k"),
}


def tecido(nome, tipo, cor):
    if tipo == "couro":
        return mat_textura(nome, "fabric_leather_02", 0.45, None, nor=0.6, rough=(0.35, 0.6), sheen=0.1)
    if tipo == "estampada":
        m = mat_textura(nome, "throw_pillows_01", 0.45, None, nor=0.5, rough=(0.8, 0.95), sheen=0.6)
        return m
    t, tile, var, nor, sheen, ext = TECIDOS[tipo]
    return mat_textura(nome, t, tile, cor, var=var, nor=nor, rough=(0.75, 0.95), sheen=sheen, ext=ext)


def trocar_material(antigo, novo):
    for o in bpy.data.objects:
        if o.type in ("MESH", "CURVE", "FONT"):
            for s in o.material_slots:
                if s.material and s.material.name == antigo:
                    s.material = novo


def objs_material(nome):
    return [o for o in bpy.data.objects if o.type == "MESH" and any(s.material and s.material.name == nome
                                                                       for s in o.material_slots)]


METAIS = {"preto": ("#1A1A1A", 0.42, 0.0), "branco": ("#ECEBE7", 0.38, 0.0), "latao": ("#B08D57", 0.28, 1.0),
          "palha": ("#C8A26B", 0.8, 0.0)}
MADEIRAS = {"carvalho": ("oak_veneer_01", (0.5, 0.9, 1.2)), "freixo": ("ash_veneer", (0.5, 0.9, 1.3)),
            "nogueira": ("walnut_veneer", (0.5, 1.05, 0.72)), "nogueira_media": ("walnut_veneer", (0.5, 1.0, 0.95))}


def madeira(nome, wid, rot90):
    tex, (h, s_, v) = MADEIRAS[wid]
    m = mat_textura(nome, tex, 1.0, None, nor=0.35, rough=(0.35, 0.7), rot90=rot90, coat=0.12)
    nt = m.node_tree
    b = bsdf(m)
    link = next(lk for lk in nt.links if lk.to_socket == b.inputs["Base Color"])
    hs = nt.nodes.new("ShaderNodeHueSaturation")
    hs.inputs["Hue"].default_value, hs.inputs["Saturation"].default_value, hs.inputs["Value"].default_value = h, s_, v
    nt.links.new(link.from_socket, hs.inputs["Color"])
    nt.links.new(hs.outputs["Color"], b.inputs["Base Color"])
    return m


# ------------------------------------------------------------------ decoração do tema (em coordenadas do layout A)
def almofada(nome, sx, sy, sz, mat, loc, rot):
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
    ob = novo_obj(nome, me, "03_MOBILIARIO", mat)
    ob.location, ob.rotation_euler = loc, rot
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("Subdiv", "SUBSURF")
    m.levels = m.render_levels = 1
    return ob


def persiana_romana(cor):
    """Persiana romana de linho por dentro da janela (Parede E): recolhida de dia, baixada até o peitoril à noite."""
    mat = mat_textura("Linho_Persiana_Romana", "rough_linen", 0.30, cor, var=0.10, nor=0.6, rough=(0.8, 0.95), sheen=0.4,
                      translucido=0.25)
    y0, y1 = JAN_Y0 - 0.06, JAN_Y1 + 0.06
    z_top = JAN_PEIT + JAN_H + 0.10
    trilho = novo_obj("Persiana_romana_trilho", malha_caixa("Persiana_romana_trilho", 0.0, y0, z_top - 0.04, 0.045, y1, z_top),
                      "02_PORTAS_JANELAS", bpy.data.materials["Preto_Fosco"])
    # recolhida: 5 dobras de 7 cm empilhadas sob o trilho
    for k in range(5):
        zc = z_top - 0.075 - k * 0.062
        me = malha_caixa(f"Persiana_romana_dobra_{k+1}", 0.004, y0, zc - 0.035, 0.040 + 0.004 * k, y1, zc + 0.035)
        ob = novo_obj(f"Persiana_romana_dobra_{k+1}", me, "02_PORTAS_JANELAS", mat)
        bv = ob.modifiers.new("Chanfro", "BEVEL")
        bv.width, bv.segments = 0.016, 4
        for p in ob.data.polygons:
            p.use_smooth = True
        ob["modo"] = "dia"
    # baixada: painel com vincos horizontais a cada 22 cm
    me = bpy.data.meshes.new("Persiana_romana_painel")
    bm = bmesh.new()
    nz = 48
    zs = [JAN_PEIT + 0.01 + (z_top - 0.04 - JAN_PEIT - 0.01) * i / nz for i in range(nz + 1)]
    vs = []
    for z in zs:
        x = 0.012 + 0.008 * abs(math.sin((z - JAN_PEIT) / 0.22 * math.pi))
        vs.append((bm.verts.new((x, y0, z)), bm.verts.new((x, y1, z))))
    for i in range(nz):
        bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1], vs[i + 1][0]))
    bm.to_mesh(me)
    bm.free()
    painel = novo_obj("Persiana_romana_painel", me, "02_PORTAS_JANELAS", mat)
    so = painel.modifiers.new("Espessura", "SOLIDIFY")
    so.thickness = 0.003
    for p in painel.data.polygons:
        p.use_smooth = True
    painel["modo"] = "noite"
    barra = novo_obj("Persiana_romana_barra", malha_caixa("Persiana_romana_barra", 0.008, y0, JAN_PEIT + 0.005, 0.026, y1,
                                                         JAN_PEIT + 0.025), "02_PORTAS_JANELAS", mat)
    barra["modo"] = "noite"
    del trilho


def arte(t):
    for letra, img in zip("ABCDE", t["arte"]):
        m = bpy.data.materials.get(f"Arte_PB_quadro_{letra}")
        if not m:
            continue
        n = next(x for x in m.node_tree.nodes if x.type == "TEX_IMAGE")
        n.image = bpy.data.images.load(str(TEX / f"{img}.jpg"), check_existing=True)


NICHO_CABER = (0.185, 0.125, 0.20)


def nichos(t):
    remover(("Nicho_1_objeto", "Nicho_2_objeto", "Nicho_3_objeto"))
    zi = PT.NICHO_Z0 + 0.015
    yc = RIP + 0.006 + (PT.NICHO_P - 0.006) / 2
    for k, modelo in enumerate(t["nichos"]):
        cx = PT.NICHOS_X0 + k * (PT.NICHO_W + PT.NICHO_GAP) + PT.NICHO_W / 2
        r = importar(modelo, "06_DECORACAO", f"Nicho_{k+1}_objeto_{modelo}")
        esc = {"carved_wooden_elephant": 1.5, "bronze_whale_statue": 0.14, "ceramic_vase_02": 0.6}.get(modelo, 1.0)
        rot = 90 if modelo == "bronze_whale_statue" else (20 if modelo == "carved_wooden_elephant" else 0)
        assentar(r, (cx, yc), zi, caber=NICHO_CABER, rot=rot, esc=esc)


def luminaria_braco(metal):
    """Troca a luminária simples pela de braço articulado (Poly Haven), escala 0,85 (89 → 76 cm). Fica a 31 cm da
    borda de trás: o braço sobe para trás e não pode encostar no ripado."""
    remover(("Luminaria_mesa", "L6_Luz", "Cabo_luminaria"))
    mesa = bpy.data.objects["Mesa_Tampo_Freijo_170x70x2_5"]
    r = importar("desk_lamp_arm_01", "06_DECORACAO", "Luminaria_mesa_braco")
    r.location, r.scale = (1.00, 0.31, MESA_Z), (0.85,) * 3
    cor, ru, me_ = METAIS["latao" if metal == "palha" else metal]
    pintura = mat_simples(f"Luminaria_braco_{metal}", cor, ru, me_)
    lamp = bpy.data.materials["Lampada_3000K"]
    for o in r.children_recursive:
        if o.type == "MESH":
            for s in o.material_slots:
                s.material = lamp if s.material and "light" in s.material.name else pintura
    bpy.context.view_layer.update()
    ld = bpy.data.lights.new("L6_Luz_luminaria_mesa", "SPOT")
    ld.energy, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 10.0, math.radians(80), 0.5, 0.03
    ld.color = kelvin(2700)
    ob = bpy.data.objects.new("L6_Luz_luminaria_mesa", ld)
    ob.location = (1.00 - 0.004, 0.31 + 0.85 * 0.165, MESA_Z + 0.85 * 0.64)
    ob.visible_camera = ob.visible_glossy = False
    col("05_ILUMINACAO").objects.link(ob)
    for o in (r, ob):
        o.parent = mesa
        o.matrix_parent_inverse = mesa.matrix_world.inverted()


def acabamento_arandela(metal):
    if metal == "preto":
        return
    cor, ru, me_ = METAIS[metal]
    m = mat_simples(f"Arandela_{metal}", cor, ru, me_)
    for o in com_prefixo(("L4_Arandela",)):
        o.data.materials.clear()
        o.data.materials.append(m)


def led(k):
    em = next(n for n in bpy.data.materials["LED_3000K"].node_tree.nodes if n.type == "EMISSION")
    em.inputs["Color"].default_value = (*kelvin(k), 1)
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith(("L1_", "L2_", "L5_")):
            o.data.color = kelvin(k)


def tapete(t):
    tp = t["tapete"]
    obj = bpy.data.objects["Tapete_140x200"]
    if tp["tex"] == "liso":
        bsdf(bpy.data.materials["Tapete_Cinza_Escuro"]).inputs["Base Color"].default_value = srgb_lin(tp["cor"])
        return
    if tp["tex"] == "listrado":
        m = mat_textura("Tapete_listrado", "rough_linen", 0.25, tp["cor"], var=0.15, nor=0.9, rough=(0.85, 1.0), sheen=0.6)
        nt = m.node_tree
        b = bsdf(m)
        mix = next(n for n in nt.nodes if n.type == "MIX" and n.blend_type == "MULTIPLY")
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sx = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Object"], sx.inputs["Vector"])
        mt = nt.nodes.new("ShaderNodeMath")
        mt.operation, mt.inputs[1].default_value = "FRACT", 0.0
        esc = nt.nodes.new("ShaderNodeMath")
        esc.operation, esc.inputs[1].default_value = "MULTIPLY", 1 / 0.25          # listras a cada 25 cm (no comprimento)
        nt.links.new(sx.outputs["Y"], esc.inputs[0])
        nt.links.new(esc.outputs["Value"], mt.inputs[0])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        els = ramp.color_ramp.elements
        els[0].position, els[0].color = 0.0, srgb_lin(tp["cor"])
        els[1].position, els[1].color = 0.70, srgb_lin("#9C4F2E")
        e3 = els.new(0.80)
        e3.color = srgb_lin("#E2D5BF")
        e4 = els.new(0.86)
        e4.color = srgb_lin("#4A3022")
        nt.links.new(mt.outputs["Value"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], mix.inputs["A"])
        del b
    else:
        base, tile, ext = {"linho": ("rough_linen", 0.55, "1k"), "juta": ("rough_linen", 0.12, "1k"),
                           "espinha": ("poly_wool_herringbone", 0.55, "2k")}[tp["tex"]]
        m = mat_textura(f"Tapete_{tp['tex']}", base, tile, tp["cor"], var=0.22 if tp["tex"] == "juta" else 0.12,
                        nor=1.0, rough=(0.85, 1.0), sheen=0.7, ext=ext)
    obj.data.materials.clear()
    obj.data.materials.append(m)


def aplicar_tema(t):
    # paredes
    pa = t["parede"]
    tipo = pa["tipo"]
    base, tile, var, nor = {"pintura": ("painted_plaster_wall", 1.2, 0.05, 0.35), "cal": ("clay_plaster", 1.5, 0.10, 0.45),
                            "cimento": ("plaster_grey_04", 1.6, 0.22, 0.4), "argila": ("clay_plaster", 1.5, 0.16, 0.6)}[tipo]
    parede = mat_textura(f"Parede_{TEMA}", base, tile, pa["cor"], var=var, nor=nor, rough=(0.78, 0.93))
    trocar_material("Tinta_Grafite_3A3C40", parede)
    # madeira (ripado, tampo, prateleira, nichos)
    if t["madeira"] != "freijo":
        trocar_material("Madeira_Freijo_vertical", madeira(f"Madeira_{t['madeira']}_vertical", t["madeira"], True))
        trocar_material("Madeira_Freijo_angli_veneer", madeira(f"Madeira_{t['madeira']}", t["madeira"], False))
    bsdf(bpy.data.materials["MDF_Preto_Fundo"]).inputs["Base Color"].default_value = srgb_lin(t["fundo_ripado"])
    # cama
    c = t["cama"]
    bsdf(bpy.data.materials["Tecido_Box_Grafite"]).inputs["Base Color"].default_value = srgb_lin(c["box"])
    bsdf(bpy.data.materials["Tecido_Fronha"]).inputs["Base Color"].default_value = srgb_lin(c["fronha"])
    ed = tecido("Tecido_Edredom_tema", *c["edredom"])
    for o in com_prefixo(("Cama_Edredom",)):
        o.data.materials.clear()
        o.data.materials.append(ed)
    ma = tecido("Tecido_Manta_tema", *c["manta"])
    for o in com_prefixo(("Cama_Manta",)):
        o.data.materials.clear()
        o.data.materials.append(ma)
    remover(("Cama_Almofada",))
    y0 = RIP
    for k, ((tipo_a, cor_a), x, rz) in enumerate(zip(c["almofadas"], (0.25, 0.63), (5, -6))):
        almofada(f"Cama_Almofada_tema_{k+1}", 0.42, 0.42, 0.14, tecido(f"Tecido_Almofada_tema_{k+1}", tipo_a, cor_a),
                 (x, y0 + 0.30, CAMA_H + 0.26), (math.radians(-70), 0, math.radians(rz)))
    tapete(t)
    persiana_romana(t["persiana"])
    arte(t)
    nichos(t)
    luminaria_braco(t["metal"])
    acabamento_arandela(t["metal"])
    led(t["led_k"])
    # prateleira: troca a suculenta (ou os livros) pela peça extra do tema
    zp = PT.PRAT_H + 0.025
    for extra in t["plantas_extra"]:
        if extra == "book_encyclopedia_set_01":
            remover(("Livros_prateleira",))
            r = importar(extra, "06_DECORACAO", "Prateleira_item_livros")
            assentar(r, (MX0 + MESA_W - 0.25, RIP + 0.10), zp, caber=(0.40, 0.14, 0.24))
        else:
            remover(("Vaso_suculenta_prateleira",))
            modelo, caber = {"ceramic_vase_03": ("ceramic_vase_03", (0.12, 0.12, 0.32)),
                             "planter_pot_clay": ("potted_plant_01", (0.20, 0.20, 0.36))}[extra]
            r = importar(modelo, "06_DECORACAO", f"Prateleira_item_{modelo}")
            assentar(r, (MX0 + 0.13, RIP + 0.12), zp, caber=caber)
    if t["cesto"]:
        r = importar("wicker_basket_02", "06_DECORACAO", "Cesto_tema_vime")
        assentar(r, (2.04, 0.24), 0.0)


# ------------------------------------------------------------------ layouts
GRUPO_MESA = ["Mesa_Tampo_Freijo", "L3_", "Cesto_tema"]
GRUPO_CAMA = ["Cama_", "L4_", "Nicho_", "L5_"]
GRUPO_PRAT = ["Prateleira_", "L1_", "Livros_prateleira", "Vaso_suculenta_prateleira", "Vaso_planta_prateleira",
              "Quadro_D_", "Quadro_E_", "Relogio_LED_"]
QUADROS_E = ["Quadro_A_", "Quadro_B_", "Quadro_C_"]
SUBGRUPOS_MESA = {   # rearranjo espelhado sobre o tampo (B e C): PC vai para a ponta oposta, longe da cabeceira
    "pc": ["PC_"], "fone": ["Suporte_headphone", "Headphone_"], "caneca": ["Caneca"],
    "notebook": ["Notebook_", "Suporte_Notebook"], "luminaria": ["Luminaria_mesa", "L6_Luz"],
    "monitores": ["Monitor_27_", "Braco_ELG", "Barra_Luz_Monitor", "Cabo_monitor_", "L3_"], "cesto": ["Cesto_tema"],
}


def rearranjar_mesa():
    lo_t, hi_t = caixa(["Mesa_Tampo_Freijo_170x70x2_5"])
    for nome, pref in SUBGRUPOS_MESA.items():
        objs = com_prefixo(pref)
        if not objs:
            continue
        lo, hi = caixa(pref)
        dx = 2 * CX_MESA - (lo.x + hi.x)              # centro espelhado (a peça não é espelhada: textos continuam legíveis)
        if nome not in ("cesto", "luminaria"):         # mantém a peça dentro do tampo (a luminária avança 3 cm como no A)
            dx = min(dx, hi_t.x - 0.01 - hi.x) if hi.x + dx > hi_t.x - 0.01 else dx
            dx = max(dx, lo_t.x + 0.01 - lo.x) if lo.x + dx < lo_t.x + 0.01 else dx
        for o in raizes(pref):
            o.matrix_world = Matrix.Translation((dx, 0, 0)) @ o.matrix_world
        bpy.context.view_layer.update()
    # teclado e mouse acompanham os monitores (sem espelhar: mouse continua à direita)
    dm = 2 * (CX_MESA - PT.MON_CX)
    for o in raizes(["Teclado", "Mouse"]):
        o.matrix_world = Matrix.Translation((dm, 0, 0)) @ o.matrix_world
    bpy.context.view_layer.update()


def espelho_x(cx):
    return Matrix.Translation((2 * cx, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))


def matriz_troca_xy(dx, dy):
    """(x, y) → (y + dx, x + dy): troca os eixos (espelho na diagonal). Usada na cama do layout C."""
    return Matrix(((0, 1, 0, dx), (1, 0, 0, dy), (0, 0, 1, 0), (0, 0, 0, 1)))


def mover_l2(x):
    lo, hi = caixa(["L2_Fita_LED_vertical"])
    transformar(["L2_"], Matrix.Translation((x - (lo.x + hi.x) / 2, 0, 0)))


def aplicar_layout(L):
    cadeira = bpy.data.objects["Cadeira_DT3_Elin"]
    if L == "A":
        return
    rearranjar_mesa()
    cadeira.location.x = 2 * CX_MESA - cadeira.location.x
    bpy.context.view_layer.update()
    if L == "B":
        transformar(GRUPO_CAMA, espelho_x(D / 2))
        dx = 0.02 - MX0
        transformar(GRUPO_MESA, Matrix.Translation((dx, 0, 0)))
        transformar(GRUPO_PRAT, Matrix.Translation((dx, 0, 0)))
        transformar(["Cadeira_DT3_Elin"], Matrix.Translation((dx, 0, 0)))
        transformar(["Tapete_"], espelho_x(D / 2))
        mover_l2(VAO0 + PASSO * 50)                    # vão entre a mesa (até 1,72) e a cama (desde 1,77)
    elif L == "C":
        transformar(GRUPO_CAMA, matriz_troca_xy(-RIP, RIP))
        transformar(QUADROS_E, espelho_x(D / 2))       # galeria vai para a Parede C (a Parede E recebe os nichos)
        M = Matrix.Translation((-0.03, 3.58, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")
        transformar(GRUPO_MESA, M)
        transformar(["Cadeira_DT3_Elin"], M)
        transformar(GRUPO_PRAT, Matrix.Translation((0.10 - MX0, 0, 0)))   # prateleira sobre a cama (Parede D)
        transformar(["Tapete_"], Matrix.Translation((1.62, 1.75, 0)) @ Matrix.Rotation(math.radians(90), 4, "Z")
                    @ Matrix.Translation((-1.78, -1.78, 0)))
        mover_l2(VAO0 + PASSO * 55)                    # logo depois do pé da cama


PLANTA_CHAO = {"A": (2.33, 1.12), "B": (0.30, 1.10), "C": (2.30, 0.45)}
PENDENTE = {"A": (0.30, 2.25), "B": (0.30, 2.25), "C": (2.30, 1.80)}
TOMADA = {"A": ("D", (P.D / 2, RIP + 0.012, 0.30)), "B": ("D", (P.D / 2, RIP + 0.012, 0.30)),
          "C": ("E", (0.012, E / 2, 0.33))}


def cabo(nome, pts, raio):
    cu = bpy.data.curves.new(nome, "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", raio, 3
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    sp.order_u, sp.use_endpoint_u = 3, True
    return novo_obj(nome, cu, "03_MOBILIARIO", bpy.data.materials["Preto_Fosco"])


def pos_layout(L, t):
    # planta pendente
    px, py = PENDENTE[L]
    lo, hi = caixa(["Planta_pendente_vaso"])
    transformar(["Planta_pendente_"], Matrix.Translation((px - (lo.x + hi.x) / 2, py - (lo.y + hi.y) / 2, 0)))
    # planta de chão (canto morto do layout)
    if t["planta_chao"]:
        r = importar("potted_plant_01", "06_DECORACAO", "Planta_chao_tema")
        assentar(r, PLANTA_CHAO[L], 0.0, esc=0.7 if L == "B" else 0.8, rot=25)   # no B fica abaixo do peitoril
    # cabos até a tomada do layout: descem pelo vão entre a borda de trás da mesa e a parede
    remover(("Cabo_feixe_tomada", "Cabo_PC_energia", "Cabo_luminaria"))
    mesa = bpy.data.objects["Mesa_Tampo_Freijo_170x70x2_5"]
    Mw = mesa.matrix_world                              # tampo: origem no canto (MX0, MY0) do layout A
    def local(x, y, z):                                 # ponto no referencial do tampo do layout A → mundo
        return tuple(Mw @ Vector((x - MX0, y - MY0, z - (MESA_Z - 0.025))))
    _, tom = TOMADA[L]
    lo_m, hi_m = caixa(["Braco_ELG_F160N_coluna"])
    lo_p, hi_p = caixa(["PC_Gabinete_fundo"])
    lo_l, hi_l = caixa(["Luminaria_mesa_braco"]) if com_prefixo(["Luminaria_mesa_braco"]) else (None, None)
    inv = Mw.inverted()
    def ref_a(v):                                       # mundo → referencial do layout A
        q = inv @ Vector(v)
        return (q.x + MX0, q.y + MY0, q.z + MESA_Z - 0.025)
    mc = ref_a((lo_m + hi_m) / 2)
    pc = ref_a((lo_p + hi_p) / 2)
    pts_fim = [tom]
    cabo("Cabo_feixe_tomada", [local(mc[0], MY0 + 0.06, MESA_Z - 0.03), local(mc[0] - 0.08, MY0 - 0.008, 0.55)]
         + pts_fim, 0.006)
    cabo("Cabo_PC_energia", [local(pc[0] + 0.03, pc[1] - 0.01, MESA_Z + 0.07), local(pc[0] + 0.03, MY0 - 0.01, MESA_Z + 0.02),
                             local(pc[0] - 0.02, MY0 - 0.008, 0.58)] + pts_fim, 0.004)
    if lo_l is not None:
        lc = ref_a((lo_l + hi_l) / 2)
        cabo("Cabo_luminaria", [local(lc[0] + 0.03, lc[1], MESA_Z + 0.003), local(lc[0] + 0.03, MY0 + 0.01, MESA_Z + 0.003),
                                local(lc[0] + 0.03, MY0 - 0.006, MESA_Z - 0.10), local(lc[0], MY0 - 0.008, 0.42)]
              + pts_fim, 0.0022)


# ------------------------------------------------------------------ validação do layout
def validar(L):
    R = []

    def chk(nome, status, det):
        R.append({"verificacao": nome, "status": status, "detalhe": det})

    def sep(a, b, filhos=True):
        la, ha = caixa(a, filhos)
        lb, hb = caixa(b, filhos)
        return max(max(lb[i] - ha[i], la[i] - hb[i]) for i in range(3))

    def ok(nome, folga, minimo, aviso=False):
        chk(nome, "OK" if folga >= minimo - 1e-4 else ("ATENÇÃO" if aviso else "FALHA"),
            f"folga {folga*100:.1f} cm (mínimo {minimo*100:.1f} cm)")
    rig = ["Cama_Box_base", "Cama_Colchao_88x188", "Cama_Box_rodape_preto"]
    tampo = ["Mesa_Tampo_Freijo_170x70x2_5"]
    ok("Mesa × cama (partes rígidas)", sep(tampo + ["Mesa_Estrutura_"], rig, False), 0.04)
    ok("Mesa × ripado / Parede E / Parede C", min(sep(tampo, ["Ripado_Ripas"], False), sep(tampo, ["Parede_E_"], False),
                                                  sep(tampo, ["Parede_C"], False)), 0.019)
    ok("Mesa × portas do armário", sep(tampo, ["Armario_existente_porta_"], False), 0.15)
    ok("Cama × portas do armário (circulação)", sep(rig, ["Armario_existente_porta_"]), 0.60)
    ok("Cadeira × cama", sep(["Cadeira_"], ["Cama_"]), 0.05)
    ok("Cadeira × armário (recuo + passagem)", sep(["Cadeira_"], ["Armario_existente_"]), 0.60)
    # PC × travesseiro: distância horizontal
    lp, hp = caixa(["PC_Gabinete_"])
    lt, ht = caixa(["Cama_Travesseiro"])
    dh = max(max(lt[i] - hp[i], lp[i] - ht[i]) for i in range(2))
    ok("PC longe da cabeceira (ruído e LED)", dh, 0.90, aviso=True)
    # monitores × prateleira com a mesa no máximo (só se a prateleira está sobre a mesa)
    lm, hm = caixa(["Monitor_27_"])
    lr, hr = caixa(["Prateleira_Freijo"])
    sobre = lm.x < hr.x and hm.x > lr.x and lm.y < hr.y + 0.5 and hm.y > lr.y - 0.5
    if sobre:
        topo = hm.z + 0.45
        chk("Monitores × prateleira com a mesa no máximo", "OK" if topo < PT.PRAT_H else "FALHA",
            f"topo {topo:.3f} m · prateleira {PT.PRAT_H} m")
    else:
        chk("Prateleira fora da mesa", "OK", "a prateleira não fica sobre a mesa neste layout")
    # janela: nada acima do peitoril na frente dela (exceto persiana)
    na_frente = []
    for nome, pref in (("monitores", ["Monitor_27_"]), ("cama", ["Cama_"]), ("PC", ["PC_Gabinete_"]),
                       ("planta de chão", ["Planta_chao"]), ("luminária", ["Luminaria_mesa_braco"])):
        topo = 0.0
        for o in com_prefixo(pref):                     # objeto a objeto (a caixa do grupo inteiro daria falso alarme)
            lo, hi = caixa_mundo([o] + list(o.children_recursive))
            if lo.x < 0.80 and hi.y > JAN_Y0 and lo.y < JAN_Y1 and hi.z > JAN_PEIT + 0.02:
                topo = max(topo, hi.z)
        if topo:
            na_frente.append(f"{nome} (topo {topo:.2f} m)")
    chk("Janela: frente livre acima do peitoril", "OK" if not na_frente else "ATENÇÃO",
        "nada acima do peitoril" if not na_frente else "na frente da janela: " + ", ".join(na_frente))
    # ar-condicionado
    la, ha = caixa(["ArCondicionado_existente"])
    sob = []
    for nome, pref in (("cama", rig), ("monitores", ["Monitor_27_"]), ("cadeira", ["Cadeira_"])):
        lo, hi = caixa(pref)
        ox = hi.x - (la.x - 0.60)                     # quanto entra na faixa de 0,6 m à frente do aparelho
        oy = min(hi.y, ha.y) - max(lo.y, la.y)        # quanto fica na largura do aparelho
        if ox > 0.25 and oy > 0.25:
            sob.append(nome)
    chk("Ar-condicionado: ninguém no jato direto", "OK" if not sob else "ATENÇÃO",
        "nada a menos de 0,6 m do aparelho" if not sob else
        "a menos de 0,6 m do aparelho: " + ", ".join(sob) + " — direcionar as aletas para o centro do quarto")
    # faixa de entrada e banheiro livres
    inv = []
    for nome, pref in (("cama", ["Cama_"]), ("mesa", tampo), ("cadeira", ["Cadeira_"]), ("tapete", ["Tapete_"]),
                       ("planta de chão", ["Planta_chao"])):
        if not com_prefixo(pref):
            continue
        lo, hi = caixa(pref)
        if hi.x > D + 1e-3 and hi.y > C + 1e-3:
            inv.append(nome)
    chk("Faixa de entrada e porta do banheiro livres", "OK" if not inv else "FALHA", "livres" if not inv else ", ".join(inv))
    # portas do armário se forem de abrir (folha de ~0,77 m)
    zona = E - 0.77
    no_arco = []
    for nome, pref in (("mesa", tampo), ("cama", rig), ("planta pendente", ["Planta_pendente_vaso"]),
                       ("planta de chão", ["Planta_chao"]), ("cadeira", ["Cadeira_"])):
        if not com_prefixo(pref):
            continue
        lo, hi = caixa(pref)
        if hi.y > zona and lo.x < D:
            no_arco.append(f"{nome} (até y = {hi.y:.2f})")
    chk("Arco das portas do armário (se forem de abrir)", "OK" if not no_arco else "ATENÇÃO",
        "nada no arco de 0,77 m" if not no_arco else "no arco: " + ", ".join(no_arco) + " — ok se as portas forem de correr")
    lo_n, _ = caixa(["Nicho_1_base", "Nicho_2_base", "Nicho_3_base"])
    ok("Nichos ≥ 0,90 m acima do colchão", lo_n.z - CAMA_H, 0.90)
    lo, hi = caixa(["Planta_pendente_"])
    ok("Planta pendente: folhas acima de 1,90 m", lo.z - 1.90, 0.0)
    ok("Planta pendente × ventilador", sep(["Planta_pendente_"], ["Ventilador_"]), 0.10)
    if com_prefixo(["Planta_chao"]):
        ok("Planta de chão × cadeira", sep(["Planta_chao"], ["Cadeira_"]), 0.05)
        ok("Planta de chão × mesa e cama", min(sep(["Planta_chao"], tampo), sep(["Planta_chao"], rig)), 0.0)
        lo, hi = caixa(["Planta_chao"])
        chk("Planta de chão dentro do quarto", "OK" if lo.x >= 0 and hi.x <= D and lo.y >= RIP and hi.y <= E else "FALHA",
            f"x {lo.x:.2f}–{hi.x:.2f}, y {lo.y:.2f}–{hi.y:.2f}")
    lo, hi = caixa(["Tapete_"])
    chk("Tapete dentro do quarto", "OK" if lo.x >= -1e-3 and hi.x <= D + 1e-3 and lo.y >= RIP - 1e-3 and hi.y <= E else "FALHA",
        f"x {lo.x:.2f}–{hi.x:.2f}, y {lo.y:.2f}–{hi.y:.2f}")
    lo, hi = caixa(["Luminaria_mesa_braco"])
    ok("Luminária de braço × monitores", sep(["Luminaria_mesa_braco"], ["Monitor_27_"]), 0.015)
    ok("Luminária de braço × ripado/paredes", min(sep(["Luminaria_mesa_braco"], ["Ripado_Ripas"]),
                                                   sep(["Luminaria_mesa_braco"], ["Parede_E_"])), 0.005)
    nome_t, tom = TOMADA[L]
    chk(f"Tomada usada pela mesa (Parede {nome_t})", "OK", f"cabos descem até ({tom[0]:.2f}, {tom[1]:.2f}, {tom[2]:.2f})")
    dados = json.loads(VALID.read_text(encoding="utf-8")) if VALID.exists() else {}
    dados[L] = R
    VALID.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print("VALIDACAO", L, sum(r["status"] == "OK" for r in R), "/", len(R),
          "atencao", sum(r["status"] == "ATENÇÃO" for r in R), "falha", sum(r["status"] == "FALHA" for r in R))
    for r in R:
        print(r["status"], "|", r["verificacao"], "|", r["detalhe"])


# ------------------------------------------------------------------ render
def renderizar(L):
    import runpy
    sys_argv = sys.argv
    sys.argv = ["x"]                                   # renderizar.py lê argumentos ao ser carregado
    ns = runpy.run_path(str(SCRIPTS / "renderizar.py"), run_name="modulo")
    sys.argv = sys_argv
    modo, gpu, ocultar = ns["modo"], ns["gpu"], ns["ocultar"]
    sc = bpy.context.scene
    gpu()
    sc.render.resolution_x, sc.render.resolution_y = (RES[0] // 2, RES[1] // 2) if TESTE else RES
    sc.render.resolution_percentage = 100
    sc.cycles.samples = 24 if TESTE else AMOSTRAS
    sc.cycles.use_adaptive_sampling, sc.cycles.adaptive_threshold = True, 0.02
    sc.render.image_settings.file_format, sc.render.image_settings.quality = "JPEG", 88
    cd = bpy.data.cameras.new("CAM_tema")
    cd.lens, cd.sensor_width, cd.clip_start = LAYOUTS[L]["cam"]["lens"], 36, 0.05
    cam = bpy.data.objects.new("CAM_tema", cd)
    cam.location = LAYOUTS[L]["cam"]["loc"]
    cam.rotation_euler = (Vector(LAYOUTS[L]["cam"]["alvo"]) - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    col("07_CAMERAS").objects.link(cam)
    OUT.mkdir(parents=True, exist_ok=True)
    base = {o.name: o.hide_render for o in bpy.data.objects}
    for m in RENDER:
        for o in bpy.data.objects:
            o.hide_render = base[o.name]
            o.pop("_hide_base", None)
        modo("noite" if m == "noite" else "dia")
        exp_dia, exp_noite = TEMAS[TEMA].get("exp", (0.0, 0.0))   # paredes claras refletem mais luz que o grafite
        sc.view_settings.exposure += exp_noite if m == "noite" else exp_dia
        for o in bpy.data.objects:                   # persiana romana: recolhida de dia, baixada à noite
            if "modo" in o:
                o.hide_render = o["modo"] != ("noite" if m == "noite" else "dia")
        if m == "planta":
            sc.camera = bpy.data.objects["CAM_vista_superior"]
            ocultar(["Teto", "Ventilador_", "Plafon_faixa", "Planta_pendente_"])
            sc.render.filepath = str(OUT / f"planta_{L}.jpg")
        else:
            sc.camera = cam
            sc.render.filepath = str(OUT / f"{TEMA}_{L}_{m}.jpg")
        bpy.ops.render.render(write_still=True)
        print("RENDER", TEMA, L, m, sc.render.filepath)


def main():
    t = TEMAS[TEMA]
    aplicar_tema(t)
    aplicar_layout(LAYOUT)
    pos_layout(LAYOUT, t)
    bpy.context.view_layer.update()
    validar(LAYOUT)
    if "--salvar" in ARGS:
        destino = PROJ / "05_BLENDER" / "temas" / f"quarto_{TEMA}_{LAYOUT}.blend"
        destino.parent.mkdir(exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(destino), copy=True, relative_remap=True)
        print("SALVO", destino)
    if RENDER:
        renderizar(LAYOUT)


if __name__ == "__main__":
    main()
