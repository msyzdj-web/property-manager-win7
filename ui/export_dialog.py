"""
导出对话框
"""
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt
from datetime import datetime

from utils.excel_exporter import ExcelExporter
from utils.report_generator import ReportGenerator


class ExportDialog(QDialog):
    """导出对话框"""
    
    def __init__(self, parent=None, export_type='unpaid'):
        super().__init__(parent)
        self.export_type = export_type  # 'unpaid', 'payments', 'report'
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        if self.export_type == 'unpaid':
            self.setWindowTitle('导出欠费清单')
        elif self.export_type == 'payments':
            self.setWindowTitle('导出缴费记录')
        else:
            self.setWindowTitle('生成统计报表')
        
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 周期选择（如果需要）
        if self.export_type in ['unpaid', 'report']:
            period_layout = QHBoxLayout()
            period_layout.addWidget(QLabel('选择周期:'))
            self.period_combo = QComboBox()
            period_layout.addWidget(self.period_combo)
            layout.addLayout(period_layout)

        # 报表粒度（仅 report）
        if self.export_type == 'report':
            gran_layout = QHBoxLayout()
            gran_layout.addWidget(QLabel('统计粒度:'))
            self.gran_combo = QComboBox()
            self.gran_combo.addItems(['按月', '按日', '按年'])
            self.gran_combo.currentTextChanged.connect(self.on_gran_changed)
            gran_layout.addWidget(self.gran_combo)
            layout.addLayout(gran_layout)
        
        # 说明
        if self.export_type == 'unpaid':
            info_text = '将导出指定周期的欠费清单到Excel文件'
        elif self.export_type == 'payments':
            info_text = '将导出缴费记录到Excel文件'
        else:
            info_text = '将生成月度统计报表到Excel文件'
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.export_btn = QPushButton('导出' if self.export_type != 'report' else '生成')
        self.cancel_btn = QPushButton('取消')
        self.export_btn.clicked.connect(self.do_export)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.period = None
    
    def set_periods(self, periods):
        """设置周期列表"""
        if hasattr(self, 'period_combo'):
            self.period_combo.clear()
            self.period_combo.addItems(periods)
            if periods:
                self.period_combo.setCurrentIndex(0)
        # 保存原始周期列表，同时生成年度列表供按年统计使用
        self._available_periods = periods or []
        years = sorted(list({p.split('-')[0] for p in self._available_periods}), reverse=True)
        self._available_years = years

    def on_gran_changed(self, text):
        """当选择按月/日/年时更新 period_combo 的内容"""
        if text == '按年':
            # 显示年份
            if hasattr(self, '_available_years'):
                self.period_combo.clear()
                self.period_combo.addItems(self._available_years)
        else:
            # 恢复为月份列表
            if hasattr(self, '_available_periods'):
                self.period_combo.clear()
                self.period_combo.addItems(self._available_periods)
    
    def do_export(self):
        """执行导出"""
        # 获取周期
        if self.export_type in ['unpaid', 'report']:
            if not hasattr(self, 'period_combo') or not self.period_combo.currentText():
                QMessageBox.warning(self, '提示', '请选择周期')
                return
            period = self.period_combo.currentText()
        else:
            period = None
        
        # 设置默认保存目录（程序目录下的exports文件夹）
        from utils.path_utils import get_app_path
        default_dir = os.path.join(get_app_path(), 'exports')
        os.makedirs(default_dir, exist_ok=True)
        
        # 选择保存路径
        if self.export_type == 'unpaid':
            default_filename = f'欠费清单_{period}.xlsx'
            file_filter = 'Excel文件 (*.xlsx)'
        elif self.export_type == 'payments':
            default_filename = f'缴费记录_{datetime.now().strftime("%Y%m%d")}.xlsx'
            file_filter = 'Excel文件 (*.xlsx)'
        else:
            # 根据粒度选择默认文件名（按日时使用导出日期精确到日）
            gran = '按月'
            if hasattr(self, 'gran_combo'):
                gran = self.gran_combo.currentText()
            if gran == '按日':
                today_str = datetime.now().strftime('%Y-%m-%d')
                default_filename = f'日度统计报表_{today_str}.xlsx'
            else:
                default_filename = f'月度统计报表_{period}.xlsx'
            file_filter = 'Excel文件 (*.xlsx)'
        
        default_path = os.path.join(default_dir, default_filename)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存文件',
            default_path,
            file_filter
        )
        
        if not file_path:
            return
        
        try:
            if self.export_type == 'unpaid':
                ExcelExporter.export_unpaid_list(period, file_path)
                QMessageBox.information(self, '成功', f'欠费清单已导出到：\n{file_path}')
            elif self.export_type == 'payments':
                ExcelExporter.export_payments(period, file_path)
                QMessageBox.information(self, '成功', f'缴费记录已导出到：\n{file_path}')
            else:
                # 根据粒度选择生成不同报表
                gran = '按月'
                if hasattr(self, 'gran_combo'):
                    gran = self.gran_combo.currentText()
                if gran == '按日':
                    ReportGenerator.generate_daily_report(period, file_path)
                elif gran == '按年':
                    # period holds year in this mode
                    ReportGenerator.generate_year_report(period, file_path)
                else:
                    ReportGenerator.generate_monthly_report(period, file_path)
                QMessageBox.information(self, '成功', f'统计报表已生成到：\n{file_path}')
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败：{str(e)}')

