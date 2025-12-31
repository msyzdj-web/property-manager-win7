@echo off
chcp 65001
echo ========================================
echo 推送代码到 GitHub 仓库
echo ========================================
echo.

echo [1/4] 检查 Git 状态...
git status
if errorlevel 1 (
    echo 错误: Git 仓库未初始化
    echo 请先运行 执行Git操作.bat
    pause
    exit /b 1
)
echo.

echo [2/4] 添加远程仓库...
git remote add origin https://github.com/msyzdj-web/property-manager-win7.git
if errorlevel 1 (
    echo 警告: 远程仓库可能已存在，继续下一步...
)
echo.

echo [3/4] 推送代码到 GitHub...
echo 正在推送代码，请稍候...
git push -u origin main
if errorlevel 1 (
    echo.
    echo 推送失败，可能需要认证信息
    echo.
    echo 请按以下步骤操作：
    echo 1. 创建 Personal Access Token：
    echo    - GitHub Settings → Developer settings → Personal access tokens
    echo    - 点击 "Generate new token (classic)"
    echo    - 选择 repo 权限
    echo    - 使用 token 作为密码
    echo.
    echo 2. 重新执行推送：
    echo    git push -u origin main
    echo.
    pause
    exit /b 1
)
echo.

echo [4/4] 验证推送结果...
git remote -v
echo.

echo ========================================
echo 推送成功！
echo ========================================
echo.
echo 下一步操作：
echo 1. 打开 GitHub 仓库：https://github.com/msyzdj-web/property-manager-win7
echo 2. 点击 "Actions" 标签页
echo 3. 选择 "Build Windows 7 Compatible EXE" 工作流
echo 4. 点击 "Run workflow" 触发打包
echo 5. 等待打包完成（约 5-10 分钟）
echo 6. 从 Artifacts 下载 exe 文件
echo.
echo 详细步骤请查看：GitHub Actions 最终步骤.md
echo.
pause

