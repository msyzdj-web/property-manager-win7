# Windows 7 打包快速指南

## 🚀 快速开始（3 步完成）

### 方式一：使用 GitHub Actions（推荐，无需 Windows 环境）

#### 步骤 1：准备 GitHub 仓库

如果你还没有 GitHub 仓库：

```bash
# 初始化 git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "添加 Windows 7 兼容打包配置"

# 在 GitHub 上创建新仓库，然后：
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

#### 步骤 2：触发 GitHub Actions 打包

1. 打开浏览器，访问你的 GitHub 仓库
2. 点击顶部的 **"Actions"** 标签页
3. 在左侧工作流列表中找到 **"Build Windows 7 Compatible EXE"**
4. 点击右侧的 **"Run workflow"** 按钮
5. 选择分支（通常是 `main`），然后点击绿色的 **"Run workflow"** 按钮

#### 步骤 3：下载打包结果

1. 等待打包完成（通常需要 5-10 分钟）
2. 打包完成后，在 Actions 页面找到对应的运行记录
3. 滚动到页面底部，在 **"Artifacts"** 部分下载 `PropertyManager-Win7-EXE`
4. 解压下载的文件，即可得到 `物业收费管理系统_Win7.exe`

---

### 方式二：本地打包（需要 Windows 环境）

#### 前提条件

- Windows 7 SP1 或 Windows 10/11
- Python 3.8.10（[下载地址](https://www.python.org/downloads/release/python-3810/)）

#### 步骤 1：安装 Python 3.8.10

1. 从 [Python 官网](https://www.python.org/downloads/release/python-3810/) 下载 Python 3.8.10
2. 安装时勾选 "Add Python to PATH"
3. 验证安装：打开命令提示符，运行 `python --version`，应显示 `Python 3.8.10`

#### 步骤 2：安装依赖并打包

```bash
# 安装依赖
pip install -r requirements-win7.txt

# 执行打包脚本
build-win7.bat
```

#### 步骤 3：获取打包结果

打包完成后，exe 文件位于：`dist\物业收费管理系统_Win7.exe`

---

## 📋 打包前检查清单

在打包前，请确认：

- [ ] 所有代码已保存
- [ ] `requirements-win7.txt` 文件存在
- [ ] `PropertyManager-win7.spec` 文件存在
- [ ] `build-win7.bat` 文件存在（本地打包需要）
- [ ] `.github/workflows/build-win7.yml` 文件存在（GitHub Actions 需要）

---

## 🔍 验证打包结果

### 在 Windows 7 上测试

1. **系统要求检查**
   - ✅ Windows 7 SP1
   - ✅ 已安装 Visual C++ Redistributable 2015-2022
   - ✅ 至少 100MB 可用空间

2. **功能测试**
   - [ ] 双击 exe 文件，程序正常启动
   - [ ] 创建新住户
   - [ ] 添加收费项目
   - [ ] 生成账单
   - [ ] 标记缴费
   - [ ] 打印收据
   - [ ] 导出 Excel

---

## ❓ 常见问题

### Q: GitHub Actions 打包失败怎么办？

**检查点：**
1. 查看 Actions 日志，找到错误信息
2. 确认所有文件都已提交到仓库
3. 检查 `requirements-win7.txt` 中的依赖版本是否正确

**常见错误：**
- `找不到 requirements-win7.txt`：确保文件已提交到仓库根目录
- `PyInstaller 版本错误`：检查 `requirements-win7.txt` 中是否为 `pyinstaller==4.10`

### Q: 本地打包时提示 Python 版本不对？

**解决方案：**
- 确保使用 Python 3.8.10
- 如果安装了多个 Python 版本，使用完整路径：
  ```bash
  C:\Python38\python.exe -m pip install -r requirements-win7.txt
  C:\Python38\Scripts\pyinstaller.exe --clean PropertyManager-win7.spec
  ```

### Q: 打包后的 exe 在 Windows 7 上无法运行？

**可能原因和解决方案：**
1. **缺少 Visual C++ Redistributable**
   - 下载安装：https://aka.ms/vs/17/release/vc_redist.x64.exe

2. **Windows 7 版本过低**
   - 确保已安装 Windows 7 SP1

3. **杀毒软件拦截**
   - 将 exe 添加到杀毒软件白名单

4. **首次运行慢**
   - 这是正常现象，PyInstaller 需要解压文件，后续运行会快很多

---

## 📞 获取帮助

如果遇到问题：

1. 查看详细文档：`文档/Windows7打包说明.md`
2. 检查 GitHub Actions 日志（如果使用 GitHub Actions）
3. 在 Windows 7 上运行 exe 时，如果有错误，查看错误提示信息

---

## ✅ 成功标志

打包成功的标志：

- ✅ GitHub Actions 显示绿色 ✓
- ✅ 能够下载 Artifacts
- ✅ exe 文件大小约 50-100MB
- ✅ 在 Windows 7 上能够正常启动和运行

---

**祝你打包顺利！** 🎉

