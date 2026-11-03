import tkinter as tk
from tkinter import filedialog, messagebox
from cairosvg import svg2png
from pathlib import Path

def select_svg():
    path = filedialog.askopenfilename(
        title="SVGファイルを選択",
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
    )
    if path:
        svg_path_var.set(path)

def select_output():
    path = filedialog.asksaveasfilename(
        title="保存先を選択",
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")]
    )
    if path:
        output_path_var.set(path)

def convert_svg():
    svg_path = svg_path_var.get().strip()
    output_path = output_path_var.get().strip()

    if not svg_path:
        messagebox.showerror("エラー", "SVGファイルを選択してください")
        return

    if not output_path:
        messagebox.showerror("エラー", "保存先を選択してください")
        return

    try:
        svg2png(
            url=svg_path,
            write_to=output_path,
            output_width=int(width_var.get()) if width_var.get().strip() else None,
            output_height=int(height_var.get()) if height_var.get().strip() else None
        )
        messagebox.showinfo("完了", f"PNGに変換しました\n{output_path}")
    except Exception as e:
        messagebox.showerror("変換失敗", str(e))

root = tk.Tk()
root.title("SVG → PNG 変換")
root.geometry("500x220")

svg_path_var = tk.StringVar()
output_path_var = tk.StringVar()
width_var = tk.StringVar()
height_var = tk.StringVar()

tk.Label(root, text="SVGファイル").pack(anchor="w", padx=10, pady=(10, 0))
tk.Entry(root, textvariable=svg_path_var, width=50).pack(padx=10)
tk.Button(root, text="SVGを選択", command=select_svg).pack(padx=10, pady=5)

tk.Label(root, text="保存先PNG").pack(anchor="w", padx=10, pady=(10, 0))
tk.Entry(root, textvariable=output_path_var, width=50).pack(padx=10)
tk.Button(root, text="保存先を選択", command=select_output).pack(padx=10, pady=5)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="幅").grid(row=0, column=0, padx=5)
tk.Entry(frame, textvariable=width_var, width=10).grid(row=0, column=1, padx=5)
tk.Label(frame, text="高さ").grid(row=0, column=2, padx=5)
tk.Entry(frame, textvariable=height_var, width=10).grid(row=0, column=3, padx=5)

tk.Button(root, text="PNGに変換", command=convert_svg, bg="#3b82f6", fg="white").pack(pady=10)

root.mainloop()
