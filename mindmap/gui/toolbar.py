
import tkinter as tk


class Toolbar(tk.Frame):
    def __init__(self, parent, canvas):
        super().__init__(parent, bg="#2e2e2e")
        self.canvas = canvas

        # ボタンの共通スタイル
        btn_style = {
            "bg": "#3b3b3b", "fg": "#ffffff",
            "activebackground": "#555555", "activeforeground": "#ffffff",
            "relief": "flat", "padx": 10, "pady": 4,
            "font": ("Arial", 10),
        }

        # ファイル操作
        tk.Button(self, text="保存 (Ctrl+S)", command=self.canvas.save_mindmap, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(self, text="読込 (Ctrl+O)", command=self.canvas.load_mindmap, **btn_style).pack(side="left", padx=3, pady=5)

        # セパレータ
        tk.Frame(self, width=2, bg="#555555").pack(side="left", fill="y", padx=6, pady=4)

        # ノード操作
        tk.Button(self, text="新規ノード", command=self.add_node_action, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(self, text="子ノード (Tab)", command=self.add_subnode_action, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(self, text="削除 (Del)", command=self.delete_selected_node, **btn_style).pack(side="left", padx=3, pady=5)

        # セパレータ
        tk.Frame(self, width=2, bg="#555555").pack(side="left", fill="y", padx=6, pady=4)

        # レイアウト
        tk.Button(self, text="ツリー整列", command=self.tree_layout_action, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(self, text="力学整列", command=self.force_layout_action, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(self, text="全体表示 (Ctrl+F)", command=self.canvas.fit_to_screen, **btn_style).pack(side="left", padx=3, pady=5)

        # セパレータ
        tk.Frame(self, width=2, bg="#555555").pack(side="left", fill="y", padx=6, pady=4)

        # 編集
        tk.Button(self, text="元に戻す", command=self.undo_action, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(self, text="やり直し", command=self.redo_action, **btn_style).pack(side="left", padx=3, pady=5)

        # 右端にスナップ切替
        self.snap_var = tk.BooleanVar(value=True)
        snap_cb = tk.Checkbutton(
            self, text="スナップ", variable=self.snap_var,
            command=self.toggle_snap,
            bg="#2e2e2e", fg="#ffffff", selectcolor="#3b3b3b",
            activebackground="#2e2e2e", activeforeground="#ffffff",
            font=("Arial", 10),
        )
        snap_cb.pack(side="right", padx=8, pady=5)

    def toggle_snap(self):
        self.canvas.snap_enabled = self.snap_var.get()
        self.canvas.draw()

    def delete_selected_node(self):
        """選択されたノードを削除"""
        if self.canvas.selected_node:
            self.canvas.mindmap.snapshot()
            self.canvas.mindmap.delete_node_and_descendants(self.canvas.selected_node.id)
            self.canvas.selected_node = None
            self.canvas.draw()

    def add_node_action(self):
        """新しいルートノードを追加"""
        self.canvas.mindmap.snapshot()
        new_node = self.canvas.mindmap.add_node("新規ノード")
        self.canvas.selected_node = new_node
        self.canvas.draw()
        self.canvas.edit_node_text_on_canvas(new_node)

    def add_subnode_action(self):
        """選択中のノードにサブノード追加"""
        if self.canvas.selected_node:
            self.canvas.mindmap.snapshot()
            new_node = self.canvas.mindmap.add_node("", parent_id=self.canvas.selected_node.id)
            self.canvas.draw()
            self.canvas.edit_node_text_on_canvas(new_node)

    def tree_layout_action(self):
        """ツリーレイアウトを適用"""
        self.canvas.mindmap.snapshot()
        self.canvas.mindmap.apply_tree_layout()
        self.canvas.fit_to_screen()

    def force_layout_action(self):
        """力学レイアウトを適用"""
        self.canvas.mindmap.snapshot()
        self.canvas.mindmap.apply_force_layout()
        self.canvas.fit_to_screen()

    def undo_action(self):
        """元に戻す"""
        if self.canvas.mindmap.undo():
            self.canvas.selected_node = None
            self.canvas.draw()

    def redo_action(self):
        """やり直し"""
        if self.canvas.mindmap.redo():
            self.canvas.selected_node = None
            self.canvas.draw()
