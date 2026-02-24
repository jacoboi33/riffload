import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PyQt6.sip',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtNetwork',
        'libtorrent',
        'bs4',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'requests',
        'xml.etree.ElementTree',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='riffload',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/logo.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='riffload',
)

# macOS: wrap in a .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Riffload.app',
        icon='assets/logo.icns',
        bundle_identifier='com.riffload.app',
        info_plist={
            'CFBundleName': 'Riffload',
            'CFBundleDisplayName': 'Riffload',
            'CFBundleShortVersionString': '0.1.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # supports dark mode
        },
    )
