
import sys
import os

def get_app_path():
    """获取应用程序根目录
    
    如果是打包后的exe，返回exe所在目录
    如果是源码运行，返回项目根目录
    """
    if getattr(sys, 'frozen', False):
        # 打包后的exe，使用exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境，使用文件所在目录的上级目录（项目根目录）
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_path(filename):
    """获取数据文件路径"""
    app_path = get_app_path()
    candidate = os.path.join(app_path, filename)
    if os.path.exists(candidate):
        return candidate
    # if not found next to exe, try parent directory (handles onedir layout where exe is under a subfolder)
    parent_candidate = os.path.join(os.path.dirname(app_path), filename)
    return parent_candidate
