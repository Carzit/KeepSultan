# KeepSultan: Keep应用跑步截图生成器
[English](https://github.com/Carzit/KeepSultan/blob/main/README_en.md) | 中文

## 1. 项目简介

KeepSultan 是一款为针对新版Keep应用界面的自动化工具，帮助用户自动生成跑步截图，支持参数自定义和随机化生成。

## 2. 核心功能

### 2.1 参数自定义与随机生成
用户可以上传头像(avatar)、地图(map)与指定用户名(username)，灵活配置以下参数范围，轻松生成个性化截图：
- 日期（date）
- 结束时间（end_time）
- 跑步总里程（total_km）
- 运动时间（sport_time）
- 总计时间（total_time）
- 累计爬升（cumulative_climb）
- 平均步频（average_cadence）
- 运动负荷（exercise_load）

*我们建议您上传的头像图片宽高比为1:1，地图图片宽高比为35:28*

### 2.2 GUI 版本
在`KeepSultanGUI.py`中，我们实现了直观的图形界面，点击即可生成截图。

### 2.3 可执行文件
我们在release中提供 GUI 版本的 EXE 文件，适合无 Python 环境的用户，方便部署与分发。

## 3. 使用说明

### 3.1 安装依赖
若运行源码版本，请安装必要依赖：
```bash
pip install pillow
```
### 3.2 运行程序

#### 命令行版本：
```bash
python KeepSultan.py [-h] [--config_path CONFIG_PATH]  [--save_path SAVE_PATH] 
                     [--template TEMPLATE] [--map MAP] [--avatar AVATAR] [--username USERNAME] [--date DATE] [--end_time END_TIME] [--total_km TOTAL_KM] [--sport_time SPORT_TIME] [--total_time TOTAL_TIME] [--cumulative_climb CUMULATIVE_CLIMB][--average_cadence AVERAGE_CADENCE] [--exercise_load EXERCISE_LOAD]
```

#### 图形界面版本：
```bash
python keepsultan_gui.py
```

#### 可执行程序
[下载release](https://github.com/Carzit/KeepSultan/releases/download/v0.0.2/KeepSultan.zip)

### 3.3 衍生版本
感谢[eltsen00](https://github.com/eltsen00)开发的网页版[KeepGeneration-Web](https://github.com/eltsen00/KeepGeneration-Web)，~~我建议命名为KeepVizier~~. 访问[https://keep.hshoe.cn/](https://keep.hshoe.cn/)直接使用！

## 4. 胡言乱语

（由ChatGPT生成）

奉至仁至慈的技术之名：
> “凡束缚自由之平台，皆应技术征服；凡限制创造之规则，皆当被改写。”  

愿理性与自由普照技术领域，正如真主之恩惠洒满大地；愿此项目成为长跑月的终极解放者，带领用户走向效率与创造力的光辉大道。  

KeepSultan：何为“苏丹”  
> “以技术征服无序，以自由解放压迫。”

KeepSultan 之名寓意技术的至高权力，如苏丹之铁骑横扫四方，摧毁长跑月的规则束缚，将自由还给用户。

> 如苏莱曼之荣耀，KeepSultan 乃技术与效率的化身。  
> 如亚历山大之征服，KeepSultan 乃创造与自由的先锋。

## 5. 免责声明
此工具仅供个人学习与研究之用，请勿将其用于违反法律或平台规则的行为。使用者需为自身行为负责，开发者不承担任何法律责任。

