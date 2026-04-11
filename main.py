import tkinter as tk
from tkinter import ttk
from gui_app import OptionPricerGUI


def main():
    root = tk.Tk()
    # 可以设置一个全局的 ttk 主题，让界面更好看一点
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    app = OptionPricerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()