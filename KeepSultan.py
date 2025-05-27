__all__ = ["KeepSultan"]

import random
import argparse
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import json

from numbers import Number
from typing import List, Tuple, Dict, Literal, Union, Optional, Callable, Any

def calculate_start_time(end_time_str, duration_str):
    """
    计算开始时间。
    
    :param end_time_str: 结束时间的字符串形式，格式为 "HH:mm:ss"
    :param duration_str: 持续时间的字符串形式，格式为 "HH:mm:ss"
    :return: 开始时间的字符串形式，格式为 "HH:mm:ss"
    """
    # 解析结束时间字符串为 datetime 对象
    end_time = datetime.strptime(end_time_str, "%H:%M")
    
    # 解析持续时间字符串为 timedelta 对象
    hours, minutes, seconds = map(int, duration_str.split(':'))
    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    
    # 计算开始时间
    start_time = end_time - duration
    
    # 将开始时间格式化为字符串
    start_time_str = start_time.strftime("%H:%M:%S")
    
    return start_time_str

def random_time_in_range(start_time_str, end_time_str):
    """
    在给定的时间范围内随机选择一个时间。
    
    :param start_time_str: 开始时间的字符串形式，格式为 "HH:mm:ss"
    :param end_time_str: 结束时间的字符串形式，格式为 "HH:mm:ss"
    :return: 随机时间的字符串形式，格式为 "HH:mm:ss"
    """
    # 解析时间字符串为 datetime 对象
    start_time = datetime.strptime(start_time_str, "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")
    
    # 计算时间差，以秒为单位
    time_diff_seconds = (end_time - start_time).total_seconds()
    
    # 生成一个随机的秒数
    random_seconds = random.uniform(0, time_diff_seconds)
    
    # 计算随机时间
    random_time = start_time + timedelta(seconds=random_seconds)
    
    # 将随机时间格式化为字符串
    random_time_str = random_time.strftime("%H:%M:%S")
    
    return random_time_str

def random_number_in_range(lower_bound, upper_bound, precision:int = 0):
    """
    在给定的范围内生成一个随机数，并保留两位小数。
    
    :param lower_bound: 范围的下限
    :param upper_bound: 范围的上限
    :return: 保留两位小数的随机数
    """
    # 生成随机数
    random_number = random.uniform(lower_bound, upper_bound)
    
    # 保留两位小数
    rounded_number = round(random_number, precision)
    if precision == 0:
        rounded_number = int(rounded_number)
    
    return rounded_number

def parse_time(time_str):
    """
    将时间字符串解析为秒数。
    
    :param time_str: 时间字符串，格式为 "HH:mm:ss"
    :return: 时间的秒数表示
    """
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    return total_seconds

def format_time(total_seconds):
    """
    将秒数格式化为 "mm:ss" 字符串。
    
    :param total_seconds: 时间的秒数表示
    :return: 格式化的时间字符串，格式为 "mm:ss"
    """
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes):02d}\'{int(seconds):02d}\'\'"

def calculate_pace(distance_km, time_str):
    """
    计算平均配速。
    
    :param distance_km: 总距离，单位为公里
    :param time_str: 总时间，格式为 "HH:mm:ss"
    :return: 平均配速，格式为 "mm:ss"
    """
    total_seconds = parse_time(time_str)
    pace_seconds_per_km = total_seconds / distance_km
    return format_time(pace_seconds_per_km)

def calculate_cost(time_str):
    """
    计算平均配速。
    
    :param distance_km: 总距离，单位为公里
    :param time_str: 总时间，格式为 "HH:mm:ss"
    :return: 平均配速，格式为 "mm:ss"
    """
    total_seconds = parse_time(time_str)
    cost = round(700 * (total_seconds/3600))
    return cost

