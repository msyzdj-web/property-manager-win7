# PyInstaller弹窗问题修复工具

## 问题描述
运行PyInstaller打包的exe文件时出现弹窗警告，通常是由于：
1. Windows Defender等杀软在PyInstaller解包时干预
2. 临时目录中存在旧的_MEI残留文件

## 解决方案
运行 `fix_defender_issue.bat` 来自动修复这些问题。

## 使用步骤
1. **关闭所有相关程序**
   - 关闭物业收费管理系统.exe的所有实例
   - 确保没有其他Python程序在运行

2. **运行修复工具**
   - 双击 `fix_defender_issue.bat`
   - 或者右键PowerShell脚本，选择"以管理员身份运行"

3. **测试运行**
   - 尝试运行物业收费管理系统.exe
   - 检查是否还有弹窗

## 脚本执行内容
- ✅ 查看并删除1分钟以前的_MEI临时目录
- ✅ 添加项目目录到Windows Defender排除列表
- ✅ 添加临时目录到Windows Defender排除列表
- ✅ 如有需要，临时关闭实时防护（测试完成后请手动恢复）

## 恢复实时防护
如果脚本临时关闭了实时防护，测试完成后请运行：
```powershell
Set-MpPreference -DisableRealtimeMonitoring $false
```

## 备用方案
如果自动脚本无法解决问题，请手动：
1. 打开Windows安全中心
2. 病毒和威胁防护 → 管理设置
3. 添加排除项：`E:\桌面\wykf` 和 `%TEMP%`

## 长期解决方案
考虑使用项目中的 `launcher_win7.bat` 作为默认启动器，它可以避免大部分路径冲突问题。
