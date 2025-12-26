from git import Repo
from models import CommandResult


class GitOperations:
    def __init__(self, repo):
        """
        直接呼ばず、クラスメソッド（open_repository等）を使う

        Args:
            repo: GitPythonのRepoオブジェクト
        """
        self.repo = repo
        if self.repo.bare:
            raise Exception("Repository is bare")

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
        self.repo.index.add(file_paths)
        return CommandResult(
            success=True,
            command=f"git add {' '.join(file_paths)}",
            description="ファイルをステージングエリアに追加",
        )

    def commit_changes(self, message):
        self.repo.index.commit(message)
        return CommandResult(
            success=True,
            command=f"git commit -m '{message}'",
            description="変更を保存",
        )

    def push_changes(self, remote="origin", branch="main"):
        self.repo.git.push(remote, branch)
        return CommandResult(
            success=True,
            command=f"git push {remote} {branch}",
            description="変更をリモートリポジトリに反映",
        )

    def pull_changes(self, remote="origin", branch="main"):
        self.repo.git.pull(remote, branch)
        return CommandResult(
            success=True,
            command=f"git pull {remote} {branch}",
            description="リモートリポジトリから変更を取得",
        )

    # branches

    def create_branch(self, branch_name):
        self.repo.git.checkout("-b", branch_name)
        return CommandResult(
            success=True,
            command=f"git checkout -b {branch_name}",
            description="新しいブランチを作成",
        )

    def switch_branch(self, branch_name):
        self.repo.git.checkout(branch_name)
        return CommandResult(
            success=True,
            command=f"git checkout {branch_name}",
            description="ブランチを切り替え",
        )

    def delete_branch(self, branch_name):
        self.repo.git.branch("-d", branch_name)
        return CommandResult(
            success=True,
            command=f"git branch -d {branch_name}",
            description="ブランチを削除",
        )
