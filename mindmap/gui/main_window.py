import tkinter as tk
from gui.canvas import Canvas
from gui.toolbar import Toolbar
from model.data_model import MindMap

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MindMap Editor")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")  # dark background

        self.mindmap = MindMap()
        self.canvas = Canvas(self.root, self.mindmap)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.toolbar = Toolbar(self.root, self.canvas)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()
