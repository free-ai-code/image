import os
import sys
import threading
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, Entry, filedialog, messagebox, StringVar, IntVar
from tkinter import ttk
import subprocess

# ============================================================================
# インストール確認・実行
# ============================================================================
def check_and_install_dependencies():
    """必要なライブラリのインストール確認と自動インストール"""
    required_packages = {
        'cairosvg': 'cairosvg',
        'PIL': 'pillow'
    }
    
    missing_packages = []
    
    # インストール済みライブラリを確認
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)
    
    # 不足しているパッケージをインストール
    if missing_packages:
        for package in missing_packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


# ============================================================================
# SVG変換処理コア
# ============================================================================
class SVGConverter:
    """SVGからPNGへの変換処理を担当するクラス"""
    
    def __init__(self):
        """初期化"""
        self.is_converting = False
        self.current_progress = 0
        self.progress_callback = None
        self.completion_callback = None
        self.error_callback = None
    
    def set_progress_callback(self, callback):
        """進捗コールバック設定"""
        self.progress_callback = callback
    
    def set_completion_callback(self, callback):
        """完了コールバック設定"""
        self.completion_callback = callback
    
    def set_error_callback(self, callback):
        """エラーコールバック設定"""
        self.error_callback = callback
    
    def _update_progress(self, value, message):
        """進捗を更新"""
        if self.progress_callback:
            self.progress_callback(value, message)
    
    def convert(self, svg_path, output_path, scale_factor, dpi):
        """
        SVGをPNGに変換
        
        Args:
            svg_path: 入力SVGファイルパス
            output_path: 出力PNGファイルパス
            scale_factor: 拡大倍率
            dpi: DPI設定
        """
        import cairosvg
        from PIL import Image
        import io
        
        try:
            self.is_converting = True
            svg_file = Path(svg_path)
            output_file = Path(output_path)
            
            # ステップ1: SVGを中間フォーマットに変換
            self._update_progress(20, 'SVGを変換中...')
            png_buffer = io.BytesIO()
            
            # cairosvgでSVGをPNGに変換（高DPI設定）
            cairosvg.svg2png(
                url=str(svg_file),
                write_to=png_buffer,
                dpi=dpi
            )
            png_buffer.seek(0)
            
            # ステップ2: Pillow(PIL)で読み込み
            self._update_progress(40, '画像を読み込み中...')
            img = Image.open(png_buffer)
            img.load()
            
            # ステップ3: アップスケーリング
            self._update_progress(60, 'アップスケール処理中...')
            original_width, original_height = img.size
            
            # 指定倍率でサイズを計算
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Lanczosフィルタで最高品質のリサイズ
            img_resized = img.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # ステップ4: PNG保存
            self._update_progress(80, 'ファイルを保存中...')
            
            # 出力ディレクトリが存在しない場合は作成
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # ロスレス品質でPNG保存
            img_resized.save(
                output_file,
                'PNG',
                quality=100,
                optimize=False
            )
            
            # メモリ解放
            img.close()
            img_resized.close()
            png_buffer.close()
            
            self._update_progress(100, '完了')
            
            # ファイル情報を取得
            file_size_kb = output_file.stat().st_size / 1024
            info = {
                'file_size': file_size_kb,
                'original_size': (original_width, original_height),
                'new_size': (new_width, new_height)
            }
            
            if self.completion_callback:
                self.completion_callback(str(output_file), info)
            
            self.is_converting = False
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(str(e))
            self.is_converting = False


