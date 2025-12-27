"""
批量导入对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt
import os

from utils.excel_importer import ExcelImporter


class ImportDialog(QDialog):
    """批量导入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('批量导入住户')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 说明
        info_label = QLabel('支持格式：Excel (.xlsx, .xls)\n\n列顺序：房号、姓名、电话、面积、入住日期[, 身份(identity，可选：房主/租户), 房屋类型(property_type，可选：住宅/商铺)]\n\n第一行为标题行，将从第二行开始读取数据。identity 与 property_type 为可选列，缺省为 房主 / 住宅')
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 文件选择
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel('选择文件:'))
        self.file_path_label = QLabel('未选择文件')
        file_layout.addWidget(self.file_path_label)
        self.browse_btn = QPushButton('浏览...')
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)
        
        # 模板下载
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel('下载导入模板:'))
        self.download_template_btn = QPushButton('下载模板')
        self.download_template_btn.clicked.connect(self.download_template)
        template_layout.addWidget(self.download_template_btn)
        template_layout.addStretch()
        layout.addLayout(template_layout)
        
        # 导入结果
        result_label = QLabel('导入结果:')
        layout.addWidget(result_label)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        layout.addWidget(self.result_text)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.import_btn = QPushButton('开始导入')
        self.cancel_btn = QPushButton('关闭')
        self.import_btn.clicked.connect(self.do_import)
        self.cancel_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.file_path = None
    
    def browse_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择Excel文件',
            '',
            'Excel文件 (*.xlsx *.xls);;所有文件 (*.*)'
        )
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
    
    def download_template(self):
        """下载导入模板"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存模板文件',
            '住户导入模板.xlsx',
            'Excel文件 (*.xlsx)'
        )
        if file_path:
            try:
                ExcelImporter.create_import_template(file_path)
                QMessageBox.information(self, '成功', f'模板已保存到：\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存模板失败：{str(e)}')
    
    def do_import(self):
        """执行导入"""
        if not self.file_path:
            QMessageBox.warning(self, '提示', '请先选择要导入的文件')
            return
        
        if not os.path.exists(self.file_path):
            QMessageBox.warning(self, '提示', '文件不存在')
            return
        
        try:
            success_count, fail_count, errors = ExcelImporter.import_residents(self.file_path)
            
            # 显示结果
            result_text = f"导入完成！\n"
            result_text += f"成功: {success_count} 条\n"
            result_text += f"失败: {fail_count} 条\n"
            
            if errors:
                result_text += f"\n错误详情:\n"
                for error in errors[:10]:  # 只显示前10个错误
                    result_text += f"{error}\n"
                if len(errors) > 10:
                    result_text += f"... 还有 {len(errors) - 10} 个错误\n"
            
            self.result_text.setPlainText(result_text)
            
            if fail_count == 0:
                QMessageBox.information(self, '成功', f'成功导入 {success_count} 条住户信息')
                self.accept()
            else:
                QMessageBox.warning(self, '部分成功', f'成功导入 {success_count} 条，失败 {fail_count} 条\n\n请查看详细错误信息')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导入失败：{str(e)}')

