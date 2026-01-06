"""
部分缴费对话框（小时/天/月 通用）
使用整数输入框（QSpinBox），按单位计算金额并提交（小时/天 -> paid_units, 月 -> paid_months）
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt
from services.payment_service import PaymentService


class UnitPayDialog(QDialog):
    """按小时/天/月缴费对话框（整数）"""

    def __init__(self, parent=None, payment_id=None):
        super().__init__(parent)
        self.payment_id = payment_id
        self.payment = None
        self.unit = '月'
        self.init_ui()
        self.load_payment()

    def init_ui(self):
        self.setWindowTitle('缴费')
        self.setFixedWidth(420)
        layout = QVBoxLayout(self)

        self.info_label = QLabel('')
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        h = QHBoxLayout()
        self.paid_label = QLabel('缴费数量*:')
        h.addWidget(self.paid_label)
        self.spin = QSpinBox()
        self.spin.setMinimum(0)
        self.spin.setMaximum(9999999)
        self.spin.valueChanged.connect(self.on_value_changed)
        h.addWidget(self.spin)
        self.unit_label = QLabel('月')
        h.addWidget(self.unit_label)
        layout.addLayout(h)

        self.amount_label = QLabel('缴费金额: ¥0.00')
        self.amount_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #d32f2f;')
        layout.addWidget(self.amount_label)

        btn_h = QHBoxLayout()
        btn_h.addStretch()
        self.ok_btn = QPushButton('确认缴费')
        self.cancel_btn = QPushButton('取消')
        self.ok_btn.clicked.connect(self.pay)
        self.cancel_btn.clicked.connect(self.reject)
        btn_h.addWidget(self.ok_btn)
        btn_h.addWidget(self.cancel_btn)
        layout.addLayout(btn_h)

    def load_payment(self):
        try:
            payment = PaymentService.get_payment_by_id(self.payment_id)
            if not payment:
                QMessageBox.warning(self, '提示', '缴费记录不存在')
                self.reject()
                return
            self.payment = payment
            unit = (payment.charge_item.unit or '').lower() if payment.charge_item else ''
            self.unit = '月'
            # determine unit and defaults
            if '小时' in unit or '时' in unit:
                self.unit = '小时'
                # total hours
                seconds = (payment.billing_end_date - payment.billing_start_date).total_seconds() if payment.billing_start_date and payment.billing_end_date else 0
                total_units = max(1, int((seconds + 3599) // 3600)) if seconds else max(1, payment.billing_months or 1)
                paid_units = int((payment.paid_amount or 0) / (payment.charge_item.price or 1)) if payment.charge_item and payment.charge_item.price else 0
                remaining = max(0, total_units - paid_units)
                self.spin.setMaximum(max(0, remaining))
                self.spin.setValue(1 if remaining>0 else 0)
            elif '天' in unit or '日' in unit:
                self.unit = '天'
                total_units = (payment.billing_end_date.date() - payment.billing_start_date.date()).days + 1 if payment.billing_start_date and payment.billing_end_date else max(1, payment.billing_months or 1)
                total_units = max(1, total_units)
                paid_units = int((payment.paid_amount or 0) / (payment.charge_item.price or 1)) if payment.charge_item and payment.charge_item.price else 0
                remaining = max(0, total_units - paid_units)
                self.spin.setMaximum(max(0, remaining))
                self.spin.setValue(1 if remaining>0 else 0)
            else:
                # month fallback
                self.unit = '月'
                remaining = max(0, (payment.billing_months or 0) - (payment.paid_months or 0))
                self.spin.setMaximum(max(0, remaining))
                self.spin.setValue(1 if remaining>0 else 0)

            info_text = (
                f"住户: {getattr(payment.resident, 'full_room_no', payment.resident.room_no)} - {payment.resident.name}\n"
                f"收费项目: {payment.charge_item.name}\n"
                f"计费周期: {payment.billing_start_date.strftime('%Y-%m-%d')} 至 {payment.billing_end_date.strftime('%Y-%m-%d')}\n"
            )
            self.info_label.setText(info_text)
            self.unit_label.setText(self.unit)
            self.on_value_changed(self.spin.value())
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载缴费数据失败：{e}')

    def on_value_changed(self, v):
        try:
            ci = self.payment.charge_item if self.payment and self.payment.charge_item else None
            price = float(ci.price) if ci and ci.price is not None else 0.0
            if self.unit in ('小时','天'):
                amt = price * int(v)
            else:
                # month
                # approximate monthly prorate: use payment.amount / billing_months as monthly_amount
                try:
                    monthly_amount = float(self.payment.amount) / max(1, int(self.payment.billing_months or 1))
                except Exception:
                    monthly_amount = 0.0
                amt = monthly_amount * int(v)
            self.amount_label.setText(f'缴费金额: ¥{amt:.2f}')
        except Exception:
            self.amount_label.setText('缴费金额: ¥0.00')

    def pay(self):
        try:
            v = int(self.spin.value())
            if v <= 0:
                QMessageBox.warning(self, '提示', '缴费数量必须大于0')
                return
            if self.unit in ('小时','天'):
                PaymentService.mark_paid(self.payment_id, paid_units=v, operator='管理员')
                QMessageBox.information(self, '成功', f'缴费成功（{v} {self.unit}）')
            else:
                PaymentService.mark_paid(self.payment_id, paid_months=v, operator='管理员')
                QMessageBox.information(self, '成功', f'缴费成功（{v} 个月）')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'缴费失败：{e}')


