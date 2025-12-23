"""Git操作の実行結果を表すデータクラス"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CommandResult:
    """
    Git操作の実行結果を表すデータクラス

    Attributes:
        success (bool): 操作が成功したかどうか
        command (str): 実行されたGitコマンド文字列(例: "git commit -m 'message'")
        description (str): 操作の説明(日本語、UI表示用)
        output (Optional[str]): コマンドの標準出力
        error_message (Optional[str]): エラーメッセージ（失敗時）
        data (Optional[Any]): 追加データ(GitPythonのオブジェクト等)
    """

    success: bool
    command: str
    description: str
    output: Optional[str] = None
    error_message: Optional[str] = None
    data: Optional[Any] = None

    def __bool__(self) -> bool:
        """
        結果をブール値として評価できるようにする

        Returns:
            bool: 操作が成功したかどうか
        """
        return self.success

    @property
    def is_error(self) -> bool:
        """エラーが発生したかどうか"""
        return not self.success and self.error_message is not None

    def to_log_dict(self) -> dict:
        """
        ログ保存用の辞書に変換

        Returns:
            dict: データベースやJSONに保存可能な辞書形式
        """
        return {
            "command": self.command,
            "description": self.description,
            "success": self.success,
            "output": self.output,
            "error_message": self.error_message,
        }
