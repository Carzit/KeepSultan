
"""
KeepSultan (refactored)
-----------------------

关键改动：
1) 以数据类管理配置（支持从 JSON 读取/写回偏好与默认设置合并）。
2) 支持 Avatar / Map 既可本地文件也可 HTTP(S) URL（含本地缓存）。
3) 更健壮的时间/数值区间表达和随机生成逻辑，统一校验与格式化。
4) 清晰的模块分层：Config、Assets、ImageEditor、KeepSultanApp。
5) 规范 CLI：命令行参数会覆盖 JSON 中的设置。

依赖：Pillow
标准库：argparse, dataclasses, datetime, hashlib, io, json, logging, os, pathlib, random, re, typing, urllib

使用示例：
    python KeepSultan_refactored.py --config config.json --save save.png --username YOUR_NAME --avatar https://example.com/Avatar.png --map scr/map.png
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import re
import hashlib
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Literal

from urllib.parse import urlparse
from urllib.request import urlopen, Request

from PIL import Image, ImageDraw, ImageFont

# ------------------------------
# 类型与工具
# ------------------------------

TimeStr = str  # 格式统一为 "HH:MM:SS"
Color = Tuple[int, int, int]
Point = Tuple[int, int]
Size = Tuple[int, int]

def _ensure_time_str_hms(s: str) -> TimeStr:
    """
    校验并标准化时间字符串为 'HH:MM:SS'。
    支持输入 'H:M', 'HH:MM', 'H:M:S', 'HH:MM:SS' 等变体。
    """
    if not isinstance(s, str):
        raise TypeError("time must be a string")
    parts = s.strip().split(":")
    if len(parts) == 2:
        h, m = parts
        s = f"{int(h):02d}:{int(m):02d}:00"
    elif len(parts) == 3:
        h, m, sec = parts
        s = f"{int(h):02d}:{int(m):02d}:{int(sec):02d}"
    else:
        raise ValueError(f"Invalid time string: {s!r}")
    # 最终再正则校验
    if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", s):
        raise ValueError(f"Invalid time format: {s!r}")
    return s

def parse_time_to_seconds(s: TimeStr) -> int:
    """将 'HH:MM:SS' 转换为秒。"""
    s = _ensure_time_str_hms(s)
    hh, mm, ss = map(int, s.split(":"))
    return hh * 3600 + mm * 60 + ss

def seconds_to_hms(sec: Union[int, float]) -> TimeStr:
    """将秒（可为浮点）转换为 'HH:MM:SS'。"""
    sec = int(round(sec))
    hh, rem = divmod(sec, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

def seconds_to_pace_mmss(sec_per_km: Union[int, float]) -> str:
    """将每公里用时（秒）格式化为 'mm\'ss\'\''（如 05'23''）。"""
    total = int(round(sec_per_km))
    mm, ss = divmod(total, 60)
    return f"{mm:02d}\'{ss:02d}\'\'"

def random_in_range_numeric(low: float, high: float, precision: int = 0) -> Union[int, float]:
    """在 [low, high] 内随机取值，按 precision 保留小数位，precision=0 返回 int。"""
    if low > high:
        low, high = high, low
    val = random.uniform(low, high)
    if precision <= 0:
        return int(round(val))
    return round(val, precision)

def random_time_between(start: TimeStr, end: TimeStr) -> TimeStr:
    """在两个时间点之间随机选择一个时间（均为 'HH:MM:SS'）。"""
    s = parse_time_to_seconds(start)
    e = parse_time_to_seconds(end)
    if s > e:
        s, e = e, s
    t = random.uniform(s, e)
    return seconds_to_hms(t)

def safe_int(v: Any) -> int:
    return int(round(float(v)))

# ------------------------------
# 配置
# ------------------------------

@dataclass
class NumberRange:
    """数值区间 [low, high]。"""
    low: float
    high: float
    precision: int = 0

    def sample(self) -> Union[int, float]:
        return random_in_range_numeric(self.low, self.high, self.precision)

@dataclass
class TimeRange:
    """时间区间 [start, end]，'HH:MM:SS'。"""
    start: TimeStr
    end: TimeStr

    def __post_init__(self) -> None:
        self.start = _ensure_time_str_hms(self.start)
        self.end = _ensure_time_str_hms(self.end)

    def sample(self) -> TimeStr:
        return random_time_between(self.start, self.end)

