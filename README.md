# MindMap Editor

**MindMap Editor** is a windows application that allows users to create, edit, save, and visualize mind maps intuitively. It leverages a tree-like structure to organize relationships between nodes and supports flexible editing operations. You can upload saved mindmap file to LLM model to disscuss.

---

## 📋 Features
- **Add Nodes**:
  - Add main nodes or sub-nodes with ease.
- **Delete Nodes**:
  - Delete a selected node and all its descendant nodes in one action.
- **Real-Time Editing**:
  - Double-click on a node to edit its text instantly.
- **Drag & Drop**:
  - Move nodes by dragging them to adjust their position.
- **Zoom Functionality**:
  - Zoom in and out with the mouse wheel for better navigation.
- **Save and Load**:
  - Save mind maps in JSON format and load them later.
- **Auto Layout**:
  - Automatically adjust node positions using a force-directed layout algorithm.
- **Context Menu**:
  - Right-click a node to quickly add or delete child nodes.
- **Selection Highlight**:
  - Selected nodes are outlined in yellow for better visibility.

---

## 🛠️ Installation

### Install Python:
Requires Python 3.8 or later.

### Clone the Repository:
```bash
git clone https://github.com/tsukitsukiotsukimi/mindmap.git
cd mindmap
``` 

### Run
```bash
python3 -m pip install -r requirements.txt  # if requirements exist
python3 mindmap/main.py
```
