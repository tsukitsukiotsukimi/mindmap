import tkinter as tk
from gui.canvas import Canvas
from gui.toolbar import Toolbar
from model.data_model import MindMap


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MindMap Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")

        self.mindmap = MindMap()

        # ツールバーを上部に配置
        self.toolbar_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        # キャンバスを中央に配置
        self.canvas = Canvas(self.root, self.mindmap)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ツールバー初期化（キャンバスの後）
        self.toolbar = Toolbar(self.toolbar_frame, self.canvas)
        self.toolbar.pack(fill=tk.X)

        # ウィンドウリサイズ時に再描画
        self.canvas.bind("<Configure>", self._on_resize)

        # 初回描画を遅延実行
        self.root.after(100, self.canvas.draw)

    def _on_resize(self, event):
        """ウィンドウリサイズ時の再描画"""
        self.canvas.draw()

    def run(self):
        """Tkinterメインループ開始"""
        self.root.mainloop()
