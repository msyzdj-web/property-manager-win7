"""
物业收费管理系统主程序入口
"""
import sys
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

from models.database import init_db
from migrate_db import migrate_database
from ui.main_window import MainWindow


def main():
    """主函数"""
    try:
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

