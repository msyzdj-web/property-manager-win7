"""
数据备份对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFileDialog)
from PyQt5.QtCore import Qt
import os

from utils.backup_manager import BackupManager


class BackupDialog(QDialog):
    """数据备份对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_backups()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('数据备份与恢复')
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 备份按钮
        backup_layout = QHBoxLayout()
        self.backup_btn = QPushButton('创建备份')
        self.backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(self.backup_btn)
        backup_layout.addStretch()
        layout.addLayout(backup_layout)
        
        # 备份列表
        list_label = QLabel('备份列表:')
        layout.addWidget(list_label)
        
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(3)
        self.backup_table.setHorizontalHeaderLabels(['备份文件', '大小', '备份时间'])
        self.backup_table.horizontalHeader().setStretchLastSection(True)
        self.backup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.backup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.backup_table)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.restore_btn = QPushButton('恢复选中备份')
        self.delete_btn = QPushButton('删除选中备份')
        self.restore_btn.clicked.connect(self.restore_backup)
        self.delete_btn.clicked.connect(self.delete_backup)
        btn_layout.addWidget(self.restore_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        self.close_btn = QPushButton('关闭')
        self.close_btn.clicked.connect(self.accept)
        close_layout.addWidget(self.close_btn)
        layout.addLayout(close_layout)
    
    def load_backups(self):
        """加载备份列表"""
        try:
            backups = BackupManager.get_backup_list()
            self.backup_table.setRowCount(len(backups))
            
            for row, (file_path, file_size, mtime) in enumerate(backups):
                filename = os.path.basename(file_path)
                size_mb = file_size / (1024 * 1024)
                
                self.backup_table.setItem(row, 0, QTableWidgetItem(filename))
                self.backup_table.setItem(row, 1, QTableWidgetItem(f"{size_mb:.2f} MB"))
                self.backup_table.setItem(row, 2, QTableWidgetItem(mtime))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载备份列表失败：{str(e)}')
    
    def create_backup(self):
        """创建备份"""
        try:
            backup_path = BackupManager.backup_database()
            QMessageBox.information(self, '成功', f'备份已创建：\n{backup_path}')
            self.load_backups()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建备份失败：{str(e)}')
    
    def restore_backup(self):
        """恢复备份"""
        selected_rows = self.backup_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要恢复的备份')
            return
        
        filename = self.backup_table.item(selected_rows[0].row(), 0).text()
        
        reply = QMessageBox.question(
            self, 
            '确认恢复', 
            f'确定要恢复备份 "{filename}" 吗？\n\n恢复前会自动创建当前数据库的备份。',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 获取备份文件路径
                backups = BackupManager.get_backup_list()
                backup_path = backups[selected_rows[0].row()][0]
                
                BackupManager.restore_database(backup_path)
                QMessageBox.information(self, '成功', '数据库已恢复！\n\n请重启程序使更改生效。')
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'恢复失败：{str(e)}')
    
    def delete_backup(self):
        """删除备份"""
        selected_rows = self.backup_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要删除的备份')
            return
        
        filename = self.backup_table.item(selected_rows[0].row(), 0).text()
        
        reply = QMessageBox.question(
            self, 
            '确认删除', 
            f'确定要删除备份 "{filename}" 吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                backups = BackupManager.get_backup_list()
                backup_path = backups[selected_rows[0].row()][0]
                BackupManager.delete_backup(backup_path)
                QMessageBox.information(self, '成功', '备份已删除')
                self.load_backups()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败：{str(e)}')

