#!/bin/bash

# エラーが発生したら処理を中断
set -e

echo "=== 環境構築を開始します ==="

# 1. 仮想環境 (venv) の作成
if [ ! -d "venv" ]; then
    echo "[1/3] 仮想環境 'venv' を作成しています..."
    python3 -m venv venv
else
    echo "[1/3] 既に 'venv' 環境が存在するためスキップします。"
fi

# 2. 仮想環境の有効化
echo "[2/3] 仮想環境を有効化しています..."
source venv/bin/activate

# 3. パッケージのアップデート & インストール
echo "[3/3] パッケージをインストールしています..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "警告: requirements.txt が見つかりません。Pillowを直接インストールします。"
    pip install Pillow
fi

echo "=========================================="
echo " Setup が完了しました！"
echo " 以下のコマンドでアプリを起動できます:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo "=========================================="
