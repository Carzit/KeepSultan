# KeepSultan: Keep App Running Screenshot Generator
English | [中文](https://github.com/Carzit/KeepSultan/blob/main/README.md)

## 1. Project Overview

KeepSultan is an automation tool tailored for the latest version of the Keep app interface, designed to help users automatically generate running screenshots. It supports customizable parameters and random generation.

## 2. Core Features

### 2.1 Customizable Parameters & Random Generation
Users can upload their avatar, map and specify a username, flexibly configure the following parameter ranges, and easily generate personalized screenshots:
- Date (date)
- End Time (end_time)
- Total Distance Run (total_km)
- Exercise Duration (sport_time)
- Total Time (total_time)
- Cumulative Elevation Gain (cumulative_climb)
- Average Cadence (average_cadence)
- Exercise Load (exercise_load)

### 2.2 GUI Version
We have implemented an intuitive graphical user interface with `KeepSultanGUI.py`, allowing users to generate screenshots with just a few clicks.

### 2.3 Executable File
An EXE file for the GUI version is provided, suitable for users without a Python environment, making deployment and distribution more convenient.

## 3. Usage Instructions

### 3.1 Install Dependencies
If running the source code version, please install necessary dependencies:
```bash
pip install pillow
```
### 3.2 Running the Program

#### Command Line Version:
```bash
python KeepSultan.py [-h] [--config_path CONFIG_PATH]  [--save_path SAVE_PATH] 
                     [--template TEMPLATE] [--map MAP] [--avatar AVATAR] [--username USERNAME] [--date DATE] [--end_time END_TIME] [--total_km TOTAL_KM] [--sport_time SPORT_TIME] [--total_time TOTAL_TIME] [--cumulative_climb CUMULATIVE_CLIMB][--average_cadence AVERAGE_CADENCE] [--exercise_load EXERCISE_LOAD]
```

#### Graphical Interface Version:
```bash
python KeepSultanGUI.py
```

#### Executable Program
[Download Release](https://github.com/Carzit/KeepSultan/releases/download/v0.0.2/KeepSultan.zip).

### 3.3 Derivative Versions
Thanks to [eltsen00](https://github.com/eltsen00) for developing the web version [KeepGeneration-Web](https://github.com/eltsen00/KeepGeneration-Web),~~I suggest naming it KeepVizier~~. Visit [https://keep.hshoe.cn/](https://keep.hshoe.cn/) to use it directly!

## 4. Loose Talk
In the name of the Most Gracious and Merciful Technology:
> "Any platform that binds freedom should be conquered by technology; any rule that limits creativity should be rewritten."

May reason and freedom illuminate the realm of technology, just as the grace of God showers upon the earth; may this project become the ultimate liberator of the Long Running Month, leading users onto the bright path of efficiency and creativity.

What is "Sultan" in KeepSultan?
> "To conquer disorder with technology, to liberate oppression with freedom."

The name KeepSultan symbolizes the supreme power of technology, like the iron cavalry of a Sultan sweeping across all fronts, breaking the shackles of rules during the Long Running Month, and returning freedom to users.

> Like the glory of Solomon, KeepSultan is the embodiment of technology and efficiency.  
> Like the conquests of Alexander, KeepSultan is the vanguard of creation and freedom.

## 5. Disclaimer
This tool is intended solely for personal learning and research purposes. Please do not use it for actions that violate laws or platform rules. Users are responsible for their own actions, and the developers bear no legal responsibility.