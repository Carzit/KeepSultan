import os
import json
from datetime import datetime
from typing import Tuple, Callable

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

from KeepSultan import KeepSultan

class ConfigManager:
    def __init__(self, manager):
        self.config_file:str = "config.json"
        self.configs:dict = {}
        self.manager:KeepSultan = manager
        self.initialize()
    
    def initialize(self):
        now = datetime.now()
        self.configs = {
            "template": "scr/template.png",
            "map": "scr/map3.png",
            "avatar": "",
            "username": "",
            "date": now.date().strftime("%Y/%m/%d"),
            "end_time": now.time().strftime("%H:%M"),
            "total_km": [3.02, 3.3],
            "sport_time": ["00:21:00", "00:23:00"],
            "total_time": ["00:34:00", "00:39:00"],
            "cumulative_climb": [90, 96],
            "average_cadence": [76, 81],
            "exercise_load": [48, 51]
        }
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                load_configs = json.load(f)
            self.configs["template"] = load_configs.get("template", "scr/template.png")
            self.configs["map"] = load_configs.get("map", "scr/map.png")
            self.configs["avatar"] = load_configs["avatar"]
            self.configs["username"] = load_configs["username"]
            self.configs["total_km"] = load_configs["total_km"]
            self.configs["sport_time"] = load_configs["sport_time"]
            self.configs["total_time"] = load_configs["total_time"]
            self.configs["cumulative_climb"] = load_configs["cumulative_climb"]
            self.configs["average_cadence"] = load_configs["average_cadence"]
            self.configs["exercise_load"] = load_configs["exercise_load"]

    def update(self):
        with open("config.json", "w", encoding="gbk") as f:
            json.dump(self.manager.configs, f, indent=4)

class KeepSultanGUI:
    def __init__(self, root):
        self.manager = KeepSultan()
        self.config_manager = ConfigManager(self.manager)

        self.root = root
        self.root.title("KeepSultan GUI")
        self.root.iconbitmap("scr/icon.ico")
        

        # Variables to hold file paths and configuration values
        self.template_path = tk.StringVar()
        self.map_path = tk.StringVar()

        self.avatar_path = tk.StringVar()
        self.params = {key: [tk.StringVar(), tk.StringVar()] if isinstance(value, list) else tk.StringVar()
                       for key, value in self.manager.configs.items()if (key != "avatar" and key != "template" and key != "map")}
        
        self.create_file_selector("Template:", self.template_path, "template", lambda: self.manager.load_template(self.template_path.get()), 0, "scr")
        self.create_file_selector("Map:", self.map_path, "map", lambda: True, 1, "scr")
        self.create_file_selector("Avatar:", self.avatar_path, "avatar", lambda: True, 2)

        # Configuration inputs
        config_frame = tk.Frame(root)
        config_frame.grid(row=4, column=0, columnspan=3, sticky="w")
        self.create_config_inputs(config_frame)

        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20)

        # Generate Button
        generate_button = tk.Button(button_frame, text="Generate", command=self.generate_image)
        generate_button.pack(side="left", padx=10)

        # Load Config Button
        load_config_button = tk.Button(button_frame, text="Save", command=self.save_image)
        load_config_button.pack(side="left", padx=10)

        foot_frame = tk.Frame(self.root)
        foot_frame.grid(row=11, column=0, columnspan=2, pady=20)
        footer = tk.Label(foot_frame, text="Developed by github.com/Carzit", font=("Arial", 8))
        footer.pack(side=tk.BOTTOM, pady=10)

    def create_file_selector(self, label_text:str, var:tk.Variable, config_key:str, command:Callable, row:int, initial_dir=None):
        tk.Label(self.root, text=label_text).grid(row=row, column=0, sticky="w")
        entry = tk.Entry(self.root, textvariable=var, width=40)
        entry.grid(row=row, column=1, columnspan=1)
        if self.config_manager.configs[config_key]:
            entry.insert(0, self.config_manager.configs[config_key])
        tk.Button(self.root, text="Browse", command=lambda: self.browse_file(var, command, initial_dir)).grid(row=row, column=2)

    def create_config_inputs(self, frame):
        for i, (key, value) in enumerate(self.params.items()):
            tk.Label(frame, text=key.capitalize()).grid(row=i, column=0, sticky="w")
            if isinstance(value, list):  # Handle ranges
                e1 = tk.Entry(frame, textvariable=value[0], width=7)
                e1.grid(row=i, column=1)
                e1.insert(0, str(self.config_manager.configs[key][0]))
                tk.Label(frame, text=" - ", width=2).grid(row=i, column=2)
                e2 = tk.Entry(frame, textvariable=value[1], width=7)
                e2.grid(row=i, column=3)
                e2.insert(0, str(self.config_manager.configs[key][1]))
            else:  # Handle single values
                e = tk.Entry(frame, textvariable=value, width=20)
                e.grid(row=i, column=1, columnspan=3)
                e.insert(0, str(self.config_manager.configs[key]))

    def browse_file(self, var, command, initial_dir=None):
        file_path = filedialog.askopenfilename(initialdir=initial_dir)
        if file_path:
            var.set(file_path)
            command()

    def show_preview(self, img:Image.Image):
        """
        打开一个新窗口显示生成的图像预览。
        :param image_path: 生成图像的路径
        """
        # 创建新窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Image Preview")
        preview_window.geometry("600x600")
        
        # 加载并调整图像大小以适配窗口
        img.thumbnail((600, 600))
        photo = ImageTk.PhotoImage(img)

        # 显示图像
        img_label = tk.Label(preview_window, image=photo)
        img_label.image = photo  # 保存引用以防止被垃圾回收
        img_label.pack(expand=True, fill="both")


    def generate_image(self):
        # Update manager's configs based on GUI inputs
        for key, value in self.params.items():
            if isinstance(value, list):
                self.manager.configs[key] = [value[0].get(), value[1].get()]
            else:
                self.manager.configs[key] = value.get()
        self.manager.load_template(self.template_path.get())
        self.manager.configs["map"] = self.map_path.get()
        self.manager.configs["avatar"] = self.avatar_path.get()
        
        self.manager.process()
        self.config_manager.update()
        self.show_preview(self.manager.image_editor.img.copy())

    def save_image(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if save_path:
            self.manager.save(save_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = KeepSultanGUI(root)
    root.mainloop()
