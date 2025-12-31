"""
测试PyQt5是否正确安装
"""
import sys

print("=" * 50)
print("PyQt5 安装测试")
print("=" * 50)

try:
    print("\n1. 测试导入PyQt5...")
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    print("   ✓ PyQt5导入成功")
except ImportError as e:
    print(f"   ✗ PyQt5导入失败: {e}")
    print("\n解决方案：")
    print("   pip install PyQt5==5.15.10")
    sys.exit(1)

try:
    print("\n2. 测试创建QApplication...")
    app = QApplication(sys.argv)
    print("   ✓ QApplication创建成功")
except Exception as e:
    print(f"   ✗ QApplication创建失败: {e}")
    print("\n这可能是Qt插件问题。")
    print("解决方案：")
    print("   1. 运行 fix_qt_plugin.bat")
    print("   2. 或重新安装: pip install --force-reinstall PyQt5==5.15.10")
    sys.exit(1)

try:
    print("\n3. 测试Qt插件路径...")
    import os
    import PyQt5
    pyqt5_path = os.path.dirname(PyQt5.__file__)
    plugin_path = os.path.join(pyqt5_path, 'Qt5', 'plugins')
    print(f"   PyQt5路径: {pyqt5_path}")
    print(f"   插件路径: {plugin_path}")
    if os.path.exists(plugin_path):
        print("   ✓ 插件目录存在")
        plugins = os.listdir(plugin_path)
        print(f"   找到 {len(plugins)} 个插件目录")
        if 'platforms' in plugins:
            platforms_path = os.path.join(plugin_path, 'platforms')
            platforms = os.listdir(platforms_path)
            print(f"   ✓ platforms插件目录存在，包含 {len(platforms)} 个文件")
        else:
            print("   ✗ 缺少platforms插件目录")
    else:
        print("   ✗ 插件目录不存在")
except Exception as e:
    print(f"   ⚠ 检查插件路径时出错: {e}")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
print("\n如果所有测试都通过，但程序仍无法启动，")
print("请尝试：")
print("  1. 重新安装PyQt5: pip install --force-reinstall PyQt5==5.15.10")
print("  2. 检查虚拟环境是否正确激活")
print("  3. 尝试在系统Python环境中运行")

