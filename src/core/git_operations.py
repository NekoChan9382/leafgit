from git import Repo
from git.exc import GitCommandError
from models import CommandResult
from utils import get_logger
import os

logger = get_logger(__name__)


class GitOperations:
    def __init__(self, repo):
        """
        直接呼ばず、クラスメソッド(open_repository等)を使う

        Args:
            repo: GitPythonのRepoオブジェクト
        """
        self.repo = repo
        if self.repo.bare:
            raise Exception("Repository is bare")

    # エラーパターンとユーザー向けメッセージのマッピング
    _ERROR_PATTERNS = {
        # ネットワーク関連
        "could not resolve host": "ネットワークに接続できません",
        "connection refused": "リモートサーバーに接続できません",
        "timed out": "接続がタイムアウトしました",
        # 認証関連
        "authentication failed": "認証に失敗しました",
        "permission denied": "アクセス権限がありません",
        "invalid username or password": "ユーザー名またはパスワードが正しくありません",
        # リモート関連
        "rejected": "プッシュが拒否されました(先にpullしてください)",
        "no such remote": "指定されたリモートが存在しません",
        "remote origin already exists": "リモート'origin'は既に存在します",
        # ブランチ関連
        "already exists": "ブランチは既に存在します",
        "did not match any": "ブランチが見つかりません",
        "not found": "ブランチが見つかりません",
        "cannot delete checked out branch": "現在のブランチは削除できません",
        "not fully merged": "マージされていない変更があります(強制削除は -D を使用)",
        # コミット/ステージング関連
        "nothing to commit": "コミットする変更がありません",
        "nothing added to commit": "ステージされたファイルがありません",
        "pathspec": "指定されたファイルが見つかりません",
        # マージ/コンフリクト関連
        "conflict": "コンフリクトが発生しました。手動で解決してください",
        "merge is not possible": "マージできません",
        "not something we can merge": "マージ対象が無効です",
        "you have divergent branches and need to specify how to reconcile them": "マージ方法を指定する必要があります",
        # 作業ツリー関連
        "local changes would be overwritten": "未コミットの変更が上書きされます。先にコミットまたはstashしてください",
        "uncommitted changes": "未コミットの変更があります。先にコミットまたはstashしてください",
        "your local changes": "未コミットの変更があります。先にコミットまたはstashしてください",
        # リポジトリ関連
        "repository not found": "リポジトリが見つかりません",
        "not a git repository": "Gitリポジトリではありません",
    }

    def _handle_error(
        self, error: Exception, command: str, description: str
    ) -> CommandResult:
        """
        エラーをユーザーフレンドリーなCommandResultに変換

        Args:
            error: 発生した例外
            command: 実行しようとしたGitコマンド
            description: 操作の説明

        Returns:
            CommandResult: エラー情報を含む結果オブジェクト
        """
        # GitCommandErrorの場合はstderrを取得
        if isinstance(error, GitCommandError):
            error_text = (error.stderr or str(error)).lower()
        else:
            error_text = str(error).lower()
        logger.error("GitError: %s", error_text)
        # エラーパターンをマッチング
        user_message = None
        for pattern, message in self._ERROR_PATTERNS.items():
            if pattern in error_text:
                user_message = message
                break

        # マッチしなかった場合はデフォルトメッセージ
        if user_message is None:
            if isinstance(error, GitCommandError) and error.stderr:
                user_message = error.stderr.strip()
            else:
                user_message = str(error)

        return CommandResult(
            success=False,
            command=command,
            description=f"{description}に失敗しました",
            error_message=user_message,
        )

    @classmethod
    def open_repository(cls, repo_path):
        """既存リポジトリを開く"""
        repo = Repo(repo_path)
        return cls(repo)  # cls は GitOperations クラス自身

    @classmethod
    def init_repository(cls, repo_path):
        """新規リポジトリを作成"""
        repo = Repo.init(repo_path)
        return cls(repo)

    @classmethod
    def clone_repository(cls, repo_url, destination):
        """リモートリポジトリをクローン"""
        repo = Repo.clone_from(repo_url, destination)
        return cls(repo)

    def stage_files(self, file_paths):
        cmd = f"git add {' '.join(file_paths)}"
        description = "ファイルをステージングエリアに追加"
        try:

            # ファイルの存在確認
            existing_files = []
            deleted_files = []

            repo_path = self.repo.working_tree_dir
            for file_path in file_paths:
                full_path = os.path.join(repo_path, file_path)
                if os.path.exists(full_path):
                    existing_files.append(file_path)
                else:
                    deleted_files.append(file_path)

            # 存在するファイル: 通常のadd
            if existing_files:
                self.repo.index.add(existing_files)

            # 削除されたファイル: removeでステージング
            if deleted_files:
                self.repo.index.remove(deleted_files, working_tree=False)

            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def unstage_files(self, file_paths):
        """ファイルをアンステージ"""
        cmd = f"git reset HEAD {' '.join(file_paths)}"
        description = "ファイルをアンステージ"
        try:
            # HEADが有効かチェック（初回コミット前）
            if self.repo.head.is_valid():
                self.repo.index.reset(paths=file_paths)
            else:
                # 初回コミット前: インデックスから削除
                self.repo.index.remove(file_paths, working_tree=False)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def commit_changes(self, message):
        cmd = f"git commit -m '{message}'"
        description = "変更を保存"
        try:
            self.repo.index.commit(message)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def connect_remote(self, url, name="origin"):
        cmd = f"git remote add {name} {url}"
        description = "リモートリポジトリに接続"
        try:
            self.repo.create_remote(name, url)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def push_changes(self, remote="origin", branch="main"):
        cmd = f"git push {remote} {branch}"
        description = "変更をリモートリポジトリに反映"
        try:
            self.repo.git.push(remote, branch)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def pull_changes(self, remote="origin", branch="main"):
        cmd = f"git pull {remote} {branch}"
        description = "リモートリポジトリから変更を取得"
        try:
            self.repo.git.pull(remote, branch, "--no-rebase")
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    # branches

    def get_branches(self):
        """ローカルブランチの一覧を取得"""
        try:
            branches = [branch.name for branch in self.repo.branches]
            return branches
        except Exception as e:
            logger.warning(f"ブランチ一覧の取得に失敗: {e}")
            return []

    def get_current_branch(self):
        """
        現在のブランチ名を取得

        Returns:
            str or None: ブランチ名。HEAD未確定（初回コミット前）の場合はNone
        """
        try:
            # HEADが存在するか確認
            if self.repo.head.is_valid():
                return self.repo.active_branch.name
            else:
                # 初回コミット前: HEADは存在するがコミットを指していない
                # この場合でもブランチ名は取得可能な場合がある
                try:
                    return self.repo.active_branch.name
                except TypeError:
                    # detached HEAD 状態
                    return None
        except TypeError:
            # detached HEAD 状態
            return None
        except Exception as e:
            logger.warning(f"現在のブランチ取得に失敗: {e}")
            return None

    def create_branch(self, branch_name):
        cmd = f"git checkout -b {branch_name}"
        description = "新しいブランチを作成"
        try:
            self.repo.git.checkout("-b", branch_name)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def switch_branch(self, branch_name):
        cmd = f"git checkout {branch_name}"
        description = "ブランチを切り替え"
        try:
            self.repo.git.checkout(branch_name)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def delete_branch(self, branch_name):
        cmd = f"git branch -d {branch_name}"
        description = "ブランチを削除"
        try:
            self.repo.git.branch("-d", branch_name)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    def merge_branch(self, source_branch, target_branch=None):
        if target_branch is None:
            target_branch = self.repo.active_branch.name
        cmd = f"git checkout {target_branch} && git merge {source_branch}"
        description = "ブランチをマージ"
        try:
            self.repo.git.checkout(target_branch)
            self.repo.git.merge(source_branch)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    # files

    def get_changed_files(self):
        """
        変更されたファイルを取得

        Returns:
            dict: ステージされたファイル、ステージされていないファイル、未追跡ファイル、削除されたファイルのリスト
        """
        try:
            staged = []
            unstaged = []
            deleted = []

            # HEADが有効かチェック（初回コミット前は無効）
            if self.repo.head.is_valid():
                # ステージされた変更 (HEAD vs Index)
                for item in self.repo.index.diff("HEAD"):
                    # 削除されたファイルはa_path、追加/変更されたファイルもa_path
                    path = item.a_path if item.a_path else item.b_path
                    if path:
                        staged.append(path)
            else:
                # 初回コミット前: インデックスに追加されたファイルをstagedとみなす
                staged = [entry[0] for entry in self.repo.index.entries.keys()]

            # ステージされていない変更 (Index vs Working Tree)
            for item in self.repo.index.diff(None):
                # 削除されたファイルはa_path、変更されたファイルもa_path
                path = item.a_path if item.a_path else item.b_path
                if path:
                    if item.change_type == "D":
                        deleted.append(path)
                    else:
                        unstaged.append(path)

            untracked = self.repo.untracked_files

            return {
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
                "deleted": deleted,
            }
        except Exception as e:
            logger.warning(f"変更ファイルの取得に失敗: {e}")
            return {
                "staged": [],
                "unstaged": [],
                "untracked": [],
                "deleted": [],
            }
