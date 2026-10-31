"""Renderiza os panoramas 360° (equirretangulares) do tour virtual.

Uso: blender -b quarto_escritorio_realista.blend --python renderizar_360.py -- [--teste] [--so PANO_a,PANO_b] [--modos dia,noite]
Saída: 06_RENDERS/360/<ponto>_<modo>.jpg  (teste: 06_RENDERS/360/_teste/)
"""
import sys
from pathlib import Path

import bpy

PROJ = Path(bpy.data.filepath).resolve().parents[1]
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
TESTE = "--teste" in ARGS
SO = ARGS[ARGS.index("--so") + 1].split(",") if "--so" in ARGS else None
MODOS = ARGS[ARGS.index("--modos") + 1].split(",") if "--modos" in ARGS else ["dia", "noite"]
OUT = PROJ / "06_RENDERS" / "360" / ("_teste" if TESTE else "")

LUZES = ["L1_Luz_prateleira", "L2_Luz_vertical", "L3_Luz_barra_monitor", "L4_Luz_arandela", "Luz_Ventilador_3000K",
         "Luz_Plafon_faixa"]
EMISSORES = {"LED_3000K": 8.0, "Lampada_3000K": 6.0, "LED_Barra_Monitor_4000K": 4.0}
# no ponto da mesa a pessoa está sentada na cadeira: a cadeira some da vista
OCULTAR = {"PANO_mesa": ("Cadeira_",)}


def gpu():
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
        except TypeError:
            continue
        if any(d.type == tipo for d in prefs.devices):
            for d in prefs.devices:
                d.use = d.type == tipo
            bpy.context.scene.cycles.device = "GPU"
            return tipo
    bpy.context.scene.cycles.device = "CPU"
    return "CPU"


def modo(m):
    sc = bpy.context.scene
    noite = m == "noite"
    for n in LUZES:
        if n in bpy.data.objects:
            bpy.data.objects[n].hide_render = not noite
    for n, forca in EMISSORES.items():
        if n in bpy.data.materials:
            em = next(x for x in bpy.data.materials[n].node_tree.nodes if x.type == "EMISSION")
            em.inputs["Strength"].default_value = forca if noite else 0.0
    tela = bpy.data.materials["Tela_Monitor"]
    b = next(x for x in tela.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    b.inputs["Emission Strength"].default_value = tela.get("emissao_noite", 0.9) if noite else tela.get("emissao_dia", 1.6)
    bpy.data.objects["Sol_Manha_Leste"].hide_render = noite
    env = sc.world.node_tree.nodes["HDRI"]
    env.image = bpy.data.images["modern_buildings_night_2k.hdr" if noite else "modern_buildings_2_2k.hdr"]
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35 if noite else 1.0
    per = bpy.data.objects["Persiana_externa_laminas"]
    per.scale = (1, 1, 1)
    if noite:
        per.location.z = 1.35
        per.dimensions = (per.dimensions.x, per.dimensions.y, 2.20 - 1.35)
    else:
        per.location.z = 2.20 - 0.12
    sc.view_settings.exposure = 0.7 if noite else 1.7


def main():
    sc = bpy.context.scene
    print("DISPOSITIVO", gpu())
    sc.render.resolution_x, sc.render.resolution_y = (1024, 512) if TESTE else (4096, 2048)
    sc.render.resolution_percentage = 100
    sc.cycles.samples = 40 if TESTE else 160
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 86
    OUT.mkdir(parents=True, exist_ok=True)
    panos = [o for o in bpy.data.objects if o.name.startswith("PANO_") and (not SO or o.name in SO)]
    base = {o.name: o.hide_render for o in bpy.data.objects}
    for cam in panos:
        for m in MODOS:
            for o in bpy.data.objects:
                o.hide_render = base[o.name]
            modo(m)
            for o in bpy.data.objects:
                if o.name.startswith(OCULTAR.get(cam.name, ("\0",))):
                    o.hide_render = True
            sc.camera = cam
            nome = f"{cam.name.replace('PANO_', '')}_{m}"
            sc.render.filepath = str(OUT / f"{nome}.jpg")
            bpy.ops.render.render(write_still=True)
            print("PANO", nome)


main()
