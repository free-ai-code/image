#!/bin/bash

# エラーが発生したらその時点で処理を中断する設定
set -e

echo "=== 1. OpenCVのインストールを開始します ==="
pip install opencv-python

echo "=== 2. リアルタイムカメラ（シンプル版）を起動します ==="
echo "※終了するには、カメラウィンドウをアクティブにして 'q' キーを押してください。"
python face_blur_basic.py

echo "=== 3. リアルタイムカメラ（拡張版）を起動します ==="
echo "※終了するには、カメラウィンドウをアクティブにして 'q' キーを押してください。"
python face_blur_advanced.py

echo "=== 4. 動画ファイル処理を開始します ==="
python face_blur_video.py

echo "=== すべての処理が正常に完了しました ==="
