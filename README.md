# 物业收费管理软件

## 项目简介
本地运行的物业收费管理系统，用于小型物业场景的住户管理、收费管理、欠费查询和收据打印。

## 技术栈
- Python 3.10+
- PyQt5
- SQLAlchemy
- SQLite

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行程序
```bash
python main.py
```

## 运行测试
项目包含单元测试，使用 pytest 运行：
```bash
# 安装 pytest
pip install pytest

# 运行测试
pytest tests/
```

## 打包为exe

### 标准打包（Windows 10/11）
```bash
# 使用标准依赖
pip install -r requirements.txt
build.bat
```

### Windows 7 兼容打包

本项目支持 Windows 7 兼容打包，确保打包后的 exe 可以在 Windows 7 SP1 系统上运行。

**方式一：使用 GitHub Actions（推荐，无需 Windows 环境）**
1. 将代码推送到 GitHub 仓库
2. 在 GitHub Actions 中运行 "Build Windows 7 Compatible EXE" 工作流
3. 下载构建产物

详细步骤请参考：[Windows7打包快速指南.md](Windows7打包快速指南.md)

**方式二：本地打包**
```bash
# 使用 Windows 7 兼容依赖
pip install -r requirements-win7.txt
build-win7.bat
```

**Windows 7 打包说明：**
- 使用 Python 3.8.10（最后一个支持 Windows 7 的 Python 版本）
- 使用 PyInstaller 4.10（最后支持 Windows 7 的稳定版）
- 依赖版本已调整为 Windows 7 兼容版本
- 详细文档：[文档/Windows7打包说明.md](文档/Windows7打包说明.md)

## 功能模块
1. **住户管理**：新增、编辑、删除住户，房号唯一性校验
2. **收费项目管理**：支持固定、按面积、手动三种收费类型
3. **收费管理**：生成账单、缴费标记、缴费记录
4. **欠费查询**：按月份查看未缴费清单
5. **收据打印**：打印缴费收据，支持重复打印

## 数据备份
复制 `property.db` 文件即可完成数据备份。

## 注意事项
- 首次运行会自动创建数据库文件
- 房号必须唯一
- 删除住户前请确保没有关联的缴费记录

## 常见问题解决

### 1. Qt平台插件错误
如果遇到 `Could not find the Qt platform plugin "windows"` 错误：

**解决方案：**
```bash
# 方法1：重新安装PyQt5
pip uninstall PyQt5 -y
pip install PyQt5==5.15.10

# 方法2：运行修复脚本
fix_qt_plugin.bat

# 方法3：测试PyQt5安装
python test_qt.py
```

### 2. 生成账单时程序闪退
- 确保已选择住户和收费项目
- 检查控制台错误信息
- 确保数据库文件未被锁定

### 3. 程序无法启动
- 检查Python版本（需要3.10+）
- 检查是否安装了所有依赖
- 运行 `python test_qt.py` 诊断问题

