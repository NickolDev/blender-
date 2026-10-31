"""Constrói a cena 3D da Suíte 01 (Layout A, cenário Equilibrado) em escala 1:1.

Uso (Blender 5.2, modo background):
    blender -b --factory-startup --python construir_cena.py

As medidas vêm dos MESMOS módulos que geram as plantas 2D (03_PLANTAS/fonte), para que a planta,
o orçamento e o 3D não divirjam. Sistema de coordenadas = o da planta: origem no canto interno
Parede E × Parede D, x → leste-oeste da planta (direita), y → em direção ao armário, z para cima.
O norte fica em −y (a Parede D está voltada ao norte).
"""
import math
import shutil
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

PROJ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJ / "03_PLANTAS" / "fonte"))
import planta_v1 as P                     # noqa: E402
import planta_tecnica as PT               # noqa: E402

ASSETS = PROJ / "05_BLENDER" / "assets"
BLEND = PROJ / "05_BLENDER" / "quarto_escritorio.blend"

# ------------------------------------------------------------------ medidas (do 2D)
D, E, C, LARG, FAIXA, PE = P.D, P.E, P.C, P.LARG, P.FAIXA, P.PE
T, TC = P.T, P.TC
JAN_Y0, JAN_Y1, JAN_PEIT, JAN_H = P.JAN_Y0, P.JAN_Y1, P.JAN_PEIT, P.JAN_H
BLD, PBWC, PENT = P.BLD, P.PBWC, P.PENT
PROF_ARM = P.PROF_ARM
AC_W, AC_Y = P.AC_W, P.AC_Y
RIP, GAP = P.RIP, P.GAP
CAMA_W, CAMA_L, CAMA_H = P.CAMA_W, P.CAMA_L, PT.CAMA_H
MX0, MY0, MESA_W, MESA_P = PT.MX0, PT.MY0, PT.MESA_W, PT.MESA_P
PRAT_P, PRAT_H = PT.PRAT_P, PT.PRAT_H
ARAND_X, ARAND_H = PT.ARAND_X, PT.ARAND_H
PC_X0, PC_Y0, PC_W, PC_P, PC_H = PT.PC_X0, PT.PC_Y0, PT.PC_W, PT.PC_P, PT.PC_H
MON_CX = PT.MON_CX
NB = PT.NB
TAP = PT.TAP
TOM_D = PT.TOM_D
PORTA_H = 2.10                       # estimada (padrão)
MESA_Z = 0.73                        # altura sentada (Starlift: 73–118)
TAMPO = 0.025
FAN = (D / 2, E / 2)                 # centro do quarto
LUZ_FAIXA = (D + TC + BLD + PBWC / 2, C + FAIXA / 2)

