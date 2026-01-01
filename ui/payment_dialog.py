"""
缴费管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QComboBox, QDoubleSpinBox,
                             QDateEdit, QGroupBox, QSpinBox, QCompleter)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta

from services.resident_service import ResidentService
from services.charge_service import ChargeService
from services.payment_service import PaymentService


class PaymentDialog(QDialog):
    """缴费管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_residents()
        self.load_charge_items()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('生成账单')
        self.setFixedWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 住户选择
        resident_group = QGroupBox('选择住户')
        resident_layout = QVBoxLayout(resident_group)
        self.resident_combo = QComboBox()
        self.resident_combo.setEditable(True)
        self.resident_combo.setInsertPolicy(QComboBox.NoInsert)
        
        # 启用模糊搜索（包含匹配）
        completer = QCompleter(self.resident_combo.model())
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.resident_combo.setCompleter(completer)
        
        self.resident_combo.currentIndexChanged.connect(self.on_resident_changed)
        # 某些样式下 editable combobox 会有背景色问题，这里显式设置一下样式（可选，视主题而定）
        self.resident_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        resident_layout.addWidget(self.resident_combo)
        layout.addWidget(resident_group)
        
        # 收费项目选择
        charge_group = QGroupBox('选择收费项目')
        charge_layout = QVBoxLayout(charge_group)
        self.charge_combo = QComboBox()
        self.charge_combo.currentIndexChanged.connect(self.on_charge_changed)
        charge_layout.addWidget(self.charge_combo)
        layout.addWidget(charge_group)
        
        # 计费周期
        billing_group = QGroupBox('计费周期')
        billing_layout = QVBoxLayout(billing_group)
        
        # 计费开始日期
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel('计费开始日期*:'))
        self.billing_start_date = QDateEdit()
        self.billing_start_date.setCalendarPopup(True)
        self.billing_start_date.setDate(QDate.currentDate())
        self.billing_start_date.setDisplayFormat('yyyy-MM-dd')
        self.billing_start_date.dateChanged.connect(self.on_billing_date_changed)
        start_layout.addWidget(self.billing_start_date)
        billing_layout.addLayout(start_layout)
        
        # 计费结束日期
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel('计费结束日期*:'))
        self.billing_end_date = QDateEdit()
        self.billing_end_date.setCalendarPopup(True)
        self.billing_end_date.setDate(QDate.currentDate())
        self.billing_end_date.setDisplayFormat('yyyy-MM-dd')
        self.billing_end_date.dateChanged.connect(self.on_billing_date_changed)
        end_layout.addWidget(self.billing_end_date)
        billing_layout.addLayout(end_layout)
        
        # 计费周期数（自动计算）
        months_layout = QHBoxLayout()
        months_layout.addWidget(QLabel('计费周期数:'))
        self.billing_months_label = QLabel('1 月')
        months_layout.addWidget(self.billing_months_label)
        months_layout.addStretch()
        billing_layout.addLayout(months_layout)
        
        layout.addWidget(billing_group)
        
        # 缴费周期（用于分类）
        period_group = QGroupBox('缴费周期（用于分类）')
        period_layout = QVBoxLayout(period_group)
        self.period_date = QDateEdit()
        self.period_date.setCalendarPopup(True)
        self.period_date.setDate(QDate.currentDate())
        self.period_date.setDisplayFormat('yyyy-MM')
        period_layout.addWidget(self.period_date)
        layout.addWidget(period_group)
        
        # 金额计算
        amount_group = QGroupBox('缴费金额')
        amount_layout = QVBoxLayout(amount_group)
        
        self.amount_label = QLabel('金额: ¥0.00')
        self.amount_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #d32f2f;')
        amount_layout.addWidget(self.amount_label)
        
        # 手动输入金额（仅当收费类型为手动时显示）
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel('手动输入金额:'))
        self.manual_amount_input = QDoubleSpinBox()
        self.manual_amount_input.setMinimum(0.0)
        self.manual_amount_input.setMaximum(99999.99)
        self.manual_amount_input.setDecimals(2)
        self.manual_amount_input.setSuffix(' 元')
        self.manual_amount_input.setVisible(False)
        self.manual_amount_input.valueChanged.connect(self.calculate_amount)
        manual_layout.addWidget(self.manual_amount_input)
        amount_layout.addLayout(manual_layout)
        
        layout.addWidget(amount_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton('生成账单')
        self.cancel_btn = QPushButton('取消')
        self.save_btn.clicked.connect(self.save_payment)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def load_residents(self):
        """加载住户列表"""
        try:
            residents = ResidentService.get_all_residents(active_only=True)
            self.resident_combo.clear()
            for resident in residents:
                self.resident_combo.addItem(f"{getattr(resident,'full_room_no', resident.room_no)} - {resident.name}", resident.id)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载住户列表失败：{str(e)}')
    
    def load_charge_items(self):
        """加载收费项目列表"""
        try:
            charge_items = ChargeService.get_all_charge_items(active_only=True)
            self.charge_combo.clear()
            for item in charge_items:
                self.charge_combo.addItem(f"{item.name} ({item.get_charge_type_name()})", item.id)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载收费项目列表失败：{str(e)}')
    
    def on_resident_changed(self):
        """住户改变时的处理"""
        # 如果住户有入住日期，自动设置计费开始日期
        resident_id = self.resident_combo.currentData()
        if resident_id:
            resident = ResidentService.get_resident_by_id(resident_id)
            if resident and resident.move_in_date:
                self.billing_start_date.setDate(QDate(
                    resident.move_in_date.year,
                    resident.move_in_date.month,
                    resident.move_in_date.day
                ))
        self.calculate_amount()
    
    def on_billing_date_changed(self):
        """计费日期改变时的处理"""
        self.calculate_billing_months()
        self.calculate_amount()
    
    def calculate_billing_months(self):
        """计算计费周期数"""
        start_date = self.billing_start_date.date().toPyDate()
        end_date = self.billing_end_date.date().toPyDate()
        
        if end_date < start_date:
            self.billing_months_label.setText('0 月（结束日期不能早于开始日期）')
            return
        
        # 计算月数
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        # 如果结束日期的天数大于等于开始日期的天数，加1个月
        if end_date.day >= start_date.day:
            months += 1
        
        self.billing_months_label.setText(f'{months} 月')
    
    def on_charge_changed(self):
        """收费项目改变时的处理"""
        charge_item_id = self.charge_combo.currentData()
        if charge_item_id:
            charge_item = ChargeService.get_charge_item_by_id(charge_item_id)
            if charge_item:
                # 如果是手动类型，显示手动输入框
                self.manual_amount_input.setVisible(charge_item.charge_type == 'manual')
                if charge_item.charge_type != 'manual':
                    self.manual_amount_input.setValue(0.0)
        
        self.calculate_amount()
    
    def calculate_amount(self):
        """计算金额"""
        try:
            resident_id = self.resident_combo.currentData()
            charge_item_id = self.charge_combo.currentData()
            
            if not resident_id or not charge_item_id:
                self.amount_label.setText('金额: ¥0.00')
                return
            
            resident = ResidentService.get_resident_by_id(resident_id)
            charge_item = ChargeService.get_charge_item_by_id(charge_item_id)
            
            if not resident or not charge_item:
                self.amount_label.setText('金额: ¥0.00')
                return
            
            # 计算计费周期数
            start_date = self.billing_start_date.date().toPyDate()
            end_date = self.billing_end_date.date().toPyDate()
            if end_date < start_date:
                self.amount_label.setText('金额: ¥0.00（请检查日期）')
                return
            
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if end_date.day >= start_date.day:
                months += 1
            
            if months <= 0:
                self.amount_label.setText('金额: ¥0.00（周期数无效）')
                return
            
            # 计算金额
            if charge_item.charge_type == 'manual':
                amount = self.manual_amount_input.value()
            else:
                # 传入计费开始/结束日期，ChargeService 会根据 charge_item.unit 自动处理按日/按月/按年
                billing_start_date_py = self.billing_start_date.date().toPyDate()
                billing_end_date_py = self.billing_end_date.date().toPyDate()
                amount = ChargeService.calculate_amount(
                    charge_item,
                    resident_area=float(resident.area) if resident.area else 0.0,
                    months=months,
                    billing_start_date=billing_start_date_py,
                    billing_end_date=billing_end_date_py
                )
            
            self.amount_label.setText(f'金额: ¥{amount:.2f}（{months}个月）')
        except Exception as e:
            # 静默处理错误，避免影响用户体验
            self.amount_label.setText('金额: ¥0.00')
            # 只在调试模式下打印错误
            import sys
            if hasattr(sys, '_getframe'):
                import traceback
                print(f"计算金额时出错: {e}")
                traceback.print_exc()
    
    def save_payment(self):
        """保存缴费记录（生成账单）"""
        resident_id = self.resident_combo.currentData()
        charge_item_id = self.charge_combo.currentData()
        
        if not resident_id:
            QMessageBox.warning(self, '提示', '请选择住户')
            return
        
        if not charge_item_id:
            QMessageBox.warning(self, '提示', '请选择收费项目')
            return
        
        # 获取周期
        date = self.period_date.date()
        period = f"{date.year():04d}-{date.month():02d}"
        
        # 获取计费日期
        billing_start_date = self.billing_start_date.date().toPyDate()
        billing_end_date = self.billing_end_date.date().toPyDate()
        
        if billing_end_date < billing_start_date:
            QMessageBox.warning(self, '提示', '计费结束日期不能早于开始日期')
            return
        
        # 计算计费周期数
        months = (billing_end_date.year - billing_start_date.year) * 12 + (billing_end_date.month - billing_start_date.month)
        if billing_end_date.day >= billing_start_date.day:
            months += 1
        
        if months <= 0:
            QMessageBox.warning(self, '提示', '计费周期数必须大于0')
            return
        
        # 计算金额
        try:
            resident = ResidentService.get_resident_by_id(resident_id)
            charge_item = ChargeService.get_charge_item_by_id(charge_item_id)
            
            if not resident:
                QMessageBox.warning(self, '提示', '住户不存在')
                return
            
            if not charge_item:
                QMessageBox.warning(self, '提示', '收费项目不存在')
                return
            
            if charge_item.charge_type == 'manual':
                amount = self.manual_amount_input.value()
                if amount <= 0:
                    QMessageBox.warning(self, '提示', '请输入金额')
                    return
            else:
                billing_start_date_py = billing_start_date
                billing_end_date_py = billing_end_date
                amount = ChargeService.calculate_amount(
                    charge_item,
                    resident_area=float(resident.area) if resident.area else 0.0,
                    months=months,
                    billing_start_date=billing_start_date_py,
                    billing_end_date=billing_end_date_py
                )
            
            PaymentService.create_payment(
                resident_id=resident_id,
                charge_item_id=charge_item_id,
                period=period,
                billing_start_date=billing_start_date,
                billing_end_date=billing_end_date,
                billing_months=months,
                amount=amount
            )
            QMessageBox.information(self, '成功', f'账单生成成功（{months}个月）')
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            import traceback
            error_msg = f'生成账单失败：{str(e)}\n\n详细信息：\n{traceback.format_exc()}'
            QMessageBox.critical(self, '错误', error_msg)