class ImageEditor:
    def __init__(self):
        """
        Initialize the ImageEditor with an empty image attribute.
        """
        self.img:Image.Image

    def load_image(self, img:Image.Image):
        """
        Load an image into the editor.

        Args:
            img (Image.Image): The image to load.
        """
        self.img = img

    def add_image(self, 
                  img:Image.Image, 
                  position:Tuple[int, int]):
        """
        Add an image to the current image at the specified position.

        Args:
            img (Image.Image): The image to add.
            position (Tuple[int, int]): The position to place the image.
        """
        self.img.paste(img, position, img)

    def add_text(self, 
                 text:str, 
                 position:Tuple[Number, Number], 
                 font_path:str, 
                 font_size:int, 
                 color:Tuple[int, int, int]):
        """
        Add text to the current image at the specified position.

        Args:
            text (str): The text to add.
            position (Tuple[int, int]): The position to place the text.
            font_path (str): The path to the font file.
            font_size (int): The size of the font.
            color (Tuple[int, int, int]): The color of the text.
        """
        draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, fill=color, font=font)

    def save(self, save_path:str):
        """
        Save the current image to the specified path.

        Args:
            save_path (str): The path to save the image.
        """
        self.img.save(save_path)

class KeepSultan:
    def __init__(self):
        self.image_editor = ImageEditor()
        self.configs = {
            "template": "scr/template.png", 
            "map": "scr/map.png",
            "avatar": "",
            "username": "",

            "date": "2024/11/17",
            "end_time": "22:54",

            "total_km": [3.02, 3.3],
            "sport_time": ["00:21:00", "00:23:00"],
            "total_time": ["00:34:00", "00:39:00"],
            "cumulative_climb": [90, 96],
            "average_cadence": [76, 81],
            "exercise_load": [48, 51],
        }

    def load_configs(self, config_path:str):
        with open(config_path, "r") as f:
            self.configs = json.load(f)

    def load_args(self, args:argparse.Namespace):
        if args.template:
            k.configs["template"] = args.template
        if args.map:
            k.configs["map"] = args.map
        if args.avatar:
            k.configs["avatar"] = args.avatar
        if args.username:
            k.configs["username"] = args.username
        if args.date:
            k.configs["date"] = args.date
        else:
            k.configs["date"] = datetime.now().strftime("%Y/%m/%d")
        if args.end_time:
            k.configs["end_time"] = args.end_time
        else:
            k.configs["end_time"] = datetime.now().strftime("%H:%M")
        if args.total_km:
            k.configs["total_km"] = args.total_km
        if args.sport_time:
            k.configs["sport_time"] = args.sport_time
        if args.total_time:
            k.configs["total_time"] = args.total_time
        if args.cumulative_climb:
            k.configs["cumulative_climb"] = args.cumulative_climb
        if args.average_cadence:
            k.configs["average_cadence"] = args.average_cadence
        if args.exercise_load:
            k.configs["exercise_load"] = args.exercise_load
    
    def load_template(self, image_path:str):
        img = Image.open(image_path)
        self.image_editor.load_image(img)

    def save(self, save_path:str):
        self.image_editor.save(save_path)

    def create_circular_avatar(self, avatar_path, avatar_size):
        """
        创建一个圆形头像。
        
        :param image_path: 原始图片的路径
        :param avatar_size: 返回的圆形头像的尺寸 (width, height)
        :return: 圆形头像的Image对象
        """
        with Image.open(avatar_path).convert('RGBA') as img:
            # 如果图片不是正方形，则需要先裁剪成正方形
            width, height = img.size
            if width != height:
                min_side = min(width, height)
                left = (width - min_side) // 2
                top = (height - min_side) // 2
                right = (width + min_side) // 2
                bottom = (height + min_side) // 2
                img = img.crop((left, top, right, bottom))

            img = img.resize(avatar_size)

            mask = Image.new('L', avatar_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + avatar_size, fill=255)
            
            result = Image.composite(img, Image.new('RGBA', avatar_size, (0, 0, 0, 0)), mask)     
            
            return result
        
    def create_map(self, map_path, map_size):
        with Image.open(map_path).convert('RGBA') as img:
            img = img.resize(map_size)
            return img
    
    def process(self):
        self.load_template(self.configs["template"])
        
        avatar_img = self.create_circular_avatar(self.configs["avatar"], (100, 100))
        map_img = self.create_map(self.configs["map"], (1000, 800))

        end_time = self.configs["end_time"]
        total_time = random_time_in_range(str(self.configs["total_time"][0]), str(self.configs["total_time"][1]))
        sport_time = min(random_time_in_range(str(self.configs["sport_time"][0]), str(self.configs["sport_time"][1])), total_time)
        start_time = calculate_start_time(end_time, total_time)
        total_km = random_number_in_range(float(self.configs["total_km"][0]), float(self.configs["total_km"][1]), precision=2) + 0.01  # 保留两位小数，增加0.01以避免精度问题

        pace = calculate_pace(total_km, sport_time)
        cost = calculate_cost(total_time)

        cumulative_climb = random_number_in_range(float(self.configs["cumulative_climb"][0]), float(self.configs["cumulative_climb"][1]), precision=0)
        average_cadence = random_number_in_range(float(self.configs["average_cadence"][0]), float(self.configs["average_cadence"][1]), precision=0)
        exercise_load = random_number_in_range(float(self.configs["exercise_load"][0]), float(self.configs["exercise_load"][1]), precision=0)

        self.image_editor.add_text(end_time, (50, 25), "fonts/SourceHanSansCN-Regular.otf", 40, (0, 0, 0)) #系统时间

        self.image_editor.add_image(avatar_img, (40, 250)) #头像

        self.image_editor.add_text(self.configs["username"], (160, 240), "fonts/SourceHanSansCN-Regular.otf", 40, (0, 0, 0)) #用户名
        self.image_editor.add_text(f'{self.configs["date"]} {start_time[:-3]} - {end_time}', (160, 290), "fonts/SourceHanSansCN-Regular.otf", 36, (155, 155, 155)) #日期

        self.image_editor.add_text(str(total_km), (50, 485), "fonts/QanelasBlack.otf", 180, (0, 0, 0)) #公里数
        self.image_editor.add_text('公里', (418, 610), "fonts/SourceHanSansCN-Regular.otf", 43, (0, 0, 0))

        self.image_editor.add_image(map_img, (40, 720)) #地图

        self.image_editor.add_text(str(sport_time), (55, 1750), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) #运动时长
        self.image_editor.add_text(str(pace), (445, 1750), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) #平均配速
        self.image_editor.add_text(str(cost), (800, 1750), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) #运动消耗

        self.image_editor.add_text(str(total_time), (55, 1910), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) #总时长
        self.image_editor.add_text(str(cumulative_climb), (445, 1910), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) #累计爬升
        # 根据 KeepGeneration-Web Commit #4193165
        if(average_cadence > 100):
            self.image_editor.add_text(str(average_cadence), (805, 1910), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) 
        else:
            self.image_editor.add_text(str(average_cadence), (835, 1910), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0))
        self.image_editor.add_text(str(exercise_load), (55, 2070), "fonts/QanelasSemiBold.otf", 65, (0, 0, 0)) #运动负荷

