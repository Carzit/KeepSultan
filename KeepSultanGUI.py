#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: KeepSultan.py
About: 生成Keep跑步截图
OriginalAuthor: Carzit

Modified by LynxFrost  


基于 KeepSultan.py 的图形界面版本。

特性：
1. GUI 修改配置后自动写入 config.json。
2. “预览” 按钮弹出新窗口显示预览。
3. “保存” 按钮保存 PNG 文件。
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict
import threading
import time
import webbrowser
# 导入天气API函数
from KeepSultan import fetch_weather_data

from PIL import Image, ImageTk

from KeepSultan import (
    KeepConfig,
    NumberRange,
    TimeRange,
    KeepSultanApp,
)


class ConfigManager:
    """负责管理 KeepConfig 与 JSON 文件。"""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_path = config_path
        self.cfg: KeepConfig = KeepConfig.from_json(config_path)

    def save(self) -> None:
        """写回 JSON。"""
        self.cfg.to_json(self.config_path)


class KeepSultanGUI:
    def __init__(self, root: tk.Tk, config_path: str = "config.json") -> None:
        self.root = root
        self.root.title("KeepSultan 图形界面")
        try:
            self.root.iconbitmap("src/icon.ico")
        except Exception:
            pass
        
        # 设置固定窗口大小
        self.root.geometry("450x800")
        # 禁止调整窗口大小
        self.root.resizable(False, False)
        
        # 配置网格布局的权重，使界面可以缩放
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)
        
        # 添加滚动条
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")
        # 隐藏滚动条但保留滚动功能
        # scrollbar.grid(row=0, column=3, sticky="ns")
        
        # 添加鼠标滚轮事件支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 绑定鼠标滚轮事件
        canvas.bind("<MouseWheel>", _on_mousewheel)
        # 确保canvas获得焦点时能响应键盘箭头键
        canvas.bind("<FocusIn>", lambda e: canvas.focus_set())
        
        # 配置画布列权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Config ---
        self.config_manager = ConfigManager(config_path)
        self.cfg = self.config_manager.cfg
        self.app = KeepSultanApp(self.cfg)

        # 保存 StringVar 以便 trace
        self.vars: Dict[str, any] = {}
        
        # 将之前定义的scrollable_frame存储为实例变量
        self.scrollable_frame = scrollable_frame

        # --- 文件选择器 ---
        self._create_file_selector("模板图片:", "template", self.cfg.template, 0, "src", parent=self.scrollable_frame)
        self._create_file_selector("地图图片:", "map", self.cfg.map, 1, "src", parent=self.scrollable_frame)
        self._create_file_selector("头像图片:", "avatar", self.cfg.avatar, 2, parent=self.scrollable_frame)

        # --- 单值输入 ---
        self._create_entry("用户名:", "username", self.cfg.username, 3, parent=self.scrollable_frame)
        self._create_entry("日期:", "date", self.cfg.date, 4, parent=self.scrollable_frame)
        self._create_entry("结束时间:", "end_time", self.cfg.end_time, 5, parent=self.scrollable_frame)
        self._create_entry("地点:", "location", self.cfg.location, 6, parent=self.scrollable_frame)
        self._create_entry("天气:", "weather", self.cfg.weather, 7, parent=self.scrollable_frame)
        self._create_entry("温度:", "temperature", self.cfg.temperature, 8, parent=self.scrollable_frame)

        # --- 区间输入 ---
        config_frame = tk.Frame(self.scrollable_frame)
        config_frame.grid(row=9, column=0, columnspan=3, sticky="w", pady=10)
        self._create_range_inputs(config_frame)
        
        # --- 轨迹生成配置 ---
        track_frame = tk.LabelFrame(self.scrollable_frame, text="轨迹生成配置")
        track_frame.grid(row=10, column=0, columnspan=3, sticky="w", pady=10, padx=10)
        
        # 地图文件选择器
        self._create_file_selector("地图背景:", "map_bg_path", self.cfg.map_bg_path, 0, "src", parent=track_frame)
        self._create_file_selector("路径掩码:", "map_mask_path", self.cfg.map_mask_path, 1, "src", parent=track_frame)
        
        # 轨迹参数输入
        track_params = {
            "轨迹颜色 B:": ("track_color", 0, self.cfg.track_color[0]),
            "轨迹颜色 G:": ("track_color", 1, self.cfg.track_color[1]),
            "轨迹颜色 R:": ("track_color", 2, self.cfg.track_color[2]),
            "轨迹厚度:": ("track_thickness", None, self.cfg.track_thickness),
            "采样率:": ("track_sample_rate", None, self.cfg.track_sample_rate),
            "最大步数:": ("track_max_steps", None, self.cfg.track_max_steps),
            "完成度阈值:": ("track_completion_threshold", None, self.cfg.track_completion_threshold),
            "目标长度:": ("track_target_length", None, self.cfg.track_target_length),
        }
        
        for i, (label, (key, idx, value)) in enumerate(track_params.items(), start=2):
            tk.Label(track_frame, text=label).grid(row=i, column=0, sticky="w")
            var = tk.StringVar(value=str(value))
            entry = tk.Entry(track_frame, textvariable=var, width=10)
            entry.grid(row=i, column=1)
            
            if idx is not None:
                # 处理颜色元组
                var.trace_add("write", lambda *args, k=key, v=var, idx=idx: self._on_track_color_change(k, v, idx))
            else:
                # 处理普通数值
                var.trace_add("write", lambda *args, k=key, v=var: self._on_track_param_change(k, v))
            
            self.vars[f"{key}_{idx}" if idx is not None else key] = var

        # --- 按钮区 ---
        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.grid(row=20, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="预览", command=self.preview_image, width=15).pack(side="left", padx=10)
        tk.Button(button_frame, text="保存", command=self.save_image, width=15).pack(side="left", padx=10)

        # 页脚点击事件处理函数
        def open_github_carzit(event):
            webbrowser.open("https://github.com/Carzit")
        
        def open_github_itrf(event):
            webbrowser.open("https://github.com/itrfcn")
        
        # 页脚
        footer = tk.Label(self.scrollable_frame, text="由 github.com/Carzit 开发", font=("Arial", 8), 
                         fg="blue", cursor="hand2")  # 蓝色文字，手型光标
        footer.grid(row=30, column=0, columnspan=3, pady=5, sticky="s")
        footer.bind("<Button-1>", open_github_carzit)  # 绑定左键点击事件
        
        # 添加额外信息
        extra_info = tk.Label(self.scrollable_frame, text="由 github.com/itrfcn 修改", font=("Arial", 8), 
                            fg="blue", cursor="hand2")  # 蓝色文字，手型光标
        extra_info.grid(row=31, column=0, columnspan=3, pady=5, sticky="s")
        extra_info.bind("<Button-1>", open_github_itrf)  # 绑定左键点击事件

    # ------------------------------
    # 输入组件生成
    # ------------------------------

    def _create_file_selector(self, label: str, key: str, value: str, row: int, initial_dir: str | None = None, parent: tk.Frame = None) -> None:
        parent = parent or self.root
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        var = tk.StringVar(value=value)
        entry = tk.Entry(parent, textvariable=var, width=40)
        entry.grid(row=row, column=1, columnspan=1)
        tk.Button(
            parent,
            text="浏览",
            command=lambda: self._browse_file(var, key, initial_dir),
        ).grid(row=row, column=2)

        var.trace_add("write", lambda *args: self._on_var_change(key, var))
        self.vars[key] = var

    def _create_entry(self, label: str, key: str, value: str, row: int, parent: tk.Frame = None) -> None:
        parent = parent or self.root
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        var = tk.StringVar(value=value)
        tk.Entry(parent, textvariable=var, width=30).grid(row=row, column=1, columnspan=2)

        var.trace_add("write", lambda *args: self._on_var_change(key, var))
        self.vars[key] = var

    def _create_range_inputs(self, frame: tk.Frame) -> None:
        """生成数值/时间区间输入框。"""
        ranges = {
            "总公里数: ": ("total_km", self.cfg.total_km.low, self.cfg.total_km.high),
            "运动时长: ": ("sport_time", self.cfg.sport_time.start, self.cfg.sport_time.end),
            "总时长: ": ("total_time", self.cfg.total_time.start, self.cfg.total_time.end),
            "累计爬升: ": ("cumulative_climb", self.cfg.cumulative_climb.low, self.cfg.cumulative_climb.high),
            "平均步频: ": ("average_cadence", self.cfg.average_cadence.low, self.cfg.average_cadence.high),
            "运动负荷: ": ("exercise_load", self.cfg.exercise_load.low, self.cfg.exercise_load.high),
        }
        for i, (label, (key, v1, v2)) in enumerate(ranges.items()):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
            v1_var = tk.StringVar(value=str(v1))
            v2_var = tk.StringVar(value=str(v2))
            tk.Entry(frame, textvariable=v1_var, width=10).grid(row=i, column=1)
            tk.Entry(frame, textvariable=v2_var, width=10).grid(row=i, column=2)

            v1_var.trace_add("write", lambda *args, k=key, v1v=v1_var, v2v=v2_var: self._on_range_change(k, v1v, v2v))
            v2_var.trace_add("write", lambda *args, k=key, v1v=v1_var, v2v=v2_var: self._on_range_change(k, v1v, v2v))

            self.vars[key] = (v1_var, v2_var)

    # ------------------------------
    # 事件响应
    # ------------------------------

    def _browse_file(self, var: tk.StringVar, key: str, initial_dir: str | None = None) -> None:
        file_path = filedialog.askopenfilename(initialdir=initial_dir)
        if file_path:
            var.set(file_path)  # trace 会触发更新

    def _update_weather_and_temperature(self, location: str):
        """
        在后台线程中更新天气和温度信息，避免阻塞GUI主线程
        """
        try:
            # 调用天气API获取数据
            weather, temperature = fetch_weather_data(location)
            
            # 在主线程中更新GUI
            self.root.after(0, lambda: self._apply_weather_update(weather, temperature))
        except Exception as e:
            # 错误处理
            self.root.after(0, lambda: self._show_weather_error(e))
    
    def _apply_weather_update(self, weather: str, temperature: str):
        """
        在主线程中应用天气和温度更新
        """
        self.cfg.weather = weather
        self.cfg.temperature = temperature
        # 更新对应的输入框
        if "weather" in self.vars:
            self.vars["weather"].set(weather)
        if "temperature" in self.vars:
            self.vars["temperature"].set(temperature)
        # 保存配置
        self.config_manager.save()
    
    def _show_weather_error(self, error: Exception):
        """
        显示天气更新错误信息
        """
        messagebox.showwarning("天气更新失败", f"无法获取天气数据: {error}")
    
    def _on_var_change(self, key: str, var: tk.StringVar) -> None:
        setattr(self.cfg, key, var.get())
        
        # 如果修改的是地点，自动获取新地区的天气和温度（在后台线程中）
        if key == "location":
            # 启动新线程处理天气API调用，避免阻塞GUI主线程
            threading.Thread(
                target=self._update_weather_and_temperature,
                args=(var.get(),),
                daemon=True  # 设置为守护线程，程序退出时自动结束
            ).start()
        else:
            # 其他配置修改直接保存
            self.config_manager.save()

    def _on_range_change(self, key: str, v1_var: tk.StringVar, v2_var: tk.StringVar) -> None:
        v1, v2 = v1_var.get(), v2_var.get()
        try:
            if key in {"sport_time", "total_time"}:
                setattr(self.cfg, key, TimeRange(v1, v2))
            if key in {"total_km"}:
                setattr(self.cfg, key, NumberRange(float(v1), float(v2), 2))
            else:
                setattr(self.cfg, key, NumberRange(float(v1), float(v2)))
            self.config_manager.save()
        except Exception:
            # 输入非法时忽略，避免闪退
            pass
    
    def _on_track_color_change(self, key: str, var: tk.StringVar, idx: int) -> None:
        try:
            # 获取当前颜色元组
            current_color = list(getattr(self.cfg, key))
            # 更新对应通道的值
            current_color[idx] = int(var.get())
            # 确保颜色值在有效范围内
            current_color[idx] = max(0, min(255, current_color[idx]))
            # 设置新的颜色元组
            setattr(self.cfg, key, tuple(current_color))
            self.config_manager.save()
        except Exception:
            # 输入非法时忽略，避免闪退
            pass
    
    def _on_track_param_change(self, key: str, var: tk.StringVar) -> None:
        try:
            value = var.get()
            # 根据参数类型转换值
            if key in {"track_completion_threshold"}:
                # 浮点型参数
                setattr(self.cfg, key, float(value))
            else:
                # 整数型参数
                setattr(self.cfg, key, int(value))
            self.config_manager.save()
        except Exception:
            # 输入非法时忽略，避免闪退
            pass

    # ------------------------------
    # 图像生成/预览
    # ------------------------------

    def preview_image(self) -> None:
        """生成并在新窗口显示预览。"""
        try:
            img = self.app.process().copy()
            preview_window = tk.Toplevel(self.root)
            preview_window.title("预览窗口")
            preview_window.geometry("600x600")

            img.thumbnail((600, 600))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(preview_window, image=photo)
            label.image = photo
            label.pack(expand=True, fill="both")
        except Exception as e:
            tk.messagebox.showerror("错误", f"预览失败: {e}")

    def save_image(self) -> None:
        """另存为 PNG 文件。"""
        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
            )
            if save_path:
                # 如果没有预览，先生成图片
                if self.app.editor.img is None:
                    self.app.process()
                self.app.save(save_path)
                messagebox.showinfo("保存成功", f"图片已保存到: {save_path}")
        except Exception as e:
            messagebox.showerror("保存失败", f"图片保存失败: {e}")

def main():
    root = tk.Tk()
    app = KeepSultanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

