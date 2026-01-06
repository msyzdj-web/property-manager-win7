"""
运行时错误日志工具
用于记录程序运行时的异常和关键操作
"""
import os
import traceback
import sys
from datetime import datetime
from utils.path_utils import get_data_path


class RuntimeLogger:
    """运行时日志记录器"""

    def __init__(self):
        self.logs_dir = get_data_path('logs')
        self.error_log_path = os.path.join(self.logs_dir, 'run_errors.log')
        self.exports_dir = get_data_path('exports')

        # 确保日志目录存在
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)

    def log_error(self, error, context="", include_stack=True):
        """记录错误到日志文件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{timestamp}] ERROR in {context}: {str(error)}"

        if include_stack:
            error_msg += f"\nStack trace:\n{traceback.format_exc()}"

        error_msg += "\n" + "="*50 + "\n"

        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(error_msg)
        except Exception as log_error:
            # 如果日志写入失败，尝试写到控制台
            print(f"Failed to write to log file: {log_error}")
            print(error_msg)

    def log_operation(self, operation, details=""):
        """记录关键操作"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] OPERATION: {operation}"
        if details:
            log_msg += f" - {details}"

        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(log_msg + "\n")
        except Exception as log_error:
            print(f"Failed to log operation: {log_error}")

    def log_startup_info(self):
        """记录启动信息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        startup_info = f"""[{timestamp}] APP STARTUP
Python version: {sys.version}
Platform: {sys.platform}
Frozen: {getattr(sys, 'frozen', False)}
MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}
Working dir: {os.getcwd()}
Data path: {get_data_path('')}
{'='*50}
"""
        try:
            with open(self.error_log_path, 'a', encoding='utf-8') as f:
                f.write(startup_info)
        except Exception as log_error:
            print(f"Failed to log startup: {log_error}")

    def get_recent_errors(self, lines=50):
        """获取最近的错误日志"""
        try:
            if os.path.exists(self.error_log_path):
                with open(self.error_log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines_list = content.split('\n')
                    return '\n'.join(lines_list[-lines:])
        except Exception:
            pass
        return "No error logs found"


# 全局日志器实例
logger = RuntimeLogger()


def safe_execute(func, context="", *args, **kwargs):
    """安全执行函数，自动捕获并记录异常"""
    try:
        logger.log_operation(f"Starting {context}")
        result = func(*args, **kwargs)
        logger.log_operation(f"Completed {context}")
        return result
    except Exception as e:
        logger.log_error(e, context)
        raise


def setup_global_exception_handler():
    """设置全局未捕获异常处理器"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 忽略键盘中断
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.log_error(f"Uncaught exception: {error_msg}", "GLOBAL_EXCEPTION_HANDLER", include_stack=False)

        # 继续使用默认的异常处理器
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
