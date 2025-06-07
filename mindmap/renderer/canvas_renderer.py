class CanvasRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_node(self, node, selected=False):
        """Draw a node and optionally highlight it if selected."""
        x, y = node.position
        base_height = 20  # テキスト行ごとの基本高さ
        padding_x = 20    # 横方向の余白
        padding_y = 10    # 縦方向の余白

        # テキストの幅を計算
        text_width = self.canvas.bbox(
            self.canvas.create_text(0, 0, text=node.text, font=("Arial", 12, "bold"))
        )[2]
        # 幅と高さを計算
        width = text_width + padding_x * 2  # テキスト幅 + 横余白
        height = base_height + padding_y * 2  # テキスト高さ + 縦余白

        # 四角形の頂点座標を計算
        x0, y0 = x - width / 2, y - height / 2
        x1, y1 = x + width / 2, y + height / 2

        # ノードの背景 (青色)
        radius = 10  # 角の丸み
        if selected:
            self.canvas.create_rectangle(
                x0 - 4,
                y0 - 4,
                x1 + 4,
                y1 + 4,
                outline="#ffeb3b",
                width=2,
                tags=f"highlight_{node.id}",
            )
        self.canvas.create_rectangle(
            x0 + radius, y0, x1 - radius, y1, fill="#2d89ef", outline="", tags=f"node_bg_{node.id}"
        )
        self.canvas.create_rectangle(
            x0, y0 + radius, x1, y1 - radius, fill="#2d89ef", outline="", tags=f"node_bg_{node.id}"
        )
        self.canvas.create_oval(
            x0, y0, x0 + 2 * radius, y0 + 2 * radius, fill="#2d89ef", outline="", tags=f"node_bg_{node.id}"
        )
        self.canvas.create_oval(
            x1 - 2 * radius, y0, x1, y0 + 2 * radius, fill="#2d89ef", outline="", tags=f"node_bg_{node.id}"
        )
        self.canvas.create_oval(
            x0, y1 - 2 * radius, x0 + 2 * radius, y1, fill="#2d89ef", outline="", tags=f"node_bg_{node.id}"
        )
        self.canvas.create_oval(
            x1 - 2 * radius, y1 - 2 * radius, x1, y1, fill="#2d89ef", outline="", tags=f"node_bg_{node.id}"
        )

        # ノードのテキスト
        self.canvas.create_text(
            x, y, text=node.text, fill="#ffffff", font=("Arial", 12, "bold"), tags=f"text_{node.id}"
        )
        
    def draw_link(self, parent, child):
        """
        親ノードと子ノードを結ぶリンクを描画
        """
        x1, y1 = parent.position
        x2, y2 = child.position

        # ノード間のリンクを描画 (滑らかな線)
        self.canvas.create_line(
            x1, y1, x2, y2, fill="#ffffff", width=2, smooth=True, tags=f"link_{parent.id}_{child.id}"
        )

    def get_node_at(self, x, y):
        for node in self.canvas.mindmap.nodes.values():
            nx, ny = node.position
            if (x - nx) ** 2 + (y - ny) ** 2 <= 20 ** 2:
                return node
