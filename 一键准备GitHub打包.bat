@echo off
chcp 65001
echo ========================================
echo 准备 GitHub Actions 打包环境
echo ========================================
echo.

echo [1/4] 检查 Git 安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo Git 未安装
    echo.
    echo 请先安装 Git：
    echo 1. 访问 https://git-scm.com/download/win
    echo 2. 下载并安装 Git for Windows
    echo 3. 安装完成后重新运行此脚本
    echo.
    echo 正在打开下载页面...
    start https://git-scm.com/download/win
    pause
    exit /b 1
) else (
    git --version
    echo Git 已安装 ✓
)
echo.

echo [2/4] 检查 Git 仓库状态...
if not exist .git (
    echo 初始化 Git 仓库...
    git init
    echo Git 仓库已初始化 ✓
) else (
    echo Git 仓库已存在 ✓
)
echo.

echo [3/4] 检查必要文件...
set MISSING_FILES=0

if not exist "requirements-win7.txt" (
    echo [错误] 缺少 requirements-win7.txt
    set MISSING_FILES=1
)

if not exist "PropertyManager-win7.spec" (
    echo [错误] 缺少 PropertyManager-win7.spec
    set MISSING_FILES=1
)

if not exist ".github\workflows\build-win7.yml" (
    echo [错误] 缺少 .github\workflows\build-win7.yml
    set MISSING_FILES=1
)

if not exist "main.py" (
    echo [错误] 缺少 main.py
    set MISSING_FILES=1
)

if %MISSING_FILES%==1 (
    echo.
    echo 请确保所有必要文件都存在！
    pause
    exit /b 1
) else (
    echo 所有必要文件已存在 ✓
)
echo.

echo [4/4] 准备提交代码...
echo.
echo 当前未提交的文件：
git status --short
echo.

echo ========================================
echo 准备完成！
echo ========================================
echo.
echo 下一步操作：
echo.
echo 1. 提交所有文件到 Git：
echo    git add .
echo    git commit -m "添加 Windows 7 兼容打包配置"
echo.
echo 2. 在 GitHub 上创建新仓库
echo    - 访问 https://github.com
echo    - 点击右上角 + 号 → New repository
echo    - 输入仓库名称，创建仓库
echo.
echo 3. 推送代码到 GitHub：
echo    git remote add origin https://github.com/你的用户名/仓库名.git
echo    git push -u origin main
echo.
echo 4. 在 GitHub Actions 中触发打包：
echo    - 进入仓库的 Actions 标签页
echo    - 选择 "Build Windows 7 Compatible EXE"
echo    - 点击 "Run workflow"
echo.
echo 详细步骤请查看：GitHub Actions 打包指南.md
echo.
pause

