"""Converte um .glb em glTF JSON autocontido (buffer em data URI base64).

O Blender 5 não exporta mais "glTF Embedded"; a página web só pode servir .json.
Uso: python3 glb_para_json.py entrada.glb saida.json
"""
import base64
import json
import struct
import sys

src, dst = sys.argv[1], sys.argv[2]
data = open(src, "rb").read()
magic, versao, total = struct.unpack_from("<4sII", data, 0)
assert magic == b"glTF" and versao == 2, "não é um GLB 2.0"
off, gltf, binario = 12, None, b""
while off < total:
    tam, tipo = struct.unpack_from("<I4s", data, off)
    bloco = data[off + 8: off + 8 + tam]
    if tipo == b"JSON":
        gltf = json.loads(bloco)
    elif tipo == b"BIN\x00":
        binario = bloco
    off += 8 + tam
gltf["buffers"][0]["uri"] = "data:application/octet-stream;base64," + base64.b64encode(binario).decode()
json.dump(gltf, open(dst, "w"), separators=(",", ":"))
print(dst, round(len(open(dst, "rb").read()) / 1e6, 2), "MB")