@dataclass
class TextStyle:
    """文本样式。"""
    font_path: str
    font_size: int
    color: Color = (0, 0, 0)

@dataclass
class KeepConfig:
    """
    应用配置 + 偏好。

    注：avatar 与 map 支持本地路径或 HTTP(S) URL。
    """
    # 资源
    template: str = "scr/template.png"
    map: str = "scr/map.png"
    avatar: str = ""
    username: str = ""

    # 时间与日期
    date: str = ""  # 默认留空，运行时自动填充今天
    end_time: TimeStr = ""  # 默认留空，运行时自动填充当前时间

    # 指标区间（与原始脚本保持一致）
    total_km: NumberRange = field(default_factory=lambda: NumberRange(3.02, 3.30, precision=2))
    sport_time: TimeRange = field(default_factory=lambda: TimeRange("00:21:00", "00:23:00"))
    total_time: TimeRange = field(default_factory=lambda: TimeRange("00:34:00", "00:39:00"))
    cumulative_climb: NumberRange = field(default_factory=lambda: NumberRange(90, 96, precision=0))
    average_cadence: NumberRange = field(default_factory=lambda: NumberRange(76, 81, precision=0))
    exercise_load: NumberRange = field(default_factory=lambda: NumberRange(48, 51, precision=0))

    # 字体样式（可进一步外置到 JSON）
    font_regular: TextStyle = field(default_factory=lambda: TextStyle("fonts/SourceHanSansCN-Regular.otf", 36, (0, 0, 0)))
    font_bold_big: TextStyle = field(default_factory=lambda: TextStyle("fonts/QanelasBlack.otf", 180, (0, 0, 0)))
    font_semibold: TextStyle = field(default_factory=lambda: TextStyle("fonts/QanelasSemiBold.otf", 65, (0, 0, 0)))
    font_clock: TextStyle = field(default_factory=lambda: TextStyle("fonts/SourceHanSansCN-Regular.otf", 40, (0, 0, 0)))

    # 偏好文件（可记录最近保存路径、上次用户名等）
    prefs_file: str = "keepsultan_prefs.json"

    @staticmethod
    def from_json(path: Union[str, Path]) -> "KeepConfig":
        """
        从 JSON 文件读取配置，自动将简单对象转为数据类实例。
        未提供的字段使用默认值。
        """
        base = KeepConfig()
        p = Path(path)
        if p.is_file():
            with p.open("r", encoding="utf-8") as f:
                raw: Dict[str, Any] = json.load(f)
        else:
            raw = {}

        def _nr(v: Any, default: NumberRange) -> NumberRange:
            if isinstance(v, dict):
                return NumberRange(
                    low=float(v.get("low", default.low)),
                    high=float(v.get("high", default.high)),
                    precision=int(v.get("precision", default.precision)),
                )
            elif isinstance(v, (int, float)):
                return NumberRange(float(v), float(v), precision=default.precision)
            else:
                return default

        def _tr(v: Any, default: TimeRange) -> TimeRange:
            if isinstance(v, dict):
                return TimeRange(
                    start=_ensure_time_str_hms(v.get("start", default.start)),
                    end=_ensure_time_str_hms(v.get("end", default.end)),
                )
            elif isinstance(v, str):
                # 单值 -> 单点区间
                s = _ensure_time_str_hms(v)
                return TimeRange(s, s)
            else:
                return default

        for k, v in raw.items():
            if k in {"template", "map", "avatar", "username", "date", "end_time", "prefs_file"}:
                setattr(base, k, str(v))
            elif k == "total_km":
                base.total_km = _nr(v, base.total_km)
            elif k == "sport_time":
                base.sport_time = _tr(v, base.sport_time)
            elif k == "total_time":
                base.total_time = _tr(v, base.total_time)
            elif k == "cumulative_climb":
                base.cumulative_climb = _nr(v, base.cumulative_climb)
            elif k == "average_cadence":
                base.average_cadence = _nr(v, base.average_cadence)
            elif k == "exercise_load":
                base.exercise_load = _nr(v, base.exercise_load)
            # 字体配置可选
            elif k == "font_regular" and isinstance(v, dict):
                base.font_regular = TextStyle(v.get("font_path", base.font_regular.font_path),
                                              int(v.get("font_size", base.font_regular.font_size)),
                                              tuple(v.get("color", base.font_regular.color)))  # type: ignore
            elif k == "font_bold_big" and isinstance(v, dict):
                base.font_bold_big = TextStyle(v.get("font_path", base.font_bold_big.font_path),
                                               int(v.get("font_size", base.font_bold_big.font_size)),
                                               tuple(v.get("color", base.font_bold_big.color)))  # type: ignore
            elif k == "font_semibold" and isinstance(v, dict):
                base.font_semibold = TextStyle(v.get("font_path", base.font_semibold.font_path),
                                               int(v.get("font_size", base.font_semibold.font_size)),
                                               tuple(v.get("color", base.font_semibold.color)))  # type: ignore
            elif k == "font_clock" and isinstance(v, dict):
                base.font_clock = TextStyle(v.get("font_path", base.font_clock.font_path),
                                            int(v.get("font_size", base.font_clock.font_size)),
                                            tuple(v.get("color", base.font_clock.color)))  # type: ignore

        return base

    def to_json(self, path: Union[str, Path]) -> None:
        """将当前配置写回 JSON（便于作为模板/偏好）。"""
        data = asdict(self)
        # dataclass 嵌套已被 asdict 展开，确保可 JSON 序列化
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# ------------------------------
# 资源加载（支持 URL + 缓存）
# ------------------------------

