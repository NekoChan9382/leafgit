"""メインウィンドウの実装"""

from datetime import datetime
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
    QFileDialog,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from core.app_controller import AppController
from models import CommandResult
from utils import get_logger

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication
logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """LeafGitのメインウィンドウ"""

    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("LeafGit")
        self.setMinimumSize(1000, 700)

        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_status_bar()
        self._connect_signals()

    def _connect_signals(self):
        """Controllerのシグナルを接続"""
        # Controller -> UI
        self.controller.repository_opened.connect(self._on_repository_opened)
        self.controller.repository_closed.connect(self._on_repository_closed)
        self.controller.command_executed.connect(self._on_command_executed)
        self.controller.files_changed.connect(self._on_files_changed)
        self.controller.branch_changed.connect(self._on_branch_changed)
        self.controller.error_occurred.connect(self._on_error_occurred)

    def _setup_menu_bar(self):
        """メニューバーの設定"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")

        open_repo_action = QAction("リポジトリを開く(&O)", self)
        open_repo_action.setShortcut("Ctrl+O")
        open_repo_action.triggered.connect(self._on_open_repository)
        file_menu.addAction(open_repo_action)

        init_repo_action = QAction("新規リポジトリ(&N)", self)
        init_repo_action.setShortcut("Ctrl+N")
        init_repo_action.triggered.connect(self._on_init_repository)
        file_menu.addAction(init_repo_action)

        clone_repo_action = QAction("クローン(&C)", self)
        clone_repo_action.setShortcut("Ctrl+Shift+C")
        file_menu.addAction(clone_repo_action)

        file_menu.addSeparator()

        update_action = QAction("更新(&R)", self)
        update_action.setShortcut("Ctrl+R")
        update_action.triggered.connect(self._update_file_tree)
        file_menu.addAction(update_action)

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
        commit_action.triggered.connect(self._on_commit)
        git_menu.addAction(commit_action)

        push_action = QAction("プッシュ(&P)", self)
        push_action.setShortcut("Ctrl+Shift+P")
        push_action.triggered.connect(self._on_push)
        git_menu.addAction(push_action)

        pull_action = QAction("プル(&L)", self)
        pull_action.setShortcut("Ctrl+Shift+L")
        pull_action.triggered.connect(self._on_pull)
        git_menu.addAction(pull_action)

        git_menu.addSeparator()

        branch_menu = git_menu.addMenu("ブランチ(&B)")
        create_branch_action = QAction("新規ブランチ(&N)", self)
        create_branch_action.triggered.connect(self._on_create_branch)
        branch_menu.addAction(create_branch_action)
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

        self.branch_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.branch_tree.customContextMenuRequested.connect(
            self._show_branch_context_menu
        )

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
        unstaged_layout.setContentsMargins(5, 5, 5, 5)

        unstaged_label = QLabel("ステージされていないファイル")
        unstaged_layout.addWidget(unstaged_label)

        self.unstaged_list = QListWidget()
        self.unstaged_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.unstaged_list.customContextMenuRequested.connect(
            self._show_unstaged_context_menu
        )
        self.unstaged_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        unstaged_layout.addWidget(self.unstaged_list)

        # Stageボタン
        stage_button = QPushButton("Stage Selected")
        stage_button.clicked.connect(self._stage_selected_files)
        unstaged_layout.addWidget(stage_button)

        diff_tabs.addTab(unstaged_widget, "Unstaged")

        # Stagedタブ
        staged_widget = QWidget()
        staged_layout = QVBoxLayout(staged_widget)
        staged_layout.setContentsMargins(5, 5, 5, 5)

        staged_label = QLabel("ステージされたファイル")
        staged_layout.addWidget(staged_label)

        self.staged_list = QListWidget()
        self.staged_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.staged_list.customContextMenuRequested.connect(
            self._show_staged_context_menu
        )
        self.staged_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        staged_layout.addWidget(self.staged_list)

        # Unstageボタン
        unstage_button = QPushButton("Unstage Selected")
        unstage_button.clicked.connect(self._unstage_selected_files)
        staged_layout.addWidget(unstage_button)

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
        self.stage_button.clicked.connect(self._on_stage_files)
        button_layout.addWidget(self.stage_button)

        self.commit_button = QPushButton("コミット")
        self.commit_button.setDefault(True)
        self.commit_button.clicked.connect(self._on_commit)
        button_layout.addWidget(self.commit_button)

        commit_layout.addLayout(button_layout)
        layout.addWidget(commit_group)

        return main_area

    def _create_command_history_panel(self) -> QWidget:
        """コマンド履歴パネルを作成"""
        panel = QGroupBox("コマンド履歴")
        layout = QVBoxLayout(panel)

        # ツールバー
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 5)

        # クリアボタン
        clear_button = QPushButton("クリア")
        clear_button.clicked.connect(self._clear_command_history)
        toolbar.addWidget(clear_button)

        # コピーボタン
        copy_button = QPushButton("全体をコピー")
        copy_button.clicked.connect(self._copy_command_history)
        toolbar.addWidget(copy_button)

        toolbar.addStretch()

        # 履歴件数表示
        self.history_count_label = QLabel("0 件")
        toolbar.addWidget(self.history_count_label)

        layout.addLayout(toolbar)

        # 履歴表示エリア
        self.command_history = QPlainTextEdit()
        self.command_history.setReadOnly(True)
        self.command_history.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.command_history.customContextMenuRequested.connect(
            self._show_history_context_menu
        )
        self.command_history.setMaximumBlockCount(50)  # 最大50行
        self.command_history.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: monospace;
                font-size: 12px;
                padding: 5px;
            }
        """
        )
        self.command_history.setPlaceholderText(
            "Git操作を行うと、対応するコマンドがここに表示されます...\n\n"
            "・コマンドを右クリックでコピーできます\n"
            "・最大50件まで保持されます"
        )

        layout.addWidget(self.command_history)

        # 履歴カウンターを初期化
        self.history_count = 0

        layout.addWidget(self.command_history)

        return panel

    def _setup_status_bar(self):
        """ステータスバーの設定"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # リポジトリ情報
        self.repo_label = QLabel("リポジトリ: 未選択")
        status_bar.addWidget(self.repo_label)

        # 操作情報
        self.operation_label = QLabel("")
        status_bar.addWidget(self.operation_label)

        # ブランチ情報
        self.branch_label = QLabel("ブランチ: -")
        status_bar.addPermanentWidget(self.branch_label)

    # ==================== アクションハンドラ ====================

    def _on_open_repository(self):
        """リポジトリを開く"""
        path = QFileDialog.getExistingDirectory(
            self, "リポジトリを選択", "", QFileDialog.Option.ShowDirsOnly
        )
        if path:
            result = self.controller.open_repository(path)
            if not result.success:
                QMessageBox.warning(self, "エラー", result.error_message)

    def _on_init_repository(self):
        """新規リポジトリを作成"""
        path = QFileDialog.getExistingDirectory(
            self, "リポジトリを作成する場所を選択", "", QFileDialog.Option.ShowDirsOnly
        )
        if path:
            result = self.controller.init_repository(path)
            if not result.success:
                QMessageBox.warning(self, "エラー", result.error_message)

    def _on_commit(self):
        """コミットを実行"""
        message = self.commit_message.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "エラー", "コミットメッセージを入力してください")
            return

        result = self.controller.commit(message)
        if result.success:
            self.commit_message.clear()

    def _on_push(self):
        """プッシュを実行"""
        self.controller.push()

    def _on_pull(self):
        """プルを実行"""
        self.controller.pull()

    def _on_stage_files(self):
        """選択ファイルをステージング"""
        selected_items = self.file_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self, "情報", "ステージするファイルを選択してください"
            )
            return

        file_paths = [item.text(0) for item in selected_items]
        self.controller.stage_files(file_paths)
    # TODO: ブランチ名のバリデーションを実装
    def _on_create_branch(self):
        """新規ブランチを作成"""
        branch_name, ok = QInputDialog.getText(
            self, "新規ブランチ", "ブランチ名を入力:"
        )
        if ok and branch_name:
            result = self.controller.create_branch(branch_name)
            if not result.success:
                QMessageBox.warning(self, "エラー", result.error_message)

    def _on_checkout_branch(self):
        """選択されたブランチに移動"""
        selected_items = self.branch_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "情報", "移動するブランチを選択してください")
            return

        branch_name = selected_items[0].text(0).strip("● ").strip()
        result = self.controller.switch_branch(branch_name)
        if not result.success:
            QMessageBox.warning(self, "エラー", result.error_message)
    # TODO: 削除確認ダイアログを追加
    def _on_delete_branch(self):
        """選択されたブランチを削除"""
        selected_items = self.branch_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "情報", "削除するブランチを選択してください")
            return

        branch_name = selected_items[0].text(0).strip("● ").strip()
        result = self.controller.delete_branch(branch_name)
        if not result.success:
            QMessageBox.warning(self, "エラー", result.error_message)

    # ==================== シグナルスロット ====================

    def _on_repository_opened(self, path: str):
        """リポジトリが開かれた時の処理"""
        self.repo_label.setText(f"リポジトリ: {path}")
        self.setWindowTitle(f"LeafGit - {path}")
        self._update_file_tree()
        self._update_branch_list()

    def _on_repository_closed(self):
        """リポジトリが閉じられた時の処理"""
        self.repo_label.setText("リポジトリ: 未選択")
        self.branch_label.setText("ブランチ: -")
        self.setWindowTitle("LeafGit")
        self.file_tree.clear()
        self.branch_tree.clear()

    def _on_command_executed(self, result: CommandResult):
        """コマンドが実行された時の処理"""
        self._add_to_command_history(result)

    def _on_files_changed(self, files: list):
        """ファイル状態が変化した時の処理"""
        self._update_file_tree()

    def _on_branch_changed(self, branch_name: str):
        """ブランチが変化した時の処理"""
        self.branch_label.setText(f"ブランチ: {branch_name}")
        self._update_branch_list()

    def _on_error_occurred(self, error_message: str):
        """エラーが発生した時の処理"""
        QMessageBox.warning(self, "エラー", error_message)

    # ==================== UI更新メソッド ====================

    def _add_to_command_history(self, result: CommandResult):
        """コマンド履歴に追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✓" if result.success else "✗"

        # 色付きHTMLでコマンド行を作成
        if result.success:
            color = "#00ff00"  # 緑
        else:
            color = "#ff5555"  # 赤

        # プレーンテキストで追加（色は付けられないがシンプル）
        line = f"[{timestamp}] {status_icon} {result.command}"

        # 履歴に追加
        self.command_history.appendPlainText(line)

        # 説明があれば追加
        if result.description:
            self.command_history.appendPlainText(f"    ├─ {result.description}")

        # エラーメッセージがあれば追加
        if result.error_message:
            self.command_history.appendPlainText(
                f"    └─ エラー: {result.error_message}"
            )

        # 空行を追加（読みやすさ向上）
        self.command_history.appendPlainText("")

        # 履歴カウンターを更新
        self.history_count += 1
        self.history_count_label.setText(f"{self.history_count} 件")

        # 最新のコマンドに自動スクロール
        scrollbar = self.command_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _update_file_tree(self):
        """ファイルツリーを更新"""
        self.file_tree.clear()
        self.unstaged_list.clear()
        self.staged_list.clear()

        if not self.controller.is_repository_open:
            return

        files = self.controller.get_changed_files()

        # ステージされたファイル
        for file_path in files["staged"]:
            # 左サイドバーのツリー
            item = QTreeWidgetItem([file_path, "Staged"])
            item.setForeground(1, Qt.GlobalColor.green)
            self.file_tree.addTopLevelItem(item)

            # Stagedリスト
            list_item = QListWidgetItem(file_path)
            self.staged_list.addItem(list_item)

        # ステージされていない変更
        for file_path in files["unstaged"]:
            # 左サイドバーのツリー
            item = QTreeWidgetItem([file_path, "Modified"])
            item.setForeground(1, Qt.GlobalColor.yellow)
            self.file_tree.addTopLevelItem(item)

            # Unstagedリスト
            list_item = QListWidgetItem(file_path)
            self.unstaged_list.addItem(list_item)

        # 未追跡ファイル
        for file_path in files["untracked"]:
            # 左サイドバーのツリー
            item = QTreeWidgetItem([file_path, "Untracked"])
            item.setForeground(1, Qt.GlobalColor.red)
            self.file_tree.addTopLevelItem(item)

            # Unstagedリスト
            list_item = QListWidgetItem(file_path)
            self.unstaged_list.addItem(list_item)

        # 削除されたファイル
        for file_path in files["deleted"]:
            # 左サイドバーのツリー
            item = QTreeWidgetItem([file_path, "Deleted"])
            item.setForeground(1, Qt.GlobalColor.darkRed)
            self.file_tree.addTopLevelItem(item)

            # Unstagedリスト
            list_item = QListWidgetItem(file_path)
            self.unstaged_list.addItem(list_item)

    def _update_branch_list(self):
        """ブランチ一覧を更新"""
        self.branch_tree.clear()

        if not self.controller.is_repository_open:
            return

        current_branch = self.controller.current_branch
        branches = self.controller.get_branches()

        for branch in branches:
            prefix = "● " if branch == current_branch else "  "
            item = QTreeWidgetItem([f"{prefix}{branch}"])
            if branch == current_branch:
                item.setForeground(0, Qt.GlobalColor.green)
            self.branch_tree.addTopLevelItem(item)

    # ==================== ステージング操作 ====================

    def _stage_selected_files(self):
        """選択されたファイルをステージング"""
        selected_items = self.unstaged_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ファイルが選択されていません")
            return

        file_paths = [item.text() for item in selected_items]
        result = self.controller.stage_files(file_paths)

        if result.success:
            self.operation_label.setText(
                f"✓ {len(file_paths)}個のファイルをステージしました"
            )
        else:
            QMessageBox.critical(
                self, "エラー", f"ステージに失敗しました\n{result.error_message}"
            )

    def _unstage_selected_files(self):
        """選択されたファイルをアンステージ"""
        selected_items = self.staged_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "ファイルが選択されていません")
            return

        file_paths = [item.text() for item in selected_items]
        result = self.controller.unstage_files(file_paths)

        if result.success:
            self.operation_label.setText(
                f"✓ {len(file_paths)}個のファイルをアンステージしました"
            )
        else:
            QMessageBox.critical(
                self, "エラー", f"アンステージに失敗しました\n{result.error_message}"
            )

    def _show_unstaged_context_menu(self, position):
        """Unstagedリストのコンテキストメニューを表示"""
        if not self.unstaged_list.selectedItems():
            return

        menu = QMenu(self)
        stage_action = menu.addAction("Stage")
        stage_action.triggered.connect(self._stage_selected_files)

        menu.exec(self.unstaged_list.mapToGlobal(position))

    def _show_staged_context_menu(self, position):
        """Stagedリストのコンテキストメニューを表示"""
        if not self.staged_list.selectedItems():
            return

        menu = QMenu(self)
        unstage_action = menu.addAction("Unstage")
        unstage_action.triggered.connect(self._unstage_selected_files)

        menu.exec(self.staged_list.mapToGlobal(position))

    def _show_branch_context_menu(self, position):
        """ブランチ一覧のコンテキストメニューを表示"""
        selected_item = self.branch_tree.selectedItems()
        if not selected_item:
            return

        menu = QMenu(self)
        checkout_action = menu.addAction("移動")
        delete_action = menu.addAction("削除")

        checkout_action.triggered.connect(self._on_checkout_branch)
        delete_action.triggered.connect(self._on_delete_branch)

        menu.exec(self.branch_tree.mapToGlobal(position))

    # ==================== コマンド履歴操作 ====================

    def _clear_command_history(self):
        """コマンド履歴をクリア"""
        reply = QMessageBox.question(
            self,
            "確認",
            "コマンド履歴をクリアしますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.command_history.clear()
            self.history_count = 0
            self.history_count_label.setText("0 件")

    def _copy_command_history(self):
        """コマンド履歴全体をクリップボードにコピー"""

        text = self.command_history.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.operation_label.setText(
                "✓ コマンド履歴をクリップボードにコピーしました"
            )
        else:
            QMessageBox.information(self, "情報", "コピーする履歴がありません")

    def _show_history_context_menu(self, position):
        """コマンド履歴のコンテキストメニューを表示"""
        menu = QMenu(self)

        # 選択されたテキストをコピー
        copy_selected_action = menu.addAction("選択部分をコピー")
        copy_selected_action.triggered.connect(self._copy_selected_history)

        # 全体をコピー
        copy_all_action = menu.addAction("全体をコピー")
        copy_all_action.triggered.connect(self._copy_command_history)

        menu.addSeparator()

        # クリア
        clear_action = menu.addAction("履歴をクリア")
        clear_action.triggered.connect(self._clear_command_history)

        # 選択されているテキストがない場合は選択コピーを無効化
        if not self.command_history.textCursor().hasSelection():
            copy_selected_action.setEnabled(False)

        menu.exec(self.command_history.mapToGlobal(position))

    def _copy_selected_history(self):

        cursor = self.command_history.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.operation_label.setText("✓ 選択したテキストをコピーしました")