# ripado: ripa 2,0 cm × 1,8 cm, vão 1,5 cm, fundo preto 1,2 cm
RIPA_W, RIPA_D, RIPA_GAP, FUNDO = 0.020, 0.018, 0.015, 0.012
PITCH = RIPA_W + RIPA_GAP
RIPA_X0 = RIPA_GAP / 2
N_RIPAS = int((D - RIPA_X0 - RIPA_W) // PITCH) + 1
# o LED vertical ocupa o vão mais próximo do x da planta (PT.LED_V_X)
_i = round((PT.LED_V_X - (RIPA_X0 + RIPA_W + RIPA_GAP / 2)) / PITCH)
LED_V_X = RIPA_X0 + RIPA_W + RIPA_GAP / 2 + _i * PITCH


# ------------------------------------------------------------------ utilidades
def srgb_lin(hexs):
    hexs = hexs.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(hexs[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def kelvin(k):
    """Aproximação Tanner Helland → RGB linear."""
    t = k / 100
    r = 255 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    rgb = [max(0, min(255, v)) / 255 for v in (r, g, b)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)


COLS = {}


def coll(name):
    if name not in COLS:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLS[name] = c
    return COLS[name]


def link(obj, cname):
    coll(cname).objects.link(obj)
    return obj


def box(name, x0, y0, z0, x1, y1, z1, mat, cname, bevel=0.0, local=False):
    """Caixa em coordenadas reais.

    local=False: origem no canto mínimo (x0, y0, z0).
    local=True:  vértices exatamente em (x0..x1, y0..y1, z0..z1) em torno da origem do objeto; usar quando
                 a posição/rotação é definida depois (monitores, pás, raios da cadeira).
    """
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    ox, oy, oz = (x0, y0, z0) if local else (0.0, 0.0, 0.0)
    for v in bm.verts:
        v.co = Vector((ox + (v.co.x + 0.5) * (x1 - x0), oy + (v.co.y + 0.5) * (y1 - y0), oz + (v.co.z + 0.5) * (z1 - z0)))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = (0.0, 0.0, 0.0) if local else (x0, y0, z0)
    if mat:
        me.materials.append(mat)
    if bevel:
        m = ob.modifiers.new("Bevel", "BEVEL")
        m.width, m.segments, m.limit_method = bevel, 3, "ANGLE"
    for p in me.polygons:
        p.use_smooth = bool(bevel)
    return link(ob, cname)


def cyl(name, x, y, z0, r, h, mat, cname, verts=32, rot=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = (x, y, z0)
    if rot:
        ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return link(ob, cname)


def parent(child, par):
    bpy.context.view_layer.update()      # garante matrix_world atualizada antes de calcular a inversa
    child.parent = par
    child.matrix_parent_inverse = par.matrix_world.inverted()


# ------------------------------------------------------------------ materiais
def principled(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0, transm=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = srgb_lin(color) if isinstance(color, str) else color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if transm:
        b.inputs["Transmission Weight"].default_value = transm
        b.inputs["IOR"].default_value = 1.5
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = emit
        b.inputs["Emission Strength"].default_value = estr
    return m


def textured(name, asset, tile_m, tint=None, rough_mul=1.0, nor_str=0.6, rot90=False, hsv=None):
    """Material PBR do Poly Haven com projeção em caixa (coordenadas do objeto = metros)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    s = 1.0 / tile_m
    mp.inputs["Scale"].default_value = (s, s, s)
    if rot90:
        mp.inputs["Rotation"].default_value = (0, 0, math.pi / 2)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])

    def img(kind, noncolor):
        n = N.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(str(ASSETS / "textures" / f"{asset}_{kind}_2k.jpg"), check_existing=True)
        if noncolor:
            n.image.colorspace_settings.name = "Non-Color"
        n.projection, n.projection_blend = "BOX", 0.25
        L.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    dif, rou, nor = img("diff", False), img("rough", True), img("nor", True)
    col = dif.outputs["Color"]
    if tint:
        mix = N.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        L.new(col, mix.inputs["A"])
        mix.inputs["B"].default_value = srgb_lin(tint)
        col = mix.outputs["Result"]
    if hsv:
        hs = N.new("ShaderNodeHueSaturation")
        hs.inputs["Hue"].default_value, hs.inputs["Saturation"].default_value, hs.inputs["Value"].default_value = hsv
        L.new(col, hs.inputs["Color"])
        col = hs.outputs["Color"]
    L.new(col, b.inputs["Base Color"])
    mr = N.new("ShaderNodeMath")
    mr.operation = "MULTIPLY"
    mr.inputs[1].default_value = rough_mul
    L.new(rou.outputs["Color"], mr.inputs[0])
    L.new(mr.outputs["Value"], b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = nor_str
    L.new(nor.outputs["Color"], nm.inputs["Color"])
    L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def tinta(name, color, rough=0.85):
    """Tinta acrílica com leve textura de rolo (ruído no relevo)."""
    m = principled(name, color, rough)
    nt = m.node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 180.0
    nz.inputs["Detail"].default_value = 4.0
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.04
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return m


def emissor(name, kel, estr):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*kelvin(kel), 1)
    em.inputs["Strength"].default_value = estr
    nt.links.new(em.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
    return m


def tela(name):
    """Tela de monitor ligada: gradiente escuro azulado com leve emissão."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.005, 0.005, 0.006, 1)
    b.inputs["Roughness"].default_value = 0.15
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.05, 0.07, 0.14, 1)
    ramp.color_ramp.elements[1].color = (0.60, 0.40, 0.52, 1)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (-0.5, -0.5, 0)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    nt.links.new(gr.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 2.5
    return m


def arte(name, arquivo):
    """Impressão P&B fosca; a imagem cobre a face pela coordenada Generated (Y → horizontal, Z → vertical)."""
    m = principled(name, "#FFFFFF", 0.8)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(str(ASSETS / "textures" / f"{arquivo}.jpg"), check_existing=True)
    im.extension = "EXTEND"
    nt.links.new(tc.outputs["Generated"], sp.inputs["Vector"])
    nt.links.new(sp.outputs["Y"], cb.inputs["X"])
    nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
    nt.links.new(cb.outputs["Vector"], im.inputs["Vector"])
    nt.links.new(im.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def materiais():
    M = {}
    M["grafite"] = tinta("Tinta_Grafite_3A3C40", "#3A3C40", 0.82)
    M["teto"] = tinta("Tinta_Teto_ECE8E1", "#ECE8E1", 0.9)
    M["freijo"] = textured("Madeira_Freijo_angli_veneer", "angli_veneer", 1.0, rough_mul=0.9, nor_str=0.3,
                           hsv=(0.53, 1.05, 0.80))
    M["freijo_v"] = textured("Madeira_Freijo_vertical", "angli_veneer", 1.0, rough_mul=0.9, nor_str=0.3, rot90=True,
                             hsv=(0.53, 1.05, 0.80))
    M["piso"] = textured("Piso_Madeira_wood_floor", "wood_floor", 1.70, tint="#E8D2BC", rough_mul=0.85, nor_str=0.5)
    M["edredom"] = textured("Tecido_Edredom_poly_wool", "poly_wool_herringbone", 0.27, tint="#9EA2A8", nor_str=0.8)
    M["manta"] = textured("Tecido_Manta_caramelo", "knitted_fleece", 0.27, tint="#F3B27A", nor_str=0.9)
    M["preto"] = principled("Preto_Fosco", "#1A1A1A", 0.55)
    M["preto_metal"] = principled("Metal_Preto", "#151515", 0.35, metal=1.0)
    M["fundo_ripado"] = principled("MDF_Preto_Fundo", "#0E0E0E", 0.7)
    M["box"] = principled("Tecido_Box_Grafite", "#4E5156", 0.95)
    M["colchao"] = principled("Tecido_Colchao", "#D9D6D0", 0.95)
    M["fronha"] = principled("Tecido_Fronha", "#5E6166", 0.95)
    M["almofada"] = principled("Tecido_Almofada_Caramelo", "#B5653A", 0.95)
    M["cadeira"] = principled("Tecido_Cadeira", "#202124", 0.9)
    M["armario"] = principled("Armario_Existente_cor_pendente", "#E3E0DA", 0.6)
    M["porta"] = principled("Porta_Branca", "#F2F0EC", 0.5)
    M["aluminio"] = principled("Aluminio_Esquadria_cor_pendente", "#3B3D40", 0.35, metal=0.9)
    M["vidro"] = principled("Vidro", "#FFFFFF", 0.0, transm=1.0)
    M["cromo"] = principled("Metal_Cromo", "#D8D8D8", 0.15, metal=1.0)
    M["branco_ac"] = principled("Plastico_Branco_AC", "#F4F4F2", 0.4)
    M["granito"] = principled("Peitoril_Granito", "#2A2A2B", 0.3)
    M["rodape"] = principled("Rodape_Preto", "#1C1C1C", 0.5)
    M["tapete"] = principled("Tapete_Cinza_Escuro", "#3D3F43", 1.0)
    M["tela"] = tela("Tela_Monitor")
    M["teclado"] = principled("Plastico_Teclado", "#2A2B2E", 0.6)
    M["planta"] = principled("Folhagem", "#2F5A2A", 0.6)
    M["vaso"] = principled("Ceramica_Vaso", "#D9D3C8", 0.4)
    M["livro1"] = principled("Livro_1", "#C9C1B3", 0.8)
    M["livro2"] = principled("Livro_2", "#2E3033", 0.8)
    M["livro3"] = principled("Livro_3", "#8A5A3A", 0.8)
    M["led"] = emissor("LED_3000K", 3000, 8.0)
    M["lampada"] = emissor("Lampada_3000K", 3000, 6.0)
    M["led_bar"] = emissor("LED_Barra_Monitor_4000K", 4000, 4.0)
    M["led_pc"] = emissor("LED_PC_3000K", 3000, 3.0)
    M["vidro_fume"] = principled("Vidro_Fume_Gabinete", "#3A3A3C", 0.03, transm=1.0)
    M["pcb"] = principled("Placa_Mae_PCB", "#1E2124", 0.45)
    M["ceramica_preta"] = principled("Ceramica_Preta_Fosca", "#202020", 0.55)
    M["corda"] = principled("Corda_Juta", "#9C7B55", 0.95)
    M["passe"] = principled("Passe_Partout", "#EFEDE8", 0.9)
    M["caneca"] = principled("Ceramica_Caneca", "#E9E5DE", 0.3)
    for nome in ("quadro_A", "quadro_B", "quadro_C", "quadro_D", "quadro_E"):
        M[nome] = arte(f"Arte_PB_{nome}", nome)
    return M


# ------------------------------------------------------------------ 01 estrutura
def estrutura(M):
    c = "01_ESTRUTURA"
    # piso (madeira colante nova)
    box("Piso_Quarto", 0, 0, -0.02, D, E, 0, M["piso"], c)
    box("Piso_Faixa_Entrada", D, C, -0.02, LARG, E, 0, M["piso"], c)
    box("Piso_Sob_Armario", 0, E, -0.02, LARG, E + PROF_ARM, 0, M["piso"], c)
    # teto
    box("Teto", -T, -T, PE, LARG + T, E + PROF_ARM + T, PE + 0.10, M["teto"], c)
    g = M["grafite"]
    # Parede D (atrás do ripado)
    box("Parede_D", -T, -T, 0, D + TC, 0, PE, g, c)
    # Parede E com vão da janela
    box("Parede_E_trecho_EE", -T, 0, 0, 0, JAN_Y0, PE, g, c)
    box("Parede_E_peitoril", -T, JAN_Y0, 0, 0, JAN_Y1, JAN_PEIT, g, c)
    box("Parede_E_verga", -T, JAN_Y0, JAN_PEIT + JAN_H, 0, JAN_Y1, PE, g, c)
    box("Parede_E_trecho_ED", -T, JAN_Y1, 0, 0, E + PROF_ARM + T, PE, g, c)
    # Parede C e parede norte do banheiro (com vão da porta)
    box("Parede_C", D, -T, 0, D + TC, C, PE, g, c)
    px0 = D + TC + BLD
    box("Banheiro_LD", D, C - T, 0, px0, C, PE, g, c)
    box("Banheiro_verga_porta", px0, C - T, PORTA_H, px0 + PBWC, C, PE, g, c)
    box("Banheiro_LE", px0 + PBWC, C - T, 0, LARG, C, PE, g, c)
    # parede leste da faixa (porta de entrada)
    y_p0, y_p1 = C + (FAIXA - PENT) / 2, C + (FAIXA + PENT) / 2
    box("Parede_Leste_1", LARG, C - T, 0, LARG + T, y_p0, PE, g, c)
    box("Parede_Leste_verga", LARG, y_p0, PORTA_H, LARG + T, y_p1, PE, g, c)
    box("Parede_Leste_2", LARG, y_p1, 0, LARG + T, E + PROF_ARM + T, PE, g, c)
    box("Parede_Fundo_Armario", -T, E + PROF_ARM, 0, LARG + T, E + PROF_ARM + T, PE, g, c)
    # fechamento do banheiro (não visível; evita vazamento de luz)
    box("Banheiro_fechamento_sul", D, -T - 0.10, 0, LARG + T, -T, PE, M["teto"], c)
    box("Banheiro_fechamento_leste", LARG, -T, 0, LARG + T, C - T, PE, M["teto"], c)
    box("Banheiro_piso", D + TC, -T, -0.02, LARG, C - T, 0, M["teto"], c)
    # rodapés (acompanham o piso novo; fora do orçamento)
    rh, rt, r = 0.07, 0.012, M["rodape"]
    box("Rodape_Parede_E_1", 0, RIP, 0, rt, JAN_Y0, rh, r, c)
    box("Rodape_Parede_E_2", 0, JAN_Y0, 0, rt, E, rh, r, c)
    box("Rodape_Parede_C", D - rt, RIP, 0, D, C, rh, r, c)
    box("Rodape_Banheiro_1", D, C - rt, 0, px0, C, rh, r, c)
    box("Rodape_Banheiro_2", px0 + PBWC, C - rt, 0, LARG, C, rh, r, c)
    # ar-condicionado existente (Parede C, meio) — largura/altura estimadas
    ac = box("ArCondicionado_existente", D - 0.20, AC_Y - AC_W / 2, 2.10, D, AC_Y + AC_W / 2, 2.39, M["branco_ac"], c, bevel=0.02)
    ac["status"] = "posição confirmada; dimensões estimadas"
    # tomadas existentes
    box("Tomada_Parede_E", 0, E / 2 - 0.04, 0.27, 0.008, E / 2 + 0.04, 0.39, M["porta"], c)


# ------------------------------------------------------------------ 02 portas e janelas
def esquadrias(M):
    c = "02_PORTAS_JANELAS"
    al, vi = M["aluminio"], M["vidro"]
    z0, z1 = JAN_PEIT, JAN_PEIT + JAN_H
    f = 0.04
    box("Janela_Marco_inferior", -T, JAN_Y0, z0, -0.02, JAN_Y1, z0 + f, al, c)
    box("Janela_Marco_superior", -T, JAN_Y0, z1 - f, -0.02, JAN_Y1, z1, al, c)
    box("Janela_Marco_esq", -T, JAN_Y0, z0, -0.02, JAN_Y0 + f, z1, al, c)
    box("Janela_Marco_dir", -T, JAN_Y1 - f, z0, -0.02, JAN_Y1, z1, al, c)
    meio = (JAN_Y0 + JAN_Y1) / 2
    for i, (ya, yb, xa) in enumerate(((JAN_Y0 + f, meio + 0.03, -0.075), (meio - 0.03, JAN_Y1 - f, -0.045))):
        vd = box(f"Janela_Folha_{i+1}_vidro", xa, ya + 0.03, z0 + f + 0.03, xa + 0.006, yb - 0.03, z1 - f - 0.03, vi, c)
        vd.visible_shadow = False   # deixa o sol atravessar (Cycles sem cáusticas)
        box(f"Janela_Folha_{i+1}_perfil_v1", xa - 0.01, ya, z0 + f, xa + 0.016, ya + 0.03, z1 - f, al, c)
        box(f"Janela_Folha_{i+1}_perfil_v2", xa - 0.01, yb - 0.03, z0 + f, xa + 0.016, yb, z1 - f, al, c)
        box(f"Janela_Folha_{i+1}_perfil_h1", xa - 0.01, ya, z0 + f, xa + 0.016, yb, z0 + f + 0.03, al, c)
        box(f"Janela_Folha_{i+1}_perfil_h2", xa - 0.01, ya, z1 - f - 0.03, xa + 0.016, yb, z1 - f, al, c)
    box("Janela_Peitoril_granito", -T - 0.02, JAN_Y0 - 0.02, z0 - 0.02, 0.02, JAN_Y1 + 0.02, z0, M["granito"], c)
    # persiana externa de enrolar (caixa recolhida + guias)
    box("Persiana_externa_caixa", -T - 0.20, JAN_Y0 - 0.05, z1, -T, JAN_Y1 + 0.05, z1 + 0.20, al, c)
    persiana = box("Persiana_externa_laminas", -T - 0.16, JAN_Y0, z1 - 0.12, -T - 0.14, JAN_Y1, z1, al, c)
    persiana["noite_z_inferior"] = z0 + 0.35
    # porta do banheiro (fechada)
    px0 = D + TC + BLD
    box("Porta_Banheiro_folha_0_60", px0 + (PBWC - 0.60) / 2, C - T / 2 - 0.0175, 0, px0 + (PBWC + 0.60) / 2,
        C - T / 2 + 0.0175, PORTA_H - 0.01, M["porta"], c)
    for nm, a, b in (("esq", px0, px0 + 0.065), ("dir", px0 + PBWC - 0.065, px0 + PBWC)):
        box(f"Porta_Banheiro_batente_{nm}", a, C - T - 0.01, 0, b, C + 0.01, PORTA_H, M["porta"], c)
    box("Porta_Banheiro_batente_topo", px0, C - T - 0.01, PORTA_H - 0.01, px0 + PBWC, C + 0.01, PORTA_H + 0.05, M["porta"], c)
    cyl("Porta_Banheiro_macaneta", px0 + PBWC - 0.12, C + 0.03, 1.02, 0.01, 0.12, M["cromo"], c,
        rot=Euler((0, math.pi / 2, 0)))
    # porta de entrada (fechada) — folha 0,75, batente 0,80
    y_p0 = C + (FAIXA - PENT) / 2
    box("Porta_Entrada_folha_0_75", LARG + T / 2 - 0.0175, y_p0 + 0.025, 0, LARG + T / 2 + 0.0175, y_p0 + PENT - 0.025,
        PORTA_H - 0.01, M["porta"], c)
    for nm, a, b in (("1", y_p0, y_p0 + 0.025), ("2", y_p0 + PENT - 0.025, y_p0 + PENT)):
        box(f"Porta_Entrada_batente_{nm}", LARG - 0.01, a, 0, LARG + T + 0.01, b, PORTA_H, M["porta"], c)
    box("Porta_Entrada_batente_topo", LARG - 0.01, y_p0, PORTA_H - 0.01, LARG + T + 0.01, y_p0 + PENT, PORTA_H + 0.05, M["porta"], c)
    cyl("Porta_Entrada_macaneta", LARG - 0.03, y_p0 + 0.10, 1.02, 0.01, 0.12, M["cromo"], c,
        rot=Euler((0, math.pi / 2, 0)))


# ------------------------------------------------------------------ 03 mobiliário
def mobiliario(M):
    c = "03_MOBILIARIO"
    # armário existente (fora do escopo; cor e tipo de porta pendentes)
    arm = box("Armario_existente_corpo", 0, E + 0.02, 0, LARG, E + PROF_ARM, PE, M["armario"], c)
    arm["status"] = "existente — cor e tipo de porta pendentes"
    n_portas = 6
    w = LARG / n_portas
    for i in range(n_portas):
        box(f"Armario_existente_porta_{i+1}", i * w + 0.002, E, 0.02, (i + 1) * w - 0.002, E + 0.02, PE - 0.01, M["armario"], c)
        hx = (i + 1) * w - 0.05 if i % 2 == 0 else i * w + 0.04
        box(f"Armario_existente_puxador_{i+1}", hx, E - 0.015, 0.95, hx + 0.012, E, 1.35, M["preto_metal"], c)

    # mesa regulável (estrutura Pichau Starlift Pro + tampo freijó 170×70×2,5)
    cx = MX0 + MESA_W / 2
    cy = MY0 + MESA_P / 2
    mesa = box("Mesa_Tampo_Freijo_170x70x2_5", MX0, MY0, MESA_Z - TAMPO, MX0 + MESA_W, MY0 + MESA_P, MESA_Z,
               M["freijo"], c, bevel=0.002)
    mesa["dimensoes_cm"] = "170 × 70 × 2,5 (altura 73–118)"
    for nm, lx in (("esq", cx - 0.5975), ("dir", cx + 0.5975)):
        p = box(f"Mesa_Estrutura_coluna_{nm}", lx - 0.035, cy - 0.025, 0.03, lx + 0.035, cy + 0.025, MESA_Z - TAMPO - 0.03,
                M["preto_metal"], c)
        parent(p, mesa)
        p = box(f"Mesa_Estrutura_pe_{nm}", lx - 0.03, cy - 0.29, 0, lx + 0.03, cy + 0.29, 0.03, M["preto_metal"], c)
        parent(p, mesa)
        p = box(f"Mesa_Estrutura_braco_{nm}", lx - 0.025, MY0 + 0.06, MESA_Z - TAMPO - 0.03, lx + 0.025, MY0 + MESA_P - 0.06,
                MESA_Z - TAMPO, M["preto_metal"], c)
        parent(p, mesa)
    p = box("Mesa_Estrutura_travessa", cx - 0.5975, cy - 0.02, MESA_Z - TAMPO - 0.07, cx + 0.5975, cy + 0.02,
            MESA_Z - TAMPO - 0.03, M["preto_metal"], c)
    parent(p, mesa)
    p = box("Mesa_Painel_Controle", MX0 + MESA_W - 0.25, MY0 + MESA_P - 0.06, MESA_Z - TAMPO - 0.02,
            MX0 + MESA_W - 0.13, MY0 + MESA_P - 0.01, MESA_Z - TAMPO, M["preto"], c)
    parent(p, mesa)

    # suporte articulado ELG F160N (fixação por furo) + 2 monitores 27"
    pole = cyl("Braco_ELG_F160N_coluna", MON_CX, MY0 + 0.07, MESA_Z, 0.02, 0.42, M["preto_metal"], c)
    parent(pole, mesa)
    mw, mh, md = 0.615, 0.365, 0.045
    for i, sgn in enumerate((-1, 1)):
        mx = MON_CX + sgn * 0.312
        ang = -sgn * math.radians(8)
        arm_ = box(f"Braco_ELG_F160N_braco_{i+1}", min(MON_CX, mx), MY0 + 0.06, MESA_Z + 0.33, max(MON_CX, mx), MY0 + 0.09,
                   MESA_Z + 0.36, M["preto_metal"], c)
        parent(arm_, mesa)
        mon = box(f"Monitor_27_{i+1}", -mw / 2, 0, -mh / 2, mw / 2, md, mh / 2, M["preto"], c, bevel=0.004, local=True)
        mon.location = (mx, MY0 + 0.20, MESA_Z + 0.17 + mh / 2)
        mon.rotation_euler = (0, 0, ang)
        scr = box(f"Monitor_27_{i+1}_tela", -mw / 2 + 0.008, md, -mh / 2 + 0.012, mw / 2 - 0.008, md + 0.001, mh / 2 - 0.008,
                  M["tela"], c, local=True)
        scr.location = mon.location
        scr.rotation_euler = mon.rotation_euler
        parent(scr, mon)
        parent(mon, mesa)
    # barra de luz sobre o monitor 1
    bar = box("Barra_Luz_Monitor", -0.22, -0.02, 0, 0.22, 0.03, 0.02, M["preto"], c, local=True)
    bar.location = (MON_CX - 0.312, MY0 + 0.20, MESA_Z + 0.17 + mh + 0.002)
    bar.rotation_euler = (0, 0, math.radians(8))
    parent(bar, mesa)
    led_b = box("Barra_Luz_Monitor_LED", -0.20, 0.0, -0.002, 0.20, 0.012, 0.0, M["led_bar"], c, local=True)
    led_b.location = bar.location
    led_b.rotation_euler = bar.rotation_euler
    parent(led_b, bar)
    # periféricos
    tp = box("Mousepad", cx - 0.45, MY0 + MESA_P - 0.40, MESA_Z, cx + 0.45, MY0 + MESA_P - 0.04, MESA_Z + 0.003, M["preto"], c)
    parent(tp, mesa)
    kb = box("Teclado", MON_CX - 0.20, MY0 + MESA_P - 0.26, MESA_Z + 0.003, MON_CX + 0.16, MY0 + MESA_P - 0.13, MESA_Z + 0.03,
             M["teclado"], c, bevel=0.004)
    parent(kb, mesa)
    ms = box("Mouse", MON_CX + 0.25, MY0 + MESA_P - 0.24, MESA_Z + 0.003, MON_CX + 0.31, MY0 + MESA_P - 0.12, MESA_Z + 0.04,
             M["teclado"], c, bevel=0.015)
    parent(ms, mesa)
    # notebook em suporte baixo, na frente à esquerda (não cruza o monitor esquerdo)
    nx0, ny0, nx1, ny1 = NB
    st = box("Suporte_Notebook_baixo", nx0 + 0.01, ny0 + 0.02, MESA_Z, nx1 - 0.01, ny1 - 0.01, MESA_Z + 0.018, M["preto_metal"], c)
    parent(st, mesa)
    zb = MESA_Z + 0.018
    nb = box("Notebook_base", nx0, ny0 + 0.01, zb, nx1, ny1, zb + 0.016, M["aluminio"], c, bevel=0.003)
    parent(nb, mesa)
    nbs = box("Notebook_tela", 0, -0.008, 0, nx1 - nx0, 0, 0.21, M["tela"], c, local=True)
    nbs.location = (nx0, ny0 + 0.01, zb + 0.016)            # dobradiça em y = 0,43
    nbs.rotation_euler = (math.radians(15), 0, 0)           # tela inclinada 15° para trás (−y)
    parent(nbs, mesa)
    nbt = box("Notebook_tampa", 0, -0.014, 0, nx1 - nx0, -0.008, 0.21, M["aluminio"], c, local=True)
    nbt.location, nbt.rotation_euler = nbs.location, nbs.rotation_euler
    parent(nbt, mesa)
    pc_gabinete(M, mesa)

    # cama box solteiro 88 × 188 × 62 (Gazin Maximus)
    y0 = RIP
    box("Cama_Box_base", 0.0, y0, 0.03, CAMA_W, y0 + CAMA_L, 0.32, M["box"], c, bevel=0.01)
    box("Cama_Box_rodape_preto", 0.04, y0 + 0.04, 0, CAMA_W - 0.04, y0 + CAMA_L - 0.04, 0.03, M["preto"], c)
    box("Cama_Colchao_88x188", 0.0, y0, 0.32, CAMA_W, y0 + CAMA_L, CAMA_H, M["colchao"], c, bevel=0.03)
    box("Cama_Edredom", 0.0, y0 + 0.42, 0.40, CAMA_W + 0.025, y0 + CAMA_L + 0.03, CAMA_H + 0.04, M["edredom"], c, bevel=0.035)
    box("Cama_Manta_Caramelo", -0.0, y0 + 1.40, 0.38, CAMA_W + 0.035, y0 + 1.80, CAMA_H + 0.065, M["manta"], c, bevel=0.03)
    box("Cama_Travesseiro", 0.08, y0 + 0.05, CAMA_H, CAMA_W - 0.08, y0 + 0.42, CAMA_H + 0.14, M["fronha"], c, bevel=0.06)
    al = box("Cama_Almofada_Caramelo", 0.20, y0 + 0.33, CAMA_H + 0.02, 0.62, y0 + 0.46, CAMA_H + 0.40, M["almofada"], c, bevel=0.06)
    al.rotation_euler = (math.radians(-12), 0, 0)

    # cadeira ergonômica (DT3 Elin — volumetria aproximada)
    chx, chy = PT.MX0 + PT.MESA_W / 2 - 0.10, PT.MY0 + PT.MESA_P + 0.38
    raiz = bpy.data.objects.new("Cadeira_DT3_Elin", None)
    raiz.location = (chx, chy, 0)
    link(raiz, c)
    partes = []
    for k in range(5):
        a = k * 2 * math.pi / 5
        sp = box(f"Cadeira_base_raio_{k+1}", 0, -0.02, 0.06, 0.32, 0.02, 0.09, M["preto"], c, local=True)
        sp.location = (chx, chy, 0.0)
        sp.rotation_euler = (0, 0, a)
        partes.append(sp)
        rd = cyl(f"Cadeira_rodizio_{k+1}", chx + 0.31 * math.cos(a), chy + 0.31 * math.sin(a), 0.0, 0.03, 0.05, M["preto"], c)
        partes.append(rd)
    partes.append(cyl("Cadeira_pistao", chx, chy, 0.09, 0.025, 0.36, M["preto_metal"], c))
    partes.append(box("Cadeira_assento", chx - 0.25, chy - 0.25, 0.45, chx + 0.25, chy + 0.23, 0.53, M["cadeira"], c, bevel=0.03))
    enc = box("Cadeira_encosto", chx - 0.23, chy + 0.20, 0.58, chx + 0.23, chy + 0.25, 1.20, M["cadeira"], c, bevel=0.03)
    enc.rotation_euler = (math.radians(-8), 0, 0)
    partes.append(enc)
    partes.append(box("Cadeira_apoio_cabeca", chx - 0.13, chy + 0.27, 1.22, chx + 0.13, chy + 0.33, 1.36, M["cadeira"], c, bevel=0.02))
    for s_ in (-1, 1):
        partes.append(box(f"Cadeira_braco_{'esq' if s_ < 0 else 'dir'}", chx + s_ * 0.27 - 0.03, chy - 0.18, 0.67,
                          chx + s_ * 0.27 + 0.03, chy + 0.12, 0.70, M["preto"], c, bevel=0.01))
        partes.append(box(f"Cadeira_braco_suporte_{'esq' if s_ < 0 else 'dir'}", chx + s_ * 0.27 - 0.015, chy - 0.02, 0.50,
                          chx + s_ * 0.27 + 0.015, chy + 0.02, 0.67, M["preto"], c))
    for p in partes:
        parent(p, raiz)


def pc_gabinete(M, mesa):
    """PC sobre o tampo (canto direito): gabinete 23 × 45 × 46 com vidro na frente (+y) e no lado −x, 3 fans
    frontais com anel de LED 3000 K. Tudo é filho do tampo: sobe e desce com a mesa."""
    c = "03_MOBILIARIO"
    x0, y0, z0 = PC_X0, PC_Y0, MESA_Z
    x1, y1, z1 = x0 + PC_W, y0 + PC_P, z0 + PC_H
    e, p = 0.006, []
    k = M["preto"]
    p.append(box("PC_Gabinete_fundo", x0, y0, z0 + 0.02, x1, y0 + e, z1, k, c))
    p.append(box("PC_Gabinete_lateral_direita", x1 - e, y0, z0 + 0.02, x1, y1, z1, k, c))
    p.append(box("PC_Gabinete_base", x0, y0, z0 + 0.02, x1, y1, z0 + 0.02 + e, k, c))
    p.append(box("PC_Gabinete_tampa_topo", x0, y0, z1 - e, x1, y1, z1, k, c))
    p.append(box("PC_Gabinete_moldura_frente_dir", x1 - 0.012, y1 - 0.012, z0 + 0.02, x1, y1, z1, k, c))
    p.append(box("PC_Gabinete_coluna_canto", x0, y1 - 0.012, z0 + 0.02, x0 + 0.012, y1, z1, k, c))
    p.append(box("PC_Gabinete_coluna_fundo", x0, y0, z0 + 0.02, x0 + 0.012, y0 + 0.012, z1, k, c))
    v1 = box("PC_Gabinete_vidro_frente", x0 + 0.012, y1 - 0.005, z0 + 0.02 + e, x1 - 0.012, y1 - 0.001, z1 - e, M["vidro_fume"], c)
    v2 = box("PC_Gabinete_vidro_lateral", x0 + 0.001, y0 + 0.012, z0 + 0.02 + e, x0 + 0.005, y1 - 0.012, z1 - e,
             M["vidro_fume"], c)
    for v in (v1, v2):
        v.visible_shadow = False
    p += [v1, v2]
    for i, (fx, fy) in enumerate(((x0 + 0.04, y0 + 0.08), (x1 - 0.04, y0 + 0.08), (x0 + 0.04, y1 - 0.06), (x1 - 0.04, y1 - 0.06))):
        p.append(box(f"PC_Gabinete_pe_{i+1}", fx - 0.02, fy - 0.02, z0, fx + 0.02, fy + 0.02, z0 + 0.02, M["preto_metal"], c))
    # internos: placa-mãe na lateral direita, placa de vídeo, cooler, fonte embaixo
    p.append(box("PC_Placa_mae", x1 - e - 0.004, y0 + 0.03, z0 + 0.15, x1 - e, y0 + 0.28, z1 - 0.03, M["pcb"], c))
    p.append(box("PC_Placa_video", x0 + 0.07, y0 + 0.03, z0 + 0.20, x1 - e - 0.004, y0 + 0.31, z0 + 0.25, M["preto_metal"], c,
                 bevel=0.003))
    p.append(cyl("PC_Cooler_CPU", x1 - 0.06, y0 + 0.17, z0 + 0.34, 0.045, 0.05, M["cromo"], c, rot=Euler((0, -math.pi / 2, 0))))
    p.append(box("PC_Fonte_shroud", x0 + 0.012, y0 + e, z0 + 0.02 + e, x1 - e, y1 - 0.04, z0 + 0.12, k, c))
    for i in range(3):
        fz = z0 + 0.17 + i * 0.125
        anel = cyl(f"PC_Fan_{i+1}_anel_LED", (x0 + x1) / 2, y1 - 0.035, fz, 0.058, 0.010, M["led_pc"], c, verts=48,
                   rot=Euler((-math.pi / 2, 0, 0)))
        anel.location.y = y1 - 0.030
        miolo = cyl(f"PC_Fan_{i+1}_pas", (x0 + x1) / 2, y1 - 0.029, fz, 0.052, 0.014, M["preto"], c, verts=48,
                    rot=Euler((-math.pi / 2, 0, 0)))
        p += [anel, miolo]
    luz = bpy.data.lights.new("L7_Luz_PC_fans", "POINT")
    luz.energy, luz.shadow_soft_size, luz.color = 1.5, 0.06, kelvin(3000)
    ob = bpy.data.objects.new("L7_Luz_PC_fans", luz)
    ob.location = ((x0 + x1) / 2, y1 - 0.08, z0 + 0.30)
    link(ob, "05_ILUMINACAO")
    p.append(ob)
    for o in p:
        parent(o, mesa)
    mesa["pc_sobre_tampo"] = "gabinete 23 × 45 × 46, ≈ 12 kg; carga total ≈ 64 kg < 80 kg (Starlift)"


# ------------------------------------------------------------------ 04 marcenaria
def marcenaria(M):
    c = "04_MARCENARIA"
    box("Ripado_Fundo_MDF_Preto", 0, 0, 0, D, FUNDO, PE, M["fundo_ripado"], c)
    ripa = box("Ripado_Ripas_Freijo", RIPA_X0, FUNDO, 0, RIPA_X0 + RIPA_W, FUNDO + RIPA_D, PE, M["freijo_v"], c)
    arr = ripa.modifiers.new("Array_ripas", "ARRAY")
    arr.use_relative_offset, arr.use_constant_offset = False, True
    arr.constant_offset_displace = (PITCH, 0, 0)
    arr.count = N_RIPAS
    ripa["ripas"] = f"{N_RIPAS} ripas 2,0 × 1,8 cm, vão 1,5 cm"
    # tomada da Parede D com prolongador (altura estimada 0,30)
    box("Tomada_Parede_D_prolongador", TOM_D - 0.04, RIP - 0.002, 0.24, TOM_D + 0.04, RIP + 0.006, 0.36, M["porta"], c)
    # prateleira 170 × 25 × 2,5 a 1,95 m
    box("Prateleira_Freijo_170x25", MX0, RIP, PRAT_H, MX0 + MESA_W, RIP + PRAT_P, PRAT_H + 0.025, M["freijo"], c, bevel=0.002)
    # 3 nichos iluminados sobre a cabeceira (24 × 26 × 16 cm, MDF freijó 15 mm, fundo preto, LED 3000 K)
    t = 0.015
    z0, z1 = PT.NICHO_Z0, PT.NICHO_Z0 + PT.NICHO_H
    y0, y1 = RIP, RIP + PT.NICHO_P
    for k in range(3):
        x0 = PT.NICHOS_X0 + k * (PT.NICHO_W + PT.NICHO_GAP)
        x1 = x0 + PT.NICHO_W
        n = f"Nicho_{k+1}"
        box(f"{n}_base", x0, y0, z0, x1, y1, z0 + t, M["freijo"], c, bevel=0.001)
        box(f"{n}_topo", x0, y0, z1 - t, x1, y1, z1, M["freijo"], c, bevel=0.001)
        box(f"{n}_lateral_esq", x0, y0, z0 + t, x0 + t, y1, z1 - t, M["freijo"], c, bevel=0.001)
        box(f"{n}_lateral_dir", x1 - t, y0, z0 + t, x1, y1, z1 - t, M["freijo"], c, bevel=0.001)
        box(f"{n}_fundo_preto", x0 + t, y0, z0 + t, x1 - t, y0 + 0.006, z1 - t, M["fundo_ripado"], c)
        box(f"{n}_fita_LED", x0 + t + 0.01, y1 - 0.03, z1 - t - 0.003, x1 - t - 0.01, y1 - 0.02, z1 - t, M["led"], c)
        luz_area(f"L5_Luz_nicho_{k+1}", ((x0 + x1) / 2, y1 - 0.025, z1 - t - 0.004), (0, 0, 0), PT.NICHO_W - 2 * t - 0.02,
                 0.01, 1.2, 3000, "05_ILUMINACAO")


# ------------------------------------------------------------------ 05 iluminação
def luz_area(name, loc, rot, sx, sy, watts, kel, c, portal=False):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = sx, sy
    ld.energy = watts
    ld.color = kelvin(kel)
    if portal:
        ld.cycles.is_portal = True
    ob = bpy.data.objects.new(name, ld)
    ob.location, ob.rotation_euler = loc, rot
    return link(ob, c)


def iluminacao(M):
    c = "05_ILUMINACAO"
    L = {}
    # L1 — fita sob a prateleira (emissor visível + luz de área para baixo)
    box("L1_Fita_LED_prateleira", MX0 + 0.03, RIP + PRAT_P - 0.04, PRAT_H - 0.004, MX0 + MESA_W - 0.03, RIP + PRAT_P - 0.03,
        PRAT_H, M["led"], c)
    L["L1"] = luz_area("L1_Luz_prateleira", (MX0 + MESA_W / 2, RIP + PRAT_P - 0.035, PRAT_H - 0.006), (0, 0, 0),
                       MESA_W - 0.06, 0.012, 12.0, 3000, c)
    # L2 — perfil vertical no vão do ripado
    box("L2_Fita_LED_vertical", LED_V_X - 0.006, FUNDO - 0.001, 0.10, LED_V_X + 0.006, FUNDO + 0.004, 2.50, M["led"], c)
    L["L2"] = luz_area("L2_Luz_vertical", (LED_V_X, FUNDO + 0.006, 1.30), (math.radians(-90), 0, 0), 0.012, 2.40, 6.0, 3000, c)
    # L3 — barra de luz do monitor
    L["L3"] = luz_area("L3_Luz_barra_monitor", (MON_CX - 0.312, MY0 + 0.23, MESA_Z + 0.17 + 0.365),
                       (math.radians(25), 0, math.radians(8)), 0.40, 0.02, 3.0, 4000, c)
    # L4 — arandela articulada na cabeceira
    ax, az = ARAND_X, ARAND_H
    cyl("L4_Arandela_base", ax, RIP + 0.002, az, 0.035, 0.015, M["preto"], c, rot=Euler((-math.pi / 2, 0, 0)))
    box("L4_Arandela_braco", ax - 0.008, RIP, az - 0.008, ax + 0.008, RIP + 0.16, az + 0.008, M["preto"], c)
    cyl("L4_Arandela_tubo", ax, RIP + 0.16, az - 0.02, 0.03, 0.12, M["preto"], c, rot=Euler((math.radians(20), 0, 0)))
    ld = bpy.data.lights.new("L4_Luz_arandela", "SPOT")
    ld.energy, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 25.0, math.radians(70), 0.4, 0.02
    ld.color = kelvin(2700)
    ob = bpy.data.objects.new("L4_Luz_arandela", ld)
    ob.location, ob.rotation_euler = (ax, RIP + 0.17, az - 0.03), (math.radians(-20), 0, 0)
    L["L4"] = link(ob, c)
    # ventilador de teto com luz (existente)
    fx, fy = FAN
    cyl("Ventilador_haste", fx, fy, PE - 0.18, 0.012, 0.18, M["preto_metal"], c)
    cyl("Ventilador_motor", fx, fy, PE - 0.30, 0.10, 0.12, M["preto_metal"], c, verts=48)
    for k in range(3):
        bl = box(f"Ventilador_pa_{k+1}", 0.10, -0.06, -0.004, 0.53, 0.06, 0.004, M["preto"], c, local=True)
        bl.location = (fx, fy, PE - 0.26)
        bl.rotation_euler = (math.radians(8), 0, k * 2 * math.pi / 3)
    sph = bpy.data.meshes.new("Ventilador_globo")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.09)
    bm.to_mesh(sph)
    bm.free()
    gl = bpy.data.objects.new("Ventilador_globo_luz", sph)
    gl.location = (fx, fy, PE - 0.36)
    sph.materials.append(M["lampada"])
    link(gl, c)
    ld = bpy.data.lights.new("Luz_Ventilador_3000K", "POINT")
    ld.energy, ld.shadow_soft_size, ld.color = 45.0, 0.09, kelvin(3000)
    ob = bpy.data.objects.new("Luz_Ventilador_3000K", ld)
    ob.location = (fx, fy, PE - 0.36)
    L["geral"] = link(ob, c)
    # plafon da faixa de entrada (existente)
    lx, ly = LUZ_FAIXA
    cyl("Plafon_faixa", lx, ly, PE - 0.04, 0.14, 0.04, M["lampada"], c, verts=48)
    ld = bpy.data.lights.new("Luz_Plafon_faixa", "AREA")
    ld.shape, ld.size, ld.energy, ld.color = "DISK", 0.28, 25.0, kelvin(3000)
    ob = bpy.data.objects.new("Luz_Plafon_faixa", ld)
    ob.location = (lx, ly, PE - 0.045)
    L["faixa"] = link(ob, c)
    # luz natural: portal na janela + sol da manhã vindo do leste (−x)
    L["portal"] = luz_area("Portal_Janela", (-T / 2, (JAN_Y0 + JAN_Y1) / 2, JAN_PEIT + JAN_H / 2),
                           (0, math.radians(90), 0), JAN_H, JAN_Y1 - JAN_Y0, 1.0, 6500, c, portal=True)
    ld = bpy.data.lights.new("Sol_Manha_Leste", "SUN")
    ld.energy, ld.angle, ld.color = 3.5, math.radians(1.0), kelvin(5200)
    ob = bpy.data.objects.new("Sol_Manha_Leste", ld)
    ob.rotation_euler = (math.radians(62), 0, math.radians(-75))
    L["sol"] = link(ob, c)
    return L


# ------------------------------------------------------------------ 06 decoração
def decoracao(M):
    c = "06_DECORACAO"
    box("Tapete_140x200", TAP[0], TAP[1], 0, TAP[2], TAP[3], 0.008, M["tapete"], c, bevel=0.003)
    # itens leves na prateleira
    z = PRAT_H + 0.025
    xs = MX0 + MESA_W - 0.40
    for k, (w, h, m) in enumerate(((0.03, 0.22, "livro1"), (0.025, 0.24, "livro2"), (0.035, 0.20, "livro3"),
                                   (0.028, 0.23, "livro1"), (0.03, 0.21, "livro2"))):
        box(f"Livro_{k+1}", xs, RIP + 0.04, z, xs + w, RIP + 0.20, z + h, M[m], c)
        xs += w + 0.002
    quadros(M, c)
    planta_pendente(M, c)
    acessorios(M, c)


# Quadros P&B na Parede E, entre a Parede D e a janela (y < 1,10). (nome, y0, y1, z0, z1, arte)
QUADROS = (("Quadro_A_40x55", 0.10, 0.50, 1.20, 1.75, "quadro_A"),
           ("Quadro_B_36x26", 0.58, 0.94, 1.49, 1.75, "quadro_B"),
           ("Quadro_C_36x26", 0.58, 0.94, 1.20, 1.46, "quadro_C"))
PENDENTE = (0.30, 2.25, 1.95)       # (x, y, z da base do vaso) — sobre a circulação, longe do ventilador


def quadro_parede(M, c, nome, y0, y1, z0, z1, arte_):
    box(f"{nome}_moldura", 0.0, y0, z0, 0.022, y1, z1, M["preto"], c, bevel=0.002)
    box(f"{nome}_passe_partout", 0.022, y0 + 0.012, z0 + 0.012, 0.024, y1 - 0.012, z1 - 0.012, M["passe"], c)
    m = 0.045
    box(f"{nome}_arte", 0.024, y0 + m, z0 + m, 0.025, y1 - m, z1 - m, M[arte_], c)


def quadros(M, c):
    for q in QUADROS:
        quadro_parede(M, c, *q)
    # 2 quadros pequenos apoiados na prateleira (encostados no ripado, inclinados 8°)
    z = PRAT_H + 0.025
    for nome, xa, w, h, arte_ in (("Quadro_D_20x25_prateleira", 1.58, 0.20, 0.25, "quadro_D"),
                                  ("Quadro_E_15x20_prateleira", 1.81, 0.15, 0.20, "quadro_E")):
        raiz = bpy.data.objects.new(nome, None)
        raiz.location = (xa, RIP + 0.05, z)
        raiz.rotation_euler = (math.radians(-8), 0, 0)
        link(raiz, c)
        fr = box(f"{nome}_moldura", 0, -0.018, 0, w, 0, h, M["preto"], c, bevel=0.002, local=True)
        pp = box(f"{nome}_passe_partout", 0.010, 0.0, 0.010, w - 0.010, 0.001, h - 0.010, M["passe"], c, local=True)
        ar = box(f"{nome}_arte", 0.03, 0.001, 0.03, w - 0.03, 0.002, h - 0.03, M[arte_], c, local=True)
        for o in (fr, pp, ar):
            o.location, o.rotation_euler = raiz.location, raiz.rotation_euler
            parent(o, raiz)


def planta_pendente(M, c):
    px, py, pz = PENDENTE
    cyl("Planta_pendente_vaso", px, py, pz, 0.09, 0.16, M["ceramica_preta"], c, verts=48)
    gancho = Vector((px, py, PE - 0.25))
    box("Planta_pendente_gancho_teto", px - 0.02, py - 0.02, PE - 0.008, px + 0.02, py + 0.02, PE, M["preto_metal"], c)
    cyl("Planta_pendente_corda_principal", px, py, gancho.z, 0.003, PE - gancho.z, M["corda"], c, verts=8)
    for k in range(3):
        a = k * 2 * math.pi / 3
        base = Vector((px + 0.088 * math.cos(a), py + 0.088 * math.sin(a), pz + 0.14))
        d = gancho - base
        o = cyl(f"Planta_pendente_corda_{k+1}", base.x, base.y, base.z, 0.002, d.length, M["corda"], c, verts=8)
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def acessorios(M, c):
    mesa = bpy.data.objects["Mesa_Tampo_Freijo_170x70x2_5"]
    z = MESA_Z
    ps = []
    # suporte de headphone (2,50, 0,67) + headphone
    hx, hy = 2.50, 0.67
    ps.append(cyl("Suporte_headphone_base", hx, hy, z, 0.05, 0.008, M["preto_metal"], c, verts=40))
    ps.append(cyl("Suporte_headphone_haste", hx, hy, z + 0.008, 0.008, 0.25, M["preto_metal"], c))
    ps.append(box("Suporte_headphone_apoio", hx - 0.045, hy - 0.012, z + 0.25, hx + 0.045, hy + 0.012, z + 0.265, M["preto_metal"], c))
    for s_ in (-1, 1):
        ps.append(box(f"Headphone_concha_{'esq' if s_ < 0 else 'dir'}", hx + s_ * 0.075 - 0.02, hy - 0.045, z + 0.10,
                      hx + s_ * 0.075 + 0.02, hy + 0.045, z + 0.20, M["preto"], c, bevel=0.015))
    ps.append(box("Headphone_arco", hx - 0.08, hy - 0.015, z + 0.265, hx + 0.08, hy + 0.015, z + 0.285, M["preto"], c, bevel=0.006))
    # caneca (2,30, 0,66)
    ps.append(cyl("Caneca", 2.30, 0.66, z, 0.04, 0.095, M["caneca"], c, verts=40))
    ps.append(box("Caneca_alca", 2.338, 0.655, z + 0.025, 2.355, 0.665, z + 0.075, M["caneca"], c, bevel=0.004))
    # luminária de mesa articulada (1,01, 0,12) — spot 2700 K sobre o notebook
    lx, ly = 1.01, 0.12
    ps.append(cyl("Luminaria_mesa_base", lx, ly, z, 0.06, 0.015, M["preto_metal"], c, verts=40))
    ps.append(cyl("Luminaria_mesa_haste", lx, ly, z + 0.015, 0.007, 0.38, M["preto_metal"], c))
    ps.append(box("Luminaria_mesa_braco", lx - 0.006, ly, z + 0.385, lx + 0.006, ly + 0.14, z + 0.397, M["preto_metal"], c))
    ps.append(cyl("Luminaria_mesa_cupula", lx, ly + 0.15, z + 0.33, 0.04, 0.07, M["preto"], c, verts=40,
                  rot=Euler((math.radians(-25), 0, 0))))
    ld = bpy.data.lights.new("L6_Luz_luminaria_mesa", "SPOT")
    ld.energy, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 10.0, math.radians(80), 0.5, 0.03
    ld.color = kelvin(2700)
    ob = bpy.data.objects.new("L6_Luz_luminaria_mesa", ld)
    ob.location, ob.rotation_euler = (lx, ly + 0.16, z + 0.325), (math.radians(-25), 0, 0)
    link(ob, "05_ILUMINACAO")
    ps.append(ob)
    for o in ps:
        parent(o, mesa)
    # relógio LED na prateleira
    zp = PRAT_H + 0.025
    box("Relogio_LED_prateleira", 2.02, RIP + 0.10, zp, 2.14, RIP + 0.14, zp + 0.06, M["preto"], c, bevel=0.004)
    box("Relogio_LED_display", 2.03, RIP + 0.14, zp + 0.015, 2.13, RIP + 0.141, zp + 0.045, M["led"], c)


# ------------------------------------------------------------------ 07 câmeras
def camera(name, loc, alvo, lens=18.0, ortho=None):
    cd = bpy.data.cameras.new(name)
    cd.sensor_width = 36
    if ortho:
        cd.type, cd.ortho_scale = "ORTHO", ortho
    else:
        cd.lens = lens
    cd.clip_start = 0.05
    ob = bpy.data.objects.new(name, cd)
    ob.location = loc
    d = Vector(alvo) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return link(ob, "07_CAMERAS")


def cameras():
    camera("CAM_vista_superior", (2.25, 1.65, 8.0), (2.25, 1.65, 0.0), ortho=5.6)
    camera("CAM_vista_isometrica", (7.0, 6.8, 7.0), (1.30, 1.20, 0.6), ortho=6.2)
    camera("CAM_area_trabalho", (1.95, 2.60, 1.45), (1.70, 0.10, 1.05), lens=20)
    camera("CAM_area_descanso", (2.50, 2.70, 1.55), (0.30, 0.70, 0.70), lens=17)
    camera("CAM_entrada", (4.45, 2.40, 1.60), (0.20, 1.30, 1.00), lens=18)
    camera("CAM_marcenaria_ripado", (1.32, 2.78, 1.62), (1.32, 0.0, 1.30), lens=16)
    camera("CAM_principal", (2.55, 2.75, 1.70), (0.55, 0.25, 0.85), lens=16)


# ------------------------------------------------------------------ 08 cotas / referências
def referencias():
    c = "08_COTAS_REFERENCIAS"
    pts = {"REF_origem_ParedeE_x_ParedeD": (0, 0, 0), "REF_canto_ParedeD_x_ParedeC": (D, 0, 0),
           "REF_frente_armario_ParedeE": (0, E, 0), "REF_canto_banheiro": (D, C, 0),
           "REF_pe_direito": (0, 0, PE)}
    for n, p in pts.items():
        e = bpy.data.objects.new(n, None)
        e.empty_display_type, e.empty_display_size = "PLAIN_AXES", 0.15
        e.location = p
        link(e, c)
    for nome, (txt, loc) in {"COTA_ParedeD_2_65": ("Parede D 2,65 m", (D / 2, -0.30, 0.01)),
                             "COTA_ParedeE_2_85": ("Parede E 2,85 m", (-0.35, E / 2, 0.01)),
                             "COTA_PeDireito_2_64": ("pé-direito 2,64 m", (-0.35, -0.30, PE))}.items():
        cu = bpy.data.curves.new(nome, "FONT")
        cu.body, cu.size = txt, 0.12
        ob = bpy.data.objects.new(nome, cu)
        ob.location = loc
        link(ob, c)
    coll(c).hide_render = True


# ------------------------------------------------------------------ mundo e render
def mundo():
    w = bpy.data.worlds.new("Mundo_HDRI")
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(ASSETS / "hdri" / "modern_buildings_2_2k.hdr"))
    env.name = "HDRI"
    mp = nt.nodes.new("ShaderNodeMapping")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(90))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = w
    noite = bpy.data.images.load(str(ASSETS / "hdri" / "modern_buildings_night_2k.hdr"), check_existing=True)
    noite.use_fake_user = True   # usado só no render noturno; evita ser descartado ao salvar


def render_cfg():
    sc = bpy.context.scene
    sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = "METRIC", 1.0, "METERS"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "GPU"
    sc.cycles.samples = 256
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces, sc.cycles.diffuse_bounces, sc.cycles.glossy_bounces = 10, 5, 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = 0.0


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for name in ("01_ESTRUTURA", "02_PORTAS_JANELAS", "03_MOBILIARIO", "04_MARCENARIA", "05_ILUMINACAO",
                 "06_DECORACAO", "07_CAMERAS", "08_COTAS_REFERENCIAS"):
        coll(name)
    M = materiais()
    estrutura(M)
    esquadrias(M)
    mobiliario(M)
    marcenaria(M)
    iluminacao(M)
    decoracao(M)
    cameras()
    referencias()
    mundo()
    render_cfg()
    bpy.context.scene.camera = bpy.data.objects["CAM_principal"]
    bpy.context.view_layer.update()
    BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), relative_remap=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
    versoes = BLEND.parent / "versoes"
    versoes.mkdir(exist_ok=True)
    n = len(list(versoes.glob("quarto_escritorio_v*.blend"))) + 1
    shutil.copy2(BLEND, versoes / f"quarto_escritorio_v{n:02d}.blend")
    print("SALVO", BLEND, "versão", n, "ripas", N_RIPAS, "LED_V_X", round(LED_V_X, 4))


if __name__ == "__main__":
    main()
