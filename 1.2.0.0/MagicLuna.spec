# -*- mode: python ; coding: utf-8 -*-
#
# Gera "dist/Magic Luna - Image Converter.exe" com icone da lua, metadados e suporte a PDF.
# Uso:  python -m PyInstaller MagicLuna.spec
#
# Deixe na MESMA pasta: este arquivo, magicluna.py, magic-luna.ico e version_info.txt

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []

# customtkinter (temas) e pypdfium2 (ler PDF)
for pacote in ('customtkinter', 'pypdfium2', 'pypdfium2_raw'):
    try:
        d, b, h = collect_all(pacote)
    except Exception:
        continue  # pacote nao instalado: o programa ja trata a ausencia
    datas += d
    binaries += b
    hiddenimports += h


a = Analysis(
    ['magicluna.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Magic Luna - Image Converter',
    icon=['magic-luna.ico'],
    version='version_info.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
