#!/bin/bash
# PyInstallerビルドスクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"
SPEC_FILE="$PROJECT_DIR/leafgit.spec"

echo "================================"
echo "LeafGit バイナリビルドスクリプト"
echo "================================"
echo ""

# 仮想環境の確認
if [ ! -d ".venv" ]; then
    echo "❌ 仮想環境が見つかりません。先に .venv を作成してください。"
    exit 1
fi

# 仮想環境の有効化
echo "仮想環境を有効化中..."
source .venv/bin/activate

# 依存ライブラリの確認・インストール
echo "依存ライブラリをインストール中..."
pip install -q -r requirements.txt
pip install -q pyinstaller

# 既存のビルド成果物を削除
echo "既存のビルド成果物をクリーンアップ中..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "build" "*.pyc"

# PyInstallerでビルド
echo ""
echo "ビルド中..."
pyinstaller "$SPEC_FILE" --distpath "$DIST_DIR" --workpath "$BUILD_DIR"

echo ""
echo "================================"
echo "✅ ビルド完了"
echo "================================"
echo ""
echo "出力先: $DIST_DIR/leafgit/"
echo ""
echo "実行: $DIST_DIR/leafgit/leafgit"
echo ""
