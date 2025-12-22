# LeafGit

Git/GitHub の操作を GUI で行うための学習支援アプリケーション

## 概要

LeafGit は、CLI ベースの操作に慣れていない初学者を対象とした、Git/GitHub 操作のための GUI アプリケーションです。
Git、GitHub、CLI 操作への理解と移行を支援することを目的としています。

## 主な機能

### 基本の Git 操作

- リポジトリの作成・クローン
- ファイルのステージング・コミット
- ブランチ管理
- プッシュ・プル

### 学習支援機能

- 操作に対応する Git コマンドの表示
- コマンド履歴のリアルタイム表示
- Git 用語集
- 段階的ヘルプシステム

### GitHub 連携

- Personal Access Token 認証
- リポジトリ一覧表示とクローン
- リモートリポジトリへの push/pull

## 必要要件

- Python 3.12 以上
- Git（システムにインストール済みであること）

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/NekoChan9382/leafgit.git
cd leafgit

# 依存関係のインストール
pip install -r requirements.txt

# 開発用の依存関係も含める場合
pip install -e .[dev]
```

## 使い方

```bash
# アプリケーションの起動
python src/main.py
```

## 開発

```bash
# テストの実行
pytest

# コードフォーマット
black src/

# リンターの実行
flake8 src/
```

## ライセンス

MIT License

## 作者

NekoChan9382 / bit
