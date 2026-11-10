"""Lista os icones embutidos em um .exe.
Uso: python verificar_icones.py dist\\MagicLuna.exe
"""
import struct
import sys


def icones_do_exe(caminho):
    d = open(caminho, "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    optsz = struct.unpack_from("<H", d, pe + 20)[0]
    magic = struct.unpack_from("<H", d, pe + 24)[0]
    dd = pe + 24 + (112 if magic == 0x20B else 96)
    rsrc_rva = struct.unpack_from("<II", d, dd + 16)[0]
    secoes = []
    for i in range(nsec):
        _, vs, va, rs, ro = struct.unpack_from("<8sIIII", d, pe + 24 + optsz + 40 * i)
        secoes.append((va, max(vs, rs), ro))

    def rva_para_offset(rva):
        for va, tam, ro in secoes:
            if va <= rva < va + tam:
                return rva - va + ro

    base = rva_para_offset(rsrc_rva)

    def entradas(off):
        n = struct.unpack_from("<H", d, off + 12)[0] + struct.unpack_from("<H", d, off + 14)[0]
        return [struct.unpack_from("<II", d, off + 16 + 8 * i) for i in range(n)]

    grupos = []
    for tipo, o in entradas(base):
        if tipo != 14:  # RT_GROUP_ICON
            continue
        for _, o2 in entradas(base + (o & 0x7FFFFFFF)):
            for _, o3 in entradas(base + (o2 & 0x7FFFFFFF)):
                rva, _tam = struct.unpack_from("<II", d, base + o3)
                grupos.append(rva_para_offset(rva))
    resultado = []
    for off in grupos:
        qtd = struct.unpack_from("<H", d, off + 4)[0]
        for i in range(qtd):
            w, h = struct.unpack_from("<BB", d, off + 6 + 14 * i)
            resultado.append((w or 256, h or 256))
    return resultado


if __name__ == "__main__":
    tamanhos = icones_do_exe(sys.argv[1])
    if not tamanhos:
        print("Nenhum icone embutido neste exe.")
    else:
        print(f"{len(tamanhos)} camadas de icone:", ", ".join(f"{w}x{h}" for w, h in tamanhos))
