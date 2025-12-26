@echo off
echo ========================================
echo 快速推送代码到 GitHub
echo ========================================
echo.

echo 步骤1: 配置认证
git config --global credential.helper store
echo.

echo 步骤2: 设置远程仓库
git remote set-url origin https://msyzdj-web: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@github.com/msyzdj-web/property-manager-win7.git
echo.

echo 步骤3: 推送代码
git push -u origin main
if errorlevel 1 (
    echo 尝试推送 master 分支...
    git push -u origin master
)
echo.

echo ========================================
echo 完成！请检查 GitHub 仓库
echo ========================================
echo.
echo 仓库地址: https://github.com/msyzdj-web/property-manager-win7
echo.
pause
