from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QGroupBox,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
)
from PySide6.QtCore import Qt
from models.glossary import Glossary, GlossaryTerm


class GlossaryDetailDialog(QDialog):
    """用語詳細ダイアログ"""

    def __init__(self, term: Optional[GlossaryTerm] = None, parent=None):
        super().__init__(parent)
        self.glossary = Glossary()
        self.terms = self.glossary.get_all_terms()
        self.current_term = term

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
        term_label = QLabel(
            "用語を選択してください"
            if self.current_term is None
            else self.current_term.term
        )
        term_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(term_label)

        return widget

    def _create_sidebar(self) -> QWidget:
        """サイドバー部分（目次など）を作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        glossary_group = QGroupBox("用語集")
        glossary_layout = QVBoxLayout(glossary_group)

        glossary_search = QLineEdit()
        glossary_search.setPlaceholderText("用語を検索...")
        glossary_layout.addWidget(glossary_search)

        self.glossary_list = QTreeWidget()
        self.glossary_list.setHeaderHidden(True)
        self.glossary_list.setRootIsDecorated(False)

        for term in self.terms:
            self.glossary_list.addTopLevelItem(QTreeWidgetItem([term.term]))

        glossary_layout.addWidget(self.glossary_list)
        layout.addWidget(glossary_group)

        # ここに目次やナビゲーション要素を追加

        return widget

    def _create_content(self) -> QWidget:

        def _short_desc_widget() -> QWidget:
            """短い説明ウィジェットを作成"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel("短い説明:")
            content = QLabel(
                "" if self.current_term is None else self.current_term.short_desc
            )
            content.setWordWrap(True)

            layout.addWidget(label)
            layout.addWidget(content)

            return widget

        def _detailed_desc_widget() -> QWidget:
            """詳細説明ウィジェットを作成"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel("詳細説明:")
            content = QLabel(
                "" if self.current_term is None else self.current_term.description
            )
            content.setWordWrap(True)

            layout.addWidget(label)
            layout.addWidget(content)

            return widget

        def _related_terms_widget() -> QWidget:
            """関連用語ウィジェットを作成"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel("関連用語:")
            layout.addWidget(label)

            if self.current_term is not None and self.current_term.related:
                for related_term_name in self.current_term.related:
                    related_label = QLabel(f"- {related_term_name}")
                    layout.addWidget(related_label)
            else:
                no_related_label = QLabel("関連用語はありません。")
                layout.addWidget(no_related_label)

            return widget

        def _command_widget() -> QWidget:
            """コマンドウィジェットを作成"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel("関連コマンド:")
            content = QLabel(
                "" if self.current_term is None else self.current_term.command
            )
            content.setWordWrap(True)

            layout.addWidget(label)
            layout.addWidget(content)

            return widget

        """コンテンツ部分（説明など）を作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ここに短い説明、詳細説明、関連用語などを追加
        short_desc_widget = _short_desc_widget()
        layout.addWidget(short_desc_widget)

        detailed_desc_widget = _detailed_desc_widget()
        layout.addWidget(detailed_desc_widget)

        related_terms_widget = _related_terms_widget()
        layout.addWidget(related_terms_widget)

        command_widget = _command_widget()
        layout.addWidget(command_widget)

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
