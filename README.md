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
## 发布与启动器（防止 PyInstaller 解包弹窗）

建议在发布包中包含 `tools/launcher_win7.bat` 并将其作为推荐的启动入口。launcher 会为每次运行创建独立临时目录、预清理旧的 `_MEI*` 解包目录并在检测到冲突时等待/重试，从而显著降低因杀软扫描导致的“file already exists”弹窗概率。

发布时请务必包含以下说明给终端用户（管理员权限）：

- **以 launcher 启动（推荐）**：双击 `tools/launcher_win7.bat`（或右键以管理员身份运行）启动程序，launcher 会自动在临时目录中复制 exe 并运行，减少解包冲突。
- **添加 Windows Defender 排除（可选但强烈推荐）**：以管理员 PowerShell 运行：
  ```powershell
  # 将应用专用 runtime_tmpdir 加入排除（推荐）
  Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\PropertyManager\MEI"

  # 或排除系统临时目录（更宽泛）
  Add-MpPreference -ExclusionPath $env:TEMP
  ```
  如果 PowerShell 因策略被限制，请在“Windows 安全”→“病毒与威胁防护”→“管理设置”→“排除项”中手动添加上述目录。

- **打包时使用 application-specific runtime_tmpdir（已在 spec 中设置）**：本仓库的 `PropertyManager.spec` 与 `PropertyManager-win7.spec` 已设置 `runtime_tmpdir` 指向 `%LOCALAPPDATA%\PropertyManager\MEI`，请使用这些 spec 打包以减少冲突：
  ```bash
  pyinstaller PropertyManager-win7.spec
  ```

- **测试建议**：在干净的 Windows（开启 Defender）环境下用 launcher 测试 10 次以上，或并发启动多个实例以确认稳定性。

注意：即使采取所有缓解措施，也无法 100% 排除在某些严格或受限环境（企业组策略或第三方杀软）出现弹窗的可能性；因此建议同时使用 launcher 与 Defender 排除作为最佳实践。

（更多详细打包/发布步骤见 `RELEASE_INSTRUCTIONS.md`）
