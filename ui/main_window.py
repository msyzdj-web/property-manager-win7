"""
主窗口界面
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QComboBox, QMessageBox, QLineEdit, QMenuBar, QMenu,
                             QDialog, QFileDialog, QDoubleSpinBox)
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import os
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from services.resident_service import ResidentService
from services.charge_service import ChargeService
from services.payment_service import PaymentService
from models.database import DB_PATH, SessionLocal
from models.payment import Payment
from models.payment_transaction import PaymentTransaction
from utils.logger import logger
from ui.resident_dialog import ResidentDialog
from ui.charge_dialog import ChargeDialog
from ui.payment_dialog import PaymentDialog
from ui.receipt_dialog import ReceiptDialog
from ui.pay_dialog import PayDialog
from ui.import_dialog import ImportDialog
from ui.export_dialog import ExportDialog
from ui.backup_dialog import BackupDialog

# Small helper QTableWidgetItem subclass to support custom sort keys
class SortableItem(QTableWidgetItem):
    def __init__(self, text, sort_key=None):
        super().__init__(str(text))
        self.sort_key = sort_key if sort_key is not None else text

    def __lt__(self, other):
        try:
            a = self.sort_key
            b = other.sort_key
            # try direct compare first (numbers, tuples)
            return a < b
        except Exception:
            try:
                return str(self.text()) < str(other.text())
            except Exception:
                return False


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
        self.apply_stylesheet()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('四川盛涵物业缴费系统')
        self.setGeometry(100, 100, 1200, 700)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 头部区域：LOGO + 标题
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        # LOGO
        logo_label = QLabel()
        logo_path = "logo.jpg"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # 缩放到合适高度，例如 48px
            logo_label.setPixmap(pixmap.scaledToHeight(48, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)
        
        # 标题
        title_label = QLabel('盛世金龙小区')
        title_label.setObjectName("title_label")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        # main_layout.addWidget(title_label) # Removed old direct add

        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 住户管理标签页
        self.create_resident_tab()
        
        # 收费项目管理标签页
        self.create_charge_tab()
        
        # 收费管理标签页
        self.create_payment_tab()

        
        # 欠费查询标签页
        self.create_unpaid_tab()
    
    def apply_stylesheet(self):
        """应用美化样式表"""
        style = """
            QMainWindow {
                background-color: #f5f6f8;
            }
            QLabel {
                color: #333;
                font-family: "Microsoft YaHei";
            }
            /* 标题样式 */
            #title_label {
                color: #1a237e;
                font-size: 26px;
                font-weight: bold;
                padding-left: 10px;
            }
            /* 按钮通用样式 */
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-family: "Microsoft YaHei";
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
            QPushButton:pressed {
                background-color: #1976d2;
            }
            /* 特殊按钮样式 - 删除/危险 */
            QPushButton[text^="删除"] {
                background-color: #ff5252;
            }
            QPushButton[text^="删除"]:hover {
                background-color: #ff867f;
            }
            /* 表格样式 */
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
                selection-color: #333;
            }
            QHeaderView::section {
                background-color: #fafafa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #eeeeee;
                font-weight: bold;
                color: #666;
            }
            /* 输入框和下拉框 */
            QLineEdit, QComboBox {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2196f3;
            }
            /* 标签页 */
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background: white;
                border-radius: 4px;
                top: -1px; 
            }
            QTabBar::tab {
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #666;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                color: #2196f3;
                font-weight: bold;
            }
        """
        self.setStyleSheet(style)
    
    def create_resident_tab(self):
        """创建住户管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        self.add_resident_btn = QPushButton('新增住户')
        self.edit_resident_btn = QPushButton('编辑住户')
        self.delete_resident_btn = QPushButton('删除住户')
        self.import_resident_btn = QPushButton('批量导入')
        self.refresh_resident_btn = QPushButton('刷新')
        
        self.add_resident_btn.clicked.connect(self.add_resident)
        self.edit_resident_btn.clicked.connect(self.edit_resident)
        self.delete_resident_btn.clicked.connect(self.delete_resident)
        self.import_resident_btn.clicked.connect(self.import_residents)
        self.refresh_resident_btn.clicked.connect(self.load_residents)
        
        toolbar_layout.addWidget(self.add_resident_btn)
        toolbar_layout.addWidget(self.edit_resident_btn)
        toolbar_layout.addWidget(self.delete_resident_btn)
        toolbar_layout.addWidget(self.import_resident_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.refresh_resident_btn)
        layout.addLayout(toolbar_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('搜索:'))
        self.resident_search = QLineEdit()
        self.resident_search.setPlaceholderText('输入房号或姓名搜索')
        self.resident_search.textChanged.connect(self.search_residents)
        search_layout.addWidget(self.resident_search)
        layout.addLayout(search_layout)
        
        # 住户列表表格
        self.resident_table = QTableWidget()
        self.resident_table.setColumnCount(8)
        self.resident_table.setHorizontalHeaderLabels(['ID', '房号', '姓名', '电话', '面积', '入住日期', '身份', '状态'])
        self.resident_table.horizontalHeader().setStretchLastSection(True)
        # 启用表头点击排序
        self.resident_table.setSortingEnabled(True)
        self.resident_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.resident_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.resident_table)
        
        self.tab_widget.addTab(tab, '住户管理')

    # 金额显示：四舍五入到整数元并返回字符串
    def _fmt_amount_int(self, value):
        try:
            if value is None:
                return "0"
            v = Decimal(str(value))
            return str(int(v.quantize(0, rounding=ROUND_HALF_UP)))
        except Exception:
            try:
                return str(int(round(float(value))))
            except Exception:
                return str(value)
    
    def create_charge_tab(self):
        """创建收费项目管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        self.add_charge_btn = QPushButton('新增收费项目')
        self.edit_charge_btn = QPushButton('编辑收费项目')
        self.delete_charge_btn = QPushButton('删除收费项目')
        self.refresh_charge_btn = QPushButton('刷新')
        
        self.add_charge_btn.clicked.connect(self.add_charge_item)
        self.edit_charge_btn.clicked.connect(self.edit_charge_item)
        self.delete_charge_btn.clicked.connect(self.delete_charge_item)
        self.refresh_charge_btn.clicked.connect(self.load_charge_items)
        
        toolbar_layout.addWidget(self.add_charge_btn)
        toolbar_layout.addWidget(self.edit_charge_btn)
        toolbar_layout.addWidget(self.delete_charge_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.refresh_charge_btn)
        layout.addLayout(toolbar_layout)
        
        # 收费项目列表表格
        self.charge_table = QTableWidget()
        self.charge_table.setColumnCount(6)
        self.charge_table.setHorizontalHeaderLabels(['ID', '项目名称', '单价/金额', '单位', '收费类型', '状态'])
        self.charge_table.horizontalHeader().setStretchLastSection(True)
        self.charge_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.charge_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.charge_table)
        
        self.tab_widget.addTab(tab, '收费项目管理')
    
    def create_payment_tab(self):
        """创建收费管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        self.add_payment_btn = QPushButton('生成账单')
        self.edit_payment_btn = QPushButton('编辑账单')
        self.mark_paid_btn = QPushButton('缴费')
        self.delete_payment_btn = QPushButton('批量删除')
        self.print_receipt_btn = QPushButton('打印收据')
        self.refresh_payment_btn = QPushButton('刷新')
        
        self.add_payment_btn.clicked.connect(self.add_payment)
        self.edit_payment_btn.clicked.connect(self.edit_payment)
        self.mark_paid_btn.clicked.connect(self.mark_payment_paid)
        self.delete_payment_btn.clicked.connect(self.delete_payment)
        self.print_receipt_btn.clicked.connect(self.print_receipt)
        # 合并打印按钮
        self.merge_print_btn = QPushButton('合并打印')
        self.merge_print_btn.clicked.connect(self.merge_print_receipts)
        toolbar_layout.addWidget(self.merge_print_btn)
        self.refresh_payment_btn.clicked.connect(self.load_payments)
        
        self.batch_payment_btn = QPushButton('批量生成')
        self.export_payment_btn = QPushButton('导出记录')
        self.report_btn = QPushButton('生成报表')
        
        toolbar_layout.addWidget(self.add_payment_btn)
        toolbar_layout.addWidget(self.edit_payment_btn)
        toolbar_layout.addWidget(self.batch_payment_btn)
        toolbar_layout.addWidget(self.mark_paid_btn)
        toolbar_layout.addWidget(self.delete_payment_btn)
        toolbar_layout.addWidget(self.print_receipt_btn)
        toolbar_layout.addWidget(self.export_payment_btn)
        toolbar_layout.addWidget(self.report_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.refresh_payment_btn)
        
        self.batch_payment_btn.clicked.connect(self.batch_create_payments)
        self.export_payment_btn.clicked.connect(self.export_payments)
        self.report_btn.clicked.connect(self.generate_report)
        # 新增年统计按钮
        self.year_report_btn = QPushButton('年统计')
        self.year_report_btn.clicked.connect(self.generate_year_report)
        toolbar_layout.addWidget(self.year_report_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 周期选择和搜索
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel('缴费周期:'))
        self.period_combo = QComboBox()
        self.period_combo.currentTextChanged.connect(self.load_payments)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()
        period_layout.addWidget(QLabel('搜索:'))
        self.payment_search = QLineEdit()
        self.payment_search.setPlaceholderText('输入房号、姓名或收费项目搜索')
        self.payment_search.textChanged.connect(self.search_payments)
        period_layout.addWidget(self.payment_search)
        layout.addLayout(period_layout)
        
        # 缴费记录列表表格
        self.payment_table = QTableWidget()
        # 新增“已缴金额”列（在金额后）
        self.payment_table.setColumnCount(11)
        self.payment_table.setHorizontalHeaderLabels(['ID', '房号', '姓名', '收费项目', '计费周期', '总月数', '已缴月数', '金额', '已缴金额', '缴费状态', '缴费时间'])
        self.payment_table.horizontalHeader().setStretchLastSection(True)
        self.payment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.payment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.payment_table)
        
        self.tab_widget.addTab(tab, '收费管理')
    
    def create_unpaid_tab(self):
        """创建欠费查询标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 周期选择
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel('查询周期:'))
        self.unpaid_period_combo = QComboBox()
        self.unpaid_period_combo.currentTextChanged.connect(self.load_unpaid)
        period_layout.addWidget(self.unpaid_period_combo)
        period_layout.addStretch()
        period_layout.addWidget(QLabel('搜索:'))
        self.unpaid_search = QLineEdit()
        self.unpaid_search.setPlaceholderText('输入房号、姓名或收费项目搜索')
        self.unpaid_search.textChanged.connect(self.load_unpaid)
        period_layout.addWidget(self.unpaid_search)
        period_layout.addStretch()
        
        self.export_unpaid_btn = QPushButton('导出欠费清单')
        self.export_unpaid_btn.clicked.connect(self.export_unpaid_list)
        period_layout.addWidget(self.export_unpaid_btn)
        
        # 统计信息
        self.unpaid_stats_label = QLabel('')
        period_layout.addWidget(self.unpaid_stats_label)
        layout.addLayout(period_layout)
        
        # 欠费列表表格
        self.unpaid_table = QTableWidget()
        self.unpaid_table.setColumnCount(7)
        self.unpaid_table.setHorizontalHeaderLabels(['ID', '房号', '姓名', '收费项目', '周期', '金额', '生成时间'])
        self.unpaid_table.horizontalHeader().setStretchLastSection(True)
        self.unpaid_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.unpaid_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.unpaid_table)
        
        self.tab_widget.addTab(tab, '欠费查询')
    
    def load_data(self):
        """加载所有数据"""
        self.load_residents()
        self.load_charge_items()
        self.load_periods()
        self.load_payments()
        self.load_unpaid()
    
    def load_residents(self):
        """加载住户列表"""
        try:
            residents = ResidentService.get_all_residents()
            self.resident_table.setRowCount(len(residents))
            
            for row, resident in enumerate(residents):
                # ID 列使用可排序的整数 key
                try:
                    id_key = int(resident.id)
                except Exception:
                    id_key = resident.id
                self.resident_table.setItem(row, 0, SortableItem(str(resident.id), sort_key=id_key))
                # 房号解析为整数元组作为排序 key，例如 "1-1-1001" -> (1,1,1001)
                def _room_key(s):
                    parts = str(s).split('-')
                    key = []
                    for p in parts:
                        try:
                            key.append(int(p))
                        except Exception:
                            key.append(p)
                    return tuple(key)
                room_display = getattr(resident, 'full_room_no', resident.room_no)
                self.resident_table.setItem(row, 1, SortableItem(room_display, sort_key=_room_key(room_display)))
                self.resident_table.setItem(row, 2, QTableWidgetItem(resident.name))
                self.resident_table.setItem(row, 3, QTableWidgetItem(resident.phone or ''))
                self.resident_table.setItem(row, 4, QTableWidgetItem(str(float(resident.area) if resident.area else 0.0)))
                self.resident_table.setItem(row, 5, QTableWidgetItem(
                    resident.move_in_date.strftime('%Y-%m-%d') if resident.move_in_date else ''))
                # 身份列
                identity_text = '房主' if getattr(resident, 'identity', 'owner') == 'owner' else '租户'
                self.resident_table.setItem(row, 6, QTableWidgetItem(identity_text))
                self.resident_table.setItem(row, 7, QTableWidgetItem('正常' if resident.status == 1 else '停用'))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载住户列表失败：{str(e)}')
    
    def search_residents(self):
        """搜索住户"""
        keyword = self.resident_search.text().strip()
        if not keyword:
            self.load_residents()
            return
        
        try:
            residents = ResidentService.search_residents(keyword)
            self.resident_table.setRowCount(len(residents))
            
            for row, resident in enumerate(residents):
                try:
                    id_key = int(resident.id)
                except Exception:
                    id_key = resident.id
                self.resident_table.setItem(row, 0, SortableItem(str(resident.id), sort_key=id_key))
                def _room_key(s):
                    parts = str(s).split('-')
                    key = []
                    for p in parts:
                        try:
                            key.append(int(p))
                        except Exception:
                            key.append(p)
                    return tuple(key)
                room_display = getattr(resident, 'full_room_no', resident.room_no)
                self.resident_table.setItem(row, 1, SortableItem(room_display, sort_key=_room_key(room_display)))
                self.resident_table.setItem(row, 2, QTableWidgetItem(resident.name))
                self.resident_table.setItem(row, 3, QTableWidgetItem(resident.phone or ''))
                self.resident_table.setItem(row, 4, QTableWidgetItem(str(float(resident.area) if resident.area else 0.0)))
                self.resident_table.setItem(row, 5, QTableWidgetItem(
                    resident.move_in_date.strftime('%Y-%m-%d') if resident.move_in_date else ''))
                self.resident_table.setItem(row, 6, QTableWidgetItem('正常' if resident.status == 1 else '停用'))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'搜索失败：{str(e)}')
    
    def add_resident(self):
        """新增住户"""
        dialog = ResidentDialog(self)
        if dialog.exec_() == ResidentDialog.Accepted:
            self.load_residents()
    
    def edit_resident(self):
        """编辑住户"""
        selected_rows = self.resident_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要编辑的住户')
            return
        
        resident_id = int(self.resident_table.item(selected_rows[0].row(), 0).text())
        dialog = ResidentDialog(self, resident_id=resident_id)
        if dialog.exec_() == ResidentDialog.Accepted:
            self.load_residents()
    
    def delete_resident(self):
        """删除住户"""
        selected_ranges = self.resident_table.selectionModel().selectedRows()
        if not selected_ranges:
            QMessageBox.warning(self, '提示', '请选择要删除的住户（可多选）')
            return

        resident_ids = []
        room_nos = []
        for idx in selected_ranges:
            r = idx.row()
            resident_ids.append(int(self.resident_table.item(r, 0).text()))
            room_nos.append(self.resident_table.item(r, 1).text())
        # 统计将被删除的相关缴费记录数与流水数，提示用户
        db = SessionLocal()
        try:
            payments = db.query(Payment).filter(Payment.resident_id.in_(resident_ids)).all()
            payment_ids = [p.id for p in payments if p.id is not None]
            payment_count = len(payment_ids)
            tx_count = 0
            if payment_ids:
                tx_count = db.query(PaymentTransaction).filter(PaymentTransaction.payment_id.in_(payment_ids)).count()
        finally:
            db.close()

        # 使用自定义的可滚动确认对话框，避免大量项时按钮被遮挡
        from ui.confirm_delete_dialog import ConfirmDeleteDialog
        dlg = ConfirmDeleteDialog(self, items=room_nos, title='确认删除住户')

        # 在对话框外再弹一层强确认，显示将删除的记录统计和备份提示
        if dlg.exec_() == ConfirmDeleteDialog.Accepted:
            msg = f"将删除 {len(resident_ids)} 个住户，及其关联的 {payment_count} 条缴费记录和 {tx_count} 条流水。\n\n操作前会自动备份数据库，确定继续吗？"
            reply = QMessageBox.question(self, '最终确认', msg, QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

            # 备份数据库文件
            try:
                import shutil, os, datetime
                os.makedirs('exports', exist_ok=True)
                ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                backup_path = os.path.join('exports', f'property_db_backup_{ts}.db')
                shutil.copy2(DB_PATH, backup_path)
            except Exception as e:
                QMessageBox.warning(self, '警告', f'无法创建数据库备份：{e}\n继续删除可能无法恢复。')

            failed = []
            for rid in resident_ids:
                try:
                    ResidentService.delete_resident(rid)
                except Exception as e:
                    failed.append((rid, str(e)))

            if not failed:
                QMessageBox.information(self, '成功', f'已删除选中住户（并删除其关联缴费与流水）。\n备份：{backup_path if os.path.exists(backup_path) else "未生成"}')
            else:
                msgs = '\n'.join([f"{rid}: {err}" for rid, err in failed])
                QMessageBox.warning(self, '部分失败', f'部分住户删除失败：\n{msgs}')
            self.load_residents()
    
    def load_charge_items(self):
        """加载收费项目列表"""
        try:
            charge_items = ChargeService.get_all_charge_items()
            self.charge_table.setRowCount(len(charge_items))
            
            for row, item in enumerate(charge_items):
                self.charge_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
                self.charge_table.setItem(row, 1, QTableWidgetItem(item.name))
                self.charge_table.setItem(row, 2, QTableWidgetItem(str(float(item.price))))
                self.charge_table.setItem(row, 3, QTableWidgetItem(item.unit or '元/月'))
                self.charge_table.setItem(row, 4, QTableWidgetItem(item.get_charge_type_name()))
                self.charge_table.setItem(row, 5, QTableWidgetItem('启用' if item.status == 1 else '停用'))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载收费项目列表失败：{str(e)}')
    
    def add_charge_item(self):
        """新增收费项目"""
        dialog = ChargeDialog(self)
        if dialog.exec_() == ChargeDialog.Accepted:
            self.load_charge_items()
    
    def edit_charge_item(self):
        """编辑收费项目"""
        selected_rows = self.charge_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要编辑的收费项目')
            return
        
        item_id = int(self.charge_table.item(selected_rows[0].row(), 0).text())
        dialog = ChargeDialog(self, item_id=item_id)
        if dialog.exec_() == ChargeDialog.Accepted:
            self.load_charge_items()
    
    def delete_charge_item(self):
        """删除收费项目"""
        selected_rows = self.charge_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要删除的收费项目')
            return
        
        item_id = int(self.charge_table.item(selected_rows[0].row(), 0).text())
        item_name = self.charge_table.item(selected_rows[0].row(), 1).text()
        
        reply = QMessageBox.question(self, '确认', f'确定要删除收费项目 {item_name} 吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                ChargeService.delete_charge_item(item_id)
                QMessageBox.information(self, '成功', '删除成功')
                self.load_charge_items()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'删除失败：{str(e)}')
    
    def load_periods(self):
        """加载周期列表"""
        try:
            payments = PaymentService.get_all_payments()
            periods = set()
            for payment in payments:
                periods.add(payment.period)
            
            periods = sorted(list(periods), reverse=True)
            
            # 如果没有记录，添加当前月份
            current_period = datetime.now().strftime('%Y-%m')
            if current_period not in periods:
                periods.insert(0, current_period)
            
            self.period_combo.clear()
            self.period_combo.addItems(periods)
            
            self.unpaid_period_combo.clear()
            self.unpaid_period_combo.addItems(periods)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载周期列表失败：{str(e)}')
    
    def load_payments(self):
        """加载缴费记录列表"""
        try:
            period = self.period_combo.currentText()
            if not period:
                return
            
            payments = PaymentService.get_payments_by_period(period)
            self.payment_table.setRowCount(len(payments))

            # 根据 payments 中最常见的单位调整表头（尽量反映度/小时/天/月）
            try:
                units = [ (p.charge_item.unit or '').lower() if p.charge_item else '' for p in payments ]
                uniq = set(units)
                if len(uniq) == 1:
                    u = list(uniq)[0]
                    if '度' in u:
                        header_total = '总度数'
                        header_paid = '已缴度数'
                    elif '小时' in u or '时' in u:
                        header_total = '总小时数'
                        header_paid = '已缴小时数'
                    elif '天' in u or '日' in u:
                        header_total = '总天数'
                        header_paid = '已缴天数'
                    else:
                        header_total = '总月数'
                        header_paid = '已缴月数'
                else:
                    # 混合单位时使用通用表头
                    header_total = '总计'
                    header_paid = '已缴'
                # 更新表头显示（列 5 为总，列6 为已缴）
                try:
                    self.payment_table.horizontalHeaderItem(5).setText(header_total)
                    self.payment_table.horizontalHeaderItem(6).setText(header_paid)
                except Exception:
                    pass
            except Exception:
                pass
            
            for row, payment in enumerate(payments):
                self.payment_table.setItem(row, 0, QTableWidgetItem(str(payment.id)))
                self.payment_table.setItem(row, 1, QTableWidgetItem(getattr(payment.resident, 'full_room_no', payment.resident.room_no)))
                self.payment_table.setItem(row, 2, QTableWidgetItem(payment.resident.name))
                self.payment_table.setItem(row, 3, QTableWidgetItem(payment.charge_item.name))
                # 计费周期显示：对不同单位展示为 月/天/小时/度 等
                billing_period = f"{payment.billing_start_date.strftime('%Y-%m-%d %H:%M') } 至 {payment.billing_end_date.strftime('%Y-%m-%d %H:%M')}" if payment.billing_start_date and payment.billing_end_date else payment.period
                self.payment_table.setItem(row, 4, QTableWidgetItem(billing_period))

                unit = (payment.charge_item.unit or '').lower() if payment.charge_item else ''
                # 按小时
                if ('小时' in unit or '时' in unit) and payment.billing_start_date and payment.billing_end_date:
                    seconds = (payment.billing_end_date - payment.billing_start_date).total_seconds()
                    hours = max(1, int((seconds + 3599) // 3600))
                    self.payment_table.setItem(row, 5, QTableWidgetItem(f"{hours} 小时"))
                    # 已缴按小时：以已缴金额 / 单价 计算已缴小时数（向下取整）
                    try:
                        paid_hours = int((float(payment.paid_amount or 0.0) / float(payment.charge_item.price)) if payment.charge_item and payment.charge_item.price else 0)
                    except Exception:
                        paid_hours = 0
                    self.payment_table.setItem(row, 6, QTableWidgetItem(f"{paid_hours} 小时"))
                # 按天
                elif ('天' in unit or '日' in unit) and payment.billing_start_date and payment.billing_end_date:
                    days = (payment.billing_end_date.date() - payment.billing_start_date.date()).days + 1
                    days = max(1, days)
                    self.payment_table.setItem(row, 5, QTableWidgetItem(f"{days} 天"))
                    # 已缴按天：以已缴金额 / 单价 计算已缴天数（向下取整）
                    try:
                        paid_days = int((float(payment.paid_amount or 0.0) / float(payment.charge_item.price)) if payment.charge_item and payment.charge_item.price else 0)
                    except Exception:
                        paid_days = 0
                    self.payment_table.setItem(row, 6, QTableWidgetItem(f"{paid_days} 天"))
                # 按度（显示用量）
                elif '度' in unit:
                    usage_text = f"{payment.usage:.2f} 度" if getattr(payment, 'usage', None) is not None else '-'
                    self.payment_table.setItem(row, 5, QTableWidgetItem(usage_text))
                    # 已缴按度：以已缴金额 / 单价 计算已缴度数（保留2位）
                    try:
                        paid_degrees = (float(payment.paid_amount or 0.0) / float(payment.charge_item.price)) if payment.charge_item and payment.charge_item.price else 0.0
                        paid_degrees_text = f"{paid_degrees:.2f} 度"
                    except Exception:
                        paid_degrees_text = "0.00 度"
                    self.payment_table.setItem(row, 6, QTableWidgetItem(paid_degrees_text))
                else:
                    self.payment_table.setItem(row, 5, QTableWidgetItem(f"{payment.billing_months} 月"))
                    self.payment_table.setItem(row, 6, QTableWidgetItem(f"{payment.paid_months} 月"))
                self.payment_table.setItem(row, 6, QTableWidgetItem(f"{payment.paid_months} 月"))
                # 计算并显示按单位感知的金额（避免旧数据未正确计算时显示错误）
                try:
                    resident_area = float(payment.resident.area) if getattr(payment.resident, 'area', None) else 0.0
                except Exception:
                    resident_area = 0.0
                try:
                    calc_amount = ChargeService.calculate_amount(
                        payment.charge_item,
                        resident_area=resident_area,
                        months=payment.billing_months if getattr(payment, 'billing_months', None) else 1,
                        billing_start_date=payment.billing_start_date,
                        billing_end_date=payment.billing_end_date,
                        usage=getattr(payment, 'usage', None)
                    )
                except Exception:
                    calc_amount = payment.amount or 0.0
                self.payment_table.setItem(row, 7, QTableWidgetItem(self._fmt_amount_int(calc_amount)))
                # 已缴金额列
                self.payment_table.setItem(row, 8, QTableWidgetItem(self._fmt_amount_int(payment.paid_amount)))
                # 缴费状态
                if payment.paid == 1:
                    status_text = '已缴费'
                elif payment.paid_months > 0:
                    status_text = f'部分缴费({payment.paid_months}/{payment.billing_months})'
                else:
                    status_text = '未缴费'
                self.payment_table.setItem(row, 9, QTableWidgetItem(status_text))
                self.payment_table.setItem(row, 10, QTableWidgetItem(
                    payment.paid_time.strftime('%Y-%m-%d %H:%M:%S') if payment.paid_time else ''))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载缴费记录失败：{str(e)}')
    
    def add_payment(self):
        """生成账单"""
        logger.log_operation("UI_ADD_PAYMENT_START")
        try:
            dialog = PaymentDialog(self)
            if dialog.exec_() == PaymentDialog.Accepted:
                self.load_periods()
                self.load_payments()
                logger.log_operation("UI_ADD_PAYMENT_SUCCESS")
            else:
                logger.log_operation("UI_ADD_PAYMENT_CANCELLED")
        except Exception as e:
            logger.log_error(e, "UI_ADD_PAYMENT")
            QMessageBox.critical(self, '错误', f'生成账单失败：{str(e)}')

    def edit_payment(self):
        """编辑选中的账单"""
        try:
            selected_rows = self.payment_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, '提示', '请选择要编辑的账单')
                return

            payment_id = int(self.payment_table.item(selected_rows[0].row(), 0).text())
            dialog = PaymentDialog(self)
            # 加载账单到对话框以编辑
            dialog.load_payment(payment_id)
            if dialog.exec_() == PaymentDialog.Accepted:
                self.load_periods()
                self.load_payments()
        except Exception as e:
            logger.log_error(e, "UI_EDIT_PAYMENT")
            QMessageBox.critical(self, '错误', f'编辑账单失败：{str(e)}')
    
    def mark_payment_paid(self):
        """标记已缴费（支持部分缴费）"""
        selected_rows = self.payment_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要缴费的记录')
            return
        
        payment_id = int(self.payment_table.item(selected_rows[0].row(), 0).text())
        
        # 打开缴费对话框
        dialog = PayDialog(self, payment_id=payment_id)
        if dialog.exec_() == PayDialog.Accepted:
            self.load_payments()
            self.load_unpaid()
    
    def delete_payment(self):
        """删除账单"""
        logger.log_operation("UI_DELETE_PAYMENT_START")
        try:
            selected_ranges = self.payment_table.selectionModel().selectedRows()
            if not selected_ranges:
                logger.log_operation("UI_DELETE_PAYMENT_NO_SELECTION")
                QMessageBox.warning(self, '提示', '请选择要删除的账单（可多选）')
                return

            payment_ids = []
            items = []
            for idx in selected_ranges:
                r = idx.row()
                payment_ids.append(int(self.payment_table.item(r, 0).text()))
                items.append(f"{self.payment_table.item(r,1).text()} {self.payment_table.item(r,4).text()}")

            # 使用可滚动的确认对话框，避免长列表导致按钮不可见的问题
            from ui.confirm_delete_dialog import ConfirmDeleteDialog
            dlg = ConfirmDeleteDialog(self, items=items, title='确认删除账单')
            if dlg.exec_() == ConfirmDeleteDialog.Accepted:
                logger.log_operation("UI_DELETE_PAYMENT_CONFIRMED", f"payment_ids={payment_ids}")
                try:
                    # 使用批量删除以避免死锁和提高性能
                    deleted_count, failed = PaymentService.delete_payments_batch(payment_ids)

                    if not failed:
                        logger.log_operation("UI_DELETE_PAYMENT_SUCCESS", f"deleted {deleted_count} payments")
                        QMessageBox.information(self, '成功', f'已删除 {deleted_count} 个账单')
                    else:
                        logger.log_operation("UI_DELETE_PAYMENT_PARTIAL", f"deleted {deleted_count}, failed {len(failed)}")
                        msgs = "\n".join([f"{pid}: {err}" for pid, err in failed])
                        QMessageBox.warning(self, '部分失败', f'成功删除 {deleted_count} 个账单，失败 {len(failed)} 个：\n{msgs}')
                except Exception as e:
                    logger.log_error(e, "UI_DELETE_PAYMENT_BATCH_FAILED")
                    QMessageBox.critical(self, '错误', f'删除账单时发生错误：{str(e)}')

                self.load_payments()
                self.load_unpaid()
            else:
                logger.log_operation("UI_DELETE_PAYMENT_CANCELLED")
        except Exception as e:
            logger.log_error(e, "UI_DELETE_PAYMENT")
            QMessageBox.critical(self, '错误', f'删除账单时发生错误：{str(e)}')
    
    def search_payments(self):
        """搜索账单"""
        keyword = self.payment_search.text().strip()
        period = self.period_combo.currentText()
        
        if not keyword:
            self.load_payments()
            return
        
        if not period:
            QMessageBox.warning(self, '提示', '请先选择缴费周期')
            return
        
        try:
            payments = PaymentService.search_payments(keyword, period=period)
            self.payment_table.setRowCount(len(payments))
            
            for row, payment in enumerate(payments):
                # Match the same columns/format as load_payments to avoid misalignment
                self.payment_table.setItem(row, 0, QTableWidgetItem(str(payment.id)))
                self.payment_table.setItem(row, 1, QTableWidgetItem(getattr(payment.resident, 'full_room_no', payment.resident.room_no)))
                self.payment_table.setItem(row, 2, QTableWidgetItem(payment.resident.name))
                self.payment_table.setItem(row, 3, QTableWidgetItem(payment.charge_item.name))
                # 计费周期显示：优先显示起止日期范围，否则显示 period 文本
                billing_period = f"{payment.billing_start_date.strftime('%Y-%m-%d')} 至 {payment.billing_end_date.strftime('%Y-%m-%d')}" if payment.billing_start_date and payment.billing_end_date else payment.period
                self.payment_table.setItem(row, 4, QTableWidgetItem(billing_period))
                # 总月数 / 已缴月数 / 金额 / 已缴金额 / 状态 / 缴费时间
                try:
                    self.payment_table.setItem(row, 5, QTableWidgetItem(f"{payment.billing_months} 月"))
                except Exception:
                    self.payment_table.setItem(row, 5, QTableWidgetItem(''))
                try:
                    self.payment_table.setItem(row, 6, QTableWidgetItem(f"{payment.paid_months} 月"))
                except Exception:
                    self.payment_table.setItem(row, 6, QTableWidgetItem(''))
                self.payment_table.setItem(row, 7, QTableWidgetItem(self._fmt_amount_int(payment.amount)))
                self.payment_table.setItem(row, 8, QTableWidgetItem(self._fmt_amount_int(payment.paid_amount)))
                # 缴费状态文本
                if getattr(payment, 'paid', 0) == 1:
                    status_text = '已缴费'
                elif getattr(payment, 'paid_months', 0) > 0:
                    status_text = f'部分缴费({payment.paid_months}/{payment.billing_months})'
                else:
                    status_text = '未缴费'
                self.payment_table.setItem(row, 9, QTableWidgetItem(status_text))
                self.payment_table.setItem(row, 10, QTableWidgetItem(
                    payment.paid_time.strftime('%Y-%m-%d %H:%M:%S') if payment.paid_time else ''))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'搜索失败：{str(e)}')
    
    def print_receipt(self):
        """打印收据"""
        selected_rows = self.payment_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, '提示', '请选择要打印的缴费记录')
            return
        
        payment_id = int(self.payment_table.item(selected_rows[0].row(), 0).text())
        
        dialog = ReceiptDialog(self, payment_id=payment_id)
        dialog.exec_()

    def merge_print_receipts(self):
        """合并打印选中多笔账单到一张收据"""
        selected_ranges = self.payment_table.selectionModel().selectedRows()
        if not selected_ranges:
            QMessageBox.warning(self, '提示', '请选择要合并打印的账单（可多选）')
            return

        payment_ids = []
        for idx in selected_ranges:
            r = idx.row()
            payment_ids.append(int(self.payment_table.item(r, 0).text()))
        
        # 收集 payment 对象
        payments = []
        for pid in payment_ids:
            p = PaymentService.get_payment_by_id(pid)
            if p:
                payments.append(p)

        try:
            from utils.printer import ReceiptPrinter
            import tempfile, os
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QFileDialog
            from PyQt5.QtGui import QPixmap
            
            # 弹出预览对话框
            dlg = QDialog(self)
            dlg.setWindowTitle('合并收据预览')
            dlg.resize(1000, 600)
            vbox = QVBoxLayout(dlg)
            
            # 纸张选择
            hbox_ctrl = QHBoxLayout()
            hbox_ctrl.addWidget(QLabel("纸张尺寸:"))
            combo_size = QComboBox()
            combo_size.addItems(['收据纸 (241×93mm)'])
            combo_size.setCurrentText('收据纸 (241×93mm)')
            hbox_ctrl.addWidget(combo_size)
            # 顶部偏移微调（mm）
            hbox_ctrl.addWidget(QLabel(" 上移(mm):"))
            combo_top_offset = QDoubleSpinBox()
            combo_top_offset.setRange(-10.0, 20.0)
            combo_top_offset.setSingleStep(0.5)
            combo_top_offset.setValue(3.0)
            hbox_ctrl.addWidget(combo_top_offset)
            # 标题缩放系数
            hbox_ctrl.addWidget(QLabel(" 标题缩放:"))
            combo_comp_scale = QDoubleSpinBox()
            combo_comp_scale.setRange(0.6, 1.2)
            combo_comp_scale.setSingleStep(0.01)
            combo_comp_scale.setValue(0.95)
            hbox_ctrl.addWidget(combo_comp_scale)
            # 内容字号缩放系数
            hbox_ctrl.addWidget(QLabel(" 内容字号:"))
            combo_content_scale = QDoubleSpinBox()
            combo_content_scale.setRange(0.7, 1.3)
            combo_content_scale.setSingleStep(0.01)
            combo_content_scale.setValue(1.00)
            hbox_ctrl.addWidget(combo_content_scale)
            # 左右边距
            hbox_ctrl.addWidget(QLabel(" 左边距(mm):"))
            combo_left_margin = QDoubleSpinBox()
            combo_left_margin.setRange(0.0, 20.0)
            combo_left_margin.setSingleStep(0.5)
            combo_left_margin.setValue(4.0)
            hbox_ctrl.addWidget(combo_left_margin)
            hbox_ctrl.addWidget(QLabel(" 右边距(mm):"))
            combo_right_margin = QDoubleSpinBox()
            combo_right_margin.setRange(0.0, 20.0)
            combo_right_margin.setSingleStep(0.5)
            combo_right_margin.setValue(8.0)
            hbox_ctrl.addWidget(combo_right_margin)
            # 尝试加载用户设置并应用到合并预览控件（放在控件创建后）
            try:
                cfg = Path.home() / '.property_manager_settings.json'
                if cfg.exists():
                    data = json.loads(cfg.read_text(encoding='utf-8'))
                    if 'top_offset_mm' in data:
                        combo_top_offset.setValue(float(data.get('top_offset_mm', combo_top_offset.value())))
                    if 'company_font_scale_adj' in data:
                        combo_comp_scale.setValue(float(data.get('company_font_scale_adj', combo_comp_scale.value())))
                    if 'content_font_scale' in data:
                        try:
                            combo_content_scale.setValue(float(data.get('content_font_scale', combo_content_scale.value())))
                        except Exception:
                            pass
                    # 左右边距（若存在）
                    if 'left_margin_mm' in data and 'right_margin_mm' in data:
                        try:
                            combo_left_margin.setValue(float(data.get('left_margin_mm', combo_left_margin.value())))
                            combo_right_margin.setValue(float(data.get('right_margin_mm', combo_right_margin.value())))
                        except Exception:
                            pass
            except Exception:
                pass
            # 标题缩放系数
            hbox_ctrl.addWidget(QLabel(" 标题缩放:"))
            combo_comp_scale = QDoubleSpinBox()
            combo_comp_scale.setRange(0.6, 1.2)
            combo_comp_scale.setSingleStep(0.01)
            combo_comp_scale.setValue(0.95)
            hbox_ctrl.addWidget(combo_comp_scale)
            # 左右边距
            hbox_ctrl.addWidget(QLabel(" 左边距(mm):"))
            combo_left_margin = QDoubleSpinBox()
            combo_left_margin.setRange(0.0, 20.0)
            combo_left_margin.setSingleStep(0.5)
            combo_left_margin.setValue(4.0)
            hbox_ctrl.addWidget(combo_left_margin)
            hbox_ctrl.addWidget(QLabel(" 右边距(mm):"))
            combo_right_margin = QDoubleSpinBox()
            combo_right_margin.setRange(0.0, 20.0)
            combo_right_margin.setSingleStep(0.5)
            combo_right_margin.setValue(8.0)
            hbox_ctrl.addWidget(combo_right_margin)
            hbox_ctrl.addStretch()
            vbox.addLayout(hbox_ctrl)
            
            # 预览图片容器
            lbl_preview = QLabel()
            lbl_preview.setAlignment(Qt.AlignCenter)
            # 使用 ScrollArea 更好，但为了保持简洁，使用缩放显示
            vbox.addWidget(lbl_preview, 1) # Stretch factor 1
            
            # 按钮区
            hbox_btn = QHBoxLayout()
            print_btn = QPushButton('打印')
            save_pdf_btn = QPushButton('保存为 PDF')
            close_btn = QPushButton('关闭')
            hbox_btn.addStretch()
            hbox_btn.addWidget(print_btn)
            hbox_btn.addWidget(save_pdf_btn)
            hbox_btn.addWidget(close_btn)
            vbox.addLayout(hbox_btn)

            # 状态持有
            state = {'printer': None, 'tmp_png': None}

            def refresh_preview():
                size = combo_size.currentText()
                top_offset = float(combo_top_offset.value()) if combo_top_offset else 0.0
                comp_scale = float(combo_comp_scale.value()) if combo_comp_scale else 1.0
                left_margin = float(combo_left_margin.value()) if combo_left_margin else 4.0
                right_margin = float(combo_right_margin.value()) if combo_right_margin else 8.0
                content_scale_val = float(combo_content_scale.value()) if combo_content_scale else 1.0
                state['printer'] = ReceiptPrinter(paper_size=size, top_offset_mm=top_offset, company_font_scale_adj=comp_scale, content_font_scale=content_scale_val, safe_margin_left_mm=left_margin, safe_margin_right_mm=right_margin)
                
                tmp_dir = tempfile.gettempdir()
                state['tmp_png'] = os.path.join(tmp_dir, f"receipt_merged_preview_{os.getpid()}.png")
                
                # 渲染预览
                ok_img = state['printer'].render_merged_receipt_to_image(payments, state['tmp_png'], dpi=150)
                if ok_img and os.path.exists(state['tmp_png']):
                    pix = QPixmap(state['tmp_png'])
                    if not pix.isNull():
                        # 适应窗口显示
                        available_size = lbl_preview.size()
                        # 给一点 padding
                        w = max(100, dlg.width() - 40)
                        h = max(100, dlg.height() - 100)
                        lbl_preview.setPixmap(pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            # 绑定事件
            combo_size.currentTextChanged.connect(refresh_preview)
            
            # 初始刷新（需要等对话框显示后尺寸才准确，或者先简单的刷一下）
            refresh_preview()

            def do_print():
                if state['printer']:
                    okp = state['printer'].print_merged_receipt(payment_ids)
                    if not okp:
                        QMessageBox.warning(self, '提示', '打印失败或被取消')

            def do_save_pdf():
                if not state['printer']: return
                path, _ = QFileDialog.getSaveFileName(self, "保存合并收据为 PDF", "", "PDF Files (*.pdf)")
                if path:
                    # 确保后缀
                    if not path.lower().endswith('.pdf'):
                        path += '.pdf'
                    okpdf = state['printer'].print_merged_receipt(payment_ids, output_file=path)
                    if okpdf:
                        QMessageBox.information(self, '成功', '已保存为 PDF')
                    else:
                        QMessageBox.warning(self, '提示', '保存为 PDF 失败')

            print_btn.clicked.connect(do_print)
            save_pdf_btn.clicked.connect(do_save_pdf)
            close_btn.clicked.connect(dlg.accept)
            
            dlg.exec_()
            
            # 清理
            try:
                if state['tmp_png'] and os.path.exists(state['tmp_png']):
                    os.remove(state['tmp_png'])
            except:
                pass

        except Exception as e:
            QMessageBox.critical(self, '错误', f'合并打印失败：{str(e)}')
    
    def load_unpaid(self):
        """加载欠费列表"""
        try:
            period = self.unpaid_period_combo.currentText()
            if not period:
                return
            
            unpaid_payments = PaymentService.get_unpaid_payments_by_period(period)
            # 支持按搜索关键词过滤（房号/姓名/收费项目）
            keyword = ''
            try:
                keyword = self.unpaid_search.text().strip().lower()
            except Exception:
                keyword = ''

            filtered = []
            for p in unpaid_payments:
                try:
                    if not keyword:
                        filtered.append(p)
                        continue
                    name = (p.resident.name or '').lower()
                    room = (p.resident.room_no or '').lower()
                    phone = (p.resident.phone or '').lower()
                    item = (p.charge_item.name or '').lower() if p.charge_item else ''
                    if keyword in name or keyword in room or keyword in phone or keyword in item:
                        filtered.append(p)
                except Exception:
                    # 如果访问字段出错，忽略该记录
                    continue

            self.unpaid_table.setRowCount(len(filtered))
            
            unpaid_total_remaining = 0.0
            for row, payment in enumerate(filtered):
                self.unpaid_table.setItem(row, 0, QTableWidgetItem(str(payment.id)))
                self.unpaid_table.setItem(row, 1, QTableWidgetItem(getattr(payment.resident, 'full_room_no', payment.resident.room_no)))
                self.unpaid_table.setItem(row, 2, QTableWidgetItem(payment.resident.name))
                self.unpaid_table.setItem(row, 3, QTableWidgetItem(payment.charge_item.name))
                self.unpaid_table.setItem(row, 4, QTableWidgetItem(payment.period))
                # 显示剩余欠费金额 = 总金额 - 已缴金额
                try:
                    total_amt = float(payment.amount or 0.0)
                except Exception:
                    total_amt = 0.0
                try:
                    paid_amt = float(payment.paid_amount or 0.0)
                except Exception:
                    paid_amt = 0.0
                remaining = total_amt - paid_amt
                if remaining < 0:
                    remaining = 0.0
                unpaid_total_remaining += remaining
                self.unpaid_table.setItem(row, 5, QTableWidgetItem(self._fmt_amount_int(remaining)))
                self.unpaid_table.setItem(row, 6, QTableWidgetItem(
                    payment.created_at.strftime('%Y-%m-%d %H:%M:%S') if payment.created_at else ''))
            
            # 显示统计信息（使用剩余欠费合计）
            stats = PaymentService.get_statistics_by_period(period)
            stats_text = f"总计: {stats['total_count']} 条 | "
            stats_text += f"已缴费: {stats['paid_count']} 条 | "
            stats_text += f"未缴费: {stats['unpaid_count']} 条 | "
            stats_text += f"欠费总额: ¥{self._fmt_amount_int(unpaid_total_remaining)}"
            self.unpaid_stats_label.setText(stats_text)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载欠费列表失败：{str(e)}')
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 数据菜单
        data_menu = menubar.addMenu('数据')
        data_menu.addAction('数据备份', self.show_backup_dialog)
        data_menu.addAction('住户批量导入', self.import_residents)
        data_menu.addSeparator()
        data_menu.addAction('导出缴费记录', self.export_payments)
        data_menu.addAction('导出欠费清单', self.export_unpaid_list)
        data_menu.addAction('生成统计报表', self.generate_report)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        tools_menu.addAction('批量生成账单', self.batch_create_payments)
    
    def import_residents(self):
        """批量导入住户"""
        dialog = ImportDialog(self)
        if dialog.exec_() == ImportDialog.Accepted:
            self.load_residents()
    
    def export_unpaid_list(self):
        """导出欠费清单"""
        period = self.unpaid_period_combo.currentText()
        if not period:
            QMessageBox.warning(self, '提示', '请先选择查询周期')
            return
        
        dialog = ExportDialog(self, export_type='unpaid')
        dialog.set_periods([period])
        dialog.exec_()
    
    def export_payments(self):
        """导出缴费记录"""
        # 获取所有周期
        all_payments = PaymentService.get_all_payments()
        periods = sorted(set(p.period for p in all_payments), reverse=True)
        if not periods:
            QMessageBox.warning(self, '提示', '没有可用的周期数据')
            return
        
        dialog = ExportDialog(self, export_type='payments')
        dialog.set_periods(periods)
        dialog.exec_()
    
    def generate_report(self):
        """生成统计报表"""
        # 获取所有周期
        all_payments = PaymentService.get_all_payments()
        periods = sorted(set(p.period for p in all_payments), reverse=True)
        if not periods:
            QMessageBox.warning(self, '提示', '没有可用的周期数据')
            return
        
        dialog = ExportDialog(self, export_type='report')
        dialog.set_periods(periods)
        dialog.exec_()

    def generate_year_report(self):
        """按年生成统计（简单弹窗展示）"""
        year, ok = QInputDialog.getInt(self, "年统计", "请输入年份（例如 2025）：", datetime.now().year, 2000, 2100, 1)
        if not ok:
            return
        try:
            stats = PaymentService.get_statistics_by_year(year)
            lines = [f"年度统计：{year}", f"合计金额：¥{stats['total_amount']:.2f}", ""]
            for name, amt in stats['by_item']:
                lines.append(f"{name}: ¥{amt:.2f}")
            QMessageBox.information(self, f"{year} 年统计", "\n".join(lines))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成年度统计失败：{str(e)}')
    
    def show_backup_dialog(self):
        """显示备份对话框"""
        dialog = BackupDialog(self)
        dialog.exec_()
    
    def batch_create_payments(self):
        """批量生成账单"""
        from ui.batch_payment_dialog import BatchPaymentDialog
        dialog = BatchPaymentDialog(self)
        if dialog.exec_() == BatchPaymentDialog.Accepted:
            self.load_periods()
            self.load_payments()
            self.load_unpaid()

