from git import Repo
from models import CommandResult


class GitOperations:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
        if self.repo.bare:
            raise Exception("Repository is bare")

    def clone_repository(self, repo_url, destination):
        self.repo.git.clone(repo_url, destination)
        return CommandResult(
            success=True,
            command=f"git clone {repo_url} {destination}",
            description="リポジトリのクローンを実行",
        )

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
