"""
缴费对话框（按度数）
专用于按度计费：只显示度数输入（支持小数），金额按单价 * 度数计算。
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from services.payment_service import PaymentService


class DegreePayDialog(QDialog):
    """按度缴费对话框"""

    def __init__(self, parent=None, payment_id=None):
        super().__init__(parent)
        self.payment_id = payment_id
        self.payment = None
        self.init_ui()
        self.load_payment()

    def init_ui(self):
        self.setWindowTitle('度数缴费')
        self.setFixedWidth(420)
        layout = QVBoxLayout(self)

        self.info_label = QLabel('')
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # input
        h = QHBoxLayout()
        h.addWidget(QLabel('缴费度数*:'))
        self.input_spin = QDoubleSpinBox()
        self.input_spin.setMinimum(0.0)
        self.input_spin.setMaximum(9999999.99)
        self.input_spin.setDecimals(2)
        self.input_spin.valueChanged.connect(self.on_value_changed)
        h.addWidget(self.input_spin)
        h.addWidget(QLabel('度'))
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
            ci = payment.charge_item
            total_units = float(payment.usage) if getattr(payment, 'usage', None) is not None else 0.0
            try:
                paid_amt = float(payment.paid_amount or 0.0)
                price_val = float(ci.price) if ci and ci.price is not None else 1.0
                paid_units = paid_amt / price_val if price_val else 0.0
            except Exception:
                paid_units = 0.0
            remaining = max(0.0, total_units - paid_units)
            info_text = (
                f"住户: {getattr(payment.resident, 'full_room_no', payment.resident.room_no)} - {payment.resident.name}\n"
                f"收费项目: {ci.name if ci else '未知'}\n"
                f"总用量: {total_units:.2f} 度\n"
                f"已缴: {paid_units:.2f} 度\n"
                f"剩余: {remaining:.2f} 度\n"
                f"单价: ¥{float(ci.price) if ci and ci.price is not None else 0.0:.2f}"
            )
            self.info_label.setText(info_text)
            # set spin bounds and default to remaining
            try:
                self.input_spin.setMaximum(max(0.0, remaining))
                self.input_spin.setValue(max(0.0, remaining))
            except Exception:
                self.input_spin.setValue(0.0)
            self.on_value_changed(self.input_spin.value())
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载缴费数据失败：{e}')

    def on_value_changed(self, v):
        try:
            ci = self.payment.charge_item if self.payment and self.payment.charge_item else None
            price = float(ci.price) if ci and ci.price is not None else 0.0
            amt = price * float(v)
            self.amount_label.setText(f'缴费金额: ¥{amt:.2f}')
        except Exception:
            self.amount_label.setText('缴费金额: ¥0.00')

    def pay(self):
        try:
            units = float(self.input_spin.value())
            if units <= 0:
                QMessageBox.warning(self, '提示', '缴费度数必须大于0')
                return
            PaymentService.mark_paid(self.payment_id, paid_units=units, operator='管理员')
            QMessageBox.information(self, '成功', f'缴费成功（{units:.2f} 度）')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'缴费失败：{e}')


