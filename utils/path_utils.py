
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
    return os.path.join(get_app_path(), filename)
