import cv2
import numpy as np
import time

# カスケード分類器を読み込む
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

class FaceBlurApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mode = 'block'           # 'block', 'blur', 'stamp'
        self.intensity = 15            # モザイク粗さ
        self.is_enabled = True         # モザイク有効/無効
        self.fps = 0
        self.prev_time = time.time()
    
    def apply_block_mosaic(self, roi):
        """ブロックモザイク処理"""
        h, w = roi.shape[:2]
        # 小さくしてから拡大でモザイク化
        small = cv2.resize(roi, (w // self.intensity, h // self.intensity))
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    
    def apply_blur_mosaic(self, roi):
        """ぼかし処理"""
        blur_size = self.intensity * 2 + 1
        return cv2.GaussianBlur(roi, (blur_size, blur_size), 0)
    
    def apply_stamp(self, frame, x, y, w, h):
        """スタンプ表示（枠と印）"""
        # 緑の枠
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        # 中央に円
        cx, cy = x + w // 2, y + h // 2
        cv2.circle(frame, (cx, cy), w // 3, (0, 255, 0), 2)
    
    def update_fps(self):
        """FPS計算"""
        current_time = time.time()
        self.fps = 1 / (current_time - self.prev_time + 0.001)
        self.prev_time = current_time
    
    def draw_info(self, frame):
        """画面に情報を表示"""
        h = frame.shape[0]
        
        # 左上にモード表示
        info_text = f"Mode: {self.mode.upper()} | FPS: {self.fps:.1f}"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 強度表示
        intensity_text = f"Intensity: {self.intensity}"
        cv2.putText(frame, intensity_text, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # ステータス表示
        status = "ON" if self.is_enabled else "OFF"
        status_text = f"Mosaic: {status}"
        cv2.putText(frame, status_text, (10, h - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def handle_key(self, key):
        """キー入力処理"""
        if key == ord('1'):
            self.mode = 'block'
            print("🟨 ブロックモザイクに変更")
        
        elif key == ord('2'):
            self.mode = 'blur'
            print("🌫️  ぼかしに変更")
        
        elif key == ord('3'):
            self.mode = 'stamp'
            print("🎯 スタンプモードに変更")
        
        elif key == ord('m'):
            self.is_enabled = not self.is_enabled
            status = "有効" if self.is_enabled else "無効"
            print(f"モザイク: {status}")
        
        elif key == ord('+') or key == ord('='):
            self.intensity = min(30, self.intensity + 1)
            print(f"強度UP: {self.intensity}")
        
        elif key == ord('-') or key == ord('_'):
            self.intensity = max(5, self.intensity - 1)
            print(f"強度DOWN: {self.intensity}")
    
    def process_frame(self, frame):
        """フレーム処理のメイン"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 顔を検出
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # 各顔を処理
        for (x, y, w, h) in faces:
            if self.mode == 'stamp':
                # スタンプモード：顔の枠を描画
                self.apply_stamp(frame, x, y, w, h)
            elif self.is_enabled:
                # モザイクモード
                face_roi = frame[y:y+h, x:x+w]
                
                if self.mode == 'block':
                    mosaic = self.apply_block_mosaic(face_roi)
                elif self.mode == 'blur':
                    mosaic = self.apply_blur_mosaic(face_roi)
                
                frame[y:y+h, x:x+w] = mosaic
        
        return frame
    
    def run(self):
        """メインループ"""
        print("\n=== 顔隠しカメラ ===")
        print("キー操作:")
        print("  1: ブロックモザイク")
        print("  2: ぼかし")
        print("  3: スタンプ表示")
        print("  m: モザイク ON/OFF")
        print("  +/-: 強度調整")
        print("  q: 終了")
        print("==================\n")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # フレーム処理
            frame = self.process_frame(frame)
            
            # 情報表示
            self.draw_info(frame)
            self.update_fps()
            
            # 表示
            cv2.imshow('Face Blur Camera', frame)
            
            # キー入力
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("終了します")
                break
            elif key != 255:
                self.handle_key(key)
        
        # クリーンアップ
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    app = FaceBlurApp()
    app.run()
