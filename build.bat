@echo off
REM PyInstallerビルドスクリプト (Windows)

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ================================
echo LeafGit バイナリビルドスクリプト
echo ================================
echo.

REM 仮想環境の確認
if not exist ".venv" (
    echo ❌ 仮想環境が見つかりません。先に .venv を作成してください。
    pause
    exit /b 1
)

REM 仮想環境の有効化
echo 仮想環境を有効化中...
call .venv\Scripts\activate.bat

REM 依存ライブラリのインストール
echo 依存ライブラリをインストール中...
pip install -q -r requirements.txt
pip install -q pyinstaller

REM 既存のビルド成果物を削除
echo 既存のビルド成果物をクリーンアップ中...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM PyInstallerでビルド
echo.
echo ビルド中...
pyinstaller leafgit.spec

echo.
echo ================================
echo ✅ ビルド完了
echo ================================
echo.
echo 出力先: dist\leafgit\
echo.
echo 実行: dist\leafgit\leafgit.exe
echo.
pause
