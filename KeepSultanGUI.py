"""
KeepSultan GUI (refactored with Preview/Save buttons)
-----------------------------------------------------
基于 KeepSultan_refactored 的图形界面版本。

特性：
1. GUI 修改配置后自动写入 config.json。
2. “Preview” 按钮弹出新窗口显示预览。
3. “Save” 按钮保存 PNG 文件。
"""

import tkinter as tk
from tkinter import filedialog
from typing import Dict

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
        self.root.title("KeepSultan GUI")
        try:
            self.root.iconbitmap("scr/icon.ico")
        except Exception:
            pass

        # --- Config ---
        self.config_manager = ConfigManager(config_path)
        self.cfg = self.config_manager.cfg
        self.app = KeepSultanApp(self.cfg)

        # 保存 StringVar 以便 trace
        self.vars: Dict[str, any] = {}

        # --- 文件选择器 ---
        self._create_file_selector("Template:", "template", self.cfg.template, 0, "scr")
        self._create_file_selector("Map:", "map", self.cfg.map, 1, "scr")
        self._create_file_selector("Avatar:", "avatar", self.cfg.avatar, 2)

        # --- 单值输入 ---
        self._create_entry("Username:", "username", self.cfg.username, 3)
        self._create_entry("Date:", "date", self.cfg.date, 4)
        self._create_entry("End Time:", "end_time", self.cfg.end_time, 5)

        # --- 区间输入 ---
        config_frame = tk.Frame(self.root)
        config_frame.grid(row=6, column=0, columnspan=3, sticky="w", pady=10)
        self._create_range_inputs(config_frame)

        # --- 按钮区 ---
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=20, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="Preview", command=self.preview_image).pack(side="left", padx=10)
        tk.Button(button_frame, text="Save", command=self.save_image).pack(side="left", padx=10)

        # 页脚
        footer = tk.Label(self.root, text="Developed by github.com/Carzit", font=("Arial", 8))
        footer.grid(row=30, column=0, columnspan=3, pady=5)

    # ------------------------------
    # 输入组件生成
    # ------------------------------

    def _create_file_selector(self, label: str, key: str, value: str, row: int, initial_dir: str | None = None) -> None:
        tk.Label(self.root, text=label).grid(row=row, column=0, sticky="w")
        var = tk.StringVar(value=value)
        entry = tk.Entry(self.root, textvariable=var, width=40)
        entry.grid(row=row, column=1, columnspan=1)
        tk.Button(
            self.root,
            text="Browse",
            command=lambda: self._browse_file(var, key, initial_dir),
        ).grid(row=row, column=2)

        var.trace_add("write", lambda *args: self._on_var_change(key, var))
        self.vars[key] = var

    def _create_entry(self, label: str, key: str, value: str, row: int) -> None:
        tk.Label(self.root, text=label).grid(row=row, column=0, sticky="w")
        var = tk.StringVar(value=value)
        tk.Entry(self.root, textvariable=var, width=30).grid(row=row, column=1, columnspan=2)

        var.trace_add("write", lambda *args: self._on_var_change(key, var))
        self.vars[key] = var

    def _create_range_inputs(self, frame: tk.Frame) -> None:
        """生成数值/时间区间输入框。"""
        ranges = {
            "Total KM: ": ("total_km", self.cfg.total_km.low, self.cfg.total_km.high),
            "Sport Time: ": ("sport_time", self.cfg.sport_time.start, self.cfg.sport_time.end),
            "Total Time: ": ("total_time", self.cfg.total_time.start, self.cfg.total_time.end),
            "Cumulative Climb: ": ("cumulative_climb", self.cfg.cumulative_climb.low, self.cfg.cumulative_climb.high),
            "Average Cadence: ": ("average_cadence", self.cfg.average_cadence.low, self.cfg.average_cadence.high),
            "Exercise Load: ": ("exercise_load", self.cfg.exercise_load.low, self.cfg.exercise_load.high),
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

    def _on_var_change(self, key: str, var: tk.StringVar) -> None:
        setattr(self.cfg, key, var.get())
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

    # ------------------------------
    # 图像生成/预览
    # ------------------------------

    def preview_image(self) -> None:
        """生成并在新窗口显示预览。"""
        try:
            img = self.app.process().copy()
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Preview")
            preview_window.geometry("600x600")

            img.thumbnail((600, 600))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(preview_window, image=photo)
            label.image = photo
            label.pack(expand=True, fill="both")
        except Exception as e:
            tk.messagebox.showerror("Error", f"预览失败: {e}")

    def save_image(self) -> None:
        """另存为 PNG 文件。"""
        if self.app.editor.img is None:
            tk.messagebox.showerror("Error", "请先生成预览图像。")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        if save_path:
            
            self.app.save(save_path)

def main():
    root = tk.Tk()
    app = KeepSultanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

