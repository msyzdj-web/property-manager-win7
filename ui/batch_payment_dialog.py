"""
批量生成账单对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QComboBox, QDateEdit,
                             QGroupBox, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal as Signal
from datetime import datetime, timedelta

from services.resident_service import ResidentService
from services.charge_service import ChargeService
from services.payment_service import PaymentService


class BatchPaymentWorker(QThread):
    """批量生成账单工作线程"""
    progress = Signal(int, int, str)  # 当前进度, 总数, 当前处理项
    finished = Signal(int, int, list)  # 成功数, 失败数, 错误列表
    
    def __init__(self, resident_ids, charge_item_id, period, billing_start_date, billing_end_date, billing_months):
        super().__init__()
        self.resident_ids = resident_ids
        self.charge_item_id = charge_item_id
        self.period = period
        self.billing_start_date = billing_start_date
        self.billing_end_date = billing_end_date
        self.billing_months = billing_months
    
    def run(self):
        """执行批量生成"""
        success_count = 0
        fail_count = 0
        errors = []
        total = len(self.resident_ids)
        
        charge_item = ChargeService.get_charge_item_by_id(self.charge_item_id)
        if not charge_item:
            self.finished.emit(0, 0, ['收费项目不存在'])
            return
        
        for idx, resident_id in enumerate(self.resident_ids, 1):
            try:
                resident = ResidentService.get_resident_by_id(resident_id)
                if not resident:
                    fail_count += 1
                    errors.append(f"住户ID {resident_id} 不存在")
                    continue
                
                # 计算金额
                if charge_item.charge_type == 'manual':
                    # 手动类型需要跳过或使用默认值
                    amount = 0.0
                else:
                    amount = ChargeService.calculate_amount(
                        charge_item,
                        resident_area=float(resident.area) if resident.area else 0.0,
                        months=self.billing_months
                    )
                
                # 创建账单
                PaymentService.create_payment(
                    resident_id=resident_id,
                    charge_item_id=self.charge_item_id,
                    period=self.period,
                    billing_start_date=self.billing_start_date,
                    billing_end_date=self.billing_end_date,
                    billing_months=self.billing_months,
                    amount=amount
                )
                success_count += 1
                self.progress.emit(idx, total, f"{resident.room_no} - {resident.name}")
                
            except ValueError as e:
                fail_count += 1
                errors.append(f"{resident.room_no if 'resident' in locals() else resident_id}: {str(e)}")
                self.progress.emit(idx, total, f"失败: {str(e)}")
            except Exception as e:
                fail_count += 1
                errors.append(f"{resident.room_no if 'resident' in locals() else resident_id}: {str(e)}")
                self.progress.emit(idx, total, f"失败: {str(e)}")
        
        self.finished.emit(success_count, fail_count, errors)


class BatchPaymentDialog(QDialog):
    """批量生成账单对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()
        self.worker = None
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('批量生成账单')
        self.setFixedWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 收费项目选择
        charge_group = QGroupBox('选择收费项目')
        charge_layout = QVBoxLayout(charge_group)
        self.charge_combo = QComboBox()
        charge_layout.addWidget(self.charge_combo)
        layout.addWidget(charge_group)
        
        # 计费周期
        billing_group = QGroupBox('计费周期')
        billing_layout = QVBoxLayout(billing_group)
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel('计费开始日期*:'))
        self.billing_start_date = QDateEdit()
        self.billing_start_date.setCalendarPopup(True)
        self.billing_start_date.setDate(QDate.currentDate())
        self.billing_start_date.setDisplayFormat('yyyy-MM-dd')
        start_layout.addWidget(self.billing_start_date)
        billing_layout.addLayout(start_layout)
        
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel('计费结束日期*:'))
        self.billing_end_date = QDateEdit()
        self.billing_end_date.setCalendarPopup(True)
        self.billing_end_date.setDate(QDate.currentDate())
        self.billing_end_date.setDisplayFormat('yyyy-MM-dd')
        end_layout.addWidget(self.billing_end_date)
        billing_layout.addLayout(end_layout)
        
        layout.addWidget(billing_group)
        
        # 缴费周期
        period_group = QGroupBox('缴费周期（用于分类）')
        period_layout = QVBoxLayout(period_group)
        self.period_date = QDateEdit()
        self.period_date.setCalendarPopup(True)
        self.period_date.setDate(QDate.currentDate())
        self.period_date.setDisplayFormat('yyyy-MM')
        period_layout.addWidget(self.period_date)
        layout.addWidget(period_group)
        
        # 住户选择
        resident_group = QGroupBox('选择住户')
        resident_layout = QVBoxLayout(resident_group)
        self.all_residents_check = QCheckBox('为所有住户生成')
        self.all_residents_check.setChecked(True)
        resident_layout.addWidget(self.all_residents_check)
        layout.addWidget(resident_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.generate_btn = QPushButton('开始生成')
        self.cancel_btn = QPushButton('取消')
        self.generate_btn.clicked.connect(self.start_generate)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """加载数据"""
        try:
            charge_items = ChargeService.get_all_charge_items(active_only=True)
            self.charge_combo.clear()
            for item in charge_items:
                self.charge_combo.addItem(f"{item.name} ({item.get_charge_type_name()})", item.id)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载数据失败：{str(e)}')
    
    def start_generate(self):
        """开始批量生成"""
        charge_item_id = self.charge_combo.currentData()
        if not charge_item_id:
            QMessageBox.warning(self, '提示', '请选择收费项目')
            return
        
        # 获取周期
        date = self.period_date.date()
        period = f"{date.year():04d}-{date.month():02d}"
        
        billing_start_date = self.billing_start_date.date().toPyDate()
        billing_end_date = self.billing_end_date.date().toPyDate()
        
        if billing_end_date < billing_start_date:
            QMessageBox.warning(self, '提示', '计费结束日期不能早于开始日期')
            return
        
        # 计算月数
        months = (billing_end_date.year - billing_start_date.year) * 12 + (billing_end_date.month - billing_start_date.month)
        if billing_end_date.day >= billing_start_date.day:
            months += 1
        
        if months <= 0:
            QMessageBox.warning(self, '提示', '计费周期数必须大于0')
            return
        
        # 获取住户列表
        if self.all_residents_check.isChecked():
            residents = ResidentService.get_all_residents(active_only=True)
            resident_ids = [r.id for r in residents]
        else:
            QMessageBox.warning(self, '提示', '请选择要生成账单的住户')
            return
        
        if not resident_ids:
            QMessageBox.warning(self, '提示', '没有可用的住户')
            return
        
        # 确认
        reply = QMessageBox.question(
            self, 
            '确认', 
            f'将为 {len(resident_ids)} 个住户生成账单，确定继续吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 开始生成
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(resident_ids))
        self.progress_bar.setValue(0)
        
        self.worker = BatchPaymentWorker(
            resident_ids, charge_item_id, period,
            billing_start_date, billing_end_date, months
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def on_progress(self, current, total, message):
        """进度更新"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"正在处理: {message} ({current}/{total})")
    
    def on_finished(self, success_count, fail_count, errors):
        """生成完成"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        result_text = f"批量生成完成！\n成功: {success_count} 条\n失败: {fail_count} 条"
        if errors and len(errors) <= 10:
            result_text += f"\n\n错误详情:\n" + "\n".join(errors[:10])
        elif errors:
            result_text += f"\n\n前10个错误:\n" + "\n".join(errors[:10])
            result_text += f"\n... 还有 {len(errors) - 10} 个错误"
        
        if fail_count == 0:
            QMessageBox.information(self, '成功', result_text)
            self.accept()
        else:
            QMessageBox.warning(self, '部分成功', result_text)

