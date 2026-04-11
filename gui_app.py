import tkinter as tk
from tkinter import ttk, messagebox

class OptionPricerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FITE7405 Mini Option Pricer")
        self.root.geometry("600x700")
        
        # 定义不同期权对应的参数列表
        self.param_map = {
            "European Option": ["S(0)", "sigma", "r", "q", "T", "K", "Option Type"],
            "Implied Volatility": ["S(0)", "r", "q", "T", "K", "Premium", "Option Type"],
            "American Option": ["S(0)", "sigma", "r", "T", "K", "N (Steps)", "Option Type"],
            "Geometric Asian": ["S(0)", "sigma", "r", "T", "K", "n (Obs)", "Option Type"],
            "Arithmetic Asian": ["S(0)", "sigma", "r", "T", "K", "n (Obs)", "MC Paths", "CV Method", "Option Type"],
            "Geometric Basket": ["S1(0)", "S2(0)", "sigma1", "sigma2", "r", "T", "K", "rho", "Option Type"],
            "Arithmetic Basket": ["S1(0)", "S2(0)", "sigma1", "sigma2", "r", "T", "K", "rho", "MC Paths", "CV Method", "Option Type"],
            "KIKO Put Option": ["S(0)", "sigma", "r", "T", "K", "L (Lower)", "U (Upper)", "n (Obs)", "R (Rebate)"] # KIKO 固定为 Put
        }
        
        self.entries = {}  # 存储输入框的字典
        self.setup_ui()

    def setup_ui(self):
        # 1. 顶部：期权类型选择
        top_frame = ttk.LabelFrame(self.root, text="Select Option Type", padding=(10, 10))
        top_frame.pack(fill="x", padx=15, pady=10)
        
        self.option_type_var = tk.StringVar()
        self.option_combo = ttk.Combobox(top_frame, textvariable=self.option_type_var, state="readonly")
        self.option_combo['values'] = list(self.param_map.keys())
        self.option_combo.current(0)
        self.option_combo.pack(fill="x")
        self.option_combo.bind("<<ComboboxSelected>>", self.on_option_change)

        # 2. 中部：动态参数输入区
        self.input_frame = ttk.LabelFrame(self.root, text="Input Parameters", padding=(10, 10))
        self.input_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # 初始化加载默认期权的输入框
        self.on_option_change()

        # 3. 底部：计算按钮与结果展示区
        bottom_frame = ttk.Frame(self.root, padding=(10, 10))
        bottom_frame.pack(fill="x", padx=15, pady=10)
        
        self.calc_btn = ttk.Button(bottom_frame, text="Calculate Price", command=self.calculate)
        self.calc_btn.pack(pady=5)
        
        self.result_text = tk.Text(bottom_frame, height=8, state="disabled", bg="#f0f0f0")
        self.result_text.pack(fill="x", pady=5)

    def on_option_change(self, event=None):
        """当选择不同的期权类型时，动态重绘输入框"""
        # 清空当前所有输入控件
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        
        selected_option = self.option_type_var.get()
        params = self.param_map[selected_option]
        
        # 动态生成新的标签和输入框
        for i, param in enumerate(params):
            ttk.Label(self.input_frame, text=param + ":").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            # 针对特定参数使用下拉框而不是文本框
            if param == "Option Type":
                var = tk.StringVar(value="Call")
                cb = ttk.Combobox(self.input_frame, textvariable=var, values=["Call", "Put"], state="readonly", width=17)
                cb.grid(row=i, column=1, padx=10, pady=5)
                self.entries[param] = var
            elif param == "CV Method":
                var = tk.StringVar(value="None")
                cb = ttk.Combobox(self.input_frame, textvariable=var, values=["None", "Geometric Option"], state="readonly", width=17)
                cb.grid(row=i, column=1, padx=10, pady=5)
                self.entries[param] = var
            else:
                entry = ttk.Entry(self.input_frame, width=20)
                entry.grid(row=i, column=1, padx=10, pady=5)
                self.entries[param] = entry

    def calculate(self):
        """收集数据并准备传给后端算法"""
        selected_option = self.option_type_var.get()
        input_data = {}
        
        try:
            for param, entry in self.entries.items():
                val = entry.get()
                if not val:
                    raise ValueError(f"Parameter '{param}' cannot be empty.")
                # 区分字符串参数和数字参数
                if param in ["Option Type", "CV Method"]:
                    input_data[param] = val
                else:
                    input_data[param] = float(val)
            
            # --- 这里是调用后端算法的接口 ---
            # result = some_backend_router_function(selected_option, input_data)
            
            # 模拟后端返回的结果 (暂时用于测试 GUI)
            self.display_result(f"Selected Option: {selected_option}\nCollected Data:\n{input_data}\n\n[Backend Not Connected Yet]")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def display_result(self, text):
        """在底部文本框展示结果"""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")