class AssetLoader:
    """
    图片资源加载器：支持本地路径与 HTTP(S) URL。
    远端资源会按 URL 的 MD5 命中本地缓存，避免重复下载。
    """
    def __init__(self, cache_dir: Union[str, Path] = ".keepsultan_cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _is_url(self, path: str) -> bool:
        scheme = urlparse(path).scheme.lower()
        return scheme in {"http", "https"}

    def _cache_path_for_url(self, url: str) -> Path:
        h = hashlib.md5(url.encode("utf-8")).hexdigest()
        # 尝试从 URL 后缀推断扩展名
        ext = os.path.splitext(urlparse(url).path)[1] or ".img"
        return self.cache_dir / f"{h}{ext}"

    def load_image(self, path_or_url: str) -> Image.Image:
        """
        加载图片：
        - 若为本地路径：直接打开；
        - 若为 URL：下载到缓存再打开。
        """
        if not path_or_url:
            raise ValueError("Empty image path/url")

        if self._is_url(path_or_url):
            cp = self._cache_path_for_url(path_or_url)
            if not cp.exists():
                req = Request(path_or_url, headers={"User-Agent": "KeepSultan/1.0"})
                with urlopen(req, timeout=30) as r:
                    content = r.read()
                cp.write_bytes(content)
            return Image.open(cp).convert("RGBA")
        else:
            p = Path(path_or_url)
            if (not p.exists()) or (not p.is_file()):
                raise FileNotFoundError(f"Image not found: {path_or_url}")
            return Image.open(p).convert("RGBA")

# ------------------------------
# 图像编辑
# ------------------------------

class ImageEditor:
    """对 PIL.Image 的轻量封装，提供贴图与文本绘制。"""
    def __init__(self) -> None:
        self.img: Optional[Image.Image] = None

    def load_base(self, img: Image.Image) -> None:
        self.img = img.copy()

    def paste(self, img: Image.Image, position: Point) -> None:
        if self.img is None:
            raise RuntimeError("Base image not loaded")
        self.img.paste(img, position, img if img.mode in ("RGBA",) else None)

    def draw_text(self, text: str, position: Point, style: TextStyle) -> None:
        if self.img is None:
            raise RuntimeError("Base image not loaded")
        draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype(style.font_path, style.font_size)
        draw.text(position, text, fill=style.color, font=font)

    def save(self, path: Union[str, Path]) -> None:
        if self.img is None:
            raise RuntimeError("Nothing to save")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.img.save(path)

# ------------------------------
# 业务逻辑
# ------------------------------

def make_circular_avatar(img: Image.Image, size: Size) -> Image.Image:
    """裁剪为正方形并缩放，然后生成圆形头像（带透明通道）。"""
    img = img.convert("RGBA")
    w, h = img.size
    if w != h:
        m = min(w, h)
        left = (w - m) // 2
        top = (h - m) // 2
        img = img.crop((left, top, left + m, top + m))
    img = img.resize(size)

    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size[0], size[1]), fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out

