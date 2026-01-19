from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PySide6.QtCore import Qt


class GlossaryDetailDialog(QDialog):
    """用語詳細ダイアログ"""

    def __init__(self, term, parent=None):
        super().__init__(parent)
        self.term = term

        # ウィンドウ設定
        self.setWindowTitle("用語の詳細")
        self.setMinimumSize(500, 400)

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
        layout.addWidget(self._create_footer())

    def _create_header(self) -> QWidget:
        """ヘッダー部分（用語名）を作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 用語名を大きく表示
        term_label = QLabel(self.term.term)
        term_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(term_label)

        return widget

    def _create_content(self) -> QWidget:
        """コンテンツ部分（説明など）を作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ここに短い説明、詳細説明、関連用語などを追加

        return widget

    def _create_footer(self) -> QWidget:
        """フッター部分（ボタン）を作成"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addStretch()

        # 閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        return widget
