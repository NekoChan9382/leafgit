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
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 既にハンドラが設定されている場合はスキップ
    if logger.handlers:
        return logger

    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # フォーマット
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "leafgit") -> logging.Logger:
    """
    既存のロガーを取得

    Args:
        name: ロガーの名前

    Returns:
        logging.Logger: ロガー
    """
    return logging.getLogger(name)