def resize_keep_alpha(img: Image.Image, size: Size) -> Image.Image:
    """缩放到指定尺寸，保留透明通道。"""
    return img.resize(size).convert("RGBA")

class KeepSultanApp:
    """
    生成 Keep截图的应用。
    - 使用模板图作为背景
    - 绘制用户头像、地图和数据指标
    """
    def __init__(self, cfg: KeepConfig, assets: AssetLoader | None = None, logger: logging.Logger | None = None) -> None:
        self.cfg = cfg
        self.assets = assets or AssetLoader()
        self.editor = ImageEditor()
        self.logger = logger or logging.getLogger("KeepSultan")

        self.logger.info("KeepSultanApp initialized. Config: %s", self.cfg)

    # ---- 指标计算 ----
    @staticmethod
    def calculate_start_time(end_time: TimeStr, duration: TimeStr) -> TimeStr:
        """开始时间 = 结束时间 - 持续时长。"""
        end_dt = datetime.strptime(_ensure_time_str_hms(end_time), "%H:%M:%S")
        dur_sec = parse_time_to_seconds(duration)
        start_dt = end_dt - timedelta(seconds=dur_sec)
        return start_dt.strftime("%H:%M:%S")

    @staticmethod
    def calculate_pace(distance_km: float, time_hms: TimeStr) -> str:
        """计算平均配速（mm' ss''）。"""
        total_sec = parse_time_to_seconds(time_hms)
        if distance_km <= 0:
            raise ValueError("distance_km must be positive")
        return seconds_to_pace_mmss(total_sec / distance_km)

    @staticmethod
    def calculate_cost(total_time_hms: TimeStr) -> int:
        """消耗卡路里（与原实现保持：700 * 小时数）。"""
        total_sec = parse_time_to_seconds(total_time_hms)
        return int(round(700 * (total_sec / 3600)))

    # ---- 渲染主流程 ----
    def process(self) -> Image.Image:
        #self.cfg.ensure_runtime_defaults()

        # 1) 背景模板
        base = self.assets.load_image(self.cfg.template)
        self.editor.load_base(base)

        # 2) 头像（允许为空）
        if self.cfg.avatar:
            avatar_raw = self.assets.load_image(self.cfg.avatar)
            avatar_img = make_circular_avatar(avatar_raw, (100, 100))
            self.editor.paste(avatar_img, (40, 250))

        # 3) 地图（允许为空）
        if self.cfg.map:
            map_raw = self.assets.load_image(self.cfg.map)
            map_img = resize_keep_alpha(map_raw, (1000, 800))
            self.editor.paste(map_img, (40, 720))

        # 4) 随机/计算指标
        if self.cfg.date == "today":
            date = datetime.now().strftime("%Y/%m/%d") # 如果是特殊字符"today"，则使用当前日期
        else:
            date = self.cfg.date
        if self.cfg.end_time == "now":
            end_time = datetime.now().strftime("%H:%M:%S") # 如果是特殊字符"now"，则使用当前时间
        else:
            end_time = _ensure_time_str_hms(self.cfg.end_time)
        total_time = self.cfg.total_time.sample()
        sport_time = self.cfg.sport_time.sample()
        # 运动时长不应长于总时长
        if parse_time_to_seconds(sport_time) > parse_time_to_seconds(total_time):
            sport_time = total_time

        start_time = self.calculate_start_time(end_time, total_time)
        total_km = self.cfg.total_km.sample()
        # 轻微加 0.01，避免随机数取不到两位的情形
        total_km = round(float(total_km) + 0.01, 2) if isinstance(total_km, float) else total_km

        pace = self.calculate_pace(float(total_km), sport_time)
        cost = self.calculate_cost(total_time)

        cumulative_climb = self.cfg.cumulative_climb.sample()
        average_cadence = self.cfg.average_cadence.sample()
        exercise_load = self.cfg.exercise_load.sample()

        self.logger.info(f"Generated data: date={date}, username={self.cfg.username}, end_time={end_time}, start_time={start_time}, total_km={total_km}, sport_time={sport_time}, total_time={total_time}, pace={pace}, cost={cost}, cumulative_climb={cumulative_climb}, average_cadence={average_cadence}, exercise_load={exercise_load}")

        # 5) 文本绘制（坐标与字体取自原始脚本）
        self.editor.draw_text(end_time[:5], (50, 25), self.cfg.font_clock)  # 系统时间 HH:MM
        self.editor.draw_text(self.cfg.username or "", (160, 240), TextStyle(self.cfg.font_regular.font_path, 40, (0, 0, 0))) # 用户名
        self.editor.draw_text(f"{date} {start_time[:5]} - {end_time[:5]}", (160, 290), TextStyle(self.cfg.font_regular.font_path, 36, (155, 155, 155))) # 日期时间

        self.editor.draw_text(str(total_km), (50, 485), self.cfg.font_bold_big)  # 公里数
        self.editor.draw_text("公里", (418, 610), TextStyle(self.cfg.font_regular.font_path, 43, (0, 0, 0)))

        self.editor.draw_text(str(sport_time), (55, 1750), self.cfg.font_semibold)  # 运动时长
        self.editor.draw_text(str(pace), (445, 1750), self.cfg.font_semibold)      # 平均配速
        self.editor.draw_text(str(cost), (800, 1750), self.cfg.font_semibold)      # 运动消耗

        self.editor.draw_text(str(total_time), (55, 1910), self.cfg.font_semibold)  # 总时长
        self.editor.draw_text(str(cumulative_climb), (445, 1910), self.cfg.font_semibold)  # 累计爬升
        # 对齐规则：>100 与 <=100 使用不同起点（兼容原脚本）
        cad_x = 780 if safe_int(average_cadence) > 100 else 800
        self.editor.draw_text(str(average_cadence), (cad_x, 1910), self.cfg.font_semibold)  # 平均步频
        self.editor.draw_text(str(exercise_load), (55, 2070), self.cfg.font_semibold)  # 运动负荷

        return self.editor.img

    def save(self, path: Union[str, Path]) -> None:
        self.editor.save(path)

