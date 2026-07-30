#!/bin/bash

# エラーが発生したら処理を中断
set -e

echo "=== C++ (OpenCV) 環境構築＆ビルドを開始します ==="

# 1. パッケージリストの更新と必要な依存ライブラリのインストール
echo "[1/3] システムパッケージとOpenCV依存関係をインストールしています..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev

# 2. ビルド用ディレクトリ（build/）の作成
echo "[2/3] ビルド用ディレクトリを用意しています..."
if [ -d "build" ]; then
    echo "既存の build ディレクトリをクリーンアップします。"
    rm -rf build
fi
mkdir build
cd build

# 3. CMake による構成とビルド
echo "[3/3] プロジェクトをビルドしています..."
cmake ..
make -j$(nproc)

echo "=========================================="
echo " Setup & Build が完了しました！"
echo " 実行ファイルは build/ ディレクトリ内に生成されています。"
echo "=========================================="
