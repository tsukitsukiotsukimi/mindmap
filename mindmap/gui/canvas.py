
import tkinter as tk
import numpy as np
from tkinter import filedialog
from renderer.canvas_renderer import CanvasRenderer


# スナップグリッドのサイズ
GRID_SIZE = 20


def snap_to_grid(x, y, grid_size=GRID_SIZE):
    """座標をグリッドにスナップ"""
    return round(x / grid_size) * grid_size, round(y / grid_size) * grid_size


class Canvas(tk.Canvas):

    def __init__(self, parent, mindmap):
        super().__init__(parent, bg="#1e1e1e", highlightthickness=0)
        self.mindmap = mindmap
        self.renderer = CanvasRenderer(self)
        self.selected_node = None
        self.dragging_node = None
        self.text_editor = None
        self.scale_factor = 1.0

        # パン（スクロール）用
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.panning = False

        # ドラッグ開始位置
        self.drag_start_x = 0
        self.drag_start_y = 0

        # スナップ有効/無効
        self.snap_enabled = True

        # 右クリックメニュー
        self.menu = tk.Menu(self, tearoff=0, bg="#2e2e2e", fg="#ffffff",
                            activebackground="#4a4a4a", activeforeground="#ffffff")
        self.menu.add_command(label="子ノード追加", command=self.menu_add_child)
        self.menu.add_command(label="折りたたみ切替", command=self.menu_toggle_collapse)
        self.menu.add_separator()
        self.menu.add_command(label="削除", command=self.menu_delete_node)

        # マウスイベント
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Button-3>", self.on_right_click)

        # パン操作（中クリック or Shift+左ドラッグ）
        self.bind("<Button-2>", self.on_pan_start)
        self.bind("<B2-Motion>", self.on_pan_move)
        self.bind("<ButtonRelease-2>", self.on_pan_end)
        self.bind("<Shift-Button-1>", self.on_pan_start)
        self.bind("<Shift-B1-Motion>", self.on_pan_move)
        self.bind("<Shift-ButtonRelease-1>", self.on_pan_end)

        # ズーム
        self.bind("<MouseWheel>", self.on_zoom)
        self.bind("<Button-4>", self.on_zoom_linux)  # Linux scroll up
        self.bind("<Button-5>", self.on_zoom_linux)  # Linux scroll down

        # キーボードショートカット
        self.bind("<Key>", self.on_key)
        self.focus_set()

        # ステータスバー用テキスト
        self.status_text = None

    def on_key(self, event):
        """キーボードショートカット処理"""
        # テキスト編集中はスルー
        if self.text_editor:
            return

        if event.keysym == "Tab":
            # Tab: 選択ノードに子ノード追加
            if self.selected_node:
                self.mindmap.snapshot()
                new_node = self.mindmap.add_node("", parent_id=self.selected_node.id)
                self.draw()
                self.selected_node = new_node
                self.edit_node_text_on_canvas(new_node)
            return "break"

        elif event.keysym == "Delete" or event.keysym == "BackSpace":
            # Delete: 選択ノード削除
            if self.selected_node:
                self.mindmap.snapshot()
                self.mindmap.delete_node_and_descendants(self.selected_node.id)
                self.selected_node = None
                self.draw()

        elif event.keysym == "Return":
            # Enter: 選択ノードのテキスト編集
            if self.selected_node:
                self.edit_node_text_on_canvas(self.selected_node)

        elif event.keysym == "Escape":
            # Escape: 選択解除 / テキスト編集キャンセル
            if self.text_editor:
                self.text_editor.destroy()
                self.text_editor = None
            self.selected_node = None
            self.draw()

        elif event.keysym == "space":
            # Space: 折りたたみ切替
            if self.selected_node and self.selected_node.children:
                self.mindmap.snapshot()
                self.selected_node.collapsed = not self.selected_node.collapsed
                self.draw()

        elif event.keysym == "z" and (event.state & 0x4):  # Ctrl+Z
            if self.mindmap.undo():
                self.selected_node = None
                self.draw()

        elif event.keysym == "y" and (event.state & 0x4):  # Ctrl+Y
            if self.mindmap.redo():
                self.selected_node = None
                self.draw()

        elif event.keysym == "s" and (event.state & 0x4):  # Ctrl+S
            self.save_mindmap()

        elif event.keysym == "o" and (event.state & 0x4):  # Ctrl+O
            self.load_mindmap()

        elif event.keysym == "f" and (event.state & 0x4):  # Ctrl+F
            self.fit_to_screen()

        # 矢印キーでノード間を移動
        elif event.keysym in ("Left", "Right", "Up", "Down"):
            self._navigate_nodes(event.keysym)

    def _navigate_nodes(self, direction):
        """矢印キーでノード間をナビゲーション"""
        if not self.selected_node:
            # ノード未選択ならルートを選択
            if self.mindmap.root:
                self.selected_node = self.mindmap.root
                self.draw()
            return

        node = self.selected_node
        parent = self.mindmap.get_parent(node.id)

        if direction == "Left":
            # 親ノードへ
            if parent:
                self.selected_node = parent
                self.draw()
        elif direction == "Right":
            # 最初の子ノードへ
            if node.children and not node.collapsed:
                self.selected_node = node.children[0]
                self.draw()
        elif direction == "Up" or direction == "Down":
            # 兄弟ノード間を移動
            if parent:
                siblings = parent.children
                idx = siblings.index(node)
                if direction == "Up" and idx > 0:
                    self.selected_node = siblings[idx - 1]
                    self.draw()
                elif direction == "Down" and idx < len(siblings) - 1:
                    self.selected_node = siblings[idx + 1]
                    self.draw()

    def save_mindmap(self):
        """マインドマップを保存"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if file_path:
            self.mindmap.save_to_file(file_path)

    def load_mindmap(self):
        """マインドマップを読み込み"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.mindmap.load_from_file(file_path)
            self.selected_node = None
            self.draw()

    def draw(self):
        """キャンバスを再描画"""
        self.delete("all")

        # グリッド描画（スナップ有効時）
        if self.snap_enabled:
            self._draw_grid()

        # 表示すべきリンクを描画
        visible_links = self.mindmap.get_visible_links()
        for parent, child in visible_links:
            depth = self.mindmap.get_node_depth(parent)
            self.renderer.draw_link(parent, child, depth=depth)

        # 表示すべきノードを描画
        visible_nodes = self.mindmap.get_visible_nodes()
        for node in visible_nodes:
            depth = self.mindmap.get_node_depth(node)
            self.renderer.draw_node(
                node,
                selected=(node == self.selected_node),
                depth=depth
            )

        # ステータスバー
        self._draw_status()

        # キーボードフォーカスを確保
        self.focus_set()

    def _draw_grid(self):
        """薄いドットグリッドを描画"""
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600
        grid = GRID_SIZE * 3  # グリッドは3倍の間隔でドット表示
        for x in range(0, w, grid):
            for y in range(0, h, grid):
                self.create_oval(
                    x - 1, y - 1, x + 1, y + 1,
                    fill="#2a2a2a", outline="", tags="grid"
                )

    def _draw_status(self):
        """ステータス情報を表示"""
        node_count = len(self.mindmap.nodes)
        info = f"ノード数: {node_count}"
        if self.selected_node:
            info += f"  |  選択: {self.selected_node.text}"
        if self.snap_enabled:
            info += "  |  スナップ: ON"

        self.create_text(
            10, self.winfo_height() - 10 if self.winfo_height() > 50 else 590,
            text=info, fill="#666666", font=("Arial", 9),
            anchor="sw", tags="status"
        )

    def fit_to_screen(self):
        """全ノードが画面に収まるようにビューを調整"""
        if not self.mindmap.nodes:
            return

        positions = [n.position for n in self.mindmap.nodes.values()]
        min_x = min(p[0] for p in positions) - 100
        max_x = max(p[0] for p in positions) + 100
        min_y = min(p[1] for p in positions) - 80
        max_y = max(p[1] for p in positions) + 80

        w = self.winfo_width() or 800
        h = self.winfo_height() or 600

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        target_cx = w / 2
        target_cy = h / 2

        dx = target_cx - center_x
        dy = target_cy - center_y

        for node in self.mindmap.nodes.values():
            node.position += np.array([dx, dy])

        self.draw()

    def on_zoom(self, event):
        """ズームイン/ズームアウト"""
        zoom_direction = 1 if event.delta > 0 else -1
        self._apply_zoom(zoom_direction, event.x, event.y)

    def on_zoom_linux(self, event):
        """Linux用ズーム"""
        zoom_direction = 1 if event.num == 4 else -1
        self._apply_zoom(zoom_direction, event.x, event.y)

    def _apply_zoom(self, direction, mx, my):
        scale_change = 1.1 if direction > 0 else 0.9
        self.scale_factor *= scale_change

        for node in self.mindmap.nodes.values():
            offset = node.position - np.array([mx, my])
            node.position = np.array([mx, my]) + offset * scale_change

        self.draw()

    def on_pan_start(self, event):
        """パン開始"""
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.panning = True

    def on_pan_move(self, event):
        """パン移動"""
        if self.panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.pan_start_x = event.x
            self.pan_start_y = event.y

            for node in self.mindmap.nodes.values():
                node.position += np.array([dx, dy])
            self.draw()

    def on_pan_end(self, event):
        """パン終了"""
        self.panning = False

    def on_drag(self, event):
        """ノードドラッグ"""
        if self.panning:
            return
        if self.dragging_node:
            if self.snap_enabled:
                tx, ty = snap_to_grid(event.x, event.y)
            else:
                tx, ty = event.x, event.y

            dx = tx - self.dragging_node.position[0]
            dy = ty - self.dragging_node.position[1]
            self.move_node_with_children(self.dragging_node, dx, dy)
            self.draw()

    def move_node_with_children(self, node, dx, dy):
        """ノードとすべての子ノードを移動"""
        node.position += np.array([dx, dy])
        for child in node.children:
            self.move_node_with_children(child, dx, dy)

    def on_release(self, event):
        """ドラッグ終了"""
        self.dragging_node = None

    def on_click(self, event):
        """クリック処理"""
        # テキスト編集中なら確定
        if self.text_editor:
            self.save_text_edit(self._editing_node)

        clicked_node = self.renderer.get_node_at(event.x, event.y)
        if clicked_node:
            self.dragging_node = clicked_node
            self.selected_node = clicked_node
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            # ドラッグ開始時にスナップショット保存
            self.mindmap.snapshot()
        else:
            self.selected_node = None
        self.draw()

    def on_double_click(self, event):
        """ダブルクリックでテキスト編集"""
        clicked_node = self.renderer.get_node_at(event.x, event.y)
        if clicked_node:
            self.edit_node_text_on_canvas(clicked_node)

    def edit_node_text_on_canvas(self, node):
        """ノード上で直接テキスト編集"""
        if self.text_editor:
            self.text_editor.destroy()

        self._editing_node = node
        x, y = node.position
        width = max(120, len(node.text) * 10 + 40)
        height = 28

        self.text_editor = tk.Entry(
            self, font=("Arial", 12), justify="center",
            bg="#3b3b3b", fg="#ffffff", insertbackground="#ffffff",
            relief="flat", highlightthickness=2,
            highlightcolor="#ffeb3b", highlightbackground="#555555"
        )
        self.text_editor.insert(0, node.text)
        self.text_editor.place(
            x=x - width / 2, y=y - height / 2,
            width=width, height=height
        )
        self.text_editor.focus()
        self.text_editor.select_range(0, tk.END)

        self.text_editor.bind("<Return>", lambda e: self.save_text_edit(node))
        self.text_editor.bind("<Escape>", lambda e: self.cancel_text_edit())

    def save_text_edit(self, node):
        """テキスト編集を保存"""
        if self.text_editor:
            new_text = self.text_editor.get().strip()
            if new_text:
                self.mindmap.snapshot()
                node.text = new_text
            self.text_editor.destroy()
            self.text_editor = None
            self._editing_node = None
            self.draw()

    def cancel_text_edit(self):
        """テキスト編集をキャンセル"""
        if self.text_editor:
            self.text_editor.destroy()
            self.text_editor = None
            self._editing_node = None
            self.draw()

    def on_right_click(self, event):
        """右クリックメニュー表示"""
        node = self.renderer.get_node_at(event.x, event.y)
        if node:
            self.selected_node = node
            self.draw()
            self.menu.tk_popup(event.x_root, event.y_root)
        else:
            self.selected_node = None
            self.draw()

    def menu_add_child(self):
        """右クリックメニュー: 子ノード追加"""
        if self.selected_node:
            self.mindmap.snapshot()
            new_node = self.mindmap.add_node("", parent_id=self.selected_node.id)
            self.draw()
            self.edit_node_text_on_canvas(new_node)

    def menu_toggle_collapse(self):
        """右クリックメニュー: 折りたたみ切替"""
        if self.selected_node and self.selected_node.children:
            self.mindmap.snapshot()
            self.selected_node.collapsed = not self.selected_node.collapsed
            self.draw()

    def menu_delete_node(self):
        """右クリックメニュー: ノード削除"""
        if self.selected_node:
            self.mindmap.snapshot()
            self.mindmap.delete_node_and_descendants(self.selected_node.id)
            self.selected_node = None
            self.draw()
