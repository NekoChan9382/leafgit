"""ロギング設定"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "leafgit", level: int = logging.INFO) -> logging.Logger:
    """
    アプリケーションのロガーを設定

    Args:
        name: ロガーの名前
        level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）

    Returns:
        logging.Logger: 設定されたロガー
    """
    # ルートロガーを設定（全てのloggerに適用される）
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 既にハンドラが設定されている場合はスキップ
    if root_logger.handlers:
        return logging.getLogger(name)

    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # フォーマット
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # GitPythonのログを抑制（WARNINGレベル以上のみ表示）
    logging.getLogger("git").setLevel(logging.WARNING)
    logging.getLogger("git.cmd").setLevel(logging.WARNING)
    logging.getLogger("git.repo").setLevel(logging.WARNING)

    # 指定された名前のロガーを返す
    return logging.getLogger(name)


def get_logger(name: str = "leafgit") -> logging.Logger:
    """
    既存のロガーを取得

    Args:
        name: ロガーの名前

    Returns:
        logging.Logger: ロガー
    """
    return logging.getLogger(name)
