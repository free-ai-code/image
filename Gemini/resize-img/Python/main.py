import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI画像リサイズツール")
        self.root.geometry("420x380")
        self.root.resizable(False, False)

        self.image_path = None
        self.original_img = None
        self.aspect_ratio = 1.0

        # UI要素の作成
        self.create_widgets()

    def create_widgets(self):
        # 1. ファイル選択エリア
        btn_select = tk.Button(self.root, text="画像ファイルを選択", command=self.select_image, font=("Arial", 10, "bold"))
        btn_select.pack(pady=15)

        self.lbl_path = tk.Label(self.root, text="ファイルが選択されていません", fg="gray", wraplength=380)
        self.lbl_path.pack()

        # 2. 元サイズ表示
        self.lbl_orig_size = tk.Label(self.root, text="元のサイズ: -", font=("Arial", 9))
        self.lbl_orig_size.pack(pady=5)

        # 3. サイズ入力エリア
        frame_size = tk.Frame(self.root)
        frame_size.pack(pady=15)

        tk.Label(frame_size, text="幅 (px):").grid(row=0, column=0, padx=5)
        self.entry_width = tk.Entry(frame_size, width=8)
        self.entry_width.grid(row=0, column=1, padx=5)
        self.entry_width.bind("<KeyRelease>", self.on_width_change)

        tk.Label(frame_size, text="高さ (px):").grid(row=0, column=2, padx=5)
        self.entry_height = tk.Entry(frame_size, width=8)
        self.entry_height.grid(row=0, column=3, padx=5)
        self.entry_height.bind("<KeyRelease>", self.on_height_change)

        # 4. 縦横比維持チェックボックス
        self.var_keep_aspect = tk.BooleanVar(value=True)
        chk_aspect = tk.Checkbutton(self.root, text="縦横比を維持する", variable=self.var_keep_aspect)
        chk_aspect.pack()

        # 5. 実行ボタン
        self.btn_save = tk.Button(self.root, text="リサイズして保存", command=self.save_image, state=tk.DISABLED, bg="#2563eb", fg="white", font=("Arial", 10, "bold"))
        self.btn_save.pack(pady=20)

    def select_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("画像ファイル", "*.jpg *.jpeg *.png *.webp *.bmp")]
        )
        if not path:
            return

        self.image_path = path
        self.lbl_path.config(text=os.path.basename(path), fg="black")

        # 画像読み込みとサイズ取得
        self.original_img = Image.open(path)
        w, h = self.original_img.size
        self.aspect_ratio = w / h

        self.lbl_orig_size.config(text=f"元のサイズ: {w} x {h} px")

        # 入力欄に初期値をセット
        self.entry_width.delete(0, tk.END)
        self.entry_width.insert(0, str(w))
        self.entry_height.delete(0, tk.END)
        self.entry_height.insert(0, str(h))

        self.btn_save.config(state=tk.NORMAL)

    def on_width_change(self, event):
        if not self.var_keep_aspect.get() or not self.original_img:
            return
        val = self.entry_width.get()
        if val.isdigit() and int(val) > 0:
            new_h = round(int(val) / self.aspect_ratio)
            self.entry_height.delete(0, tk.END)
            self.entry_height.insert(0, str(new_h))

    def on_height_change(self, event):
        if not self.var_keep_aspect.get() or not self.original_img:
            return
        val = self.entry_height.get()
        if val.isdigit() and int(val) > 0:
            new_w = round(int(val) * self.aspect_ratio)
            self.entry_width.delete(0, tk.END)
            self.entry_width.insert(0, str(new_w))

    def save_image(self):
        try:
            w = int(self.entry_width.get())
            h = int(self.entry_height.get())
            if w <= 0 or h <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("エラー", "幅と高さには正しい数値を入力してください。")
            return

        # 保存先を選択
        ext = os.path.splitext(self.image_path)[1]
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("画像ファイル", f"*{ext}")],
            initialfile=f"resized_{os.path.basename(self.image_path)}"
        )
        if not save_path:
            return

        # リサイズ＆保存
        resized_img = self.original_img.resize((w, h), Image.Resampling.LANCZOS)
        resized_img.save(save_path)
        messagebox.showinfo("成功", f"画像を保存しました:\n{save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()
