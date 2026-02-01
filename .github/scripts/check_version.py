import os
import re
import subprocess
import sys
from packaging import version


def set_output(name: str, value: str):
    """Sets an output variable for GitHub Actions."""
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        fh.write(f"{name}={value}\n")


def get_version_from_file(file_path: str) -> str:
    """Reads the __version__ from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError(f"Version not found in {file_path}")


def get_version_from_git(commit_ref: str, file_path: str) -> str:
    """Gets the version from a file at a specific Git commit."""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_ref}:{file_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        content = result.stdout
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        raise ValueError(f"Version not found in {file_path} at {commit_ref}")
    except subprocess.CalledProcessError:
        # ファイルが前のコミットに存在しない場合
        return None


def compare_versions(old_ver: str, new_ver: str) -> bool:
    """Compare two version strings. Returns True if new_ver > old_ver."""
    try:
        return version.parse(new_ver) > version.parse(old_ver)
    except Exception as e:
        print(f"Error comparing versions: {e}")
        return False


def main():
    is_skip = os.getenv("SKIP_VERSION_CHECK", "false").lower() == "true"
    if is_skip:
        print("Release is manually skipped.")
        set_output("skip_release", "true")
        set_output("reason", "manually skipped")
        return 0

    # src/__init__.pyのパス
    init_file = "src/__init__.py"

    # 現在のバージョンを取得
    try:
        current_version = get_version_from_file(init_file)
        print(f"Current version: {current_version}")
    except Exception as e:
        print(f"Error reading current version: {e}")
        return 1

    # 前回のバージョンを取得（HEAD^から）
    previous_version = get_version_from_git("HEAD^", init_file)

    if previous_version is None:
        print("Previous version not found (possibly first commit).")
        print("Proceeding with release.")
        set_output("skip_release", "false")
        set_output("new_version", current_version)
        return 0

    print(f"Previous version: {previous_version}")

    # バージョン比較
    if current_version == previous_version:
        print(f"Version unchanged ({current_version}). Skipping release.")
        set_output("skip_release", "true")
        set_output("reason", "version unchanged")
        return 0

    if compare_versions(previous_version, current_version):
        print(f"Version bumped: {previous_version} -> {current_version}")
        set_output("skip_release", "false")
        set_output("new_version", current_version)
        return 0
    else:
        print(f"Error: Version did not increase! {previous_version} -> {current_version}")
        set_output("skip_release", "true")
        set_output("reason", "version decreased or invalid")
        return 1


if __name__ == "__main__":
    sys.exit(main())
