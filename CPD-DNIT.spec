# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('checks', 'checks'), ('scripts', 'scripts'), ('figs', 'figs'), ('templates', 'templates')],
    # O Chroma resolve o backend e a telemetria por strings em tempo de
    # execucao. Por isso o PyInstaller nao os descobre pela analise estatica.
    hiddenimports=[
        'chromadb.api.rust',
        'chromadb_rust_bindings',
        'chromadb.telemetry.product.posthog',
    ],
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
    name='CPD-DNIT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['figs\\logo_icone.ico'],
)
