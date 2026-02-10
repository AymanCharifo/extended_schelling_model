import tkinter as tk
from gui import MainApp


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Extended Schelling Model of Segregation")
    app = MainApp(root)
    root.mainloop()
