# GitHub Actions 自动打包指南

## 🎯 为什么使用 GitHub Actions？

由于本地网络问题无法安装依赖，**使用 GitHub Actions 是最佳选择**：

✅ **无需解决网络问题** - GitHub 服务器网络稳定  
✅ **自动化流程** - 一键触发，自动打包  
✅ **可重复执行** - 随时可以重新打包  
✅ **结果可靠** - 使用标准化的构建环境  

---

## 📋 准备工作

### 1. 检查 Git 仓库状态

确保项目已初始化为 Git 仓库：

```bash
# 检查 Git 状态
git status

# 如果未初始化，运行：
git init
```

### 2. 检查文件完整性

确保以下文件已创建：

- ✅ `requirements-win7.txt`
- ✅ `PropertyManager-win7.spec`
- ✅ `build-win7.bat`
- ✅ `.github/workflows/build-win7.yml`
- ✅ `main.py`
- ✅ 所有项目源代码文件

---

## 🚀 使用步骤

### 步骤 1：提交所有文件到 Git

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "添加 Windows 7 兼容打包配置"
```

**如果遇到问题：**

```bash
# 如果提示需要配置用户信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 然后重新提交
git add .
git commit -m "添加 Windows 7 兼容打包配置"
```

### 步骤 2：创建 GitHub 仓库

1. **登录 GitHub**
   - 访问 https://github.com
   - 登录你的账号

2. **创建新仓库**
   - 点击右上角 "+" → "New repository"
   - 仓库名称：例如 `property-manager` 或 `wykf`
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

3. **获取仓库地址**
   - 复制显示的仓库 URL（例如：`https://github.com/用户名/仓库名.git`）

### 步骤 3：推送到 GitHub

```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 推送到 GitHub
git push -u origin main
```

**如果分支名是 master：**

```bash
git push -u origin master
```

**如果遇到认证问题：**

- 使用 Personal Access Token 代替密码
- 或使用 SSH 密钥

### 步骤 4：触发 GitHub Actions 打包

1. **打开 GitHub 仓库页面**
   - 在浏览器中打开你的仓库

2. **进入 Actions 标签页**
   - 点击仓库顶部的 "Actions" 标签

3. **选择工作流**
   - 在左侧找到 "Build Windows 7 Compatible EXE"
   - 点击进入

4. **运行工作流**
   - 点击右侧的 "Run workflow" 按钮
   - 选择分支（通常是 `main` 或 `master`）
   - 点击绿色的 "Run workflow" 按钮

5. **等待打包完成**
   - 点击运行记录查看进度
   - 通常需要 5-10 分钟
   - 等待所有步骤显示绿色 ✓

### 步骤 5：下载打包结果

1. **找到运行记录**
   - 在 Actions 页面找到最新的运行记录
   - 点击进入详情

2. **下载 Artifacts**
   - 滚动到页面底部
   - 找到 "Artifacts" 部分
   - 点击 "PropertyManager-Win7-EXE" 下载

3. **解压文件**
   - 下载的是一个 zip 文件
   - 解压后得到 `物业收费管理系统_Win7.exe`

---

## ✅ 验证打包结果

### 检查文件

- ✅ exe 文件存在
- ✅ 文件大小约 50-100MB
- ✅ 文件名：`物业收费管理系统_Win7.exe`

### 测试运行

1. **在 Windows 7 系统上测试**
   - 复制 exe 文件到 Windows 7 系统
   - 确保已安装 Visual C++ Redistributable 2015-2022
   - 双击运行

2. **功能测试**
   - 程序正常启动
   - 创建数据库文件
   - 测试所有功能模块

---

## 🔄 重新打包

如果需要重新打包：

1. 修改代码后提交
2. 推送到 GitHub
3. 在 Actions 中再次运行工作流
4. 下载新的打包结果

**或者：**

1. 直接在工作流页面点击 "Run workflow"
2. 选择分支
3. 等待打包完成

---

## 📝 工作流配置说明

GitHub Actions 工作流会自动：

1. ✅ 使用 Python 3.8.10
2. ✅ 安装 Windows 7 兼容依赖
3. ✅ 使用 PyInstaller 4.10 打包
4. ✅ 生成 Windows 7 兼容的 exe 文件
5. ✅ 上传构建产物供下载

**配置文件位置：** `.github/workflows/build-win7.yml`

---

## ❓ 常见问题

### Q1: 找不到 Actions 标签页

**原因：** 仓库可能未启用 Actions

**解决：**
1. 进入仓库 Settings
2. 找到 Actions → General
3. 确保 Actions 已启用

### Q2: 工作流运行失败

**检查：**
1. 查看运行日志，找到错误信息
2. 确认所有文件都已提交
3. 确认 `requirements-win7.txt` 存在
4. 确认 `PropertyManager-win7.spec` 存在

### Q3: 无法下载 Artifacts

**解决：**
1. 确保打包成功（所有步骤显示绿色）
2. 等待几分钟后重试
3. 检查浏览器下载设置

### Q4: 推送代码时认证失败

**解决：**
1. 使用 Personal Access Token
2. 或配置 SSH 密钥
3. 或使用 GitHub Desktop 客户端

---

## 🎉 完成！

打包成功后，你就有了一个可以在 Windows 7 上运行的 exe 文件！

**下一步：**
- 在 Windows 7 系统上测试
- 验证所有功能是否正常
- 分发给用户使用

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 GitHub Actions 运行日志
2. 检查错误信息
3. 参考 `文档/Windows7打包说明.md`

