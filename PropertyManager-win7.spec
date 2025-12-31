# -*- mode: python ; coding: utf-8 -*-
# Windows 7 兼容打包配置
# 使用 PyInstaller 4.10，关闭 UPX 压缩以提高 Windows 7 兼容性

from PyInstaller.utils.hooks import collect_all
import os

# application-specific runtime tmpdir to avoid using system %TEMP%
# Use an environment-variable expression so the runtime tmpdir is resolved
# on the end-user machine (not baked as an absolute path at build time).
# This expands at runtime to %LOCALAPPDATA%\PropertyManager\MEI
app_runtime_tmpdir = os.path.expandvars(r"%LOCALAPPDATA%\\PropertyManager\\MEI")

datas = [('logo.jpg', '.'), ('property.db', '.'), ('logo.ico', '.')]
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

