
import json
import copy
import numpy as np


class MindMap:
    def __init__(self):
        self.nodes = {}
        self.root = None
        self._next_id = 1
        self._undo_stack = []
        self._redo_stack = []

    def _next_node_id(self):
        while self._next_id in self.nodes:
            self._next_id += 1
        nid = self._next_id
        self._next_id += 1
        return nid

    def snapshot(self):
        """現在の状態をスナップショットとして保存（Undo用）"""
        state = self._serialize_state()
        self._undo_stack.append(state)
        self._redo_stack.clear()

    def undo(self):
        """直前の操作を元に戻す"""
        if not self._undo_stack:
            return False
        self._redo_stack.append(self._serialize_state())
        state = self._undo_stack.pop()
        self._restore_state(state)
        return True

    def redo(self):
        """元に戻した操作をやり直す"""
        if not self._redo_stack:
            return False
        self._undo_stack.append(self._serialize_state())
        state = self._redo_stack.pop()
        self._restore_state(state)
        return True

    def _serialize_state(self):
        data = {
            "nodes": [
                {
                    "id": node.id,
                    "text": node.text,
                    "position": node.position.tolist(),
                    "children": [child.id for child in node.children],
                    "collapsed": node.collapsed,
                }
                for node in self.nodes.values()
            ],
            "root_id": self.root.id if self.root else None,
        }
        return json.dumps(data)

    def _restore_state(self, state_json):
        data = json.loads(state_json)
        self.nodes = {}
        self.root = None
        for node_data in data["nodes"]:
            node = Node(
                id=node_data["id"],
                text=node_data["text"],
                position=np.array(node_data["position"], dtype=float),
            )
            node.collapsed = node_data.get("collapsed", False)
            self.nodes[node.id] = node
        for node_data in data["nodes"]:
            node = self.nodes[node_data["id"]]
            node.children = [self.nodes[cid] for cid in node_data["children"] if cid in self.nodes]
        if data["root_id"] is not None and data["root_id"] in self.nodes:
            self.root = self.nodes[data["root_id"]]

    def add_node(self, text, parent_id=None):
        node_id = self._next_node_id()
        new_node = Node(node_id, text)
        self.nodes[node_id] = new_node

        if parent_id and parent_id in self.nodes:
            parent_node = self.nodes[parent_id]
            parent_node.children.append(new_node)
            # 子ノードを親の右下に配置（後でレイアウトで調整）
            child_count = len(parent_node.children)
            offset_y = 60 * child_count - 30 * (child_count + 1) / 2
            new_node.position = np.array(
                parent_node.position + np.array([200.0, offset_y]), dtype=float
            )
        elif self.root is None:
            self.root = new_node
            new_node.position = np.array([400.0, 300.0], dtype=float)
        else:
            # 複数ルートノード：既存ノードから離れた位置に配置
            new_node.position = np.array([400.0, 300.0], dtype=float)

        return new_node

    def delete_node_and_descendants(self, node_id):
        """指定されたノードとその子孫ノードをすべて削除"""
        if node_id not in self.nodes:
            return
        node_to_delete = self.nodes[node_id]

        # 子孫ノードを再帰的に削除
        while node_to_delete.children:
            child_node = node_to_delete.children.pop(0)
            self.delete_node_and_descendants(child_node.id)

        # すべての親ノードからリンクを削除
        for parent_node in self.nodes.values():
            if node_to_delete in parent_node.children:
                parent_node.children.remove(node_to_delete)

        # ノード自体を削除
        del self.nodes[node_id]

        # ルートノードの場合はリセット
        if self.root == node_to_delete:
            self.root = None

    def get_parent(self, node_id):
        """指定ノードの親を返す"""
        for parent_node in self.nodes.values():
            for child in parent_node.children:
                if child.id == node_id:
                    return parent_node
        return None

    def get_node_depth(self, node):
        """ルートからの深さを計算"""
        depth = 0
        current = node
        while True:
            parent = self.get_parent(current.id)
            if parent is None:
                break
            depth += 1
            current = parent
        return depth

    def get_visible_nodes(self):
        """折りたたみを考慮して表示すべきノードを返す"""
        if not self.root:
            return list(self.nodes.values())

        visible = set()
        self._collect_visible(self.root, visible)

        # ルートに属さないノードも表示
        for node in self.nodes.values():
            parent = self.get_parent(node.id)
            if parent is None and node != self.root:
                visible.add(node)
                if not node.collapsed:
                    self._collect_visible(node, visible)

        return [n for n in self.nodes.values() if n in visible]

    def _collect_visible(self, node, visible):
        visible.add(node)
        if not node.collapsed:
            for child in node.children:
                self._collect_visible(child, visible)

    def get_visible_links(self):
        """表示すべきリンクを返す"""
        visible_nodes = set(n.id for n in self.get_visible_nodes())
        links = []
        for parent_node in self.nodes.values():
            if parent_node.id not in visible_nodes:
                continue
            if parent_node.collapsed:
                continue
            for child_node in parent_node.children:
                if child_node.id in visible_nodes:
                    links.append((parent_node, child_node))
        return links

    def apply_tree_layout(self, horizontal_gap=220, vertical_gap=70):
        """階層的ツリーレイアウトを適用（右方向に展開）"""
        if not self.root:
            return

        # 各ノードのサブツリーの高さを計算
        subtree_heights = {}
        self._calc_subtree_height(self.root, subtree_heights, vertical_gap)

        # ルートの位置を基点にレイアウト
        root_x, root_y = self.root.position
        self._layout_tree(self.root, root_x, root_y, subtree_heights, horizontal_gap, vertical_gap)

    def _calc_subtree_height(self, node, heights, gap):
        """サブツリーの高さを再帰的に計算"""
        if not node.children or node.collapsed:
            heights[node.id] = gap
            return gap

        total = 0
        for child in node.children:
            total += self._calc_subtree_height(child, heights, gap)
        heights[node.id] = total
        return total

    def _layout_tree(self, node, x, y, heights, h_gap, v_gap):
        """ツリーを再帰的にレイアウト"""
        node.position = np.array([x, y], dtype=float)

        if node.collapsed or not node.children:
            return

        total_height = heights[node.id]
        current_y = y - total_height / 2

        for child in node.children:
            child_height = heights[child.id]
            child_y = current_y + child_height / 2
            self._layout_tree(child, x + h_gap, child_y, heights, h_gap, v_gap)
            current_y += child_height

    def apply_force_layout(self, iterations=50, k=200.0, repulsion=500.0):
        """ノード間の力学モデルを適用してノード位置を更新"""
        for _ in range(iterations):
            forces = {node_id: np.array([0.0, 0.0]) for node_id in self.nodes}

            # 斥力の計算
            for node_a in self.nodes.values():
                for node_b in self.nodes.values():
                    if node_a != node_b:
                        delta = node_a.position - node_b.position
                        distance = np.linalg.norm(delta) + 1e-6
                        repulsion_force = (repulsion / distance**2) * (delta / distance)
                        forces[node_a.id] += repulsion_force

            # 引力の計算
            for parent_node in self.nodes.values():
                for child_node in parent_node.children:
                    delta = child_node.position - parent_node.position
                    distance = np.linalg.norm(delta) + 1e-6
                    attraction_force = -(distance**2 / k) * (delta / distance)
                    forces[child_node.id] += attraction_force
                    forces[parent_node.id] -= attraction_force

            for node_id, force in forces.items():
                self.nodes[node_id].position += force * 0.1

    def save_to_file(self, filename):
        """現在のマインドマップをJSON形式で保存"""
        data = {
            "nodes": [
                {
                    "id": node.id,
                    "text": node.text,
                    "position": node.position.tolist(),
                    "children": [child.id for child in node.children],
                    "collapsed": node.collapsed,
                }
                for node in self.nodes.values()
            ],
            "root_id": self.root.id if self.root else None,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_from_file(self, filename):
        """JSON形式のファイルからマインドマップを読み込み"""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.nodes = {}
        self.root = None
        self._undo_stack.clear()
        self._redo_stack.clear()

        for node_data in data["nodes"]:
            node = Node(
                id=node_data["id"],
                text=node_data["text"],
                position=np.array(node_data["position"], dtype=float),
            )
            node.collapsed = node_data.get("collapsed", False)
            self.nodes[node.id] = node

        for node_data in data["nodes"]:
            node = self.nodes[node_data["id"]]
            node.children = [self.nodes[child_id] for child_id in node_data["children"] if child_id in self.nodes]

        if data["root_id"] is not None and data["root_id"] in self.nodes:
            self.root = self.nodes[data["root_id"]]

        # _next_id を既存の最大IDより大きく設定
        if self.nodes:
            self._next_id = max(self.nodes.keys()) + 1

    def get_links(self):
        """親子ノード間のリンク情報を生成"""
        links = []
        for parent_node in self.nodes.values():
            for child_node in parent_node.children:
                links.append((parent_node, child_node))
        return links


class Node:
    def __init__(self, id, text, position=(0, 0)):
        self.id = id
        self.text = text
        self.position = np.array(position, dtype=float)
        self.children = []
        self.bbox = None
        self.collapsed = False  # 折りたたみ状態
