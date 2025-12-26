@echo off
chcp 65001
echo ========================================
echo 执行 Git 操作 - 初始化并提交代码
echo ========================================
echo.

echo [1/6] 检查 Git 安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Git 未安装
    echo 请先安装 Git
    pause
    exit /b 1
) else (
    echo Git 已安装 ✓
)
echo.

echo [2/6] 初始化 Git 仓库...
if not exist .git (
    git init
    if errorlevel 1 (
        echo 错误: Git 初始化失败
        pause
        exit /b 1
    )
    echo Git 仓库已初始化 ✓
) else (
    echo Git 仓库已存在 ✓
)
echo.

echo [3/6] 配置用户信息...
git config user.name "Windows7Packager"
git config user.email "windows7packager@example.com"
echo Git 用户信息已配置 ✓
echo.

echo [4/6] 添加文件到 Git...
git add .
if errorlevel 1 (
    echo 错误: 添加文件失败
    pause
    exit /b 1
)
echo 文件已添加到 Git ✓
echo.

echo [5/6] 提交更改...
git commit -m "添加 Windows 7 兼容打包配置"
if errorlevel 1 (
    echo 警告: 提交可能失败（可能没有更改）
    echo 继续下一步...
) else (
    echo 代码已提交 ✓
)
echo.

echo [6/6] 显示状态...
git status
echo.

echo ========================================
echo Git 操作完成！
echo ========================================
echo.
echo 下一步：
echo 1. 在 GitHub 上创建仓库 property-manager-win7
echo 2. 复制仓库地址
echo 3. 执行推送命令：
echo    git remote add origin https://github.com/你的用户名/property-manager-win7.git
echo    git push -u origin main
echo.
echo 详细步骤请查看：GitHub Actions 最终步骤.md
echo.
pause

