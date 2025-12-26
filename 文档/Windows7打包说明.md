# Windows 7 兼容打包说明

## 概述

本项目已配置 Windows 7 兼容打包方案，确保打包后的 exe 文件可以在 Windows 7 SP1 系统上正常运行。

## 技术方案

### 版本选择

- **Python**: 3.8.10（最后一个官方支持 Windows 7 的版本）
- **PyInstaller**: 4.10（最后支持 Windows 7 的稳定版）
- **PyQt5**: 5.15.10（保持不变，支持 Windows 7）
- **SQLAlchemy**: 1.4.46（从 2.0.23 降级，兼容 Python 3.8）
- **pandas**: 1.5.3（从 2.0.3 降级，兼容 Python 3.8）
- **openpyxl**: 3.1.2（保持不变）

### 兼容性调整

1. **关闭 UPX 压缩**：在 `PropertyManager-win7.spec` 中设置 `upx=False`，提高 Windows 7 兼容性
2. **使用兼容的 PyInstaller 版本**：4.10 是最后稳定支持 Windows 7 的版本
3. **依赖版本降级**：确保所有依赖都支持 Python 3.8

## 打包方式

### 方式一：使用 GitHub Actions（推荐）

**优点**：
- 无需本地 Windows 环境
- 自动化打包流程
- 可重复执行

**步骤**：
1. 将代码推送到 GitHub 仓库
2. 在 GitHub 上进入 Actions 标签页
3. 选择 "Build Windows 7 Compatible EXE" 工作流
4. 点击 "Run workflow" 手动触发
5. 等待打包完成，下载构建产物

**触发条件**：
- 手动触发（workflow_dispatch）
- 推送到 main/master 分支
- 创建 Release 时自动打包

### 方式二：本地 Windows 环境打包

**前提条件**：
- Windows 7 SP1 或 Windows 10/11（兼容模式）
- Python 3.8.10
- 已安装 Visual C++ Redistributable 2015-2022

**步骤**：
1. 安装 Python 3.8.10
   ```bash
   # 从 Python 官网下载 Python 3.8.10 Windows 安装包
   # https://www.python.org/downloads/release/python-3810/
   ```

2. 创建虚拟环境（可选但推荐）
   ```bash
   python -m venv venv-win7
   venv-win7\Scripts\activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements-win7.txt
   ```

4. 执行打包脚本
   ```bash
   build-win7.bat
   ```

5. 打包完成后，exe 文件位于 `dist\物业收费管理系统_Win7.exe`

### 方式三：使用 Docker（高级）

如果需要在不支持 Windows 的环境中打包，可以使用 Docker：

```bash
# 使用 Windows 容器（需要 Windows 主机）
docker run -it --rm -v ${PWD}:/workspace mcr.microsoft.com/windows/servercore:ltsc2019
```

## 代码兼容性

### SQLAlchemy 兼容性

项目代码已使用 SQLAlchemy 1.4 兼容的语法：
- 使用 `db.query()` 而不是 `select()`
- 使用 `sessionmaker` 和 `Session`
- 所有数据库操作都兼容 SQLAlchemy 1.4.46

**无需修改代码**，直接使用 `requirements-win7.txt` 即可。

### Python 特性兼容性

代码未使用 Python 3.9+ 的特性：
- ✅ 无字典合并操作符 `|`
- ✅ 无 walrus 操作符 `:=`
- ✅ 无 match-case 语句
- ✅ 所有特性都兼容 Python 3.8

## 测试建议

### 在 Windows 7 上测试

1. **系统要求检查**
   - Windows 7 SP1
   - 已安装 Visual C++ Redistributable 2015-2022
   - 至少 100MB 可用磁盘空间

2. **功能测试清单**
   - [ ] 程序正常启动
   - [ ] 创建数据库文件
   - [ ] 添加住户功能
   - [ ] 添加收费项目功能
   - [ ] 生成账单功能
   - [ ] 标记缴费功能
   - [ ] 打印收据功能
   - [ ] 导出 Excel 功能
   - [ ] 数据备份功能

3. **性能测试**
   - 首次启动时间（应在 30 秒内）
   - 界面响应速度
   - 大数据量操作（100+ 住户，1000+ 缴费记录）

## 常见问题

### Q1: 打包后的 exe 在 Windows 7 上无法运行

**可能原因**：
1. 缺少 Visual C++ Redistributable
2. Windows 7 版本过低（需要 SP1）
3. 杀毒软件拦截

**解决方案**：
1. 安装 Visual C++ Redistributable 2015-2022
2. 确保 Windows 7 已安装 SP1
3. 将 exe 添加到杀毒软件白名单

### Q2: 首次运行很慢

**原因**：PyInstaller 打包的 exe 首次运行需要解压到临时目录

**解决方案**：这是正常现象，后续运行会快很多

### Q3: 提示缺少 DLL

**解决方案**：
1. 安装 Visual C++ Redistributable 2015-2022
2. 检查是否使用了正确的打包配置（`PropertyManager-win7.spec`）

### Q4: 数据库文件找不到

**原因**：打包后的 exe 运行路径可能不同

**解决方案**：程序已使用 `utils/path_utils.py` 处理路径问题，确保数据库文件与 exe 在同一目录

## 文件说明

- `requirements-win7.txt`: Windows 7 兼容的依赖版本
- `build-win7.bat`: Windows 7 打包脚本
- `PropertyManager-win7.spec`: Windows 7 专用 PyInstaller 配置
- `.github/workflows/build-win7.yml`: GitHub Actions 自动化打包配置

## 维护建议

1. **定期测试**：在 Windows 7 虚拟机中定期测试打包结果
2. **依赖更新**：谨慎更新依赖，确保兼容 Windows 7
3. **文档更新**：如有问题或改进，及时更新本文档

## 技术支持

如遇到问题，请检查：
1. Python 版本是否为 3.8.x
2. 依赖版本是否与 `requirements-win7.txt` 一致
3. 打包配置是否使用了 `PropertyManager-win7.spec`
4. Windows 7 系统是否满足要求

