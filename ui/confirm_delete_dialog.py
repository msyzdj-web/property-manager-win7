from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class ConfirmDeleteDialog(QDialog):
    """可滚动的批量删除确认对话框，显示选中住户列表并保持确认/取消按钮可见"""
    def __init__(self, parent=None, items=None, title='确认删除住户'):
        super().__init__(parent)
        self.setWindowTitle(title)
        # 初始大小，允许用户调整；列表区域会限制高度以保证按钮可见
        self.resize(520, 360)

        layout = QVBoxLayout(self)

        count = len(items) if items else 0
        label = QLabel(f"确定要删除以下 {count} 个住户吗？\n(列表可滚动，按钮始终可见)")
        label.setWordWrap(True)
        layout.addWidget(label)

        self.list_widget = QListWidget()
        if items:
            # 列表项数量可能很多，使用列表控件自带滚动条
            self.list_widget.addItems(items)
        self.list_widget.setSelectionMode(QListWidget.NoSelection)
        # 限制列表高度，防止对话框过高导致底部按钮无法看到
        max_list_height = int(self.height() * 0.6)
        self.list_widget.setMaximumHeight(max_list_height)
        self.list_widget.setMinimumHeight(80)
        layout.addWidget(self.list_widget, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton('确认')
        self.cancel_btn = QPushButton('取消')
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def resizeEvent(self, event):
        """在窗口大小变化时调整列表最大高度，保证按钮区域可见"""
        try:
            max_list_height = max(80, int(self.height() * 0.6))
            # 预留空间给标题和按钮，大约 120px
            reserved = 120
            max_list_height = max(80, self.height() - reserved)
            self.list_widget.setMaximumHeight(max_list_height)
        except Exception:
            pass
        super().resizeEvent(event)


