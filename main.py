# main.py
import tkinter as tk
from game_controller import GameController

if __name__ == "__main__":
    root = tk.Tk()
    root.title("タイル配置ゲーム")
    app = GameController(root)
    root.mainloop()
