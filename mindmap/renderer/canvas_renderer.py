import math

# 深さに応じたノードカラーパレット
DEPTH_COLORS = [
    "#2d89ef",  # 青 (ルート)
    "#00a86b",  # 緑
    "#e67e22",  # オレンジ
    "#9b59b6",  # 紫
    "#e74c3c",  # 赤
    "#1abc9c",  # ティール
    "#f39c12",  # 黄
    "#3498db",  # ライトブルー
]

LINK_COLORS = [
    "#5ba3f0",
    "#4dc98b",
    "#f0a050",
    "#b87dd4",
    "#f07070",
    "#4dd4b0",
    "#f5b840",
    "#60b0f0",
]


class CanvasRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

    def _get_depth_color(self, depth):
        return DEPTH_COLORS[depth % len(DEPTH_COLORS)]

    def _get_link_color(self, depth):
        return LINK_COLORS[depth % len(LINK_COLORS)]

    def draw_node(self, node, selected=False, depth=0):
        """ノードを描画（深さに応じた色、影付き）"""
        x, y = node.position
        padding_x = 24
        padding_y = 12

        # テキストサイズを計算
        font_size = 14 if depth == 0 else 12
        font_weight = "bold"
        font = ("Arial", font_size, font_weight)

        temp_id = self.canvas.create_text(0, 0, text=node.text, font=font)
        bbox = self.canvas.bbox(temp_id)
        self.canvas.delete(temp_id)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        width = text_width + padding_x * 2
        height = text_height + padding_y * 2

        x0, y0 = x - width / 2, y - height / 2
        x1, y1 = x + width / 2, y + height / 2

        radius = 12
        fill_color = self._get_depth_color(depth)

        # 影を描画
        shadow_offset = 3
        self._draw_rounded_rect(
            x0 + shadow_offset, y0 + shadow_offset,
            x1 + shadow_offset, y1 + shadow_offset,
            radius, fill="#111111", outline="", tag=f"shadow_{node.id}"
        )

        # 選択ハイライト
        if selected:
            self._draw_rounded_rect(
                x0 - 4, y0 - 4, x1 + 4, y1 + 4,
                radius + 2, fill="", outline="#ffeb3b", width=3,
                tag=f"highlight_{node.id}"
            )

        # ノード本体
        self._draw_rounded_rect(
            x0, y0, x1, y1, radius,
            fill=fill_color, outline="", tag=f"node_bg_{node.id}"
        )

        # 折りたたみインジケーター
        if node.children and node.collapsed:
            indicator_x = x1 - 8
            indicator_y = y0 + 8
            self.canvas.create_text(
                indicator_x, indicator_y, text=f"+{len(node.children)}",
                fill="#ffffff", font=("Arial", 8, "bold"),
                tags=f"collapse_{node.id}"
            )

        # ノードテキスト
        self.canvas.create_text(
            x, y, text=node.text, fill="#ffffff", font=font,
            tags=f"text_{node.id}"
        )

        # バウンディングボックスを保存
        node.bbox = (x0, y0, x1, y1)

    def _draw_rounded_rect(self, x0, y0, x1, y1, radius, fill="", outline="", width=1, tag=""):
        """角丸四角形を描画"""
        r = min(radius, (x1 - x0) / 2, (y1 - y0) / 2)
        tags = tag

        # 中央部分の四角形（2つ）
        self.canvas.create_rectangle(
            x0 + r, y0, x1 - r, y1,
            fill=fill, outline="", tags=tags
        )
        self.canvas.create_rectangle(
            x0, y0 + r, x1, y1 - r,
            fill=fill, outline="", tags=tags
        )

        # 4つの角の楕円
        self.canvas.create_oval(
            x0, y0, x0 + 2 * r, y0 + 2 * r,
            fill=fill, outline="", tags=tags
        )
        self.canvas.create_oval(
            x1 - 2 * r, y0, x1, y0 + 2 * r,
            fill=fill, outline="", tags=tags
        )
        self.canvas.create_oval(
            x0, y1 - 2 * r, x0 + 2 * r, y1,
            fill=fill, outline="", tags=tags
        )
        self.canvas.create_oval(
            x1 - 2 * r, y1 - 2 * r, x1, y1,
            fill=fill, outline="", tags=tags
        )

        # アウトライン（選択ハイライト用）
        if outline:
            points = self._rounded_rect_points(x0, y0, x1, y1, r)
            self.canvas.create_polygon(
                points, fill="", outline=outline, width=width,
                smooth=True, tags=tags
            )

    def _rounded_rect_points(self, x0, y0, x1, y1, r):
        """角丸四角形のポイントリストを生成"""
        points = []
        # 各角にアーク用のポイントを追加
        steps = 8
        for i in range(steps + 1):
            angle = math.pi / 2 * i / steps
            points.extend([x1 - r + r * math.cos(angle), y0 + r - r * math.sin(angle)])
        for i in range(steps + 1):
            angle = math.pi / 2 * i / steps
            points.extend([x1 - r + r * math.sin(angle), y1 - r + r * math.cos(angle)])  # noqa: E501
        for i in range(steps + 1):
            angle = math.pi / 2 * i / steps
            points.extend([x0 + r - r * math.cos(angle), y1 - r + r * math.sin(angle)])
        for i in range(steps + 1):
            angle = math.pi / 2 * i / steps
            points.extend([x0 + r - r * math.sin(angle), y0 + r - r * math.cos(angle)])
        return points

    def draw_link(self, parent, child, depth=0):
        """親ノードと子ノードをベジェ曲線で結ぶ"""
        px, py = parent.position
        cx, cy = child.position

        link_color = self._get_link_color(depth)

        # 親ノードの右端から子ノードの左端へ
        # ベジェ曲線の制御点
        mid_x = (px + cx) / 2
        points = [
            px, py,
            mid_x, py,
            mid_x, cy,
            cx, cy,
        ]

        self.canvas.create_line(
            *points,
            fill=link_color, width=2, smooth=True,
            tags=f"link_{parent.id}_{child.id}"
        )

    def get_node_at(self, x, y):
        """指定座標にあるノードを返す（前面のノード優先）"""
        hit_node = None
        for node in self.canvas.mindmap.nodes.values():
            if node.bbox is None:
                continue
            x0, y0, x1, y1 = node.bbox
            if x0 <= x <= x1 and y0 <= y <= y1:
                hit_node = node  # 最後に描画されたノードが前面
        return hit_node
