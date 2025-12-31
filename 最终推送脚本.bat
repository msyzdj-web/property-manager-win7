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
    pause
    exit /b 1
)
echo.

echo [2/4] 配置认证信息...
echo 正在配置 GitHub 认证信息...
git config --global credential.helper store
echo.

echo [3/4] 检查和设置远程仓库...
git remote -v | findstr origin >nul
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin https://github.com/msyzdj-web/property-manager-win7.git
) else (
    echo 远程仓库已存在，检查地址...
    git remote set-url origin https://github.com/msyzdj-web/property-manager-win7.git
)
echo 远程仓库配置：
git remote -v
echo.

echo [4/4] 推送代码...
echo 正在推送代码，请稍候...
echo 如果提示输入用户名和密码：
echo 用户名：msyzdj-web
echo 密码：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
echo.

git push -u origin main
if errorlevel 1 (
    echo.
    echo main 分支推送失败，尝试 master 分支...
    git push -u origin master
    if errorlevel 1 (
        echo.
        echo 推送失败！
        echo 可能的原因：
        echo 1. 没有提交的代码
        echo 2. 分支名称错误
        echo 3. 认证问题
        echo.
        echo 请检查：
        git log --oneline -3
        git branch
        echo.
        pause
        exit /b 1
    )
)
echo.

echo ========================================
echo 推送成功！🎉
echo ========================================
echo.
echo 仓库地址：https://github.com/msyzdj-web/property-manager-win7
echo.
echo 下一步：
echo 1. 打开浏览器访问上述地址
echo 2. 点击 "Actions" 标签页
echo 3. 选择 "Build Windows 7 Compatible EXE" 工作流
echo 4. 点击 "Run workflow" 触发打包
echo 5. 等待打包完成（约 5-10 分钟）
echo 6. 从 Artifacts 下载 exe 文件
echo.
pause

