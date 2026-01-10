"""アプリケーション全体を制御するController"""

from typing import Optional, List
from PySide6.QtCore import QObject, Signal

from core.git_operations import GitOperations
from models import CommandResult


class AppController(QObject):
    """
    アプリケーション全体を制御するController

    UIとGit操作の仲介役として機能し、
    シグナルを通じてUIに状態変化を通知する
    """

    # シグナル定義
    repository_opened = Signal(str)  # リポジトリが開かれた(パス)
    repository_closed = Signal()  # リポジトリが閉じられた
    command_executed = Signal(CommandResult)  # コマンドが実行された
    files_changed = Signal(list)  # ファイル状態が変化した
    branch_changed = Signal(str)  # ブランチが変化した
    error_occurred = Signal(str)  # エラーが発生した

    def __init__(self):
        super().__init__()
        self._git_ops: Optional[GitOperations] = None
        self._repo_path: Optional[str] = None

    @property
    def is_repository_open(self) -> bool:
        """リポジトリが開かれているかどうか"""
        return self._git_ops is not None

    @property
    def repository_path(self) -> Optional[str]:
        """現在のリポジトリパス"""
        return self._repo_path

    @property
    def current_branch(self) -> Optional[str]:
        """現在のブランチ名"""
        if self._git_ops is None:
            return None
        return self._git_ops.get_current_branch()

    # ==================== リポジトリ操作 ====================

    def open_repository(self, path: str) -> CommandResult:
        """既存リポジトリを開く"""
        try:
            self._git_ops = GitOperations.open_repository(path)
            self._repo_path = path
            self.repository_opened.emit(path)
            self.branch_changed.emit(self.current_branch or "")
            self._refresh_files()
            return CommandResult(
                success=True,
                command=f"cd {path}",
                description="リポジトリを開きました",
                output=f"リポジトリ: {path}",
            )
        except Exception as e:
            result = CommandResult(
                success=False,
                command=f"cd {path}",
                description="リポジトリを開く",
                error_message=str(e),
            )
            self.error_occurred.emit(str(e))
            return result

    def init_repository(self, path: str) -> CommandResult:
        """新規リポジトリを作成"""
        try:
            self._git_ops = GitOperations.init_repository(path)
            self._repo_path = path
            result = CommandResult(
                success=True,
                command=f"git init {path}",
                description="新規リポジトリを作成しました",
                output=f"Initialized empty Git repository in {path}",
            )
            self.repository_opened.emit(path)
            self.command_executed.emit(result)
            return result
        except Exception as e:
            result = CommandResult(
                success=False,
                command=f"git init {path}",
                description="リポジトリの作成",
                error_message=str(e),
            )
            self.error_occurred.emit(str(e))
            return result

    def clone_repository(self, url: str, destination: str) -> CommandResult:
        """リポジトリをクローン"""
        try:
            self._git_ops = GitOperations.clone_repository(url, destination)
            self._repo_path = destination
            result = CommandResult(
                success=True,
                command=f"git clone {url} {destination}",
                description="リポジトリをクローンしました",
                output=f"Cloned to {destination}",
            )
            self.repository_opened.emit(destination)
            self.command_executed.emit(result)
            self._refresh_files()
            return result
        except Exception as e:
            result = CommandResult(
                success=False,
                command=f"git clone {url} {destination}",
                description="リポジトリのクローン",
                error_message=str(e),
            )
            self.error_occurred.emit(str(e))
            return result

    def close_repository(self):
        """リポジトリを閉じる"""
        self._git_ops = None
        self._repo_path = None
        self.repository_closed.emit()

    # ==================== ステージング操作 ====================

    def stage_files(self, file_paths: List[str]) -> CommandResult:
        """ファイルをステージング"""
        if not self._ensure_repository():
            return self._no_repository_error("git add")

        result = self._git_ops.stage_files(file_paths)
        self.command_executed.emit(result)
        if result.success:
            self._refresh_files()
        return result

    def unstage_files(self, file_paths: List[str]) -> CommandResult:
        """ファイルをアンステージ"""
        if not self._ensure_repository():
            return self._no_repository_error("git reset")

        result = self._git_ops.unstage_files(file_paths)
        self.command_executed.emit(result)
        if result.success:
            self._refresh_files()
        return result

    # ==================== コミット操作 ====================

    def commit(self, message: str) -> CommandResult:
        """変更をコミット"""
        if not self._ensure_repository():
            return self._no_repository_error("git commit")

        result = self._git_ops.commit_changes(message)
        self.command_executed.emit(result)
        if result.success:
            self._refresh_files()
        return result

    # ==================== リモート操作 ====================

    def connetct_remote(self, url: str, name: str = "origin") -> CommandResult:
        if not self._ensure_repository():
            return self._no_repository_error("git remote")
    def push(self, remote: str = "origin", branch: str = None) -> CommandResult:
        """変更をプッシュ"""
        if not self._ensure_repository():
            return self._no_repository_error("git push")

        if branch is None:
            branch = self.current_branch or "main"

        result = self._git_ops.push_changes(remote, branch)
        self.command_executed.emit(result)
        return result

    def pull(self, remote: str = "origin", branch: str = None) -> CommandResult:
        """変更をプル"""
        if not self._ensure_repository():
            return self._no_repository_error("git pull")

        if branch is None:
            branch = self.current_branch or "main"

        result = self._git_ops.pull_changes(remote, branch)
        self.command_executed.emit(result)
        if result.success:
            self._refresh_files()
        return result

    # ==================== ブランチ操作 ====================

    def create_branch(self, branch_name: str) -> CommandResult:
        """新規ブランチを作成"""
        if not self._ensure_repository():
            return self._no_repository_error("git checkout -b")

        result = self._git_ops.create_branch(branch_name)
        self.command_executed.emit(result)
        if result.success:
            self.branch_changed.emit(branch_name)
        return result

    def switch_branch(self, branch_name: str) -> CommandResult:
        """ブランチを切り替え"""
        if not self._ensure_repository():
            return self._no_repository_error("git checkout")

        result = self._git_ops.switch_branch(branch_name)
        self.command_executed.emit(result)
        if result.success:
            self.branch_changed.emit(branch_name)
            self._refresh_files()
        return result

    def delete_branch(self, branch_name: str) -> CommandResult:
        """ブランチを削除"""
        if not self._ensure_repository():
            return self._no_repository_error("git branch -d")

        result = self._git_ops.delete_branch(branch_name)
        self.command_executed.emit(result)
        if result.success:
            self.branch_changed.emit(self.current_branch or "")
        return result

    def merge_branch(self, source_branch: str) -> CommandResult:
        """ブランチをマージ"""
        if not self._ensure_repository():
            return self._no_repository_error("git merge")

        result = self._git_ops.merge_branch(source_branch)
        self.command_executed.emit(result)
        if result.success:
            self._refresh_files()
        return result

    def get_branches(self) -> List[str]:
        """ブランチ一覧を取得"""
        if not self._ensure_repository():
            return []

        result = self._git_ops.get_branches()
        return result

    # ==================== 情報取得 ====================

    def get_changed_files(self) -> dict:
        """
        変更されたファイルを取得

        Returns:
            dict: {
                'staged': [...],    # ステージされたファイル
                'unstaged': [...],  # 変更されているがステージされていないファイル
                'untracked': [...]  # 未追跡ファイル
            }
        """
        if not self._ensure_repository():
            return {"staged": [], "unstaged": [], "untracked": []}

        result = self._git_ops.get_changed_files()
        return result

    # ==================== プライベートメソッド ====================

    def _ensure_repository(self) -> bool:
        """リポジトリが開かれているか確認"""
        return self._git_ops is not None

    def _no_repository_error(self, command: str) -> CommandResult:
        """リポジトリ未選択エラーを生成"""
        result = CommandResult(
            success=False,
            command=command,
            description="操作を実行",
            error_message="リポジトリが選択されていません",
        )
        self.error_occurred.emit("リポジトリが選択されていません")
        return result

    def _refresh_files(self):
        """ファイル一覧を更新してシグナルを発行"""
        files = self.get_changed_files()
        all_files = files["staged"] + files["unstaged"] + files["untracked"]
        self.files_changed.emit(all_files)
