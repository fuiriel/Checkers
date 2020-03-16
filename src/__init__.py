import tkinter as tk
from src.window import CheckersApp

if __name__ == '__main__':
    root = tk.Tk()
    app = CheckersApp(root)
    app.mainloop()


