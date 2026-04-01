#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: map.py
About: 生成Keep风格运动轨迹图
Author: LynxFrost

该模块提供了生成类似Keep应用的运动轨迹图的功能，可以被其他Python文件引用。
主要功能包括路径提取、平滑处理、图标添加等。
"""

import cv2
import numpy as np
import random
import logging
from PIL import Image
import os

# 尝试导入KDTree，如果没有则使用备用方案
try:
    from scipy.spatial import KDTree
    USE_KDTREE = True
except ImportError:
    USE_KDTREE = False
    logging.warning("scipy未安装，将使用普通算法。安装scipy可提高性能: pip install scipy")

# 预加载图标缓存
START_ICON = None
END_ICON = None

def load_icons():
    """预加载图标，避免重复读取
    
    尝试从src目录加载start.png和end.png作为轨迹的起点和终点图标
    如果加载失败，后续会使用圆点标记作为备选
    """
    global START_ICON, END_ICON
    try:
        # 获取脚本所在目录的路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        start_icon_path = os.path.join(script_dir, "src", "start.png")
        end_icon_path = os.path.join(script_dir, "src", "end.png")
        
        # 使用绝对路径并确保路径正确
        START_ICON = cv2.imread(os.path.normpath(start_icon_path), cv2.IMREAD_UNCHANGED)
        END_ICON = cv2.imread(os.path.normpath(end_icon_path), cv2.IMREAD_UNCHANGED)
        
        # 如果cv2.imread返回None，尝试使用PIL读取后转换为cv2格式
        from PIL import Image
        import numpy as np
        
        # 处理起点图标
        if START_ICON is None:
            # 使用PIL读取图片
            pil_image = Image.open(start_icon_path)
            # 转换为numpy数组
            if pil_image.mode == 'RGBA':
                # 如果图片有alpha通道
                bgr = np.array(pil_image)[:, :, :3][:, :, ::-1]  # RGB转BGR
                alpha = np.array(pil_image)[:, :, 3]
                # 合并为BGRA
                START_ICON = np.dstack((bgr, alpha))
            else:
                # 没有alpha通道
                START_ICON = np.array(pil_image)[:, :, ::-1]  # RGB转BGR
        
        # 处理终点图标
        if END_ICON is None:
            # 使用PIL读取图片
            pil_image = Image.open(end_icon_path)
            # 转换为numpy数组
            if pil_image.mode == 'RGBA':
                # 如果图片有alpha通道
                bgr = np.array(pil_image)[:, :, :3][:, :, ::-1]  # RGB转BGR
                alpha = np.array(pil_image)[:, :, 3]
                # 合并为BGRA
                END_ICON = np.dstack((bgr, alpha))
            else:
                # 没有alpha通道
                END_ICON = np.array(pil_image)[:, :, ::-1]  # RGB转BGR
    except Exception as e:
        # 静默失败，后续会使用圆点标记作为备选
        logging.warning(f"Failed to load icons: {e}")
        pass

# 初始化图标缓存
load_icons()

def smooth_path(points, window_size=5):
    """使用滑动窗口平均法平滑路径
    
    Args:
        points: 原始路径点列表，每个点为(x, y)元组
        window_size: 滑动窗口大小，值越大路径越平滑，但可能会丢失细节
        
    Returns:
        平滑后的路径点列表
    """
    if len(points) < window_size:
        return points
    
    smoothed = []
    for i in range(len(points)):
        start = max(0, i - window_size // 2)
        end = min(len(points), i + window_size // 2 + 1)
        window = points[start:end]
        
        # 计算窗口内的平均坐标
        avg_x = sum(p[0] for p in window) / len(window)
        avg_y = sum(p[1] for p in window) / len(window)
        
        smoothed.append((int(avg_x), int(avg_y)))
    
    return smoothed


def generate_keep_style_path(
    bg_path: str,
    path_mask_path: str,
    track_color=(154, 201, 38),  # 26c99a的BGR格式
    thickness=12,
    sample_rate=2,  # 路径点采样率，值越大速度越快，精度越低
    max_steps=5000,  # 最大步数限制
    completion_threshold=0.9,  # 路径完成度阈值，达到后提前结束
    target_length=None  # 目标路径长度，None表示不限制
):
    """生成Keep风格的运动轨迹图
    
    Args:
        bg_path: 背景图片路径
        path_mask_path: 路径掩码图片路径（包含路径信息的图片）
        track_color: 轨迹颜色，BGR格式，默认为(154, 201, 38)（对应26c99a）
        thickness: 轨迹线条厚度，默认为12
        sample_rate: 路径点采样率，值越大处理的点数越少，速度越快，精度越低
        max_steps: 最大步数限制，防止路径太长
        completion_threshold: 路径完成度阈值，达到后提前结束
        target_length: 目标路径长度，None表示不限制，否则会截取或填充到该长度
        
    Returns:
        PIL.Image对象：生成的轨迹图
        
    Raises:
        Exception: 当图片读取失败或未检测到路径时抛出
    """
    # 1. 读取背景 + 路径图
    # 获取脚本所在目录的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试直接读取路径
    bg = cv2.imread(bg_path)
    mask = cv2.imread(path_mask_path)
    
    # 如果读取失败，尝试将路径解析为相对于脚本所在目录的路径
    if bg is None:
        bg_path = os.path.join(script_dir, bg_path)
        bg = cv2.imread(bg_path)
    
    if mask is None:
        path_mask_path = os.path.join(script_dir, path_mask_path)
        mask = cv2.imread(path_mask_path)
    
    if bg is None or mask is None:
        raise Exception("图片读取失败")

    h, w = bg.shape[:2]

    # 2. 提取路径上所有点
    gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # 使用形态学操作减少噪点
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # 开运算去噪
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)  # 闭运算填充
    
    # 提取路径点
    ys, xs = np.where(binary < 128)  # 假设路径是深色
    if len(xs) == 0:
        ys, xs = np.where(binary > 128)
    
    # 路径点下采样，减少计算量
    points = list(zip(xs[::sample_rate], ys[::sample_rate]))
    if not points:
        raise Exception("未检测到路径")
    
    # 根据点数量动态调整参数
    point_count = len(points)
    if point_count > 10000:
        # 点数量过多，进一步降采样
        additional_sample = 2
        points = points[::additional_sample]

    # 3. 随机起点
    current = random.choice(points)
    visited = set()
    path = [current]
    visited.add(current)
    
    # 4. 准备邻点查找数据结构
    if USE_KDTREE:
        points_array = np.array(points)
        kdtree = KDTree(points_array)

    # 4. 贪心走完整路径（仿Keep连续轨迹）
    step_range = 8  # 减少步长范围，生成更紧凑的路径
    direction_bias = 0.7  # 方向偏好权重，值越高路径越连贯
    
    # 动态调整最大步数和完成度阈值
    if len(points) > 5000:
        adjusted_max_steps = max_steps  # 允许处理更多步数
        adjusted_threshold = completion_threshold  # 不再限制最大完成度阈值
    else:
        adjusted_max_steps = max_steps
        adjusted_threshold = completion_threshold
    
    # 初始方向（无方向）
    prev_dx, prev_dy = 0, 0
    
    for step in range(adjusted_max_steps):
        x0, y0 = current
        nearby = []
        
        if USE_KDTREE:
            # 使用KD树快速查找邻点
            indices = kdtree.query_ball_point(current, step_range)
            nearby = [tuple(points_array[i]) for i in indices if tuple(points_array[i]) not in visited]
        else:
            # 普通算法（备用方案）- 提前过滤部分点
            nearby = [(x, y) for (x, y) in points 
                     if (x, y) not in visited 
                     and abs(x - x0) <= step_range 
                     and abs(y - y0) <= step_range]
        
        if not nearby:
            # 如果没有邻点，尝试扩大搜索范围
            extended_range = step_range * 2
            if USE_KDTREE:
                indices = kdtree.query_ball_point(current, extended_range)
                extended_nearby = [tuple(points_array[i]) for i in indices if tuple(points_array[i]) not in visited]
            else:
                extended_nearby = [(x, y) for (x, y) in points 
                                 if (x, y) not in visited 
                                 and abs(x - x0) <= extended_range 
                                 and abs(y - y0) <= extended_range]
            
            if not extended_nearby:
                break
            nearby = extended_nearby
        
        # 检查路径完成度，达到阈值后提前结束
        if len(visited) / len(points) >= adjusted_threshold:
            break
            
        # 选择邻点时增加方向偏好，保持路径连贯
        if len(nearby) > 1 and (prev_dx != 0 or prev_dy != 0):
            # 计算当前方向向量
            dir_vector = np.array([prev_dx, prev_dy])
            dir_vector = dir_vector / (np.linalg.norm(dir_vector) + 1e-6)  # 归一化
            
            # 计算每个邻点的方向得分
            best_point = nearby[0]
            best_score = -1
            
            for point in nearby:
                dx = point[0] - x0
                dy = point[1] - y0
                point_vector = np.array([dx, dy])
                point_vector = point_vector / (np.linalg.norm(point_vector) + 1e-6)  # 归一化
                
                # 计算方向一致性得分
                direction_score = np.dot(dir_vector, point_vector)
                
                # 添加距离惩罚，避免路径过长
                distance = np.sqrt(dx*dx + dy*dy)
                distance_penalty = 1 / (distance + 1)
                
                # 综合得分
                total_score = direction_bias * direction_score + (1 - direction_bias) * distance_penalty
                
                if total_score > best_score:
                    best_score = total_score
                    best_point = point
            
            nxt = best_point
        else:
            # 随机选择
            nxt = random.choice(nearby)
        
        # 更新方向
        prev_dx = nxt[0] - x0
        prev_dy = nxt[1] - y0
        
        path.append(nxt)
        visited.add(nxt)
        current = nxt
    
    # 应用路径平滑
    path = smooth_path(path, window_size=5)
    
    # 路径后处理：根据目标长度调整路径
    if target_length is not None:
        if len(path) > target_length:
            # 截取到目标长度
            path = path[:target_length]
        elif len(path) < target_length:
            # 如果路径太短，复制最后一个点填充到目标长度
            last_point = path[-1] if path else (0, 0)
            path.extend([last_point] * (target_length - len(path)))

    # 5. 在背景上画出 Keep 风格轨迹
    out = bg.copy()
    # 圆润线条
    cv2.polylines(out, [np.array(path, np.int32)], False, track_color, thickness, cv2.LINE_AA)
    
    # 添加起始和结束图标
    try:
        # 使用预加载的图标
        start_icon = START_ICON
        end_icon = END_ICON
        
        # 计算图标大小
        icon_size = (thickness * 5, thickness * 5)  # 根据线条厚度动态调整图标大小
        
        # 绘制起点图标
        if start_icon is not None:
            # 调整图标大小
            resized_start = cv2.resize(start_icon, icon_size)
            
            # 获取起点坐标
            sx, sy = path[0]
            # 计算图标绘制位置（使图标中心对齐起点）
            icon_h, icon_w = resized_start.shape[:2]
            start_x = sx - icon_w // 2
            start_y = sy - icon_h // 2
            
            # 确保图标不会超出图片边界
            if 0 <= start_x and 0 <= start_y and start_x + icon_w <= out.shape[1] and start_y + icon_h <= out.shape[0]:
                # 如果图标有alpha通道，使用透明叠加
                if resized_start.shape[2] == 4:
                    alpha = resized_start[:, :, 3] / 255.0
                    bgr = resized_start[:, :, :3]
                    # 使用向量化操作提高效率
                    out[start_y:start_y+icon_h, start_x:start_x+icon_w] = (alpha[..., np.newaxis] * bgr + 
                                                                         (1 - alpha)[..., np.newaxis] * out[start_y:start_y+icon_h, start_x:start_x+icon_w]).astype(np.uint8)
                else:
                    # 没有alpha通道，直接绘制
                    out[start_y:start_y+icon_h, start_x:start_x+icon_w] = resized_start[:, :, :3]
            else:
                # 图标超出边界时，使用圆形标记作为备用
                sx, sy = path[0]
                cv2.circle(out, (sx, sy), thickness + 2, track_color, -1)
        else:
            # 图标加载失败（start_icon为None），使用圆形标记作为备用
            sx, sy = path[0]
            cv2.circle(out, (sx, sy), thickness + 2, track_color, -1)
        
        # 绘制终点图标
        if end_icon is not None:
            # 调整图标大小
            resized_end = cv2.resize(end_icon, icon_size)
            
            # 获取终点坐标
            ex, ey = path[-1]
            # 计算图标绘制位置（使图标中心对齐终点）
            icon_h, icon_w = resized_end.shape[:2]
            end_x = ex - icon_w // 2
            end_y = ey - icon_h // 2
            
            # 确保图标不会超出图片边界
            if 0 <= end_x and 0 <= end_y and end_x + icon_w <= out.shape[1] and end_y + icon_h <= out.shape[0]:
                # 如果图标有alpha通道，使用透明叠加
                if resized_end.shape[2] == 4:
                    alpha = resized_end[:, :, 3] / 255.0
                    bgr = resized_end[:, :, :3]
                    # 使用向量化操作提高效率
                    out[end_y:end_y+icon_h, end_x:end_x+icon_w] = (alpha[..., np.newaxis] * bgr + 
                                                                   (1 - alpha)[..., np.newaxis] * out[end_y:end_y+icon_h, end_x:end_x+icon_w]).astype(np.uint8)
                else:
                    # 没有alpha通道，直接绘制
                    out[end_y:end_y+icon_h, end_x:end_x+icon_w] = resized_end[:, :, :3]
            else:
                # 图标超出边界时，使用圆形标记作为备用
                ex, ey = path[-1]
                cv2.circle(out, (ex, ey), thickness + 2, track_color, -1)
        else:
            # 图标加载失败（end_icon为None），使用圆形标记作为备用
            ex, ey = path[-1]
            cv2.circle(out, (ex, ey), thickness + 2, track_color, -1)
    except Exception:
        # 如果图标绘制失败，回退到原来的圆点标记
        # 起点圆点
        if path:
            sx, sy = path[0]
            cv2.circle(out, (sx, sy), thickness + 2, track_color, -1)
            # 终点圆点
            ex, ey = path[-1]
            cv2.circle(out, (ex, ey), thickness + 2, track_color, -1)

    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

# ------------------- 模块使用示例 -------------------
if __name__ == '__main__':
    """当直接运行此脚本时的示例用法"""
    # 生成路径长度限制在400以内的轨迹图
    img = generate_keep_style_path(
        bg_path="src/map1.png",
        path_mask_path="src/map2.png",
        sample_rate=5,  # 大幅提高采样率，显著减少处理点数
        max_steps=3000,  # 大幅减少最大步数
        completion_threshold=0.2,  # 大幅降低完成度阈值，提前结束生成
        target_length=400  # 限制路径长度在400以内
    )
    img.save("keep_style_path.png")
    print("轨迹图生成完成！")


# ------------------- 模块导出 -------------------
# 定义模块导出的内容
__all__ = [
    'generate_keep_style_path',  # 主要功能函数
    'smooth_path',  # 路径平滑函数
    'load_icons'  # 图标加载函数
]