# ------------------------------
# CLI
# ------------------------------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KeepSultan CLI")
    p.add_argument("-c", "--config", type=str, default="config.json", help="配置 JSON 路径，默认 config.json")
    p.add_argument("-s", "--save", type=str, default="save.png", help="输出图片路径（含文件名）")
    # 允许覆盖关键字段
    p.add_argument("--template", type=str, help="模板图片路径或 URL")
    p.add_argument("--map", type=str, help="地图图片路径或 URL")
    p.add_argument("--avatar", type=str, help="头像图片路径或 URL")
    p.add_argument("--username", type=str, help="用户名")
    p.add_argument("--date", type=str, help="日期（YYYY/MM/DD），留空自动填充今天")
    p.add_argument("--end-time", dest="end_time", type=str, help="结束时间（HH:MM 或 HH:MM:SS），留空自动填充当前时间")
    p.add_argument("--seed", type=int, help="随机种子（可复现）")
    return p

def apply_overrides(cfg: KeepConfig, ns: argparse.Namespace) -> KeepConfig:
    """将命令行覆盖应用到配置上。"""
    if ns.template: cfg.template = ns.template
    if ns.map: cfg.map = ns.map
    if ns.avatar: cfg.avatar = ns.avatar
    if ns.username: cfg.username = ns.username
    if ns.date: cfg.date = ns.date
    if ns.end_time: cfg.end_time = ns.end_time
    return cfg

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ap = build_argparser()
    ns = ap.parse_args()
    if ns.seed is not None:
        random.seed(ns.seed)

    cfg = KeepConfig.from_json(ns.config)
    cfg = apply_overrides(cfg, ns)
    #cfg.ensure_runtime_defaults()

    app = KeepSultanApp(cfg)
    app.process()
    app.save(ns.save)
    logging.info(f"Saved to: {ns.save}")

if __name__ == "__main__":
    main()
