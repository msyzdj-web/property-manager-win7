# -*- mode: python ; coding: utf-8 -*-
# Windows 7 兼容打包配置
# 使用 PyInstaller 4.10，关闭 UPX 压缩以提高 Windows 7 兼容性

from PyInstaller.utils.hooks import collect_all
import os

# application-specific runtime tmpdir to avoid using system %TEMP%
# use %LOCALAPPDATA%\PropertyManager\MEI
app_runtime_tmpdir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser("~")), "PropertyManager", "MEI")
if not os.path.exists(app_runtime_tmpdir):
    try:
        os.makedirs(app_runtime_tmpdir, exist_ok=True)
    except Exception:
        app_runtime_tmpdir = None

datas = [('logo.jpg', '.')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# 收集 PyQt5 相关文件
try:
    pyqt5_ret = collect_all('PyQt5')
    datas += pyqt5_ret[0]
    binaries += pyqt5_ret[1]
    hiddenimports += pyqt5_ret[2]
except:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PropertyManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 关闭 UPX 压缩，提高 Windows 7 兼容性
    upx_exclude=[],
    runtime_tmpdir=app_runtime_tmpdir,
    console=False,  # GUI 模式
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='PropertyManager'
)

