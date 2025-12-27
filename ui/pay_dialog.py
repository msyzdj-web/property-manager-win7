"""
部分缴费对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt

from services.payment_service import PaymentService


class PayDialog(QDialog):
    """部分缴费对话框"""
    
    def __init__(self, parent=None, payment_id=None):
        super().__init__(parent)
        self.payment_id = payment_id
        self.init_ui()
        self.load_payment()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('缴费')
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 账单信息
        info_group = QVBoxLayout()
        self.info_label = QLabel('')
        self.info_label.setWordWrap(True)
        info_group.addWidget(self.info_label)
        layout.addLayout(info_group)
        
        # 缴费月数
        months_layout = QHBoxLayout()
        months_layout.addWidget(QLabel('缴费月数*:'))
        self.paid_months_input = QSpinBox()
        self.paid_months_input.setMinimum(1)
        self.paid_months_input.setMaximum(999)
        self.paid_months_input.valueChanged.connect(self.calculate_paid_amount)
        months_layout.addWidget(self.paid_months_input)
        months_layout.addWidget(QLabel('月'))
        layout.addLayout(months_layout)
        
        # 缴费金额
        amount_layout = QHBoxLayout()
        self.amount_label = QLabel('缴费金额: ¥0.00')
        self.amount_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #d32f2f;')
        amount_layout.addWidget(self.amount_label)
        layout.addLayout(amount_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.pay_btn = QPushButton('确认缴费')
        self.cancel_btn = QPushButton('取消')
        self.pay_btn.clicked.connect(self.pay)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.pay_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def load_payment(self):
        """加载缴费记录信息"""
        try:
            payment = PaymentService.get_payment_by_id(self.payment_id)
            if not payment:
                QMessageBox.warning(self, '提示', '缴费记录不存在')
                self.reject()
                return
            
            # 显示账单信息
            remaining_months = payment.billing_months - payment.paid_months
            info_text = f"住户: {payment.resident.room_no} - {payment.resident.name}\n"
            info_text += f"收费项目: {payment.charge_item.name}\n"
            info_text += f"计费周期: {payment.billing_start_date.strftime('%Y-%m-%d')} 至 {payment.billing_end_date.strftime('%Y-%m-%d')}\n"
            info_text += f"总周期: {payment.billing_months} 月\n"
            info_text += f"已缴费: {payment.paid_months} 月\n"
            info_text += f"剩余: {remaining_months} 月\n"
            info_text += f"总金额: ¥{float(payment.amount):.2f}"
            self.info_label.setText(info_text)
            
            # 设置最大缴费月数
            self.paid_months_input.setMaximum(remaining_months)
            if remaining_months > 0:
                self.paid_months_input.setValue(1)
            
            self.payment = payment
            self.calculate_paid_amount()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载缴费记录失败：{str(e)}')
            self.reject()
    
    def calculate_paid_amount(self):
        """计算缴费金额"""
        try:
            if not hasattr(self, 'payment'):
                return
            
            paid_months = self.paid_months_input.value()
            monthly_amount = float(self.payment.amount) / self.payment.billing_months
            paid_amount = monthly_amount * paid_months
            
            self.amount_label.setText(f'缴费金额: ¥{paid_amount:.2f}')
        except Exception as e:
            self.amount_label.setText('缴费金额: ¥0.00')
    
    def pay(self):
        """确认缴费"""
        try:
            paid_months = self.paid_months_input.value()
            if paid_months <= 0:
                QMessageBox.warning(self, '提示', '缴费月数必须大于0')
                return
            
            PaymentService.mark_paid(self.payment_id, paid_months=paid_months, operator='管理员')
            QMessageBox.information(self, '成功', f'缴费成功（{paid_months}个月）')
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'缴费失败：{str(e)}')