# ============================================================================
# GUI アプリケーション
# ============================================================================
class SVGConverterGUI:
    """SVG変換ツールのGUIアプリケーション"""
    
    def __init__(self, root):
        """GUIの初期化"""
        self.root = root
        self.root.title('SVG to 4K PNG Converter')
        self.root.geometry('700x600')
        self.root.resizable(False, False)
        
        # パスの設定
        self.script_dir = Path(__file__).parent
        self.converter = SVGConverter()
        self.converter.set_progress_callback(self._on_progress)
        self.converter.set_completion_callback(self._on_completion)
        self.converter.set_error_callback(self._on_error)
        
        # 変数
        self.svg_path_var = StringVar(value='')
        self.output_path_var = StringVar(value='')
        self.scale_factor_var = IntVar(value=4)
        self.dpi_var = IntVar(value=96)
        self.is_converting = False
        
        # UI構築
        self._create_ui()
    
    def _create_ui(self):
        """UIコンポーネントを構築"""
        # メインフレーム
        main_frame = Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = Label(
            main_frame,
            text='SVG to 4K PNG Converter',
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 20))
        
        # 入力ファイル選択セクション
        input_frame = Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        input_frame.pack(fill='x', pady=10)
        
        Label(
            input_frame,
            text='入力SVGファイル:',
            font=('Arial', 10, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        input_inner_frame = Frame(input_frame, bg='#ffffff')
        input_inner_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        Entry(
            input_inner_frame,
            textvariable=self.svg_path_var,
            font=('Arial', 9),
            state='readonly'
        ).pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        Button(
            input_inner_frame,
            text='参照',
            command=self._select_svg_file,
            font=('Arial', 9),
            width=10
        ).pack(side='left')
        
        # 出力ファイル選択セクション
        output_frame = Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        output_frame.pack(fill='x', pady=10)
        
        Label(
            output_frame,
            text='出力PNGファイル:',
            font=('Arial', 10, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        output_inner_frame = Frame(output_frame, bg='#ffffff')
        output_inner_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        Entry(
            output_inner_frame,
            textvariable=self.output_path_var,
            font=('Arial', 9),
            state='readonly'
        ).pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        Button(
            output_inner_frame,
            text='参照',
            command=self._select_output_file,
            font=('Arial', 9),
            width=10
        ).pack(side='left')
        
        # 設定セクション
        settings_frame = Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        settings_frame.pack(fill='x', pady=10)
        
        Label(
            settings_frame,
            text='設定:',
            font=('Arial', 10, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(10, 10))
        
        # 拡大倍率
        scale_frame = Frame(settings_frame, bg='#ffffff')
        scale_frame.pack(fill='x', padx=10, pady=5)
        
        Label(
            scale_frame,
            text='拡大倍率:',
            font=('Arial', 9),
            bg='#ffffff',
            width=12,
            anchor='w'
        ).pack(side='left')
        
        scale_options = [
            ('1倍 (元のサイズ)', 1),
            ('2倍 (2K相当)', 2),
            ('3倍 (3K相当)', 3),
            ('4倍 (4K相当)', 4),
            ('6倍 (6K相当)', 6)
        ]
        
        scale_combo = ttk.Combobox(
            scale_frame,
            textvariable=self.scale_factor_var,
            values=[val for _, val in scale_options],
            state='readonly',
            width=20
        )
        scale_combo.pack(side='left', padx=(0, 10))
        
        # DPI設定
        dpi_frame = Frame(settings_frame, bg='#ffffff')
        dpi_frame.pack(fill='x', padx=10, pady=5)
        
        Label(
            dpi_frame,
            text='DPI:',
            font=('Arial', 9),
            bg='#ffffff',
            width=12,
            anchor='w'
        ).pack(side='left')
        
        dpi_options = [72, 96, 150, 300]
        
        dpi_combo = ttk.Combobox(
            dpi_frame,
            textvariable=self.dpi_var,
            values=dpi_options,
            state='readonly',
            width=20
        )
        dpi_combo.pack(side='left', padx=(0, 10))
        
        Label(
            dpi_frame,
            text='(高いほど高品質)',
            font=('Arial', 8),
            bg='#ffffff',
            fg='#666666'
        ).pack(side='left')
        
        # 進捗バー
        self.progress_var = StringVar(value='0')
        progress_frame = Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
        progress_frame.pack(fill='x', pady=10)
        
        Label(
            progress_frame,
            text='進捗:',
            font=('Arial', 9, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=400,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill='x', padx=10, pady=(0, 5))
        
        self.progress_label = Label(
            progress_frame,
            textvariable=self.progress_var,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#666666'
        )
        self.progress_label.pack(anchor='w', padx=10, pady=(0, 10))
        
        # ボタンセクション
        button_frame = Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(20, 0))
        
        self.convert_button = Button(
            button_frame,
            text='変換開始',
            command=self._start_conversion,
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=20,
            height=2
        )
        self.convert_button.pack(pady=10)
        
        self.cancel_button = Button(
            button_frame,
            text='キャンセル',
            command=self._cancel_conversion,
            font=('Arial', 9),
            bg='#f44336',
            fg='white',
            width=20,
            state='disabled'
        )
        self.cancel_button.pack()
    
    def _select_svg_file(self):
        """SVGファイル選択ダイアログ"""
        file_path = filedialog.askopenfilename(
            title='SVGファイルを選択',
            filetypes=[('SVG files', '*.svg'), ('All files', '*.*')],
            initialdir=str(self.script_dir)
        )
        
        if file_path:
            self.svg_path_var.set(file_path)
            
            # 出力パスを自動生成
            input_file = Path(file_path)
            output_file = input_file.parent / f'{input_file.stem}_4k.png'
            self.output_path_var.set(str(output_file))
    
    def _select_output_file(self):
        """出力ファイル選択ダイアログ"""
        file_path = filedialog.asksaveasfilename(
            title='保存先を選択',
            filetypes=[('PNG files', '*.png'), ('All files', '*.*')],
            initialdir=str(self.script_dir),
            defaultextension='.png'
        )
        
        if file_path:
            self.output_path_var.set(file_path)
    
    def _start_conversion(self):
        """変換処理を開始"""
        # 入力チェック
        svg_path = self.svg_path_var.get()
        output_path = self.output_path_var.get()
        
        if not svg_path:
            messagebox.showerror('エラー', 'SVGファイルを選択してください')
            return
        
        if not Path(svg_path).exists():
            messagebox.showerror('エラー', 'SVGファイルが見つかりません')
            return
        
        if not output_path:
            messagebox.showerror('エラー', '出力ファイルパスを指定してください')
            return
        
        # UI更新
        self.is_converting = True
        self.convert_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.progress_var.set('0%')
        self.progress_bar['value'] = 0
        
        # 別スレッドで変換処理を実行
        scale_factor = self.scale_factor_var.get()
        dpi = self.dpi_var.get()
        
        conversion_thread = threading.Thread(
            target=self.converter.convert,
            args=(svg_path, output_path, scale_factor, dpi),
            daemon=True
        )
        conversion_thread.start()
    
    def _cancel_conversion(self):
        """変換処理をキャンセル"""
        self.converter.is_converting = False
        self.is_converting = False
        self.convert_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.progress_var.set('キャンセルしました')
    
    def _on_progress(self, value, message):
        """進捗更新コールバック"""
        self.progress_bar['value'] = value
        self.progress_var.set(f'{value}% - {message}')
        self.root.update()
    
    def _on_completion(self, output_path, info):
        """完了コールバック"""
        file_size = info['file_size']
        original_size = info['original_size']
        new_size = info['new_size']
        
        message = (
            f'変換が完了しました！\n\n'
            f'出力ファイル: {output_path}\n'
            f'ファイルサイズ: {file_size:.2f} KB\n'
            f'元のサイズ: {original_size[0]}x{original_size[1]} px\n'
            f'変換後のサイズ: {new_size[0]}x{new_size[1]} px'
        )
        
        messagebox.showinfo('成功', message)
        
        # UI復帰
        self.convert_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.is_converting = False
    
    def _on_error(self, error_message):
        """エラーコールバック"""
        messagebox.showerror('エラーが発生しました', f'詳細: {error_message}')
        
        # UI復帰
        self.convert_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.is_converting = False


# ============================================================================
# メイン実行
# ============================================================================
if __name__ == '__main__':
    # 依存パッケージのインストール確認
    check_and_install_dependencies()
    
    # GUIアプリケーション起動
    root = Tk()
    app = SVGConverterGUI(root)
    root.mainloop()
