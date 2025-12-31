# Python 3.8.10 安装指南

## 📋 当前状态

- **当前 Python 版本**: Python 3.10.9
- **目标版本**: Python 3.8.10（Windows 7 兼容）

## 🎯 安装方式

### 方式一：与现有 Python 3.10 共存（推荐）

这样可以保留 Python 3.10 用于开发，同时使用 Python 3.8.10 进行 Windows 7 打包。

---

## 📥 下载 Python 3.8.10

### 官方下载链接

**Windows 64位安装包：**
- 直接下载：https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
- 官方页面：https://www.python.org/downloads/release/python-3810/

**Windows 32位安装包（如果系统是32位）：**
- 直接下载：https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe
- 官方页面：https://www.python.org/downloads/release/python-3810/

### 选择哪个版本？

- **64位系统**：下载 `python-3.8.10-amd64.exe`
- **32位系统**：下载 `python-3.8.10.exe`

查看系统位数：
```powershell
# 在 PowerShell 中运行
[System.Environment]::Is64BitOperatingSystem
```

---

## 🔧 安装步骤

### 步骤 1：下载安装包

1. 访问 https://www.python.org/downloads/release/python-3810/
2. 滚动到 "Files" 部分
3. 下载适合你系统的安装包（通常是 `Windows installer (64-bit)`）

### 步骤 2：运行安装程序

1. **双击下载的 `.exe` 文件**

2. **重要：勾选以下选项**
   - ✅ **"Add Python 3.8 to PATH"** （添加到系统路径）
   - ✅ **"Install for all users"** （可选，推荐）

3. **选择安装类型**
   - 选择 **"Customize installation"**（自定义安装）
   - 或者直接点击 **"Install Now"**（快速安装）

4. **如果选择自定义安装，确保勾选：**
   - ✅ pip
   - ✅ tcl/tk and IDLE
   - ✅ Python test suite
   - ✅ py launcher
   - ✅ for all users（可选）

5. **选择安装位置**（可选）
   - 默认：`C:\Program Files\Python38\`
   - 建议保持默认，或安装到：`C:\Python38\`

6. **点击 "Install" 开始安装**

7. **等待安装完成**

### 步骤 3：验证安装

安装完成后，打开**新的**命令提示符或 PowerShell，运行：

```powershell
# 检查 Python 3.8 是否安装
py -3.8 --version

# 应该显示：Python 3.8.10
```

---

## 🔀 使用 Python 3.8.10

### 方法 1：使用 py launcher（推荐）

Windows 的 `py` launcher 可以让你选择使用哪个 Python 版本：

```powershell
# 使用 Python 3.8
py -3.8 --version
py -3.8 -m pip install -r requirements-win7.txt

# 使用 Python 3.10（默认）
py --version
python --version
```

### 方法 2：创建虚拟环境

为 Windows 7 打包创建独立的虚拟环境：

```powershell
# 使用 Python 3.8 创建虚拟环境
py -3.8 -m venv venv-win7

# 激活虚拟环境
.\venv-win7\Scripts\Activate.ps1

# 如果遇到执行策略错误，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 验证 Python 版本
python --version  # 应该显示 Python 3.8.10

# 安装依赖
pip install -r requirements-win7.txt

# 执行打包
build-win7.bat
```

### 方法 3：直接指定路径

如果安装到了自定义路径，可以直接使用完整路径：

```powershell
# 假设安装到 C:\Python38\
C:\Python38\python.exe --version
C:\Python38\python.exe -m pip install -r requirements-win7.txt
```

---

## ✅ 安装后验证清单

- [ ] Python 3.8.10 已安装
- [ ] 可以使用 `py -3.8 --version` 查看版本
- [ ] 可以创建虚拟环境
- [ ] 可以安装 pip 包

### 验证命令

```powershell
# 1. 检查 Python 3.8 版本
py -3.8 --version

# 2. 检查 pip
py -3.8 -m pip --version

# 3. 列出所有已安装的 Python 版本
py --list

# 4. 测试安装包
py -3.8 -m pip install --upgrade pip
```

---

## 🚀 下一步：安装依赖并打包

安装完 Python 3.8.10 后：

### 选项 A：使用虚拟环境（推荐）

```powershell
# 1. 创建虚拟环境
py -3.8 -m venv venv-win7

# 2. 激活虚拟环境
.\venv-win7\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements-win7.txt

# 4. 执行打包
build-win7.bat
```

### 选项 B：直接使用 Python 3.8

```powershell
# 1. 安装依赖
py -3.8 -m pip install -r requirements-win7.txt

# 2. 修改 build-win7.bat，使用 py -3.8
# 或者直接运行：
py -3.8 -m PyInstaller --clean PropertyManager-win7.spec
```

---

## ⚠️ 常见问题

### Q1: 安装后 `python --version` 还是显示 3.10

**原因**：系统 PATH 中 Python 3.10 的路径在 Python 3.8 之前。

**解决方案**：
- 使用 `py -3.8` 而不是 `python`
- 或者在虚拟环境中使用（推荐）

### Q2: 提示 "py 不是内部或外部命令"

**原因**：py launcher 未安装或未添加到 PATH。

**解决方案**：
1. 重新安装 Python 3.8.10，确保勾选 "py launcher"
2. 或者直接使用完整路径：`C:\Python38\python.exe`

### Q3: 无法创建虚拟环境

**错误信息**：`python: No module named venv`

**解决方案**：
```powershell
# 确保使用正确的 Python 版本
py -3.8 -m venv venv-win7
```

### Q4: PowerShell 执行策略错误

**错误信息**：`无法加载文件，因为在此系统上禁止运行脚本`

**解决方案**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新运行激活脚本。

---

## 📝 快速参考

### 常用命令

```powershell
# 查看所有 Python 版本
py --list

# 使用 Python 3.8
py -3.8 <命令>

# 创建虚拟环境
py -3.8 -m venv venv-win7

# 激活虚拟环境（PowerShell）
.\venv-win7\Scripts\Activate.ps1

# 激活虚拟环境（CMD）
venv-win7\Scripts\activate.bat

# 安装依赖
pip install -r requirements-win7.txt

# 执行打包
build-win7.bat
```

---

## 🎉 完成标志

安装成功的标志：

- ✅ `py -3.8 --version` 显示 `Python 3.8.10`
- ✅ 可以创建虚拟环境
- ✅ 可以安装 pip 包
- ✅ 可以执行打包脚本

**安装完成后，就可以开始 Windows 7 打包了！** 🚀

