# Windows 7 打包检查清单

## 📋 打包前检查

### 文件完整性检查
- [x] `requirements-win7.txt` - Windows 7 兼容依赖配置
- [x] `PropertyManager-win7.spec` - Windows 7 专用打包配置
- [x] `build-win7.bat` - Windows 7 打包脚本
- [x] `.github/workflows/build-win7.yml` - GitHub Actions 工作流
- [x] `文档/Windows7打包说明.md` - 详细文档
- [x] `Windows7打包快速指南.md` - 快速开始指南

### 代码兼容性检查
- [x] SQLAlchemy 使用 `db.query()` 语法（兼容 1.4）
- [x] 无 Python 3.9+ 特性（字典合并、walrus 操作符等）
- [x] 所有依赖都有 Windows 7 兼容版本

### 配置验证
- [x] `PropertyManager-win7.spec` 中 `upx=False`（关闭压缩）
- [x] `requirements-win7.txt` 中版本正确：
  - Python 3.8.10
  - PyInstaller 4.10
  - SQLAlchemy 1.4.46
  - pandas 1.5.3

---

## 🚀 执行打包

### 选项 A：GitHub Actions（推荐）

**步骤：**
1. [ ] 确保所有文件已提交到 Git
2. [ ] 推送到 GitHub 仓库
3. [ ] 在 GitHub 上进入 Actions 标签页
4. [ ] 选择 "Build Windows 7 Compatible EXE" 工作流
5. [ ] 点击 "Run workflow" 手动触发
6. [ ] 等待打包完成（约 5-10 分钟）
7. [ ] 下载 Artifacts 中的 exe 文件

**验证：**
- [ ] GitHub Actions 显示绿色 ✓
- [ ] 能够下载构建产物
- [ ] exe 文件大小约 50-100MB

### 选项 B：本地打包

**前提条件：**
- [ ] 已安装 Python 3.8.10
- [ ] 已安装 Visual C++ Redistributable 2015-2022

**步骤：**
1. [ ] 打开命令提示符
2. [ ] 切换到项目目录
3. [ ] 运行 `pip install -r requirements-win7.txt`
4. [ ] 运行 `build-win7.bat`
5. [ ] 检查 `dist\物业收费管理系统_Win7.exe` 是否存在

**验证：**
- [ ] 打包脚本执行成功
- [ ] exe 文件已生成
- [ ] 无错误信息

---

## ✅ 打包后测试

### Windows 7 系统要求
- [ ] Windows 7 SP1 或更高版本
- [ ] 已安装 Visual C++ Redistributable 2015-2022
- [ ] 至少 100MB 可用磁盘空间

### 功能测试清单

**基础功能：**
- [ ] 程序能够正常启动（首次可能需要 10-30 秒）
- [ ] 界面正常显示
- [ ] 数据库文件自动创建（property.db）

**核心功能：**
- [ ] 添加住户功能正常
- [ ] 编辑住户功能正常
- [ ] 删除住户功能正常
- [ ] 添加收费项目功能正常
- [ ] 编辑收费项目功能正常
- [ ] 生成账单功能正常
- [ ] 标记缴费功能正常
- [ ] 打印收据功能正常
- [ ] 导出 Excel 功能正常
- [ ] 数据备份功能正常

**边界测试：**
- [ ] 大量数据（100+ 住户）操作流畅
- [ ] 长时间运行无崩溃
- [ ] 异常情况处理正常（如数据库锁定）

---

## 🐛 问题排查

### 如果打包失败

**检查点：**
- [ ] Python 版本是否为 3.8.x
- [ ] 依赖是否正确安装
- [ ] `PropertyManager-win7.spec` 文件是否存在
- [ ] 查看错误日志

**常见错误：**
- `找不到 requirements-win7.txt` → 确保文件在项目根目录
- `PyInstaller 版本错误` → 检查是否为 4.10
- `缺少模块` → 检查 hiddenimports 配置

### 如果 exe 无法运行

**检查点：**
- [ ] Windows 7 是否为 SP1
- [ ] 是否安装 Visual C++ Redistributable
- [ ] 杀毒软件是否拦截
- [ ] 查看错误提示信息

**解决方案：**
1. 安装 Visual C++ Redistributable 2015-2022
2. 将 exe 添加到杀毒软件白名单
3. 以管理员身份运行
4. 检查系统日志

---

## 📝 记录信息

**打包信息：**
- 打包日期：___________
- 打包方式：□ GitHub Actions  □ 本地打包
- Python 版本：___________
- PyInstaller 版本：___________
- exe 文件大小：___________

**测试信息：**
- 测试日期：___________
- 测试系统：Windows 7 ___________
- 测试结果：□ 通过  □ 部分通过  □ 失败
- 问题记录：___________

---

## ✨ 完成标志

所有检查项完成后：
- [x] 所有配置文件已创建
- [ ] 打包成功完成
- [ ] 在 Windows 7 上测试通过
- [ ] 所有功能正常工作
- [ ] 文档已更新

**恭喜！Windows 7 兼容打包已完成！** 🎉

