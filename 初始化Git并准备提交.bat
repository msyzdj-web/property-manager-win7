@echo off
chcp 65001
echo ========================================
echo 初始化 Git 并准备提交代码
echo ========================================
echo.

echo [1/5] 检查 Git 安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo Git 未安装或未添加到 PATH
    echo 请重启命令提示符后重试
    echo 或手动将 Git 添加到系统 PATH
    pause
    exit /b 1
) else (
    git --version
    echo Git 已安装 ✓
)
echo.

echo [2/5] 初始化 Git 仓库...
if not exist .git (
    git init
    echo Git 仓库已初始化 ✓
) else (
    echo Git 仓库已存在 ✓
)
echo.

echo [3/5] 配置 Git 用户信息（如果需要）...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo 未配置 Git 用户信息
    echo.
    set /p GIT_NAME="请输入你的名字（用于 Git 提交）: "
    set /p GIT_EMAIL="请输入你的邮箱（用于 Git 提交）: "
    git config user.name "%GIT_NAME%"
    git config user.email "%GIT_EMAIL%"
    echo Git 用户信息已配置 ✓
) else (
    echo Git 用户信息已配置 ✓
    git config user.name
    git config user.email
)
echo.

echo [4/5] 检查必要文件...
set MISSING=0
if not exist "requirements-win7.txt" (
    echo [警告] 缺少 requirements-win7.txt
    set MISSING=1
)
if not exist "PropertyManager-win7.spec" (
    echo [警告] 缺少 PropertyManager-win7.spec
    set MISSING=1
)
if not exist ".github\workflows\build-win7.yml" (
    echo [警告] 缺少 .github\workflows\build-win7.yml
    set MISSING=1
)
if not exist "main.py" (
    echo [警告] 缺少 main.py
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo 部分文件缺失，但可以继续
) else (
    echo 所有必要文件已存在 ✓
)
echo.

echo [5/5] 显示当前状态...
echo.
echo 未跟踪的文件：
git status --short
echo.

echo ========================================
echo 准备完成！
echo ========================================
echo.
echo 下一步操作：
echo.
echo 1. 添加所有文件到 Git：
echo    git add .
echo.
echo 2. 提交更改：
echo    git commit -m "添加 Windows 7 兼容打包配置"
echo.
echo 3. 在 GitHub 上创建新仓库：
echo    - 访问 https://github.com
echo    - 点击右上角 + 号 → New repository
echo    - 输入仓库名称（如：property-manager）
echo    - 选择 Public 或 Private
echo    - 不要勾选 "Initialize with README"
echo    - 点击 "Create repository"
echo.
echo 4. 推送代码到 GitHub：
echo    git remote add origin https://github.com/你的用户名/仓库名.git
echo    git push -u origin main
echo.
echo 5. 在 GitHub Actions 中触发打包：
echo    - 进入仓库的 Actions 标签页
echo    - 选择 "Build Windows 7 Compatible EXE"
echo    - 点击 "Run workflow"
echo    - 等待打包完成（约 5-10 分钟）
echo    - 下载 Artifacts 中的 exe 文件
echo.
echo 详细步骤请查看：GitHub Actions 打包指南.md
echo.
pause

