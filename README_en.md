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

### 2.2 GUI Mode

Provided in `KeepSultanGUI.py`:

* **Preview**: open a popup window to preview generated image
* **Save**: save final output image
* Config changes are automatically saved to JSON and reloaded on next startup

### 2.3 CLI Mode

Quickly generate screenshots with parameters:

```bash
python KeepSultan.py --config config.json --save result.png \
    --username Alice --avatar https://example.com/a.png --map scr/map.png
```

### 2.4 Executable Version

No Python required, just run the `.exe`:
👉 [Download latest release](https://github.com/Carzit/KeepSultan/releases/download/v0.0.3/KeepSultan.zip)

---

## 3. Usage

### 3.1 Install Dependencies

For source usage:

```bash
pip install pillow
```

Or synchronize environment via [uv](https://uv.doczh.com/):

```bash
uv sync
```

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
  "template": "scr/template.png",
  "map": "scr/map.png",
  "avatar": "https://example.com/avatar.png",
  "username": "Alice",
  "date": "2025/08/21",
  "end_time": "18:30:00",
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
    [--username USERNAME] [--date DATE] [--end-time END_TIME] [--seed SEED]
```

| Argument       | Type | Description                                 |
| -------------- | ---- | ------------------------------------------- |
| `-c, --config` | str  | Path to JSON config (default `config.json`) |
| `-s, --save`   | str  | Output image path (default `save.png`)      |
| `--template`   | str  | Template background path or URL             |
| `--map`        | str  | Running map path or URL                     |
| `--avatar`     | str  | Avatar path or URL                          |
| `--username`   | str  | Username                                    |
| `--date`       | str  | Date (`YYYY/MM/DD`, defaults to today)      |
| `--end-time`   | str  | End time (`HH:MM[:SS]`, defaults to now)    |
| `--seed`       | int  | Random seed for reproducible results        |

👉 CLI parameters override config file values.

#### GUI

```bash
python KeepSultanGUI.py
```

---

## 4. Credits & Related Projects

Special thanks to [eltsen00](https://github.com/eltsen00) for developing the web version [KeepGeneration-Web](https://github.com/eltsen00/KeepGeneration-Web).
Try it online 👉 [https://keep.hshoe.cn/](https://keep.hshoe.cn/)

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

