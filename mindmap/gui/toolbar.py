
import tkinter as tk


class Toolbar(tk.Frame):
    def __init__(self, parent, canvas):
        super().__init__(parent, bg="#2e2e2e")  # ダークテーマ背景
        self.canvas = canvas

        save_button = tk.Button(self, text="Save", command=self.canvas.save_mindmap, bg="#3b3b3b", fg="#ffffff")
        save_button.pack(side="left", padx=5, pady=5)

        load_button = tk.Button(self, text="Load", command=self.canvas.load_mindmap, bg="#3b3b3b", fg="#ffffff")
        load_button.pack(side="left", padx=5, pady=5)

        add_node_button = tk.Button(self, text="New Node", command=self.add_node_action, bg="#3b3b3b", fg="#ffffff")
        add_node_button.pack(side="left", padx=5, pady=5)

        add_subnode_button = tk.Button(self, text="Subnode", command=self.add_subnode_action, bg="#3b3b3b", fg="#ffffff")
        add_subnode_button.pack(side="left", padx=5, pady=5)
        delete_node_button = tk.Button(self, text="Delete", command=self.delete_selected_node, bg="#3b3b3b", fg="#ffffff")
        delete_node_button.pack(side="left", padx=5, pady=5)
    def delete_selected_node(self):
        """
        選択されたノードとその子孫ノードを削除
        """
        selected_node = self.canvas.selected_node
        if selected_node:
            self.canvas.mindmap.delete_node_and_descendants(selected_node.id)
            self.canvas.selected_node = None  # 選択状態をリセット
            self.canvas.draw()  # 再描画

    def add_node_action(self):
        """
        新しいノードを追加
        """
        new_node = self.canvas.mindmap.add_node("New Node")
        self.canvas.draw()  # 再描画

    def add_subnode_action(self):
        """
        選択中のノードにサブノードを追加
        """
        selected_node = self.canvas.selected_node
        if selected_node:
            self.canvas.mindmap.add_node("Subnode", parent_id=selected_node.id)
            self.canvas.draw()  # 再描画


