"""メインウィンドウの実装"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QToolBar,
    QStatusBar,
    QMenuBar,
    QMenu,
    QLabel,
    QComboBox,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QPlainTextEdit,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QTabWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


class MainWindow(QMainWindow):
    """LeafGitのメインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LeafGit")
        self.setMinimumSize(1000, 700)

        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_status_bar()

    def _setup_menu_bar(self):
        """メニューバーの設定"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")

        open_repo_action = QAction("リポジトリを開く(&O)", self)
        open_repo_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_repo_action)

        init_repo_action = QAction("新規リポジトリ(&N)", self)
        init_repo_action.setShortcut("Ctrl+N")
        file_menu.addAction(init_repo_action)

        clone_repo_action = QAction("クローン(&C)", self)
        clone_repo_action.setShortcut("Ctrl+Shift+C")
        file_menu.addAction(clone_repo_action)

        file_menu.addSeparator()

        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 編集メニュー
        edit_menu = menubar.addMenu("編集(&E)")

        # Git操作メニュー
        git_menu = menubar.addMenu("Git(&G)")

        commit_action = QAction("コミット(&C)", self)
        commit_action.setShortcut("Ctrl+Return")
        git_menu.addAction(commit_action)

        push_action = QAction("プッシュ(&P)", self)
        push_action.setShortcut("Ctrl+Shift+P")
        git_menu.addAction(push_action)

        pull_action = QAction("プル(&L)", self)
        pull_action.setShortcut("Ctrl+Shift+L")
        git_menu.addAction(pull_action)

        git_menu.addSeparator()

        branch_menu = git_menu.addMenu("ブランチ(&B)")
        branch_menu.addAction(QAction("新規ブランチ", self))
        branch_menu.addAction(QAction("ブランチを切り替え", self))
        branch_menu.addAction(QAction("ブランチを削除", self))

        # 表示メニュー
        view_menu = menubar.addMenu("表示(&V)")

        toggle_sidebar_action = QAction("サイドバー(&S)", self)
        toggle_sidebar_action.setCheckable(True)
        toggle_sidebar_action.setChecked(True)
        view_menu.addAction(toggle_sidebar_action)

        toggle_history_action = QAction("コマンド履歴(&H)", self)
        toggle_history_action.setCheckable(True)
        toggle_history_action.setChecked(True)
        view_menu.addAction(toggle_history_action)

        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")

        glossary_action = QAction("用語集(&G)", self)
        glossary_action.setShortcut("F1")
        help_menu.addAction(glossary_action)

        help_menu.addSeparator()

        about_action = QAction("LeafGitについて(&A)", self)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """ツールバーの設定"""
        toolbar = QToolBar("メインツールバー")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 基本操作ボタン
        toolbar.addAction(QAction("開く", self))
        toolbar.addAction(QAction("コミット", self))
        toolbar.addAction(QAction("プッシュ", self))
        toolbar.addAction(QAction("プル", self))

        toolbar.addSeparator()

        # ヘルプレベル切り替え
        help_level_label = QLabel("ヘルプレベル: ")
        toolbar.addWidget(help_level_label)

        self.help_level_combo = QComboBox()
        self.help_level_combo.addItems(
            [
                "🔰 詳細ガイド",
                "💡 簡易ヒント",
                "🚀 自立モード",
            ]
        )
        self.help_level_combo.setToolTip("ヘルプの表示レベルを切り替えます")
        toolbar.addWidget(self.help_level_combo)

    def _setup_central_widget(self):
        """中央ウィジェットの設定"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # メインスプリッター（上下分割: コンテンツ / コマンド履歴）
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # 上部スプリッター（左右分割: サイドバー / メインエリア）
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左サイドバー
        sidebar = self._create_sidebar()
        content_splitter.addWidget(sidebar)

        # 右メインエリア
        main_area = self._create_main_area()
        content_splitter.addWidget(main_area)

        # サイドバーとメインエリアの比率を設定
        content_splitter.setSizes([250, 750])

        main_splitter.addWidget(content_splitter)

        # 下部: コマンド履歴パネル
        command_history = self._create_command_history_panel()
        main_splitter.addWidget(command_history)

        # コンテンツとコマンド履歴の比率を設定
        main_splitter.setSizes([500, 150])

        main_layout.addWidget(main_splitter)

    def _create_sidebar(self) -> QWidget:
        """左サイドバーを作成"""
        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)

        # ファイルツリー（変更ファイル一覧）
        files_group = QGroupBox("変更ファイル")
        files_layout = QVBoxLayout(files_group)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["ファイル", "状態"])
        self.file_tree.setRootIsDecorated(False)

        # サンプルデータ
        sample_item = QTreeWidgetItem(["src/main.py", "変更"])
        self.file_tree.addTopLevelItem(sample_item)

        files_layout.addWidget(self.file_tree)
        layout.addWidget(files_group)

        # ブランチ一覧
        branch_group = QGroupBox("ブランチ")
        branch_layout = QVBoxLayout(branch_group)

        self.branch_tree = QTreeWidget()
        self.branch_tree.setHeaderHidden(True)
        self.branch_tree.setRootIsDecorated(False)

        # サンプルデータ
        main_branch = QTreeWidgetItem(["● main"])
        self.branch_tree.addTopLevelItem(main_branch)

        branch_layout.addWidget(self.branch_tree)
        layout.addWidget(branch_group)

        # 用語集（折りたたみ可能）
        glossary_group = QGroupBox("用語集")
        glossary_group.setCheckable(True)
        glossary_group.setChecked(False)
        glossary_layout = QVBoxLayout(glossary_group)

        glossary_search = QLineEdit()
        glossary_search.setPlaceholderText("用語を検索...")
        glossary_layout.addWidget(glossary_search)

        self.glossary_list = QTreeWidget()
        self.glossary_list.setHeaderHidden(True)
        self.glossary_list.setRootIsDecorated(False)

        # サンプル用語
        terms = ["コミット", "プッシュ", "プル", "ブランチ", "マージ"]
        for term in terms:
            self.glossary_list.addTopLevelItem(QTreeWidgetItem([term]))

        glossary_layout.addWidget(self.glossary_list)
        layout.addWidget(glossary_group)

        # 余白を埋める
        layout.addStretch()

        return sidebar

    def _create_main_area(self) -> QWidget:
        """右メインエリアを作成"""
        main_area = QWidget()
        layout = QVBoxLayout(main_area)
        layout.setContentsMargins(0, 0, 0, 0)

        # 上部: 変更内容・差分表示
        diff_tabs = QTabWidget()

        # Unstagedタブ
        unstaged_widget = QWidget()
        unstaged_layout = QVBoxLayout(unstaged_widget)
        self.unstaged_diff = QPlainTextEdit()
        self.unstaged_diff.setReadOnly(True)
        self.unstaged_diff.setPlaceholderText(
            "ステージされていない変更がここに表示されます"
        )
        unstaged_layout.addWidget(self.unstaged_diff)
        diff_tabs.addTab(unstaged_widget, "Unstaged")

        # Stagedタブ
        staged_widget = QWidget()
        staged_layout = QVBoxLayout(staged_widget)
        self.staged_diff = QPlainTextEdit()
        self.staged_diff.setReadOnly(True)
        self.staged_diff.setPlaceholderText("ステージされた変更がここに表示されます")
        staged_layout.addWidget(self.staged_diff)
        diff_tabs.addTab(staged_widget, "Staged")

        layout.addWidget(diff_tabs, stretch=1)

        # 下部: コミット操作エリア
        commit_group = QGroupBox("コミット")
        commit_layout = QVBoxLayout(commit_group)

        # コミットメッセージ入力
        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("コミットメッセージを入力...")
        self.commit_message.setMaximumHeight(100)
        commit_layout.addWidget(self.commit_message)

        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.stage_button = QPushButton("選択をステージ")
        button_layout.addWidget(self.stage_button)

        self.commit_button = QPushButton("コミット")
        self.commit_button.setDefault(True)
        button_layout.addWidget(self.commit_button)

        commit_layout.addLayout(button_layout)
        layout.addWidget(commit_group)

        return main_area

    def _create_command_history_panel(self) -> QWidget:
        """コマンド履歴パネルを作成"""
        panel = QGroupBox("コマンド履歴")
        layout = QVBoxLayout(panel)

        self.command_history = QPlainTextEdit()
        self.command_history.setReadOnly(True)
        self.command_history.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: monospace;
                font-size: 12px;
            }
        """
        )
        self.command_history.setPlaceholderText(
            "Git操作を行うと、対応するコマンドがここに表示されます..."
        )

        layout.addWidget(self.command_history)

        return panel

    def _setup_status_bar(self):
        """ステータスバーの設定"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # リポジトリ情報
        self.repo_label = QLabel("リポジトリ: 未選択")
        status_bar.addWidget(self.repo_label)

        # ブランチ情報
        self.branch_label = QLabel("ブランチ: -")
        status_bar.addPermanentWidget(self.branch_label)
