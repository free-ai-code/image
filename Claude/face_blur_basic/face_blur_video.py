import cv2

def blur_video(input_path, output_path, mode='block'):
    """動画ファイルを処理してモザイク化した動画を保存"""
    
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    cap = cv2.VideoCapture(input_path)
    
    # ビデオ情報を取得
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # ビデオライター設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        # モザイク処理
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            
            if mode == 'block':
                small = cv2.resize(face_roi, (w//15, h//15))
                mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
            elif mode == 'blur':
                mosaic = cv2.GaussianBlur(face_roi, (31, 31), 0)
            
            frame[y:y+h, x:x+w] = mosaic
        
        out.write(frame)
        
        frame_count += 1
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"処理中... {progress:.1f}%")
    
    cap.release()
    out.release()
    print(f"✅ 完成！ → {output_path}")


# 使い方
if __name__ == '__main__':
    # input_video.mp4 をモザイク化して、output_video.mp4 に保存
    blur_video('input_video.mp4', 'output_video.mp4', mode='block')
