#!/bin/bash

# エラーが発生したら処理を中断
set -e

echo "=== C# (ImageSharp) 環境構築 & ビルドを開始します ==="

# 1. dotnet CLI が利用可能かチェック
if ! command -v dotnet &> /dev/null; then
    echo "エラー: .NET SDK がインストールされていません。"
    echo "https://dotnet.microsoft.com/download からインストールしてください。"
    exit 1
fi

echo "[1/2] NuGet パッケージを復元しています..."
dotnet restore

echo "[2/2] プロジェクトをビルドしています..."
dotnet build -c Release

echo "=========================================="
echo " セットアップ & ビルドが完了しました！"
echo " 以下のコマンドで実行できます:"
echo "   dotnet run input.jpg output.jpg 800 600"
echo "=========================================="
