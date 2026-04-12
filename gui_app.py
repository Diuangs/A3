import tkinter as tk
from tkinter import ttk, messagebox

from analytic_pricer import (
    calc_european_bs,
    calc_implied_vol,
    calc_geometric_asian_closed_form,
    calc_geometric_basket_closed_form,
)
from mc_pricer import (
    calc_arithmetic_asian_mc,
    calc_arithmetic_basket_mc,
)
from advanced_pricer import (
    calc_american_binomial,
    calc_kiko_qmc,
)

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
        """收集数据并调用对应的后端算法"""
        selected_option = self.option_type_var.get()
        input_data = {}
        
        try:
            # 1. 数据收集与基础类型转换
            for param, entry in self.entries.items():
                val = entry.get()
                if not val:
                    raise ValueError(f"Parameter '{param}' cannot be empty.")
                
                if param in ["Option Type", "CV Method"]:
                    input_data[param] = val
                else:
                    input_data[param] = float(val)
            
            # 2. 准备输出文本
            result_text_output = f"--- {selected_option} Results ---\n\n"
            
            # 3. 后端路由：根据选择的期权类型调用不同的算法
            if selected_option == "Geometric Basket":
                price = calc_geometric_basket_closed_form(
                    S1=input_data["S1(0)"], S2=input_data["S2(0)"],
                    sigma1=input_data["sigma1"], sigma2=input_data["sigma2"],
                    r=input_data["r"], T=input_data["T"], K=input_data["K"],
                    rho=input_data["rho"], option_type=input_data["Option Type"]
                )
                result_text_output += f"Price: {price:.6f}\n"

            elif selected_option == "Arithmetic Basket":
                m_paths = int(input_data["MC Paths"])
                use_cv = True if input_data["CV Method"] == "Geometric Option" else False

                res = calc_arithmetic_basket_mc(
                    S1=input_data["S1(0)"], S2=input_data["S2(0)"],
                    sigma1=input_data["sigma1"], sigma2=input_data["sigma2"],
                    r=input_data["r"], T=input_data["T"], K=input_data["K"],
                    rho=input_data["rho"], option_type=input_data["Option Type"],
                    m_paths=m_paths, use_cv=use_cv
                )

                result_text_output += f"Estimated Price: {res['Price']:.6f}\n"
                result_text_output += f"95% Confidence Interval: [{res['CI_Lower']:.6f}, {res['CI_Upper']:.6f}]\n"
                result_text_output += f"Standard Error: {res['StdError']:.6f}\n"

            elif selected_option == "European Option":
                price = calc_european_bs(
                    S0=input_data["S(0)"], sigma=input_data["sigma"],
                    r=input_data["r"], q=input_data["q"],
                    T=input_data["T"], K=input_data["K"],
                    option_type=input_data["Option Type"]
                )
                result_text_output += f"Price: {price:.6f}\n"

            elif selected_option == "Implied Volatility":
                iv = calc_implied_vol(
                    S0=input_data["S(0)"], r=input_data["r"], q=input_data["q"],
                    T=input_data["T"], K=input_data["K"],
                    premium=input_data["Premium"],
                    option_type=input_data["Option Type"]
                )
                result_text_output += f"Implied Volatility: {iv:.4f}\n"

            elif selected_option == "American Option":
                price = calc_american_binomial(
                    S0=input_data["S(0)"], sigma=input_data["sigma"],
                    r=input_data["r"], T=input_data["T"], K=input_data["K"],
                    n_steps=int(input_data["N (Steps)"]),
                    option_type=input_data["Option Type"]
                )
                result_text_output += f"Price: {price:.6f}\n"

            elif selected_option == "Geometric Asian":
                price = calc_geometric_asian_closed_form(
                    S0=input_data["S(0)"], sigma=input_data["sigma"],
                    r=input_data["r"], T=input_data["T"], K=input_data["K"],
                    n_obs=int(input_data["n (Obs)"]),
                    option_type=input_data["Option Type"]
                )
                result_text_output += f"Price: {price:.6f}\n"

            elif selected_option == "Arithmetic Asian":
                m_paths = int(input_data["MC Paths"])
                use_cv = True if input_data["CV Method"] == "Geometric Option" else False
                res = calc_arithmetic_asian_mc(
                    S0=input_data["S(0)"], sigma=input_data["sigma"],
                    r=input_data["r"], T=input_data["T"], K=input_data["K"],
                    n_obs=int(input_data["n (Obs)"]),
                    option_type=input_data["Option Type"],
                    m_paths=m_paths, use_cv=use_cv
                )
                result_text_output += f"Estimated Price: {res['Price']:.6f}\n"
                result_text_output += f"95% Confidence Interval: [{res['CI_Lower']:.6f}, {res['CI_Upper']:.6f}]\n"
                result_text_output += f"Standard Error: {res['StdError']:.6f}\n"

            elif selected_option == "KIKO Put Option":
                price, delta = calc_kiko_qmc(
                    S0=input_data["S(0)"], sigma=input_data["sigma"],
                    r=input_data["r"], T=input_data["T"], K=input_data["K"],
                    L=input_data["L (Lower)"], U=input_data["U (Upper)"],
                    n_obs=int(input_data["n (Obs)"]),
                    rebate=input_data["R (Rebate)"]
                )
                result_text_output += f"Price: {price:.6f}\n"
                result_text_output += f"Delta: {delta:.6f}\n"

            else:
                result_text_output += "[Backend for this option is not connected yet.]\n\n"
                result_text_output += f"Collected Data: {input_data}"

            # 4. 在界面上展示结果
            self.display_result(result_text_output)
            
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid input: {str(ve)}")
        except Exception as e:
            # 捕捉后端计算中可能出现的数学错误（比如除以零等）
            messagebox.showerror("Calculation Error", f"An error occurred during calculation:\n{str(e)}")

    def display_result(self, text):
        """在底部文本框展示结果"""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state="disabled")