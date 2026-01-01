"""LeafGit - エントリーポイント"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from core import AppController
from ui import MainWindow
from utils import setup_logger


def main():
    """アプリケーションのメイン関数"""
    # ロガーの初期化
    # 開発中はDEBUG、本番はINFOレベル
    setup_logger("leafgit", level=logging.DEBUG)

    app = QApplication(sys.argv)

    # アプリケーション情報の設定
    app.setApplicationName("LeafGit")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("LeafGit")

    # Controllerの初期化
    controller = AppController()

    # メインウィンドウの表示
    window = MainWindow(controller)
    window.show()

    # イベントループの開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
