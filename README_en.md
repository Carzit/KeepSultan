# KeepSultan 🏃‍♂️✨

**Keep-style Running Screenshot Generator**

[中文](https://github.com/Carzit/KeepSultan/blob/main/README.md) | English

---

## 1. Introduction

**KeepSultan** is a lightweight automation tool designed to generate **Keep app-style running screenshots**.
It automatically fills in metrics, supports random generation, and even allows you to use avatars/maps directly from URLs to recreate authentic Keep-style images.

* 🎨 **Customization**: Upload your avatar & map, freely set username and metric ranges
* 🎲 **Randomization**: Auto-generate values within ranges for natural variation
* 🖥 **Dual Mode**: Supports both **CLI** and **GUI** usage
* 🌍 **Flexible Resources**: Avatars and maps can be local files or HTTP(S) URLs (cached automatically)
* ⚙️ **Preference Persistence**: Config changes are automatically saved to JSON, restored on next startup

---

## 2. Features

### 2.1 Metric Customization & Randomization

Supports configuration or random generation for:

* Date (`date`)
* End Time (`end_time`)
* Total Distance (`total_km`)
* Sport Duration (`sport_time`)
* Total Duration (`total_time`)
* Cumulative Climb (`cumulative_climb`)
* Average Cadence (`average_cadence`)
* Exercise Load (`exercise_load`)

Avatar & Map sources:

* Local file, e.g. `./avatar.png`
* Online URL, e.g. `https://example.com/avatar.jpg` (auto cached)

👉 **Recommended aspect ratios**:

* Avatar: 1:1
* Map: 35:28

### 2.2 Weather & Location Information

* **Automatic Weather Fetching**: Retrieve real-time weather and temperature data for specified cities via built-in weather API
* **Custom Location**: Manually set location information
* **Weather Override**: Manually set weather and temperature to override automatic data

### 2.3 Dynamic Path Generation

Using OpenCV and path masking technology to generate realistic running paths:

* **Intelligent Path Extraction**: Extract path points from mask images to generate natural running trajectories
* **Path Smoothing**: Apply sliding window averaging to ensure smooth and natural path curves
* **Adjustable Parameters**: Customize track color, thickness, sampling rate, and other path attributes
* **Automatic Fallback**: Automatically switch to static map if dynamic generation fails

### 2.3.1 Background & Mask Images

To generate dynamic running paths, you need to prepare two images:

* **Background Image**: The base map image, which can be a city map, park plan, or any desired background
* **Mask Image**: Defines areas where paths can be generated, distinguishing between roads and non-road areas

#### Creating a Mask Image

1. Create a new layer based on the background image
2. Use red color to draw all passable roads and paths
3. Keep non-road areas light-colored or transparent
4. Save as PNG format, ensuring path areas are clearly visible

#### Example

* **Background**: `src/map1.png` - Satellite image of a city area
* **Mask**: `src/map2.png` - Same dimensions as background, with roads drawn in red

### 2.4 GUI Mode

Provided in `KeepSultanGUI.py`:

* **Preview**: Open a popup window to preview generated image
* **Save**: Save final output image
* Config changes are automatically saved to JSON and reloaded on next startup

### 2.5 CLI Mode

Quickly generate screenshots with parameters:

```bash
python KeepSultan.py --config config.json --save result.png \
    --username Alice --avatar https://example.com/a.png --map scr/map.png
```

### 2.6 Executable Version

No Python required, just run the `.exe`:
👉 [Download latest release](https://github.com/Carzit/KeepSultan/releases/)

---

## 3. Usage

### 3.1 Install Dependencies

For source usage:

```bash
pip install pillow opencv-python numpy scipy
```

Or synchronize environment via [uv](https://uv.doczh.com/):

```bash
uv sync
```

#### Optional Dependencies

* **scipy**: Used to accelerate path generation algorithms (if not installed, a regular algorithm will be used instead)
* **requests**: Used for weather API calls (included in the standard library)
* **tkinter**: Used to run the GUI version (usually installed with Python)

### 3.2 Configuration File

The configuration file is a standard JSON used to store defaults and preferences.
Unset fields will fallback to built-in defaults.

#### Fields

* **Resource paths**

  * `template`: Template image path or URL
  * `map`: Running map path or URL
  * `avatar`: Avatar path or URL
  * `username`: Username

* **Date & Time**

  * `date`: (`YYYY/MM/DD`), `"today"` auto-fills current date
  * `end_time`: (`HH:MM:SS`), `"now"` auto-fills current time

* **Weather & Location**

  * `location`: Location information for weather data retrieval
  * `weather`: Weather information, `"auto"` automatically fetches current weather (default)
  * `temperature`: Temperature information, `"auto"` automatically fetches current temperature (default)

* **Path Generation Configuration**

  * `map_bg_path`: Path to map background image
  * `map_mask_path`: Path to path mask image, used to draw dynamic paths on the background
  * `track_color`: Track color in BGR format (default: `(154, 201, 38)`)
  * `track_thickness`: Track line thickness (default: `12`)
  * `track_sample_rate`: Path point sampling rate (default: `5`)
  * `track_max_steps`: Maximum number of steps limit (default: `3000`)
  * `track_completion_threshold`: Path completion threshold (default: `0.2`)
  * `track_target_length`: Target path length (default: `400`)

* **Metric ranges** (single value or range)

  * `total_km`: `{ "low": 3.02, "high": 3.30, "precision": 2 }`
  * `sport_time`: `{ "start": "00:21:00", "end": "00:23:00" }`
  * `total_time`: `{ "start": "00:34:00", "end": "00:39:00" }`
  * `cumulative_climb`: `{ "low": 90, "high": 96, "precision": 0 }`
  * `average_cadence`: `{ "low": 76, "high": 81, "precision": 0 }`
  * `exercise_load`: `{ "low": 48, "high": 51, "precision": 0 }`

* **Font styles** (optional)

  * `font_regular`, `font_bold_big`, `font_semibold`, `font_clock`
  * Format:

    ```json
    {
      "font_path": "fonts/SourceHanSansCN-Regular.otf",
      "font_size": 36,
      "color": [0, 0, 0]
    }
    ```

#### Example Config

```json
{
  "template": "src/template.png",
  "map": "src/map.png",
  "avatar": "https://example.com/avatar.png",
  "username": "Alice",
  "date": "2025/08/21",
  "end_time": "18:30:00",
  "location": "Beijing",
  "weather": "auto",
  "temperature": "auto",
  "map_bg_path": "src/map1.png",
  "map_mask_path": "src/map2.png",
  "track_color": [154, 201, 38],
  "track_thickness": 12,
  "track_sample_rate": 5,
  "track_max_steps": 3000,
  "track_completion_threshold": 0.2,
  "track_target_length": 400,
  "total_km": { "low": 3.04, "high": 3.3, "precision": 2 },
  "sport_time": { "start": "00:20:00", "end": "00:23:00" },
  "total_time": { "start": "00:34:00", "end": "00:39:00" },
  "cumulative_climb": { "low": 90, "high": 96, "precision": 0 },
  "average_cadence": { "low": 76, "high": 81, "precision": 0 },
  "exercise_load": { "low": 48, "high": 51, "precision": 0 }
}
```

### 3.3 Running

#### CLI

```bash
python KeepSultan.py [-h] [--config CONFIG] [--save SAVE] \
    [--template TEMPLATE] [--map MAP] [--avatar AVATAR] \
    [--username USERNAME] [--date DATE] [--end-time END_TIME] \
    [--location LOCATION] [--weather WEATHER] [--temperature TEMPERATURE] \
    [--map-bg-path MAP_BG_PATH] [--map-mask-path MAP_MASK_PATH] [--seed SEED]
```

| Argument             | Type | Description                                 |
| -------------------- | ---- | ------------------------------------------- |
| `-c, --config`       | str  | Path to JSON config (default `config.json`) |
| `-s, --save`         | str  | Output image path (default `images/save.png`) |
| `--template`         | str  | Template background path or URL             |
| `--map`              | str  | Running map path or URL                     |
| `--avatar`           | str  | Avatar path or URL                          |
| `--username`         | str  | Username                                    |
| `--date`             | str  | Date (`YYYY/MM/DD`, defaults to today)      |
| `--end-time`         | str  | End time (`HH:MM[:SS]`, defaults to now)    |
| `--location`         | str  | Location for weather data retrieval         |
| `--weather`          | str  | Weather information, leave empty for auto   |
| `--temperature`      | str  | Temperature information, leave empty for auto |
| `--map-bg-path`      | str  | Path to map background image                |
| `--map-mask-path`    | str  | Path to path mask image                     |
| `--seed`             | int  | Random seed for reproducible results        |

👉 CLI parameters override config file values.

#### GUI

```bash
python KeepSultanGUI.py
```

---

## 4. Credits & Related Projects

Special thanks to [eltsen00](https://github.com/eltsen00) for developing the web version [KeepGeneration-Web](https://github.com/eltsen00/KeepGeneration-Web).
Try it online 👉 [https://keep.hshoe.cn/](https://keep.hshoe.cn/)

Also thanks to [LynxFrost](https://github.com/itrfcn) for developing the web version (based on the new version) [KeepSultan-Web](https://github.com/itrfcn/KeepSultan-Web).
Try it online 👉 [https://k1.686909.xyz/](https://k1.686909.xyz/)

---

## 5. Fun Note 🌙

In the name of Merciful Technology:

> “All platforms that constrain freedom shall be conquered by code;
> all rules that restrict creativity shall be rewritten.”

KeepSultan — the Sultan of running screenshots:

* **Conquering chaos with technology**
* **Liberating freedom from restriction**

> May your runs go beyond your legs,
> and may your screenshots go beyond Keep.

---

## 6. Disclaimer

This tool is for **personal learning and research** purposes only.  
Do not use it for illegal activities or to violate platform policies.  
Users assume full responsibility for consequences; the developer is not liable.  

