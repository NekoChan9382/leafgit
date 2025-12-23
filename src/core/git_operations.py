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
