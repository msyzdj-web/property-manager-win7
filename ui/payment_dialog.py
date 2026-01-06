"""
缴费管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QComboBox, QDoubleSpinBox,
                             QDateTimeEdit, QDateEdit, QGroupBox, QSpinBox, QCompleter)
from PyQt5.QtCore import Qt, QDateTime, QDate
from datetime import datetime, timedelta

from services.resident_service import ResidentService
from services.charge_service import ChargeService
from services.payment_service import PaymentService


class PaymentDialog(QDialog):
    """缴费管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.payment_id = None
        self.init_ui()
        self.load_residents()
        self.load_charge_items()
        # 如果以编辑模式打开，外部可先设置 self.payment_id 再调用 load_payment()
    
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
        
        # 计费开始日期（含时间）
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel('计费开始日期*:'))
        self.billing_start_date = QDateTimeEdit()
        self.billing_start_date.setCalendarPopup(True)
        self.billing_start_date.setDateTime(QDateTime.currentDateTime())
        self.billing_start_date.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.billing_start_date.dateTimeChanged.connect(self.on_billing_date_changed)
        start_layout.addWidget(self.billing_start_date)
        billing_layout.addLayout(start_layout)
        
        # 计费结束日期
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel('计费结束日期*:'))
        self.billing_end_date = QDateTimeEdit()
        self.billing_end_date.setCalendarPopup(True)
        self.billing_end_date.setDateTime(QDateTime.currentDateTime())
        self.billing_end_date.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.billing_end_date.dateTimeChanged.connect(self.on_billing_date_changed)
        end_layout.addWidget(self.billing_end_date)
        billing_layout.addLayout(end_layout)
        
        # 计费周期数（自动计算）
        months_layout = QHBoxLayout()
        months_layout.addWidget(QLabel('计费周期数:'))
        self.billing_months_label = QLabel('1 月')
        months_layout.addWidget(self.billing_months_label)
        months_layout.addStretch()
        billing_layout.addLayout(months_layout)
        
        # 用量输入（可选，适用于 元/度 或 元/小时 场景）
        usage_layout = QHBoxLayout()
        usage_layout.addWidget(QLabel('用量(可选):'))
        self.usage_input = QDoubleSpinBox()
        self.usage_input.setMinimum(0.0)
        self.usage_input.setMaximum(9999999.99)
        self.usage_input.setDecimals(2)
        self.usage_input.setSuffix(' ')
        usage_layout.addWidget(self.usage_input)
        billing_layout.addLayout(usage_layout)
        
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
    
    def load_payment(self, payment_id: int):
        """以编辑模式加载已有账单数据"""
        try:
            payment = PaymentService.get_payment_by_id(payment_id)
            if not payment:
                raise ValueError("账单不存在")
            self.payment_id = payment_id
            # 选择住户
            idx = self.resident_combo.findData(payment.resident_id)
            if idx >= 0:
                self.resident_combo.setCurrentIndex(idx)
            # 选择收费项目
            cidx = self.charge_combo.findData(payment.charge_item_id)
            if cidx >= 0:
                self.charge_combo.setCurrentIndex(cidx)
            # 填写日期与用量
            if payment.billing_start_date:
                self.billing_start_date.setDateTime(QDateTime(payment.billing_start_date.year, payment.billing_start_date.month, payment.billing_start_date.day, payment.billing_start_date.hour if hasattr(payment.billing_start_date, 'hour') else 0, payment.billing_start_date.minute if hasattr(payment.billing_start_date, 'minute') else 0))
            if payment.billing_end_date:
                self.billing_end_date.setDateTime(QDateTime(payment.billing_end_date.year, payment.billing_end_date.month, payment.billing_end_date.day, payment.billing_end_date.hour if hasattr(payment.billing_end_date, 'hour') else 0, payment.billing_end_date.minute if hasattr(payment.billing_end_date, 'minute') else 0))
            if payment.usage is not None:
                try:
                    self.usage_input.setValue(float(payment.usage))
                except Exception:
                    pass
            # 周期
            if payment.period:
                try:
                    y, m = payment.period.split('-')
                    self.period_date.setDate(QDate(int(y), int(m), 1))
                except Exception:
                    pass
            # 手动金额显示
            if payment.charge_item and payment.charge_item.charge_type == 'manual':
                self.manual_amount_input.setVisible(True)
                try:
                    self.manual_amount_input.setValue(float(payment.amount))
                except Exception:
                    pass
            # 更改按钮文本为保存修改
            self.save_btn.setText('保存修改')
            # 重新计算并显示金额/周期（基于单位感知）
            try:
                self.calculate_billing_months()
                self.calculate_amount()
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载账单失败：{str(e)}')
    
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
        """计算并展示计费周期（根据收费项目单位：月/天/小时/度 等）"""
        # 默认清理
        self._computed_billing_count = None
        self._computed_billing_unit = '月'

        start_dt = self.billing_start_date.dateTime().toPyDateTime()
        end_dt = self.billing_end_date.dateTime().toPyDateTime()

        # 如果结束早于开始，提示并返回
        if end_dt < start_dt:
            self.billing_months_label.setText('0 月（结束日期不能早于开始日期）')
            return

        # 获取当前选中收费项目的单位（若可用）
        charge_item = None
        try:
            cid = self.charge_combo.currentData()
            if cid:
                charge_item = ChargeService.get_charge_item_by_id(cid)
        except Exception:
            charge_item = None

        unit = (charge_item.unit or '').lower() if charge_item else ''

        # 按小时计费
        if '小时' in unit or '时' in unit:
            seconds = (end_dt - start_dt).total_seconds()
            hours = max(1, int((seconds + 3599) // 3600))  # 向上取整小时
            self._computed_billing_count = hours
            self._computed_billing_unit = '小时'
            self.billing_months_label.setText(f'{hours} 小时')
            return

        # 按天计费
        if '天' in unit or '日' in unit:
            start_date = start_dt.date()
            end_date = end_dt.date()
            days = (end_date - start_date).days + 1
            if days <= 0:
                days = 1
            self._computed_billing_count = days
            self._computed_billing_unit = '天'
            self.billing_months_label.setText(f'{days} 天')
            return

        # 按度数计费 - 以用量为准（不基于日期）
        if '度' in unit:
            try:
                usage_val = float(self.usage_input.value())
            except Exception:
                usage_val = 0.0
            self._computed_billing_count = usage_val
            self._computed_billing_unit = '度'
            self.billing_months_label.setText(f'用量: {usage_val:.2f} 度')
            return

        # 否则按月计费（默认）
        start_date = start_dt.date()
        end_date = end_dt.date()
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if end_date.day >= start_date.day:
            months += 1
        months = max(1, months)
        self._computed_billing_count = months
        self._computed_billing_unit = '月'
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
                # 如果按度计费，则显示用量输入并隐藏日期；按小时/天显示日期并相应显示单位
                unit = (charge_item.unit or '').lower()
                if '度' in unit:
                    # hide start/end date controls, show usage input
                    self.billing_start_date.setVisible(False)
                    self.billing_end_date.setVisible(False)
                    self.usage_input.setVisible(True)
                    self.usage_input.setSuffix(' 度')
                else:
                    # show dates, hide usage by default
                    self.billing_start_date.setVisible(True)
                    self.billing_end_date.setVisible(True)
                    self.usage_input.setVisible(True)  # keep usage visible as optional for hours too
                    if '小时' in unit or '时' in unit:
                        self.usage_input.setSuffix(' 小时')
                    elif '天' in unit or '日' in unit:
                        self.usage_input.setSuffix(' 天')
                    else:
                        self.usage_input.setSuffix(' ')

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
            
            # 先计算并展示计费周期（不同单位展示不同）
            self.calculate_billing_months()
            months = self._computed_billing_count if self._computed_billing_unit == '月' else None
            
            # 对于无效日期或计算结果，防御性处理
            if self._computed_billing_count is None:
                self.amount_label.setText('金额: ¥0.00（请检查日期/用量）')
                return
            
            # 计算金额
            if charge_item.charge_type == 'manual':
                amount = self.manual_amount_input.value()
            else:
                # 传入计费开始/结束 datetime，ChargeService 会根据 charge_item.unit 自动处理按日/按月/按年/小时/度
                billing_start_dt = self.billing_start_date.dateTime().toPyDateTime()
                billing_end_dt = self.billing_end_date.dateTime().toPyDateTime()
                usage_val = float(self.usage_input.value()) if self.usage_input.value() and self.usage_input.value() > 0 else None
                amount = ChargeService.calculate_amount(
                    charge_item,
                    resident_area=float(resident.area) if resident.area else 0.0,
                    months=months if months is not None else 1,
                    billing_start_date=billing_start_dt,
                    billing_end_date=billing_end_dt,
                    usage=usage_val
                )
            
            # 根据展示单位格式化周期说明
            unit = getattr(self, '_computed_billing_unit', '月')
            count = getattr(self, '_computed_billing_count', 1)
            if unit == '月':
                suffix = f'（{int(count)}个月）'
            elif unit == '小时':
                suffix = f'（{int(count)}小时）'
            elif unit == '天':
                suffix = f'（{int(count)}天）'
            elif unit == '度':
                suffix = f'（用量 {count:.2f} 度）'
            else:
                suffix = ''
            self.amount_label.setText(f'金额: ¥{amount:.2f}{suffix}')
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
        
        # 先计算计费周期或用量（由 calculate_billing_months 设置 _computed_billing_*）
        self.calculate_billing_months()
        computed_unit = getattr(self, '_computed_billing_unit', '月')
        computed_count = getattr(self, '_computed_billing_count', None)

        # 对于按度计费，不要求开始/结束日期，使用用量即可
        if computed_unit == '度':
            billing_start_date = None
            billing_end_date = None
            months = 0
        else:
            billing_start_date = self.billing_start_date.dateTime().toPyDateTime()
            billing_end_date = self.billing_end_date.dateTime().toPyDateTime()
            if billing_end_date < billing_start_date:
                QMessageBox.warning(self, '提示', '计费结束日期不能早于开始日期')
                return
            # 计算计费周期数（以月为单位存储）
            months = int(computed_count) if computed_unit == '月' else int(computed_count)
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
                usage_for_calc = float(self.usage_input.value()) if hasattr(self, 'usage_input') and self.usage_input.value() > 0 else None
                amount = ChargeService.calculate_amount(
                    charge_item,
                    resident_area=float(resident.area) if resident.area else 0.0,
                    months=months,
                    billing_start_date=billing_start_date_py,
                    billing_end_date=billing_end_date_py,
                    usage=usage_for_calc
                )
            
            # 获取用量（如果适用）
            usage_val = None
            if hasattr(self, 'usage_input') and self.usage_input.value() > 0:
                usage_val = float(self.usage_input.value())

            if self.payment_id:
                # 更新现有账单
                PaymentService.update_payment(
                    payment_id=self.payment_id,
                    resident_id=resident_id,
                    charge_item_id=charge_item_id,
                    period=period,
                    billing_start_date=billing_start_date,
                    billing_end_date=billing_end_date,
                    billing_months=months,
                    amount=amount,
                    usage=usage_val
                )
                QMessageBox.information(self, '成功', f'账单已更新（{months}个月）')
                self.accept()
            else:
                PaymentService.create_payment(
                    resident_id=resident_id,
                    charge_item_id=charge_item_id,
                    period=period,
                    billing_start_date=billing_start_date,
                    billing_end_date=billing_end_date,
                    billing_months=months,
                    amount=amount,
                    usage=usage_val
                )
                QMessageBox.information(self, '成功', f'账单生成成功（{months}个月）')
                self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            import traceback
            error_msg = f'生成账单失败：{str(e)}\n\n详细信息：\n{traceback.format_exc()}'
            QMessageBox.critical(self, '错误', error_msg)

