"""
收费项目管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QDoubleSpinBox, QComboBox)
from PyQt5.QtCore import Qt

from services.charge_service import ChargeService


class ChargeDialog(QDialog):
    """收费项目管理对话框"""
    
    def __init__(self, parent=None, item_id=None):
        super().__init__(parent)
        self.item_id = item_id
        self.init_ui()
        if item_id:
            self.load_charge_item()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('收费项目管理' if not self.item_id else '编辑收费项目')
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 项目名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('项目名称*:'))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入项目名称')
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 收费类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('收费类型*:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['固定', '按面积', '手动'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 单价/金额
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel('单价/金额*:'))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.0)
        self.price_input.setMaximum(99999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(' 元')
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)
        
        # 单位
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel('单位*:'))
        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)
        self.unit_combo.addItems(['元/月', '元/年', '元/平方米', '元/平方米·月', '元'])
        unit_layout.addWidget(self.unit_combo)
        layout.addLayout(unit_layout)
        
        # 说明标签
        self.info_label = QLabel('固定：单价 × 计费月数\n按面积：单价 × 面积 × 计费月数\n手动：生成账单时手动输入金额')
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')
        self.save_btn.clicked.connect(self.save_charge_item)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.on_type_changed()
    
    def on_type_changed(self):
        """收费类型改变时的处理"""
        type_text = self.type_combo.currentText()
        if type_text == '固定':
            self.price_input.setSuffix(' 元（固定金额）')
        elif type_text == '按面积':
            self.price_input.setSuffix(' 元/平方米')
        else:
            self.price_input.setSuffix(' 元（参考金额）')
    
    def load_charge_item(self):
        """加载收费项目信息"""
        try:
            item = ChargeService.get_charge_item_by_id(self.item_id)
            if item:
                self.name_input.setText(item.name)
                self.price_input.setValue(float(item.price))
                
                type_map = {'fixed': '固定', 'area': '按面积', 'manual': '手动'}
                type_name = type_map.get(item.charge_type, '固定')
                index = self.type_combo.findText(type_name)
                if index >= 0:
                    self.type_combo.setCurrentIndex(index)
                
                # 加载单位
                unit = item.unit or '元/月'
                index = self.unit_combo.findText(unit)
                if index >= 0:
                    self.unit_combo.setCurrentIndex(index)
                else:
                    self.unit_combo.setEditText(unit)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载收费项目信息失败：{str(e)}')
    
    def save_charge_item(self):
        """保存收费项目"""
        name = self.name_input.text().strip()
        price = self.price_input.value()
        type_text = self.type_combo.currentText()
        unit = self.unit_combo.currentText().strip()
        
        if not name:
            QMessageBox.warning(self, '提示', '请输入项目名称')
            return
        
        if price <= 0:
            QMessageBox.warning(self, '提示', '单价/金额必须大于0')
            return
        
        if not unit:
            QMessageBox.warning(self, '提示', '请输入单位')
            return
        
        type_map = {'固定': 'fixed', '按面积': 'area', '手动': 'manual'}
        charge_type = type_map.get(type_text, 'fixed')
        
        try:
            if self.item_id:
                # 更新
                ChargeService.update_charge_item(
                    self.item_id,
                    name=name,
                    price=price,
                    charge_type=charge_type,
                    unit=unit
                )
                QMessageBox.information(self, '成功', '更新成功')
            else:
                # 新增
                ChargeService.create_charge_item(
                    name=name,
                    price=price,
                    charge_type=charge_type,
                    unit=unit
                )
                QMessageBox.information(self, '成功', '添加成功')
            
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败：{str(e)}')

