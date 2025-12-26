"""
数据备份管理工具
"""
import os
import shutil
from datetime import datetime
from models.database import DB_PATH
from utils.path_utils import get_app_path


class BackupManager:
    """数据备份管理类"""
    
    @staticmethod
    def backup_database(backup_dir=None):
        """备份数据库
        
        Args:
            backup_dir: 备份目录，如果为None则使用当前目录下的backup文件夹
            
        Returns:
            str: 备份文件路径
        """
        if not os.path.exists(DB_PATH):
            raise Exception("数据库文件不存在")
        
        if backup_dir is None:
            from utils.path_utils import get_app_path
            backup_dir = os.path.join(get_app_path(), 'backup')
        
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'property_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 复制数据库文件
        shutil.copy2(DB_PATH, backup_path)
        
        return backup_path
    
    @staticmethod
    def restore_database(backup_path):
        """恢复数据库
        
        Args:
            backup_path: 备份文件路径
        """
        if not os.path.exists(backup_path):
            raise Exception("备份文件不存在")
        
        # 恢复前先备份当前数据库
        try:
            current_backup = BackupManager.backup_database()
        except:
            pass
        
        # 恢复数据库
        shutil.copy2(backup_path, DB_PATH)
    
    @staticmethod
    def get_backup_list(backup_dir=None):
        """获取备份文件列表
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            list: 备份文件信息列表 [(文件路径, 文件大小, 修改时间), ...]
        """
        if backup_dir is None:
            from utils.path_utils import get_app_path
            backup_dir = os.path.join(get_app_path(), 'backup')
        
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('property_backup_') and filename.endswith('.db'):
                file_path = os.path.join(backup_dir, filename)
                file_size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                backups.append((file_path, file_size, mtime_str))
        
        # 按时间倒序排序
        backups.sort(key=lambda x: x[2], reverse=True)
        return backups
    
    @staticmethod
    def delete_backup(backup_path):
        """删除备份文件
        
        Args:
            backup_path: 备份文件路径
        """
        if os.path.exists(backup_path):
            os.remove(backup_path)

