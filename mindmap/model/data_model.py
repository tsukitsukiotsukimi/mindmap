
import json
import numpy as np

class MindMap:
    def __init__(self):
        self.nodes = {}
        self.root = None

    def add_node(self, text, parent_id=None):
        node_id = len(self.nodes) + 1
        new_node = Node(node_id, text)
        self.nodes[node_id] = new_node

        if parent_id:
            parent_node = self.nodes[parent_id]
            parent_node.children.append(new_node)
            new_node.position = np.array(parent_node.position + np.array([50.0, 50.0]), dtype=float)
        elif self.root is None:
            self.root = new_node
            new_node.position = np.array([400.0, 300.0], dtype=float)

        return new_node
    
    def delete_node_and_descendants(self, node_id):
        """
        指定されたノードとその子孫ノードをすべて削除
        """
        if node_id in self.nodes:
            # 削除対象のノードを取得
            node_to_delete = self.nodes[node_id]
    
            # 子孫ノードを再帰的に削除
            while node_to_delete.children:
                child_node = node_to_delete.children.pop(0)  # 最初の子ノードを取得して削除
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
    
    def save_to_file(self, filename):
        """
        現在のマインドマップをJSON形式で保存
        """
        data = {
            "nodes": [
                {
                    "id": node.id,
                    "text": node.text,
                    "position": node.position.tolist(),
                    "children": [child.id for child in node.children],
                }
                for node in self.nodes.values()
            ],
            "root_id": self.root.id if self.root else None,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4) 
    
    def apply_force_layout(self, iterations=50, k=200.0, repulsion=500.0):
        """
        ノード間の力学モデルを適用してノード位置を更新
        - iterations: 計算回数
        - k: 引力のスケール（増やすと間隔が広がる）
        - repulsion: 斥力のスケール（増やすと間隔が広がる）
        """
        for _ in range(iterations):
            forces = {node_id: np.array([0.0, 0.0]) for node_id in self.nodes}
    
            # 斥力の計算 (ノード同士の分散)
            for node_a in self.nodes.values():
                for node_b in self.nodes.values():
                    if node_a != node_b:
                        delta = node_a.position - node_b.position
                        distance = np.linalg.norm(delta) + 1e-6  # 距離を計算（ゼロ除算防止）
                        repulsion_force = (repulsion / distance**2) * (delta / distance)
                        forces[node_a.id] += repulsion_force
    
            # 引力の計算 (親子ノード間の吸引)
            for parent_node in self.nodes.values():
                for child_node in parent_node.children:
                    delta = child_node.position - parent_node.position
                    distance = np.linalg.norm(delta) + 1e-6
                    attraction_force = -(distance**2 / k) * (delta / distance)
                    forces[child_node.id] += attraction_force
                    forces[parent_node.id] -= attraction_force
    
            # ノード位置の更新
            for node_id, force in forces.items():
                self.nodes[node_id].position += force * 0.1  # 移動スケールを調整
    
    def load_from_file(self, filename):
        """
        JSON形式のファイルからマインドマップを読み込み
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.nodes = {}
        self.root = None

        # ノードを作成
        for node_data in data["nodes"]:
            node = Node(
                id=node_data["id"],
                text=node_data["text"],
                position=np.array(node_data["position"], dtype=float),
            )
            self.nodes[node.id] = node

        # 子ノードのリンクを復元
        for node_data in data["nodes"]:
            node = self.nodes[node_data["id"]]
            node.children = [self.nodes[child_id] for child_id in node_data["children"]]

        # ルートノードを設定
        if data["root_id"] is not None:
            self.root = self.nodes[data["root_id"]]
    
    def get_links(self):
        """
        親子ノード間のリンク情報を生成
        Returns:
            list of tuples: (parent_node, child_node)
        """
        links = []
        for parent_node in self.nodes.values():
            for child_node in parent_node.children:
                links.append((parent_node, child_node))
        return links


class Node:
    def __init__(self, id, text, position=(0, 0)):
        self.id = id
        self.text = text
        self.position = np.array(position, dtype=float)  # numpy配列に変更
        self.children = []

