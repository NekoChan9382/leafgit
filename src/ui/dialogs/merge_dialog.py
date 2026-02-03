from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QGroupBox,
    QComboBox,
)

from PySide6.QtCore import Qt
from typing import Optional, List


class MergeDialog(QDialog):
    """マージダイアログ"""

    def __init__(
        self,
        branches: Optional[List[str]] = None,
        current_branch: Optional[str] = None,
        selected_branch: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.branches = branches or []
        self.current_branch = current_branch
        self.selected_branch = selected_branch
        # ウィンドウ設定
        self.setWindowTitle("マージダイアログ")
        self.setMinimumSize(500, 100)

        # UI構築
        self._setup_ui()

    def _setup_ui(self):
        """UIを構築"""
        # メインレイアウト
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # コンテンツを追加
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_content())

    def _create_header(self) -> QWidget:
        """ヘッダー部分を作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header_label = QLabel("マージする内容を選択してください")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header_label)

        return widget

    def _create_content(self) -> QWidget:
        """コンテンツ部分を作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        branch_layout = QHBoxLayout()

        source_group = QGroupBox("マージ元")
        source_layout = QVBoxLayout(source_group)
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.branches)
        self.source_combo.setCurrentText(self.selected_branch)
        source_layout.addWidget(self.source_combo)

        branch_layout.addWidget(source_group)

        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branch_layout.addWidget(arrow_label)

        target_group = QGroupBox("マージ先")
        target_group_layout = QVBoxLayout(target_group)
        self.target_combo = QComboBox()
        self.target_combo.addItems(self.branches)
        self.target_combo.setCurrentText(self.current_branch)
        target_group_layout.addWidget(self.target_combo)

        branch_layout.addWidget(target_group)
        layout.addLayout(branch_layout)

        self.msg_label = QLabel("")
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label)

        self.source_combo.currentTextChanged.connect(self._update_msg)
        self.target_combo.currentTextChanged.connect(self._update_msg)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("キャンセル")
        self.cancel_btn.clicked.connect(self._reject)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("マージ")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self._accept)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        self._update_msg()

        return widget

    def _update_msg(self):
        """メッセージを更新"""
        source = self.source_combo.currentText()
        target = self.target_combo.currentText()

        if not source or not target:
            self.msg_label.setText("マージ元とマージ先のブランチを選択してください。")
            self.ok_btn.setEnabled(False)
            return

        if source == target:
            self.msg_label.setText(
                "マージ元とマージ先のブランチは異なる必要があります。"
            )
            self.msg_label.setStyleSheet(
                "background-color: #ffebee; color: #c62828; "
                "padding: 10px; border-left: 4px solid #f44336; border-radius: 4px;"
            )
            self.ok_btn.setEnabled(False)
        else:
            self.msg_label.setText(
                f"'{source}' ブランチを '{target}' ブランチにマージします。"
            )
            self.msg_label.setStyleSheet(
                "background-color: #e8f5e9; color: #2e7d32; "
                "padding: 10px; border-left: 4px solid #4caf50; border-radius: 4px;"
            )
            self.ok_btn.setEnabled(True)

    def get_merge_branch(self) -> tuple[str, str]:
        """選択されたマージ先とマージ元のブランチを取得"""

        merge_target = self.target_combo.currentText()
        merge_source = self.source_combo.currentText()
        return merge_target, merge_source

    def _accept(self) -> None:
        """OKボタンが押された時の処理"""
        if self.source_combo.currentText() == self.target_combo.currentText():
            return
        super().accept()

    def _reject(self) -> None:
        """キャンセルボタンが押された時の処理"""
        super().reject()
