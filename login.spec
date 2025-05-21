# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

from PyInstaller.utils.hooks import collect_submodules
from glob import glob
import os

# Recolectar imágenes
image_files = [(os.path.join('imagenes', f), 'imagenes') for f in os.listdir('imagenes') if f.endswith('.png')]
image_files += [(os.path.join('imagenes', 'panes', f), 'imagenes/panes') for f in os.listdir(os.path.join('imagenes', 'panes')) if f.endswith('.png')]

a = Analysis(
    ['login.py'],
    pathex=[],
    binaries=[],
    datas=image_files,
    hiddenimports=['mysql', 'mysql.connector'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # <- necesario para onefile
    name='login',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # <- esto es lo mismo que --windowed
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='login'
)
