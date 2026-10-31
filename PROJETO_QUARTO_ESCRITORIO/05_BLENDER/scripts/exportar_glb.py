"""Exporta uma versão leve do modelo para visualização na web (glTF binário).

Uso: blender -b quarto_escritorio.blend --python exportar_glb.py -- <saida.glb> <pasta_texturas_web>
Não altera o .blend salvo: as adaptações (UVs, materiais simplificados, sem teto) existem só nesta sessão.
"""
import sys
from pathlib import Path

import bmesh
import bpy

ARGS = sys.argv[sys.argv.index("--") + 1:]
SAIDA, TEX = Path(ARGS[0]), Path(ARGS[1])

# texturas já ajustadas (cor/tom) e reduzidas para 1k, geradas antes com ImageMagick
TEXTURAS = {
    "Madeira_Freijo_angli_veneer": ("freijo", 1.0),
    "Madeira_Freijo_vertical": ("freijo_v", 1.0),
    "Piso_Madeira_wood_floor": ("piso", 1.70),
    "Tecido_Edredom_poly_wool": ("edredom", 0.27),
    "Tecido_Manta_caramelo": ("manta", 0.27),
}
REMOVER = ("Teto", "Ventilador_", "Plafon_faixa", "Persiana_externa_caixa", "Banheiro_fechamento", "Banheiro_piso",
           "Portal_", "Sol_", "L1_Luz", "L2_Luz", "L3_Luz", "L4_Luz", "L5_Luz", "L6_Luz", "L7_Luz", "Luz_", "REF_", "COTA_", "CAM_")

for ob in list(bpy.data.objects):
    if ob.name.startswith(REMOVER):
        bpy.data.objects.remove(ob, do_unlink=True)


def uv_caixa(ob, tile):
    """UV por projeção em caixa, em metros reais (tile = tamanho real da textura)."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    mw = ob.matrix_world
    for f in bm.faces:
        n = (mw.to_3x3() @ f.normal)
        ax = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            w = mw @ lp.vert.co
            a, b = [(w.y, w.z), (w.x, w.z), (w.x, w.y)][ax]
            lp[uv].uv = (a / tile, b / tile)
    bm.to_mesh(me)
    bm.free()


def simples(mat, cor=None, rough=None, emit=None, estr=None):
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    keep = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    manter = {out.name, keep.name if keep else ""}
    for n in list(nt.nodes):
        if n.name not in manter:      # compara por nome: os wrappers do bpy não são o mesmo objeto Python
            nt.nodes.remove(n)
    if keep is None:
        keep = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(keep.outputs["BSDF"], out.inputs["Surface"])
    if cor:
        keep.inputs["Base Color"].default_value = cor
    if rough is not None:
        keep.inputs["Roughness"].default_value = rough
    if emit:
        keep.inputs["Emission Color"].default_value = emit
        keep.inputs["Emission Strength"].default_value = estr
    return keep


def texturizado(mat, chave):
    nt = mat.node_tree
    b = simples(mat)
    for kind, inp, nc in (("diff", "Base Color", False), ("rough", "Roughness", True), ("nor", None, True)):
        im = nt.nodes.new("ShaderNodeTexImage")
        im.image = bpy.data.images.load(str(TEX / f"{chave}_{kind}.jpg"))
        if nc:
            im.image.colorspace_settings.name = "Non-Color"
        if inp:
            nt.links.new(im.outputs["Color"], b.inputs[inp])
        else:
            nm = nt.nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = 0.5
            nt.links.new(im.outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])


for mat in bpy.data.materials:
    if not mat.node_tree:
        continue
    nomes = [n.type for n in mat.node_tree.nodes]
    if mat.name in TEXTURAS:
        texturizado(mat, TEXTURAS[mat.name][0])
    elif "EMISSION" in nomes:          # LEDs e lâmpadas → emissivo
        em = next(n for n in mat.node_tree.nodes if n.type == "EMISSION")
        c = tuple(em.inputs["Color"].default_value)
        simples(mat, cor=(0, 0, 0, 1), emit=c, estr=6.0)
    elif mat.name == "Tela_Monitor":
        simples(mat, cor=(0.01, 0.01, 0.012, 1), emit=(0.30, 0.22, 0.34, 1), estr=1.5)
    else:                              # tintas e cores lisas: remove ruído/bump
        simples(mat)

for ob in bpy.data.objects:
    if ob.type != "MESH" or not ob.data.materials:
        continue
    m = ob.data.materials[0]
    if m and m.name in TEXTURAS:
        uv_caixa(ob, TEXTURAS[m.name][1])

bpy.ops.export_scene.gltf(filepath=str(SAIDA), export_format="GLB", export_apply=True, export_yup=True,
                          export_lights=False, export_cameras=False, export_image_format="JPEG",
                          export_jpeg_quality=82)
print("GLB", SAIDA, round(SAIDA.stat().st_size / 1e6, 2), "MB")
