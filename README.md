# KeepSultan 🏃‍♂️✨

**Keep 风格跑步截图生成器**

[English](https://github.com/Carzit/KeepSultan/blob/main/README_en.md) | 中文

---

## 1. 项目简介

**KeepSultan** 是一个轻量化的自动化工具，用于生成新版 **Keep 应用风格的跑步截图**。
它可以自动填充参数、支持随机生成指标，甚至可以直接使用 URL 头像 / 地图，一键生成与 Keep 应用一致的截图。

* 🎨 **个性化**：上传头像、地图，随心定义用户名和数值区间
* 🎲 **随机化**：自动在设定区间内抽样生成指标，避免死板重复
* 🖥 **双模式**：支持 **命令行版本** 和 **图形化界面 (GUI)**
* 🌍 **资源扩展**：头像 / 地图既支持本地文件，也支持 HTTP(S) URL（自动缓存）
* ⚙️ **偏好保存**：每次修改配置会自动写回 JSON 文件，下次打开无需重新设置

---

## 2. 核心功能

### 2.1 参数自定义与随机生成

支持配置或随机生成以下指标：

* 日期（date）
* 结束时间（end\_time）
* 跑步总里程（total\_km）
* 运动时间（sport\_time）
* 总计时间（total\_time）
* 累计爬升（cumulative\_climb）
* 平均步频（average\_cadence）
* 运动负荷（exercise\_load）

头像与地图可选择：

* 本地文件，例如：`./avatar.png`
* 在线 URL，例如：`https://example.com/avatar.jpg` （自动下载 & 缓存）

👉 **建议比例**：

* 头像：1:1
* 地图：35:28

### 2.2 GUI 版本

在 `KeepSultanGUI.py` 中提供图形化界面：

* “Preview” 按钮：弹出新窗口实时预览截图
* “Save” 按钮：保存最终图片
* 修改配置后会自动写回 JSON 文件，下次打开直接记忆上次设置

### 2.3 命令行版本

支持通过参数快速生成截图：

```bash
python KeepSultan.py --config config.json --save result.png \
    --username Alice --avatar https://example.com/a.png --map scr/map.png
```

### 2.4 可执行文件

无需 Python 环境，直接运行exe：  
👉 [下载最新 release](https://github.com/Carzit/KeepSultan/releases/download/v0.0.3/KeepSultan.zip)

---

## 3. 使用说明

### 3.1 安装依赖

源码运行需安装：

```bash
pip install pillow
```

或者使用 [uv](https://uv.doczh.com/) 一键同步环境：

```bash
uv sync
```

### 3.2 配置文件
配置文件是一个标准 JSON，用于保存默认设置与用户偏好。
未设置的字段会使用内置默认值。

#### 字段说明

* **资源路径**

  * `template` : 模板图路径或 URL
  * `map` : 跑步地图路径或 URL
  * `avatar` : 头像路径或 URL
  * `username` : 用户名

* **时间与日期**

  * `date` : 日期 (`YYYY/MM/DD`)，使用字符串"today"将自动填充今天的日期
  * `end_time` : 结束时间 (`HH:MM:SS`)，使用字符串"now"将自动填充当前时间

* **指标区间**（均可为单值或区间）

  * `total_km` : 总里程，示例 `{ "low": 3.02, "high": 3.30, "precision": 2 }`
  * `sport_time` : 运动时长区间，示例 `{ "start": "00:21:00", "end": "00:23:00" }`
  * `total_time` : 总时长区间，示例 `{ "start": "00:34:00", "end": "00:39:00" }`
  * `cumulative_climb` : 累计爬升，示例 `{ "low": 90, "high": 96, "precision": 0 }`
  * `average_cadence` : 平均步频，示例 `{ "low": 76, "high": 81, "precision": 0 }`
  * `exercise_load` : 运动负荷，示例 `{ "low": 48, "high": 51, "precision": 0 }`

* **字体样式**（可选）

  * `font_regular`, `font_bold_big`, `font_semibold`, `font_clock`
  * 格式：

    ```json
    {
      "font_path": "fonts/SourceHanSansCN-Regular.otf",
      "font_size": 36,
      "color": [0, 0, 0]
    }
    ```

#### 示例配置文件

```json
{
  "template": "scr/template.png",
  "map": "scr/map.png",
  "avatar": "https://example.com/avatar.png",
  "username": "Alice",
  "date": "2025/08/21",
  "end_time": "18:30:00",
  "total_km": {
    "low": 3.04,
    "high": 3.3,
    "precision": 2
  },
  "sport_time": {
    "start": "00:20:00",
    "end": "00:23:00"
  },
  "total_time": {
    "start": "00:34:00",
    "end": "00:39:00"
  },
  "cumulative_climb": {
    "low": 90.0,
    "high": 96.0,
    "precision": 0
  },
  "average_cadence": {
    "low": 76.0,
    "high": 81.0,
    "precision": 0
  },
  "exercise_load": {
    "low": 48.0,
    "high": 51.0,
    "precision": 0
  },
  "font_regular": {
    "font_path": "fonts/SourceHanSansCN-Regular.otf",
    "font_size": 36,
    "color": [
      0,
      0,
      0
    ]
  },
  "font_bold_big": {
    "font_path": "fonts/QanelasBlack.otf",
    "font_size": 180,
    "color": [
      0,
      0,
      0
    ]
  },
  "font_semibold": {
    "font_path": "fonts/QanelasSemiBold.otf",
    "font_size": 65,
    "color": [
      0,
      0,
      0
    ]
  },
  "font_clock": {
    "font_path": "fonts/SourceHanSansCN-Regular.otf",
    "font_size": 40,
    "color": [
      0,
      0,
      0
    ]
  }
}
```

### 3.2 运行

#### 命令行模式

```bash
python KeepSultan.py [-h] [--config CONFIG] [--save SAVE] [--template TEMPLATE] [--map MAP] [--avatar AVATAR] [--username USERNAME] [--date DATE] [--end-time END_TIME] [--seed SEED]
```

命令行参数说明：
| 参数             | 类型    | 说明                                |
| -------------- | ----- | --------------------------------- |
| `-c, --config` | `str` | 配置 JSON 文件路径，默认 `config.json`     |
| `-s, --save`   | `str` | 输出图片路径，默认 `save.png`              |
| `--template`   | `str` | 背景模板图片路径或 URL                     |
| `--map`        | `str` | 跑步地图图片路径或 URL                     |
| `--avatar`     | `str` | 用户头像路径或 URL                       |
| `--username`   | `str` | 用户名                               |
| `--date`       | `str` | 日期（格式 `YYYY/MM/DD`，默认自动填充当天）      |
| `--end-time`   | `str` | 结束时间（`HH:MM` 或 `HH:MM:SS`，默认当前时间） |
| `--seed`       | `int` | 随机种子（用于复现同样的随机结果）                 |

*注意： 当同时传入配置 JSON 文件路径参数与其他 CLI 参数时， CLI 参数优先级高于 JSON 配置文件。*

#### GUI 模式

```bash
python KeepSultanGUI.py
```

---

## 5. 致谢 & 衍生版本

感谢 [eltsen00](https://github.com/eltsen00) 开发的网页版 [KeepGeneration-Web](https://github.com/eltsen00/KeepGeneration-Web)。  
在线体验地址 👉 [https://keep.hshoe.cn/](https://keep.hshoe.cn/)

---

## 6. 胡言乱语（保留彩蛋 🌙）

奉至仁至慈的技术之名：

> “凡束缚自由之平台，皆应技术征服；凡限制创造之规则，皆当被改写。”

KeepSultan，如苏丹般的征服者：

* **以技术征服无序**
* **以自由解放压迫**

> 愿你跑步不止于双腿，愿运动不止于长跑月。

---

## 7. 免责声明

此工具仅供 **个人学习与研究** 之用。  
请勿用于违反法律或平台规则的行为。  
使用者需自行承担全部责任，开发者不对任何后果负责。
