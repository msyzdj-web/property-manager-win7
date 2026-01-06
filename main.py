"""
物业收费管理系统主程序入口
"""
import sys
import time
import socket
import errno
import tempfile
import shutil
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# 设置Qt插件路径（解决虚拟环境中的插件问题）
if hasattr(sys, 'frozen'):
    # 如果是打包后的exe
    os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt5', 'plugins')
else:
    # 开发环境
    try:
        import PyQt5
        pyqt5_path = os.path.dirname(PyQt5.__file__)
        plugin_path = os.path.join(pyqt5_path, 'Qt5', 'plugins')
        if os.path.exists(plugin_path):
            os.environ['QT_PLUGIN_PATH'] = plugin_path
    except:
        pass

# When running as a frozen executable, ensure the unpacked MEIPASS dir and cwd are on sys.path
if getattr(sys, 'frozen', False):
    try:
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass and meipass not in sys.path:
            sys.path.insert(0, meipass)
    except Exception:
        pass
    try:
        cwd = os.getcwd()
        if cwd and cwd not in sys.path:
            sys.path.insert(0, cwd)
    except Exception:
        pass

# Local imports (after ensuring sys.path contains application files)
from models.database import init_db
from migrate_db import migrate_database
try:
    from ui.main_window import MainWindow
except ModuleNotFoundError:
    # Fallback: try importing by adjusting path to script directory
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        from ui.main_window import MainWindow
    except Exception:
        raise
from utils.logger import logger, setup_global_exception_handler


def main():
    """主函数"""
    try:
        # 设置全局异常处理器和启动日志
        setup_global_exception_handler()
        logger.log_startup_info()

        # ----------------- PyInstaller temp cleanup + single-instance -----------------
        # Clean up old PyInstaller _MEI* temp dirs to reduce "file already exists" popup risk.
        def cleanup_old_pyinstaller_dirs(days_old=1):
            """
            Remove leftover PyInstaller temp unpack directories starting with '_MEI'
            that are older than `days_old`. Skip the currently used MEIPASS dir.
            """
            try:
                tmp = tempfile.gettempdir()
                now = time.time()
                cutoff = now - days_old * 86400
                current_meipass = None
                try:
                    if getattr(sys, 'frozen', False):
                        current_meipass = getattr(sys, '_MEIPASS', None)
                except Exception:
                    current_meipass = None
                for name in os.listdir(tmp):
                    if not name.startswith('_MEI'):
                        continue
                    path = os.path.join(tmp, name)
                    try:
                        # skip if it's current process unpack dir
                        if current_meipass and os.path.normcase(os.path.normpath(path)) == os.path.normcase(os.path.normpath(current_meipass)):
                            continue
                        if not os.path.isdir(path):
                            continue
                        mtime = os.path.getmtime(path)
                        if mtime < cutoff:
                            shutil.rmtree(path, ignore_errors=True)
                    except Exception:
                        # ignore errors; don't block startup
                        pass
            except Exception:
                pass

        # Ensure single instance by binding a local TCP port.
        _SINGLE_INSTANCE_PORT = 54213

        def ensure_single_instance_or_exit(port=_SINGLE_INSTANCE_PORT):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except Exception:
                pass
            try:
                s.bind(('127.0.0.1', port))
                s.listen(1)
            except OSError as e:
                if getattr(e, 'errno', None) in (errno.EADDRINUSE,):
                    # Existing instance — exit quietly
                    sys.exit(0)
                raise
            return s

        # Run cleanup (remove >1 day old) then ensure single instance
        try:
            cleanup_old_pyinstaller_dirs(days_old=1)
        except Exception:
            pass
        _single_socket = None
        try:
            _single_socket = ensure_single_instance_or_exit(_SINGLE_INSTANCE_PORT)
        except SystemExit:
            raise
        except Exception:
            _single_socket = None
        # --------------------------------------------------------------------------
        # 迁移数据库（如果存在旧数据库）
        migrate_database()
        
        # 初始化数据库（创建表，如果不存在）
        init_db()
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用Fusion样式，更现代
        
        # 创建主窗口
        try:
            window = MainWindow()
            window.show()
        except Exception as e:
            # 如果窗口创建失败，显示错误信息
            import traceback
            error_msg = f'程序启动失败：{str(e)}\n\n详细信息：\n{traceback.format_exc()}'
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle('启动错误')
            msg_box.setText(error_msg)
            msg_box.exec_()
            return 1
        
        # 运行应用程序
        return app.exec_()
    except Exception as e:
        # 如果Qt初始化失败，尝试显示控制台错误
        import traceback
        print(f"程序启动失败：{str(e)}")
        print(traceback.format_exc())
        try:
            # 尝试创建简单的错误对话框
            app = QApplication(sys.argv)
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle('启动错误')
            msg_box.setText(f'程序启动失败：{str(e)}\n\n请检查PyQt5是否正确安装。')
            msg_box.exec_()
        except:
            pass
        return 1


if __name__ == '__main__':
    sys.exit(main())

