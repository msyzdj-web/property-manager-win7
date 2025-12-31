# GitHub 仓库创建和推送指南

## 🎯 现在开始创建 GitHub 仓库

### 步骤 1：创建 GitHub 仓库

1. **打开 GitHub**
   - 访问：https://github.com
   - 确保已登录

2. **创建新仓库**
   - 点击右上角 **"+"** 号
   - 选择 **"New repository"**

3. **填写仓库信息**
   ```
   Repository name: property-manager-win7  # 或者你喜欢的名字
   Description: 物业收费管理系统 - Windows 7 兼容版本
   Public/Private: Public  # 建议 Public，方便后续使用
   ```

   **重要：**
   - ✅ **不要勾选** "Add a README file"
   - ✅ **不要勾选** "Add .gitignore"
   - ✅ **不要勾选** "Add a license"

4. **点击 "Create repository"**

### 步骤 2：获取仓库地址

创建完成后，复制显示的仓库地址：
```
https://github.com/你的用户名/property-manager-win7.git
```

---

## 📤 推送代码到 GitHub

### 方法一：使用批处理脚本（推荐）

1. **运行批处理脚本**
   ```bash
   初始化Git并准备提交.bat
   ```

2. **按提示操作**
   - 输入你的 Git 用户名
   - 输入你的 Git 邮箱

### 方法二：手动操作

如果脚本有问题，手动执行：

1. **初始化 Git 仓库**
   ```bash
   git init
   ```

2. **配置用户信息**
   ```bash
   git config user.name "你的名字"
   git config user.email "你的邮箱"
   ```

3. **添加所有文件**
   ```bash
   git add .
   ```

4. **提交代码**
   ```bash
   git commit -m "添加 Windows 7 兼容打包配置"
   ```

5. **添加远程仓库**
   ```bash
   git remote add origin https://github.com/你的用户名/property-manager-win7.git
   ```

6. **推送代码**
   ```bash
   git push -u origin main
   ```

---

## 🚀 触发 GitHub Actions 打包

### 步骤 1：进入 Actions 页面

1. **在 GitHub 上打开你的仓库**
   - 访问：https://github.com//msyzdj-web/property-manager-win7

2. **点击 "Actions" 标签页**
   - 在仓库顶部看到 Actions 标签

### 步骤 2：运行工作流

1. **选择工作流**
   - 在左侧找到 **"Build Windows 7 Compatible EXE"**
   - 点击进入

2. **触发打包**
   - 点击右侧的 **"Run workflow"** 按钮
   - 选择分支（通常是 `main`）
   - 点击绿色的 **"Run workflow"** 按钮

3. **等待打包**
   - 工作流会显示为 "in progress"
   - 打包需要 **5-10 分钟**
   - 所有步骤都显示绿色 ✓ 表示成功

### 步骤 3：下载打包结果

1. **找到完成的工作流**
   - 在 Actions 页面找到完成的运行记录
   - 点击进入详情

2. **下载 Artifacts**
   - 滚动到页面底部
   - 找到 **"Artifacts"** 部分
   - 点击 **"PropertyManager-Win7-EXE"** 下载

3. **解压文件**
   - 下载的是 zip 文件
   - 解压后得到 `物业收费管理系统_Win7.exe`

---

## ✅ 验证成功

### 文件检查
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

## 🔧 常见问题

### Q1: 推送代码时提示认证失败

**解决方案：**
1. 使用 Personal Access Token 代替密码
2. 或使用 SSH 密钥

**获取 Personal Access Token：**
- GitHub Settings → Developer settings → Personal access tokens
- 点击 "Generate new token (classic)"
- 选择 `repo` 权限
- 使用 token 作为密码

### Q2: 工作流运行失败

**检查：**
1. 查看运行日志，找到错误信息
2. 确认所有文件都已推送
3. 确认 `requirements-win7.txt` 存在
4. 确认 `PropertyManager-win7.spec` 存在

### Q3: 无法下载 Artifacts

**解决方案：**
- 确保打包成功（所有步骤显示绿色）
- 等待几分钟后重试
- 检查浏览器下载设置

### Q4: 分支名称问题

如果推送时提示 `main` 分支不存在：
```bash
# 推送时指定分支名
git push -u origin master
```

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
3. 参考 `GitHub Actions 打包指南.md`
4. 参考 `完整打包方案总结.md`

