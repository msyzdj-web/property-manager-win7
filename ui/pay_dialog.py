"""
部分缴费对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer

from services.payment_service import PaymentService


class PayDialog(QDialog):
    """部分缴费对话框"""
    
    def __init__(self, parent=None, payment_id=None):
        super().__init__(parent)
        self.payment_id = payment_id
        # ensure attribute exists even if load fails
        self.payment = None
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
            print(f'[DEBUG] PayDialog.load_payment: payment_id={self.payment_id}')
            if not self.payment_id:
                self.amount_label.setText('缴费金额: ¥0.00')
                self.pay_btn.setEnabled(False)
                return

            payment = PaymentService.get_payment_by_id(self.payment_id)
            if not payment:
                QMessageBox.warning(self, '提示', '缴费记录不存在')
                self.pay_btn.setEnabled(False)
                self.reject()
                return

            # assign payment to self early so valueChanged handlers can read it
            self.payment = payment
            # determine unit and prepare displays
            unit = (self.payment.charge_item.unit or '').lower() if self.payment.charge_item else ''
            remaining_months = max(0, (payment.billing_months or 0) - (payment.paid_months or 0))
            total_display = ''
            paid_display = ''
            remaining_display = ''

            # Default to month behavior; we'll override per-unit below
            # Month display uses billing_months / paid_months
            total_display = f"{payment.billing_months} 月"
            paid_display = f"{payment.paid_months} 月"
            remaining_display = f"{remaining_months} 月"

            # Configure per-unit
            if '小时' in unit or '时' in unit:
                # total hours between billing dates (ceil to hours)
                seconds = (payment.billing_end_date - payment.billing_start_date).total_seconds() if payment.billing_start_date and payment.billing_end_date else 0
                total_units = max(1, int((seconds + 3599) // 3600)) if seconds else max(1, payment.billing_months or 1)
                paid_units = int((payment.paid_amount or 0) / (payment.charge_item.price or 1)) if payment.charge_item and payment.charge_item.price else 0
                total_display = f"{total_units} 小时"
                paid_display = f"{paid_units} 小时"
                remaining_display = f"{max(0, total_units - paid_units)} 小时"
                # set inputs: integer spinbox for hours
                self.paid_label.setText('缴费小时数*:')
                self.paid_unit_label.setText('小时')
                self.paid_double_input.hide()
                self.paid_months_input.show()
                self.paid_months_input.setMaximum(max(0, total_units))
                self.paid_months_input.setValue(min(max(1, 1), total_units) if total_units > 0 else 0)

            elif '天' in unit or '日' in unit:
                total_units = (payment.billing_end_date.date() - payment.billing_start_date.date()).days + 1 if payment.billing_start_date and payment.billing_end_date else max(1, payment.billing_months or 1)
                total_units = max(1, total_units)
                paid_units = int((payment.paid_amount or 0) / (payment.charge_item.price or 1)) if payment.charge_item and payment.charge_item.price else 0
                total_display = f"{total_units} 天"
                paid_display = f"{paid_units} 天"
                remaining_display = f"{max(0, total_units - paid_units)} 天"
                self.paid_label.setText('缴费天数*:')
                self.paid_unit_label.setText('天')
                self.paid_double_input.hide()
                self.paid_months_input.show()
                self.paid_months_input.setMaximum(max(0, total_units))
                self.paid_months_input.setValue(min(max(1, 1), total_units) if total_units > 0 else 0)

            elif '度' in unit:
                # degree uses double input and is based on payment.usage
                total_units = float(payment.usage) if payment.usage is not None else 0.0
                paid_units = (payment.paid_amount or 0) / (payment.charge_item.price or 1) if payment.charge_item and payment.charge_item.price else 0.0
                total_display = f"{total_units:.2f} 度"
                paid_display = f"{paid_units:.2f} 度"
                remaining_display = f"{max(0.0, total_units - paid_units):.2f} 度"
                self.paid_label.setText('缴费度数*:')
                self.paid_unit_label.setText('度')
                self.paid_months_input.hide()
                self.paid_double_input.show()
                # set sensible bounds for degree input and default to remaining_units
                try:
                    remaining_units = max(0.0, total_units - paid_units)
                    self.paid_double_input.setMaximum(max(0.0, remaining_units))
                    # default to remaining usage so user can one-click pay remaining degrees
                    self.paid_double_input.setValue(remaining_units)
                except Exception:
                    try:
                        self.paid_double_input.setValue(0.0)
                    except Exception:
                        pass

            else:
                # default month behavior; ensure month input visible
                self.paid_label.setText('缴费月数*:')
                self.paid_unit_label.setText('月')
                self.paid_double_input.hide()
                self.paid_months_input.show()
                self.paid_months_input.setMaximum(remaining_months)
                if remaining_months > 0:
                    self.paid_months_input.setValue(1)

            info_text = (
                f"住户: {getattr(payment.resident, 'full_room_no', payment.resident.room_no)} - {payment.resident.name}\n"
                f"收费项目: {payment.charge_item.name}\n"
                f"计费周期: {payment.billing_start_date.strftime('%Y-%m-%d')} 至 {payment.billing_end_date.strftime('%Y-%m-%d')}\n"
                f"总周期: {total_display}\n"
                f"已缴费: {paid_display}\n"
                f"剩余: {remaining_display}\n"
                f"总金额: ¥{float(payment.amount):.2f}"
            )
            self.info_label.setText(info_text)
            self.payment = payment
            # enable pay button now that payment loaded successfully
            try:
                self.pay_btn.setEnabled(True)
            except Exception:
                pass
            # calculate amount
            self.calculate_paid_amount()
            # Apply UI state now; final enforcement will also run on showEvent to avoid timing issues
            try:
                # schedule to run after the current event loop turn so widgets have correct native visibility
                QTimer.singleShot(0, lambda: self._apply_unit_ui(unit, locals()))
            except Exception:
                pass
            # defensive: ensure the inputs are enabled so user can type; final state will be enforced by _apply_unit_ui/showEvent
            try:
                self.paid_double_input.setEnabled(True)
                self.paid_months_input.setEnabled(True)
            except Exception:
                pass
            try:
                print(f'[DEBUG] after schedule paid_double_visible={self.paid_double_input.isVisible()}, paid_double_enabled={self.paid_double_input.isEnabled()}, paid_months_visible={self.paid_months_input.isVisible()}, paid_months_enabled={self.paid_months_input.isEnabled()}, unit_label={self.paid_unit_label.text()}')
            except Exception:
                pass
        except Exception as e:
            self.amount_label.setText('缴费金额: ¥0.00')
            self.pay_btn.setEnabled(False)

    def _apply_unit_ui(self, unit: str, ctx: dict = None):
        """Apply visibility/enabled/max/value for inputs based on unit.
        ctx: local variables from caller (should contain total_units, remaining_months, remaining_units)
        """
        try:
            # degree
            if '度' in unit:
                remaining_units = 0.0
                try:
                    remaining_units = float(ctx.get('remaining_units', None) if ctx else None)
                except Exception:
                    try:
                        # try compute from payment
                        remaining_units = max(0.0, float(self.payment.usage or 0.0) - ((self.payment.paid_amount or 0.0) / (self.payment.charge_item.price or 1)))
                    except Exception:
                        remaining_units = 0.0
                self.paid_double_input.setVisible(True)
                self.paid_double_input.setEnabled(True)
                self.paid_months_input.setVisible(False)
                self.paid_months_input.setEnabled(False)
                self.paid_unit_label.setText('度')
                try:
                    self.paid_double_input.setMaximum(max(0.0, remaining_units))
                    # default to remaining
                    self.paid_double_input.setValue(max(0.0, remaining_units))
                except Exception:
                    pass
            elif '小时' in unit or '时' in unit:
                total_units = int(ctx.get('total_units', 0) if ctx else 0)
                self.paid_double_input.setVisible(False)
                self.paid_double_input.setEnabled(False)
                self.paid_months_input.setVisible(True)
                self.paid_months_input.setEnabled(True)
                self.paid_unit_label.setText('小时')
                try:
                    self.paid_months_input.setMaximum(int(total_units))
                    if self.paid_months_input.value() <= 0:
                        self.paid_months_input.setValue(1 if total_units > 0 else 0)
                except Exception:
                    pass
            elif '天' in unit or '日' in unit:
                total_units = int(ctx.get('total_units', 0) if ctx else 0)
                self.paid_double_input.setVisible(False)
                self.paid_double_input.setEnabled(False)
                self.paid_months_input.setVisible(True)
                self.paid_months_input.setEnabled(True)
                self.paid_unit_label.setText('天')
                try:
                    self.paid_months_input.setMaximum(int(total_units))
                    if self.paid_months_input.value() <= 0:
                        self.paid_months_input.setValue(1 if total_units > 0 else 0)
                except Exception:
                    pass
            else:
                # months
                remaining_months = int(ctx.get('remaining_months', 0) if ctx else 0)
                self.paid_double_input.setVisible(False)
                self.paid_double_input.setEnabled(False)
                self.paid_months_input.setVisible(True)
                self.paid_months_input.setEnabled(True)
                self.paid_unit_label.setText('月')
                try:
                    self.paid_months_input.setMaximum(int(remaining_months))
                    if self.paid_months_input.value() <= 0:
                        self.paid_months_input.setValue(1 if remaining_months > 0 else 0)
                except Exception:
                    pass
            # adjust and repaint to ensure UI updates on show
            try:
                self.adjustSize()
                self.paid_double_input.repaint()
                self.paid_months_input.repaint()
                self.paid_unit_label.repaint()
            except Exception:
                pass
        except Exception:
            # top-level safeguard for _apply_unit_ui
            pass

    def showEvent(self, event):
        """Ensure UI state is correct when the dialog is shown (fix timing issues on some platforms)."""
        try:
            if hasattr(self, 'payment') and self.payment:
                unit = (self.payment.charge_item.unit or '').lower() if self.payment.charge_item else ''
                # recompute context values
                ctx = {}
                if '小时' in unit or '时' in unit:
                    seconds = (self.payment.billing_end_date - self.payment.billing_start_date).total_seconds() if self.payment.billing_start_date and self.payment.billing_end_date else 0
                    ctx['total_units'] = max(1, int((seconds + 3599) // 3600)) if seconds else max(1, self.payment.billing_months or 1)
                elif '天' in unit or '日' in unit:
                    total_units = (self.payment.billing_end_date.date() - self.payment.billing_start_date.date()).days + 1 if self.payment.billing_start_date and self.payment.billing_end_date else max(1, self.payment.billing_months or 1)
                    ctx['total_units'] = max(1, total_units)
                elif '度' in unit:
                    total_units = float(self.payment.usage) if self.payment.usage is not None else 0.0
                    paid_units = (self.payment.paid_amount or 0) / (self.payment.charge_item.price or 1) if self.payment.charge_item and self.payment.charge_item.price else 0.0
                    ctx['remaining_units'] = max(0.0, total_units - paid_units)
                else:
                    ctx['remaining_months'] = max(0, (self.payment.billing_months or 0) - (self.payment.paid_months or 0))
                self._apply_unit_ui(unit, ctx)
        except Exception:
            pass
        super().showEvent(event)
    
    def calculate_paid_amount(self):
        """计算缴费金额（单位感知）"""
        try:
            if not hasattr(self, 'payment'):
                return
            unit = (self.payment.charge_item.unit or '').lower() if self.payment.charge_item else ''
            price = float(self.payment.charge_item.price) if self.payment.charge_item and self.payment.charge_item.price is not None else 0.0

            # Use unit string directly (do not rely on widget visibility)
            if '度' in unit:
                units = float(self.paid_double_input.value())
                paid_amount = price * units
            else:
                units = int(self.paid_months_input.value())
                if '小时' in unit or '时' in unit or '天' in unit or '日' in unit or '度' in unit:
                    paid_amount = price * units
                else:
                    try:
                        monthly_amount = float(self.payment.amount) / self.payment.billing_months
                    except Exception:
                        monthly_amount = 0.0
                    paid_amount = monthly_amount * units
            
            self.amount_label.setText(f'缴费金额: ¥{paid_amount:.2f}')
        except Exception:
            self.amount_label.setText('缴费金额: ¥0.00')
    
    def pay(self):
        """确认缴费"""
        try:
            print(f'[DEBUG] PayDialog.pay clicked for payment_id={self.payment_id}')
            unit = (self.payment.charge_item.unit or '').lower() if self.payment.charge_item else ''
            # degree uses double input (decide by unit, not visibility)
            if '度' in unit:
                paid_units = float(self.paid_double_input.value())
                print(f'[DEBUG] degree pay_units={paid_units}')
                if paid_units <= 0:
                    QMessageBox.warning(self, '提示', '缴费度数必须大于0')
                    return
                PaymentService.mark_paid(self.payment_id, paid_units=paid_units, operator='管理员')
                QMessageBox.information(self, '成功', f'缴费成功（{paid_units:.2f} 度）')
            else:
                paid_units_int = int(self.paid_months_input.value())
                print(f'[DEBUG] int pay_units={paid_units_int}, unit={unit}')
                if paid_units_int <= 0:
                    QMessageBox.warning(self, '提示', '缴费数量必须大于0')
                    return
                # if unit is hour/day, pass as paid_units; else pass as paid_months
                if ('小时' in unit or '时' in unit) or ('天' in unit or '日' in unit):
                    PaymentService.mark_paid(self.payment_id, paid_units=paid_units_int, operator='管理员')
                    # compute unit label safely
                    unit_label = '小时' if ('小时' in unit or '时' in unit) else '天'
                    QMessageBox.information(self, '成功', f'缴费成功（{paid_units_int} {unit_label}）')
                else:
                    PaymentService.mark_paid(self.payment_id, paid_months=paid_units_int, operator='管理员')
                    QMessageBox.information(self, '成功', f'缴费成功（{paid_units_int} 个月）')
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'缴费失败：{str(e)}')

