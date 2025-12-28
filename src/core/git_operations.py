from git import Repo
from git.exc import GitCommandError
from models import CommandResult


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
            self.repo.index.add(file_paths)
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
            self.repo.git.pull(remote, branch)
            return CommandResult(
                success=True,
                command=cmd,
                description=description,
            )
        except Exception as e:
            return self._handle_error(e, cmd, description)

    # branches

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
