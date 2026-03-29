import tkinter as tk
from app.ui import AdaptiveContrastApp


def main():
    root = tk.Tk()
    AdaptiveContrastApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()