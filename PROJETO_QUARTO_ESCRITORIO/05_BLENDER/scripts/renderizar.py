"""Renderiza as vistas da Suíte 01 a partir de quarto_escritorio.blend (sem alterar o arquivo salvo).

Uso:
    blender -b quarto_escritorio.blend --python renderizar.py -- [--teste] [--so nome1,nome2]
--teste: 50% da resolução e 48 amostras, saída em 06_RENDERS/_teste/
--amostras N: troca as 256 amostras do render final (para máquinas sem GPU, ex.: 96)
"""
import math
import sys
from pathlib import Path

import bpy

PROJ = Path(bpy.data.filepath).resolve().parents[1]
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
TESTE = "--teste" in ARGS
SO = ARGS[ARGS.index("--so") + 1].split(",") if "--so" in ARGS else None
AMOSTRAS = int(ARGS[ARGS.index("--amostras") + 1]) if "--amostras" in ARGS else 256
OUT = PROJ / "06_RENDERS" / ("_teste" if TESTE else "")

LUZES_INTERNAS = ["L1_Luz_prateleira", "L2_Luz_vertical", "L3_Luz_barra_monitor", "L4_Luz_arandela",
                  "Luz_Ventilador_3000K", "Luz_Plafon_faixa", "L5_Luz_nicho_1", "L5_Luz_nicho_2", "L5_Luz_nicho_3",
                  "L6_Luz_luminaria_mesa"]
EMISSORES = ["LED_3000K", "Lampada_3000K", "LED_Barra_Monitor_4000K"]
SEM_TETO = ["Teto", "Ventilador_", "Plafon_faixa"]
CORTE_ISO = SEM_TETO + ["Parede_Fundo_Armario", "Armario_existente", "Parede_Leste", "Banheiro_", "Parede_C",
                        "Porta_", "Rodape_Banheiro", "Rodape_Parede_C", "ArCondicionado", "Parede_E_trecho_ED"]

VISTAS = [
    # nome do arquivo, câmera, modo, objetos ocultos (prefixos)
    ("vista_superior", "CAM_vista_superior", "dia", SEM_TETO),
    ("vista_isometrica", "CAM_vista_isometrica", "dia", CORTE_ISO),
    ("area_trabalho", "CAM_area_trabalho", "noite", []),
    ("area_descanso", "CAM_area_descanso", "dia", []),
    ("vista_entrada", "CAM_entrada", "dia", []),
    ("marcenaria_ripado", "CAM_marcenaria_ripado", "noite", []),
    ("iluminacao_dia", "CAM_principal", "dia", []),
    ("iluminacao_noite", "CAM_principal", "noite", []),
]


def gpu():
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
        except TypeError:
            continue
        devs = [d for d in prefs.devices if d.type == tipo]
        if devs:
            for d in prefs.devices:
                d.use = d.type in (tipo,)
            bpy.context.scene.cycles.device = "GPU"
            return tipo, [d.name for d in devs]
    bpy.context.scene.cycles.device = "CPU"
    return "CPU", []


def modo(m):
    sc = bpy.context.scene
    noite = m == "noite"
    for n in LUZES_INTERNAS:
        bpy.data.objects[n].hide_render = not noite
    for n in EMISSORES:
        if n not in bpy.data.materials:
            continue
        em = [x for x in bpy.data.materials[n].node_tree.nodes if x.type == "EMISSION"][0]
        em.inputs["Strength"].default_value = (8.0 if "LED_3000" in n else 6.0 if "Lampada" in n else 4.0) if noite else 0.0
    for tela in bpy.data.materials:                 # telas (monitores e notebook): mais fortes de dia
        if "emissao_noite" in tela:
            b = next(x for x in tela.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
            b.inputs["Emission Strength"].default_value = tela["emissao_noite"] if noite else tela["emissao_dia"]
    bpy.data.objects["Sol_Manha_Leste"].hide_render = noite
    env = sc.world.node_tree.nodes["HDRI"]
    env.image = bpy.data.images[("modern_buildings_night_2k.hdr" if noite else "modern_buildings_2_2k.hdr")]
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35 if noite else 1.0
    per = bpy.data.objects["Persiana_externa_laminas"]
    z1 = 1.00 + 1.20
    if noite:   # persiana baixada até ~35 cm do peitoril
        per.scale.z = 1.0
        per.location.z = 1.00 + 0.35
        per.dimensions = (per.dimensions.x, per.dimensions.y, z1 - (1.00 + 0.35))
    else:
        per.location.z = z1 - 0.12
        per.scale = (1, 1, 1)
    sc.view_settings.exposure = 0.6 if noite else 1.7


def ocultar(prefixos):
    for ob in bpy.data.objects:
        if ob.type in ("CAMERA",):
            continue
        base = ob.get("_hide_base", ob.hide_render)
        ob["_hide_base"] = base
        ob.hide_render = base or any(ob.name.startswith(p) for p in prefixos)


def main():
    sc = bpy.context.scene
    tipo, devs = gpu()
    print("DISPOSITIVO", tipo, devs)
    if TESTE:
        sc.render.resolution_percentage, sc.cycles.samples = 50, 48
    else:
        sc.render.resolution_percentage, sc.cycles.samples = 100, AMOSTRAS
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, cam, m, ocultos in VISTAS:
        if SO and nome not in SO:
            continue
        # base: todas as luzes internas controladas por modo(); restaura ocultação antes de aplicar a da vista
        for ob in bpy.data.objects:
            if "_hide_base" in ob:
                ob.hide_render = ob["_hide_base"]
        modo(m)
        for ob in bpy.data.objects:
            ob["_hide_base"] = ob.hide_render
        ocultar(ocultos)
        sc.camera = bpy.data.objects[cam]
        sc.render.filepath = str(OUT / f"{nome}.png")
        bpy.ops.render.render(write_still=True)
        print("RENDER", nome, cam, m)
        for ob in bpy.data.objects:
            if "_hide_base" in ob:
                ob.hide_render = ob["_hide_base"]
                del ob["_hide_base"]


if __name__ == "__main__":
    main()
