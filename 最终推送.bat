@echo off
chcp 65001
echo ========================================
echo 最终推送代码到 GitHub
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

echo [2/4] 设置远程仓库...
git remote remove origin 2>nul
git remote add origin https://msyzdj-web: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@github.com/msyzdj-web/property-manager-win7.git
if errorlevel 1 (
    echo 错误: 设置远程仓库失败
    pause
    exit /b 1
)
echo.

echo [3/4] 推送代码...
echo 正在推送代码到 GitHub，请稍候...
git push -u origin main
if errorlevel 1 (
    echo 错误: 推送失败
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. Token 权限不足
    echo 3. 分支名称问题（尝试 master）
    echo.
    echo 尝试使用 master 分支：
    git push -u origin master
    if errorlevel 1 (
        echo 推送仍然失败，请手动检查
        pause
        exit /b 1
    )
)
echo.

echo [4/4] 验证推送结果...
git remote -v
echo.

echo ========================================
echo 推送成功！
echo ========================================
echo.
echo 🎉 代码已成功推送到 GitHub！
echo.
echo 下一步操作：
echo 1. 打开浏览器访问：https://github.com/msyzdj-web/property-manager-win7
echo 2. 点击 "Actions" 标签页
echo 3. 选择 "Build Windows 7 Compatible EXE" 工作流
echo 4. 点击 "Run workflow" 按钮
echo 5. 等待打包完成（约 5-10 分钟）
echo 6. 从 Artifacts 下载 exe 文件
echo.
echo 📁 最终文件：物业收费管理系统_Win7.exe
echo 📏 文件大小：约 50-100MB
echo.
echo 祝打包顺利！🚀
echo.
pause

