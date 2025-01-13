
import tkinter as tk
import numpy as np
from tkinter import filedialog
from renderer.canvas_renderer import CanvasRenderer

class Canvas(tk.Canvas):

    def __init__(self, parent, mindmap):
        super().__init__(parent, bg="#1e1e1e", highlightthickness=0)
        self.mindmap = mindmap
        self.renderer = CanvasRenderer(self)
        self.selected_node = None
        self.dragging_node = None
        self.text_editor = None  # テキスト編集用エントリ
        self.scale_factor = 1.0

        # イベントバインディング
        self.bind("<Button-1>", self.on_click)           # ノード選択
        self.bind("<B1-Motion>", self.on_drag)          # ドラッグ中
        self.bind("<ButtonRelease-1>", self.on_release) # ドラッグ終了
        self.bind("<MouseWheel>", self.on_zoom)         # ズーム
        self.bind("<Double-1>", self.on_double_click)   # ダブルクリックで文字列編集
    
    def save_mindmap(self):
        """
        マインドマップを保存
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if file_path:
            self.mindmap.save_to_file(file_path)
            print(f"MindMap saved to {file_path}")

    def load_mindmap(self):
        """
        マインドマップを読み込み
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.mindmap.load_from_file(file_path)
            self.draw()  # 読み込み後に再描画
            print(f"MindMap loaded from {file_path}")
    
    def draw(self):
        # 全ての描画をリセット
        self.delete("all")
        for parent, child in self.mindmap.get_links():
            self.renderer.draw_link(parent, child)
        for node in self.mindmap.nodes.values():
            self.renderer.draw_node(node)

    def on_zoom(self, event):
        """
        マウスホイール位置を中心にズームイン/ズームアウトを処理
        """
        zoom_direction = 1 if event.delta > 0 else -1
        scale_change = 1.1 if zoom_direction > 0 else 0.9
        self.scale_factor *= scale_change

        # マウス位置を取得
        mouse_x, mouse_y = event.x, event.y

        print(f"Zoom scale factor: {self.scale_factor}")  # デバッグ: ズーム倍率

        # 全てのノードとリンクの位置を再計算
        for node in self.mindmap.nodes.values():
            if not isinstance(node.position, np.ndarray):
                node.position = np.array(node.position, dtype=float)
            
            # ノード位置をマウス位置を基準にスケーリング
            offset = node.position - np.array([mouse_x, mouse_y])
            scaled_offset = offset * scale_change
            node.position = np.array([mouse_x, mouse_y]) + scaled_offset

            print(f"Node {node.text} position: {node.position}")  # デバッグ: ノード位置

        self.draw()

    def on_drag(self, event):
        """
        ノードをドラッグ中に位置を更新し、親子関係を考慮して再配置
        """
        if self.dragging_node:
            # 移動量を計算
            dx = event.x - self.dragging_node.position[0]
            dy = event.y - self.dragging_node.position[1]
            
            # 親ノードを移動
            self.move_node_with_children(self.dragging_node, dx, dy)
            self.draw()  # 再描画
    
    def move_node_with_children(self, node, dx, dy):
        """
        指定されたノードとそのすべての子ノードを移動
        """
        # ノードの位置を更新
        node.position += np.array([dx, dy])
    
        # 子ノードも再帰的に移動
        for child in node.children:
            self.move_node_with_children(child, dx, dy)


    def on_release(self, event):
        # ドラッグ終了
        if self.dragging_node:
            print(f"Moved node: {self.dragging_node.text} to ({event.x}, {event.y})")
        self.dragging_node = None

    def on_double_click(self, event):
        """
        ノード上でダブルクリックしてテキストを編集
        """
        clicked_node = self.renderer.get_node_at(event.x, event.y)
        if clicked_node:
            self.edit_node_text_on_canvas(clicked_node)

    def edit_node_text_on_canvas(self, node):
        """
        ノード上で直接テキストを編集
        """
        # 既存のエントリがあれば削除
        if self.text_editor:
            self.text_editor.destroy()

        # ノード位置を取得
        x, y = node.position
        width = 100  # ノードの幅に合わせて調整
        height = 20

        # エントリ作成
        self.text_editor = tk.Entry(self, font=("Arial", 12), justify="center")
        self.text_editor.insert(0, node.text)  # 現在のノードのテキストを挿入
        self.text_editor.place(x=x - width / 2, y=y - height / 2, width=width, height=height)
        self.text_editor.focus()

        # エントリのアクション設定
        self.text_editor.bind("<Return>", lambda e: self.save_text_edit(node))
        self.text_editor.bind("<FocusOut>", lambda e: self.save_text_edit(node))
    
    def save_text_edit(self, node):
        """
        エントリのテキストをノードに保存し、エントリを削除
        """
        if self.text_editor:
            node.text = self.text_editor.get()  # ノードに新しいテキストを保存
            self.text_editor.destroy()
            self.text_editor = None
            self.draw()  # 再描画
    # Canvasクラス内の選択ノード管理
    def on_click(self, event):
        """
        クリックされたノードを取得して選択
        """
        clicked_node = self.renderer.get_node_at(event.x, event.y)
        if clicked_node:
            self.dragging_node = clicked_node  # ドラッグ対象ノードとして設定
            self.selected_node = clicked_node
            print(f"Selected node: {self.selected_node.text}")
        else:
            self.selected_node = None  # 何も選択されていない場合リセット