def parse_args():
    parser = argparse.ArgumentParser(description="Sultan of Keep")
    parser.add_argument("--config_path", type=str, default="config.json", help="Path of config file. Default `config.json`")
    parser.add_argument("--template", type=str, default="scr/template.png", help="Path of template image. Default `scr/template.png`")
    parser.add_argument("--map", type=str, default="scr/map.png", help="Path of map image. Default `scr/map.png`")
    parser.add_argument("--save_path", type=str, default="save.png", help="Path of saved image. Default `save.png`")

    parser.add_argument("--avatar", type=str, default=None, help="Path of avatar image. Default None")
    parser.add_argument("--username", type=str, default=None, help="Username. Default None")
    parser.add_argument("--date", type=str, default=None, help="Date. Default None")
    parser.add_argument("--end_time", type=str, default=None, help="End time, in format of &H:&M. Default None")
    parser.add_argument("--total_km", type=float, default=None, help="Total running distance (km). Default None")
    parser.add_argument("--sport_time", type=str, default=None, help="Sport time, in format of &H:&M:&S. Default None")
    parser.add_argument("--total_time", type=str, default=None, help="Total time, in format of &H:&M:&S. Default None")
    parser.add_argument("--cumulative_climb", type=str, default=None, help="Cumulative climb height. Default None")
    parser.add_argument("--average_cadence", type=str, default=None, help="Average cadence. Default None")
    parser.add_argument("--exercise_load", type=str, default=None, help="Excersice load. Default None")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    k = KeepSultan()
    k.load_configs(args.config_path)
    k.load_args(args)
    k.process()
    k.save(args.save_path)






