import cv2
import numpy as np

# カスケード分類器（顔検出）を読み込む
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# カメラを開く
cap = cv2.VideoCapture(0)

while True:
    # フレームを読み込む
    ret, frame = cap.read()
    if not ret:
        break
    
    # グレースケールに変換（顔検出用）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 顔を検出
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    # 検出された各顔にモザイクを適用
    for (x, y, w, h) in faces:
        # 顔の領域を切り出す
        face_region = frame[y:y+h, x:x+w]
        
        # ブロックモザイク処理
        # 小さく縮小してから拡大することでモザイク化
        small = cv2.resize(face_region, (w//15, h//15))
        mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # 元のフレームにモザイク画像を合成
        frame[y:y+h, x:x+w] = mosaic
    
    # 画面に表示
    cv2.imshow('Face Blur Camera', frame)
    
    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放
cap.release()
cv2.destroyAllWindows()
