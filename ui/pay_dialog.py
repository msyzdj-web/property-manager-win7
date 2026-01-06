"""
部分缴费对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QSpinBox, QDoubleSpinBox)
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
        
        # 缴费数量（单位感知，默认按月）
        months_layout = QHBoxLayout()
        self.paid_label = QLabel('缴费月数*:')
        months_layout.addWidget(self.paid_label)
        self.paid_months_input = QSpinBox()
        self.paid_months_input.setMinimum(0)
        self.paid_months_input.setMaximum(9999)
        self.paid_months_input.valueChanged.connect(self.calculate_paid_amount)
        months_layout.addWidget(self.paid_months_input)
        self.paid_double_input = QDoubleSpinBox()
        self.paid_double_input.setMinimum(0.0)
        self.paid_double_input.setMaximum(9999999.99)
        self.paid_double_input.setDecimals(2)
        self.paid_double_input.valueChanged.connect(self.calculate_paid_amount)
        self.paid_double_input.hide()
        months_layout.addWidget(self.paid_double_input)
        self.paid_unit_label = QLabel('月')
        months_layout.addWidget(self.paid_unit_label)
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
            
            # 显示账单信息并根据单位调整缴费输入（月/天/小时/度）
            unit = (payment.charge_item.unit or '').lower() if payment.charge_item else ''
            # 默认按月显示
            remaining_months = payment.billing_months - payment.paid_months
            total_display = f"{payment.billing_months} 月"
            paid_display = f"{payment.paid_months} 月"
            remaining_display = f"{remaining_months} 月"

            # 按小时
            if '小时' in unit or '时' in unit:
                seconds = (payment.billing_end_date - payment.billing_start_date).total_seconds() if payment.billing_start_date and payment.billing_end_date else 0
                total_units = max(1, int((seconds + 3599) // 3600)) if seconds else (payment.billing_months or 1)
                total_display = f"{total_units} 小时"
                paid_units = int((payment.paid_amount or 0) / (payment.charge_item.price or 1)) if payment.charge_item and payment.charge_item.price else 0
                paid_display = f"{paid_units} 小时"
                remaining_display = f"{max(0, total_units - paid_units)} 小时"
                # configure inputs
                self.paid_label.setText('缴费小时数*:')
                self.paid_unit_label.setText('小时')
                self.paid_double_input.hide()
                self.paid_months_input.show()
                self.paid_months_input.setMaximum(max(0, total_units))
                self.paid_months_input.setValue( min(max(1, total_units), total_units) if total_units>0 else 0)
            # 按天
            elif '天' in unit or '日' in unit:
                total_units = (payment.billing_end_date.date() - payment.billing_start_date.date()).days + 1 if payment.billing_start_date and payment.billing_end_date else (payment.billing_months or 1)
                total_units = max(1, total_units)
                total_display = f"{total_units} 天"
                paid_units = int((payment.paid_amount or 0) / (payment.charge_item.price or 1)) if payment.charge_item and payment.charge_item.price else 0
                paid_display = f"{paid_units} 天"
                remaining_display = f"{max(0, total_units - paid_units)} 天"
                self.paid_label.setText('缴费天数*:')
                self.paid_unit_label.setText('天')
                self.paid_double_input.hide()
                self.paid_months_input.show()
                self.paid_months_input.setMaximum(max(0, total_units))
                self.paid_months_input.setValue( min(max(1, total_units), total_units) if total_units>0 else 0)
            # 按度
            elif '度' in unit:
                total_units = float(payment.usage) if payment.usage is not None else 0.0
                total_display = f"{total_units:.2f} 度"
                paid_units = (payment.paid_amount or 0) / (payment.charge_item.price or 1) if payment.charge_item and payment.charge_item.price else 0.0
                paid_display = f"{paid_units:.2f} 度"
                remaining_display = f"{max(0.0, total_units - paid_units):.2f} 度"
                self.paid_label.setText('缴费度数*:')
                self.paid_unit_label.setText('度')
                # show double input for degrees
                self.paid_months_input.hide()
                self.paid_double_input.show()
                self.paid_double_input.setMaximum(max(0.0, total_units))
                self.paid_double_input.setValue( min(0.0, total_units) )
            else:
                # default month behavior
                self.paid_label.setText('缴费月数*:')
                self.paid_unit_label.setText('月')
                self.paid_double_input.hide()
                self.paid_months_input.show()
                self.paid_months_input.setMaximum(remaining_months)
                if remaining_months > 0:
                    self.paid_months_input.setValue(1)
            info_text = (\n+                f\"住户: {getattr(payment.resident, 'full_room_no', payment.resident.room_no)} - {payment.resident.name}\\n\"\n+                f\"收费项目: {payment.charge_item.name}\\n\"\n+                f\"计费周期: {payment.billing_start_date.strftime('%Y-%m-%d')} 至 {payment.billing_end_date.strftime('%Y-%m-%d')}\\n\"\n+                f\"总周期: {total_display}\\n\"\n+                f\"已缴费: {paid_display}\\n\"\n+                f\"剩余: {remaining_display}\\n\"\n+                f\"总金额: ¥{float(payment.amount):.2f}\"\n+            )\n*** End Patch
            self.info_label.setText(info_text)
            self.payment = payment
            self.calculate_paid_amount()
        except Exception as e:
            self.amount_label.setText('缴费金额: ¥0.00')
    
    def pay(self):
        """确认缴费"""
        try:
            unit = (self.payment.charge_item.unit or '').lower() if self.payment.charge_item else ''
            # degree uses double input
            if '度' in unit and self.paid_double_input.isVisible():
                paid_units = float(self.paid_double_input.value())
                if paid_units <= 0:
                    QMessageBox.warning(self, '提示', '缴费度数必须大于0')
                    return
                PaymentService.mark_paid(self.payment_id, paid_units=paid_units, operator='管理员')
                QMessageBox.information(self, '成功', f'缴费成功（{paid_units:.2f} 度）')
            else:
                paid_units_int = int(self.paid_months_input.value())
                if paid_units_int <= 0:
                    QMessageBox.warning(self, '提示', '缴费数量必须大于0')
                    return
                # if unit is month-like, pass as paid_months; else pass as paid_units
                if ('小时' in unit or '时' in unit) or ('天' in unit or '日' in unit):
                    PaymentService.mark_paid(self.payment_id, paid_units=paid_units_int, operator='管理员')
                    QMessageBox.information(self, '成功', f'缴费成功（{paid_units_int} {\"小时\" if \"小时\" in unit or \"时\" in unit else \"天\"}）')
                else:
                    PaymentService.mark_paid(self.payment_id, paid_months=paid_units_int, operator='管理员')
                    QMessageBox.information(self, '成功', f'缴费成功（{paid_units_int} 个月）')
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'缴费失败：{str(e)}')

