@echo off
chcp 65001
echo ========================================
echo 一键推送代码到 GitHub
echo ========================================
echo.

echo [1/6] 检查 Git 安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo Git 未安装或未添加到 PATH
    echo 请先安装 Git 并重启命令提示符
    pause
    exit /b 1
) else (
    echo Git 已安装 ✓
)
echo.

echo [2/6] 初始化 Git 仓库...
if not exist .git (
    git init
    echo Git 仓库已初始化 ✓
) else (
    echo Git 仓库已存在 ✓
)
echo.

echo [3/6] 配置用户信息...
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

echo [4/6] 添加文件到 Git...
git add .
echo 文件已添加到 Git ✓
echo.

echo [5/6] 提交更改...
git commit -m "添加 Windows 7 兼容打包配置" >nul 2>&1
if errorlevel 1 (
    echo 提交失败，可能没有更改需要提交
    echo 或者文件已提交，请继续下一步
) else (
    echo 代码已提交 ✓
)
echo.

echo [6/6] 准备推送...
echo.
echo ========================================
echo 推送准备完成！
echo ========================================
echo.
echo 下一步操作：
echo.
echo 1. 在 GitHub 上创建新仓库：
echo    - 访问 https://github.com
echo    - 点击右上角 + 号 → New repository
echo    - 仓库名称：property-manager-win7
echo    - 选择 Public，点击 Create repository
echo.
echo 2. 获取仓库地址并推送：
echo    git remote add origin https://github.com/你的用户名/property-manager-win7.git
echo    git push -u origin main
echo.
echo 3. 在 GitHub Actions 中触发打包：
echo    - 进入仓库的 Actions 标签页
echo    - 选择 "Build Windows 7 Compatible EXE"
echo    - 点击 "Run workflow"
echo.
echo 详细步骤请查看：GitHub仓库创建和推送指南.md
echo.
pause

