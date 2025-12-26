"""
住户管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QDoubleSpinBox, QDateEdit, QComboBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime

from services.resident_service import ResidentService


class ResidentDialog(QDialog):
    """住户管理对话框"""
    
    def __init__(self, parent=None, resident_id=None):
        super().__init__(parent)
        self.resident_id = resident_id
        self.init_ui()
        if resident_id:
            self.load_resident()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('住户管理' if not self.resident_id else '编辑住户')
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 房号
        room_layout = QHBoxLayout()
        room_layout.addWidget(QLabel('房号*:'))
        self.room_no_input = QLineEdit()
        self.room_no_input.setPlaceholderText('请输入房号')
        room_layout.addWidget(self.room_no_input)
        layout.addLayout(room_layout)
        
        # 姓名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('姓名*:'))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入姓名')
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 电话
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel('电话:'))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('请输入电话')
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # 面积
        area_layout = QHBoxLayout()
        area_layout.addWidget(QLabel('面积:'))
        self.area_input = QDoubleSpinBox()
        self.area_input.setMinimum(0.0)
        self.area_input.setMaximum(99999.99)
        self.area_input.setDecimals(2)
        self.area_input.setSuffix(' 平方米')
        area_layout.addWidget(self.area_input)
        layout.addLayout(area_layout)
        
        # 入住日期
        move_in_layout = QHBoxLayout()
        move_in_layout.addWidget(QLabel('入住日期:'))
        self.move_in_date = QDateEdit()
        self.move_in_date.setCalendarPopup(True)
        self.move_in_date.setDate(QDate.currentDate())
        self.move_in_date.setDisplayFormat('yyyy-MM-dd')
        move_in_layout.addWidget(self.move_in_date)
        layout.addLayout(move_in_layout)
        
        # 身份（房主/租户）
        identity_layout = QHBoxLayout()
        identity_layout.addWidget(QLabel('身份:'))
        self.identity_combo = QComboBox()
        self.identity_combo.addItem('房主', 'owner')
        self.identity_combo.addItem('租户', 'renter')
        identity_layout.addWidget(self.identity_combo)
        layout.addLayout(identity_layout)
        
        # 房屋类型（住宅/商铺）
        property_layout = QHBoxLayout()
        property_layout.addWidget(QLabel('房屋类型:'))
        self.property_combo = QComboBox()
        self.property_combo.addItem('住宅', 'residential')
        self.property_combo.addItem('商铺', 'commercial')
        property_layout.addWidget(self.property_combo)
        layout.addLayout(property_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')
        self.save_btn.clicked.connect(self.save_resident)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def load_resident(self):
        """加载住户信息"""
        try:
            resident = ResidentService.get_resident_by_id(self.resident_id)
            if resident:
                self.room_no_input.setText(resident.room_no)
                self.name_input.setText(resident.name)
                self.phone_input.setText(resident.phone or '')
                self.area_input.setValue(float(resident.area) if resident.area else 0.0)
                if resident.move_in_date:
                    self.move_in_date.setDate(QDate(
                        resident.move_in_date.year,
                        resident.move_in_date.month,
                        resident.move_in_date.day
                    ))
                # 身份
                if hasattr(resident, 'identity') and resident.identity:
                    idx = 0 if resident.identity == 'owner' else 1
                    self.identity_combo.setCurrentIndex(idx)
                # 房屋类型
                if hasattr(resident, 'property_type') and resident.property_type:
                    pidx = 0 if resident.property_type == 'residential' else 1
                    self.property_combo.setCurrentIndex(pidx)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载住户信息失败：{str(e)}')
    
    def save_resident(self):
        """保存住户"""
        room_no = self.room_no_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        area = self.area_input.value()
        move_in_date = self.move_in_date.date().toPyDate()
        
        if not room_no:
            QMessageBox.warning(self, '提示', '请输入房号')
            return
        
        if not name:
            QMessageBox.warning(self, '提示', '请输入姓名')
            return
        
        try:
            if self.resident_id:
                # 更新
                ResidentService.update_resident(
                    self.resident_id,
                    room_no=room_no,
                    name=name,
                    phone=phone,
                    area=area,
                    move_in_date=move_in_date,
                    identity=self.identity_combo.currentData(),
                    property_type=self.property_combo.currentData()
                )
                QMessageBox.information(self, '成功', '更新成功')
            else:
                # 新增
                ResidentService.create_resident(
                    room_no=room_no,
                    name=name,
                    phone=phone,
                    area=area,
                    move_in_date=move_in_date,
                    identity=self.identity_combo.currentData(),
                    property_type=self.property_combo.currentData()
                )
                QMessageBox.information(self, '成功', '添加成功')
            
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败：{str(e)}')

