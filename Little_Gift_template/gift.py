#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎁 名称 - 给xx的礼物

版本: 1.0.0
作者: 翊如年少
创建日期: 2026年2月
使用方法：
只有这一个代码文件
可以全局搜索TODO
并按照对应提示修改

版权声明：
本程序为个人开发程序，仅用于交流分享，帮助大家完成自己的礼物
禁止转载！禁止商用！
灵感来源：小红书博主【耶-】，账号【4288230623】
代码及文档编写、功能补充：本人【翊如年少】，账号【908975006】
代码参考：DeepSeek
图片参考：豆包

"""

# 软件封装语言参考如下：
# 注：我加入了软件图标，即.ico文件，请自行添加图标或删除图标封装语句，封装后可运行../dish/gift/gift.exe
# pyinstaller --onedir --windowed --name="gift" --icon=bg.ico --add-data "character.png;." --add-data "eye_left.png;." --add-data "eye_right.png;." --hidden-import=PyQt6 --hidden-import=PyQt6.sip gift.py
# 注：该封装语句仅适用于windows系统，IOS系统请自行封装

import sys
import random
from datetime import datetime, date
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QGraphicsOpacityEffect, QMenu)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import (Qt, QTimer, QPoint, QRect, QPropertyAnimation,
                          QEasingCurve, pyqtProperty, QParallelAnimationGroup, pyqtSlot)
from PyQt6.QtGui import (QPixmap, QPainter, QBitmap, QCursor, QFont,
                         QPainterPath, QPen, QBrush, QColor, QLinearGradient)


class Eye(QLabel):
    """眼睛控件"""
    def __init__(self, parent=None, is_left=True):
        super().__init__(parent)
        self.is_left = is_left
        self.original_pos = QPoint(0, 0)
        self.current_pos = QPoint(0, 0)
        self.max_move = 5
        self.setFixedSize(40, 40)

    def set_eye_image(self, pixmap_path):
        """设置眼睛图片"""
        pixmap = QPixmap(pixmap_path)
        self.setPixmap(pixmap.scaled(self.size(),
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))

    def track_mouse(self, mouse_pos):
        """追踪鼠标位置"""
        eye_center = self.parent().mapToGlobal(self.original_pos)
        dx = mouse_pos.x() - eye_center.x()
        dy = mouse_pos.y() - eye_center.y()
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        scale = min(self.max_move / distance, 1)
        new_x = self.original_pos.x() + dx * scale
        new_y = self.original_pos.y() + dy * scale
        self.current_pos = QPoint(int(new_x), int(new_y))
        self.move(self.current_pos)


class SpeechBubble(QLabel):
    """对话气泡控件（带淡入淡出动画）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 182, 193, 220);
                border-radius: 15px;
                padding: 2px 8px;
                border: 2px solid #ff91a4;
                color: #5a3a3a;
                font-size: 13px;
                font-weight: bold;
            }
        """)  # 这里可以修改弹窗气泡的格式

        font = QFont("Microsoft YaHei", 11)
        font.setBold(True)
        self.setFont(font)

        self.setAutoFillBackground(False)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # 淡入淡出动画
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(400)  # 淡入时长
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(0.95)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(500)  # 淡出时长
        self.fade_out_anim.setStartValue(0.95)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_anim.finished.connect(self.on_fade_out_finished)

        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)

        # 标记是否正在显示
        self.is_showing = False
        # 记录当前显示位置相对于窗口的偏移量
        self.offset_from_parent = QPoint(0, 0)

    def show_bubble(self, text, duration=3000):
        """显示气泡 - 带淡入动画"""
        # 停止所有动画和定时器
        self.fade_in_anim.stop()
        self.fade_out_anim.stop()
        self.hide_timer.stop()

        self.is_showing = True
        self.setText(text)
        self.adjustSize()

        # 计算气泡位置
        parent_pos = self.parent().pos()
        parent_width = self.parent().width()

        # 气泡水平居中
        bubble_x = parent_pos.x() + parent_width // 2 - self.width() // 2

        self.offset_from_parent = QPoint(
            parent_width // 2 - self.width() // 2,  # 水平居中偏移
            - parent_width // 4  # 从窗口底部向上的偏移
        )

        final_y = parent_pos.y() + self.parent().height() + self.offset_from_parent.y()

        # 最终位置
        self.move(bubble_x, final_y)

        # 确保气泡显示在最顶层
        self.raise_()

        # 强制更新样式
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

        # 显示气泡
        self.show()

        # 开始淡入动画
        self.fade_in_anim.start()

        # 设置隐藏定时器（淡入完成后开始计时）
        QTimer.singleShot(300, lambda: self.hide_timer.start(duration))

    def start_fade_out(self):
        """开始淡出动画"""
        if not self.is_showing:
            return

        self.hide_timer.stop()
        self.fade_out_anim.start()

    def on_fade_out_finished(self):
        """淡出动画完成后的处理"""
        self.is_showing = False
        self.hide()

    def update_position(self, parent_pos):
        """更新气泡位置（跟随窗口移动）"""
        if self.is_showing:
            # 根据窗口位置和偏移量计算气泡新位置
            new_x = parent_pos.x() + self.offset_from_parent.x()
            new_y = parent_pos.y() + self.parent().height() + self.offset_from_parent.y()
            self.move(new_x, new_y)

            # 强制重绘以确保背景正确显示
            self.update()

    def paintEvent(self, event):
        """重绘事件，确保背景正确绘制"""
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_opacity = self.opacity_effect.opacity()
        alpha = int(180 * current_opacity)  # 根据透明度调整alpha值

        painter.setBrush(QBrush(QColor(255, 192, 203, alpha)))  # 根据透明度调整
        painter.setPen(QPen(QColor(255, 145, 164, alpha), 2))  # 根据透明度调整
        painter.drawPath(path)

        # 绘制文字（透明度随气泡变化）
        painter.setPen(QPen(QColor(90, 58, 58, int(255 * current_opacity))))  # 根据透明度调整
        painter.setFont(self.font())

        # 文字位置
        text_rect = self.rect().adjusted(0, 0, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def cleanup_timers(self):
        """清理定时器和动画"""
        self.hide_timer.stop()
        self.fade_in_anim.stop()
        self.fade_out_anim.stop()


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # ============ 配置文件区域 ============
        # 获取屏幕尺寸来智能调整
        app = QApplication.instance() or QApplication([])
        screen = app.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # 计算合适的大小（根据屏幕大小自动调整）
        target_width = screen_width // 11
        target_height = int(target_width * 1.4)  # 保持长宽比

        self.config = {
            # 窗口设置
            'target_size': (target_width, target_height),  # 自动计算的大小

            # 眼睛设置
            # TODO：这里要根据实际的眼睛图片调整大小
            'eye_size': target_width // 9,  # 根据窗口大小自动调整
            'max_move': max(4, target_width // 80),

            # 眼睛位置配置 - 使用百分比，程序会自动计算实际位置
            # 这些是相对于窗口宽高的百分比位置（0.0到1.0之间）
            # TODO：这里要根据实际的图片和眼睛调整位置
            'left_eye_percent': (0.375, 0.54),  # 左眼位置：35%宽度，35%高度
            'right_eye_percent': (0.625, 0.525),  # 右眼位置：65%宽度，35%高度

            # ============ 白色背景设置 ============
            # 白色背景的配置（相对于窗口的百分比）
            # 有两种模式：'auto' 自动计算 或 'manual' 手动配置

            'white_bg_mode': 'auto',  # 'auto' 或 'manual'

            # 自动模式参数（当 white_bg_mode 为 'auto' 时使用）
            'white_bg_padding': 0.05,  # 白色背景比眼睛区域大多少（百分比）

            # 手动模式参数（当 white_bg_mode 为 'manual' 时使用）
            # 格式：(左上角x百分比, 左上角y百分比, 宽度百分比, 高度百分比)、
            # TODO：这里要根据实际的图片和眼睛调整眼睛后面的白色背景的位置
            'white_bg_rect': (0.3, 0.4, 0.4, 0.3),  # 默认覆盖眼睛区域

            # 白色背景颜色（RGBA）
            'white_bg_color': (255, 255, 255, 255),  # 完全不透明的白色
            # ====================================

            # 图片路径
            # TODO：建议把三个图片放在同一目录下，这里的位置就可以直接用
            # TODO：这里要把要用的图片名称和引用名称对应哦
            'character_img': 'character.png',
            'left_eye_img': 'eye_left.png',
            'right_eye_img': 'eye_right.png',

            # 窗口初始位置
            'initial_position': (screen_width - 190, screen_height - 245),  # 手动设置窗口位置

            # 眼睛追踪灵敏度
            'track_interval': 100,

            # 气泡设置
            # TODO：这里可以更改气泡设置
            'bubble_duration': 3000,  # 气泡显示时间（毫秒）- 3秒
            'bubble_fade_duration': 300,  # 淡入淡出动画持续时间（毫秒）
            'bubble_probability': 0.95,  # 显示普通消息的概率（0.0-1.0）
            'min_message_interval': 60000,  # 最小间隔1分钟
            'max_message_interval': 1200000,  # 最大间隔20分钟

            # ============ 互动区域配置 ============
            # 身体各部位的位置（相对于窗口的百分比）
            # TODO：这里要根据实际的图片调整
            'ear_area': (0.15, 0.05, 0.58, 0.22),  # 左耳朵区域 (x, y, width, height)
            'head_area': (0.20, 0.30, 0.60, 0.16),  # 头部区域
            'face_area': (0.27, 0.47, 0.4, 0.15),  # 面部区域（不包括眼睛）
            'body_area': (0.25, 0.7, 0.63, 0.25),  # 身体区域

            # ============ 特殊日期配置 ============
            # TODO：这里可以填入【希望显示的特殊日期】（生日、纪念日等），同格式添加即可
            'special_dates': {
                (2, 14): "💝 情人节快乐！",
                (12, 25): "🎄 圣诞快乐！",
                (1, 1): "🎉 新年快乐！",
                (5, 20): "💖 520快乐~",
                (6, 1): "🎈 儿童节快乐！"
            }
        }

        print(f"屏幕尺寸: {screen_width} x {screen_height}")
        print(f"目标窗口尺寸: {target_width} x {target_height}")
        print(f"眼睛大小: {self.config['eye_size']}")

        # ============ 原始消息库 ============
        # TODO：这里是会显示在弹窗气泡中的内容，加入自己想说的话哟~
        self.original_messages = [
            "今天按时吃饭了嘛",
            "多喝水～吨吨吨~",
            "(・ω・)",
            "功德+1",
            "❤️心情+99999999",
            "今日快乐",
            "今天也请幸福",
            "很高兴遇见你",
            "早上好中午好晚上好午夜好"
        ]

        # 消息库 - 按时间分类
        # TODO：这里是【特殊时间段】会显示在弹窗气泡中的内容，加入自己想说的话哟~
        self.messages_by_time = {
            'morning': [  # 6:00-11:00
                           "早上好呀~今天请开心！",
                           "记得吃早饭哟！",
                           "早早早~你为什么背着小书包~"
                       ] + self.original_messages,  # 添加原始消息

            'noon': [  # 11:00-14:00
                        "午饭时间到！我吃吃吃！",
                        "吃饱了有点困困的...",
                        "活力满满的一天从中午开始！"
                    ] + self.original_messages,  # 添加原始消息

            'afternoon': [  # 14:00-18:00
                             "好困好困qwq我睡大觉~",
                             "下午真好~出去玩出去玩~"
                         ] + self.original_messages,  # 添加原始消息

            'evening': [  # 18:00-24:00
                           "晚上好！今天辛苦啦！"
                       ] + self.original_messages,  # 添加原始消息

            'night': [  # 0:00-6:00
                         "夜宵时间到！吃吃吃！",
                         "晚安，今天请做个好梦"
                     ] + self.original_messages  # 添加原始消息
        }

        # 互动反馈消息
        # TODO：这里是【单击指定部位】会显示在弹窗气泡中的内容，加入自己想说的话哟~
        # TODO：这里和前面的分区身体部位的分区是对应的，可以根据分区来写，分区数量根据需要删改哟
        self.interaction_messages = {
            'ear': [
                "啊！耳朵！",
                "小白兔白又白~",
                "两只耳朵竖起来~",
                "爱吃萝卜爱吃菜~",
                "蹦蹦跳跳真可爱~",
                "小兔子的耳朵不可以摸！"
            ],
            'head': [
                "呜呜~发型qwq",
                "耶！被摸摸头了！",
                "摸头会变聪明吗？"
            ],
            'face': [
                "摸我干嘛qwq",
                "(〃∇〃)"
            ],
            'body': [
                "抱紧紧",
                "抱住~",
                "要抱抱！"
            ]
        }

        # 拖拽反馈消息（每次拖动都显示）
        # TODO：这里是【拖动角色】会显示在弹窗气泡中的内容，加入自己想说的话哟~
        self.drag_messages = [
            "诶？要去哪里呀？",
            "慢一点啦！",
            "飞起来啦！",
            "等等我呀！",
            "wiiii~",
            "晕晕的~",
            "把我放在这里就好啦"
        ]

        # ============ 新增：状态变量 ============
        self.drag_count = 0  # 拖拽计数
        self.last_drag_time = None  # 上次拖拽时间
        self.has_shown_night_message = False  # 是否已显示过夜间消息
        self.has_shown_welcome = False  # 是否已显示欢迎消息
        self.last_time_category = None  # 上次时间类别

        # ============ 新增：鼠标事件状态标志 ============
        self.is_dragging = False  # 是否正在拖动
        self.mouse_press_pos = None  # 鼠标按下时的位置
        self.drag_threshold = 10  # 拖动阈值（像素），超过这个距离才认为是拖动而不是点击
        self.drag_pos = None  # 拖动的起始位置
        self.pre_drag_pos = None  # 拖动前的位置

        # ============ 新增：双击事件处理 ============
        self.double_click_timer = QTimer()
        self.double_click_timer.setSingleShot(True)
        self.double_click_timer.setInterval(200)  # 200ms内认为是双击
        self.double_click_timer.timeout.connect(self.on_single_click_timeout)
        self.click_count = 0  # 点击计数
        self.last_click_time = None  # 上次点击时间
        self.pending_click_pos = None  # 待处理的点击位置

        self.init_ui()
        self.setup_timers()

        # ============ 新增：初始化时显示欢迎消息 ============
        self.show_welcome_message()

    def get_time_category(self, hour=None):
        """获取时间类别"""
        if hour is None:
            hour = datetime.now().hour

        if 6 <= hour < 11:
            return 'morning'
        elif 11 <= hour < 14:
            return 'noon'
        elif 14 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 24:
            return 'evening'
        else:  # 0-6点
            return 'night'

    def check_time_change(self):
        """检查时间变化，进入新时间段时显示消息"""
        current_hour = datetime.now().hour
        current_time_category = self.get_time_category(current_hour)

        # 检查是否是第一次检查或者时间类别变化了
        if self.last_time_category is None:
            self.last_time_category = current_time_category
            return

        if current_time_category != self.last_time_category:
            print(f"时间类别变化: {self.last_time_category} -> {current_time_category}")

            # 根据新时间段显示对应的问候消息
            # TODO：这里是【更新时间段时】会显示在弹窗气泡中的内容，加入自己想说的话哟~
            time_greetings = {
                'morning': [
                    "早上好呀~今天请开心！",
                    "记得吃早饭哟！",
                    "早早早~你为什么背着小书包~"
                ],
                'noon': [
                    "午饭时间到！我吃吃吃！",
                     "吃饱了有点困困的...",
                    "活力满满的一天从中午开始！"
                ],
                'afternoon': [
                    "好困好困qwq我睡大觉~"
                ],
                'evening': [
                    "晚上好！今天辛苦啦！",
                    "按时吃晚饭哟"
                ],
                'night': [
                    "夜宵时间到！吃吃吃！",
                    "梦里见~呼呼~",
                    "Zzz~",
                    "晚安，今天请做个好梦"
                ]
            }

            # 从时间段专属问候和整个消息库中随机选择
            if random.random() < 0.8:  # 80%概率显示时间段专属问候
                message = random.choice(time_greetings[current_time_category])
            else:  # 20%概率显示普通消息
                message = random.choice(self.messages_by_time[current_time_category])

            self.speech_bubble.show_bubble(message, 4000)

            # 更新上次的时间类别
            self.last_time_category = current_time_category

    def show_welcome_message(self):
        """显示欢迎消息（只在第一次启动时显示）"""
        if not self.has_shown_welcome:
            current_time_category = self.get_time_category()

            # 初始设置时间类别
            self.last_time_category = current_time_category

            # 欢迎消息使用时间段专属问候
            # TODO：这里是【启动时】会显示在弹窗气泡中的内容，加入自己想说的话哟~
            welcome_messages = {
                'morning': "早上好~",
                'noon': "午觉时间到~呼呼~zzz~",
                'afternoon': "下午好！",
                'evening': "晚上好！",
                'night': "不要熬夜！"
            }

            message = welcome_messages.get(current_time_category, "我来啦！")

            # 稍微延迟一下显示，让窗口完全加载
            QTimer.singleShot(1000, lambda: self.speech_bubble.show_bubble(message, 4000))
            self.has_shown_welcome = True

    def calculate_white_background_rect(self, window_width, window_height):
        """计算白色背景的矩形区域"""
        mode = self.config['white_bg_mode']

        if mode == 'auto':
            # 自动模式：根据眼睛位置和大小计算
            eye_size = self.config['eye_size']

            # 获取眼睛位置
            left_percent_x, left_percent_y = self.config['left_eye_percent']
            right_percent_x, right_percent_y = self.config['right_eye_percent']

            # 计算眼睛的实际像素位置
            left_eye_x = window_width * left_percent_x
            left_eye_y = window_height * left_percent_y
            right_eye_x = window_width * right_percent_x
            right_eye_y = window_height * right_percent_y

            # 计算包含两只眼睛的边界框
            min_x = min(left_eye_x - eye_size / 2, right_eye_x - eye_size / 2)
            max_x = max(left_eye_x + eye_size / 2, right_eye_x + eye_size / 2)
            min_y = min(left_eye_y - eye_size / 2, right_eye_y - eye_size / 2)
            max_y = max(left_eye_y + eye_size / 2, right_eye_y + eye_size / 2)

            # 添加边距
            padding = self.config['white_bg_padding'] * window_width
            x = max(0, min_x - padding)
            y = max(0, min_y - padding)
            width = min(window_width - x, (max_x - min_x) + 2 * padding)
            height = min(window_height - y, (max_y - min_y) + 2 * padding)

            return (x, y, width, height)

        else:  # manual模式
            # 手动模式：使用配置的百分比
            bg_x_percent, bg_y_percent, bg_width_percent, bg_height_percent = self.config['white_bg_rect']

            x = window_width * bg_x_percent
            y = window_height * bg_y_percent
            width = window_width * bg_width_percent
            height = window_height * bg_height_percent

            return (x, y, width, height)

    def init_ui(self):
        """初始化UI"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 获取目标大小
        target_width, target_height = self.config['target_size']

        # ============ 创建眼睛 ============
        self.left_eye = Eye(self, is_left=True)
        self.right_eye = Eye(self, is_left=False)

        # 设置眼睛大小
        eye_size = self.config['eye_size']
        self.left_eye.setFixedSize(eye_size, eye_size)
        self.right_eye.setFixedSize(eye_size, eye_size)
        self.left_eye.max_move = self.config['max_move']
        self.right_eye.max_move = self.config['max_move']

        # ============ 加载并缩放背景图片 ============
        self.background_label = QLabel(self)

        try:
            # 加载原始大图
            original_pixmap = QPixmap(self.config['character_img'])

            if original_pixmap.isNull():
                print("找不到背景图片，创建默认背景")
                scaled_pixmap = self.create_default_background(target_width, target_height)
            else:
                print(f"原始图片尺寸: {original_pixmap.width()} x {original_pixmap.height()}")
                print(f"目标显示尺寸: {target_width} x {target_height}")

                # 高质量缩放图片
                scaled_pixmap = original_pixmap.scaled(
                    target_width,
                    target_height,
                    Qt.AspectRatioMode.KeepAspectRatio,  # 保持比例
                    Qt.TransformationMode.SmoothTransformation  # 平滑缩放
                )

                print(f"缩放后尺寸: {scaled_pixmap.width()} x {scaled_pixmap.height()}")

        except Exception as e:
            print(f"加载图片出错: {e}")
            scaled_pixmap = self.create_default_background(target_width, target_height)

        # 获取实际缩放后的尺寸
        actual_width = scaled_pixmap.width()
        actual_height = scaled_pixmap.height()

        # 设置窗口大小为缩放后的图片大小
        self.setFixedSize(actual_width, actual_height)
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, actual_width, actual_height)

        # ============ 计算眼睛的实际位置 ============
        # 获取百分比配置
        left_eye_percent_x, left_eye_percent_y = self.config['left_eye_percent']
        right_eye_percent_x, right_eye_percent_y = self.config['right_eye_percent']

        # 计算实际像素位置
        left_eye_x = int(actual_width * left_eye_percent_x)
        left_eye_y = int(actual_height * left_eye_percent_y)
        right_eye_x = int(actual_width * right_eye_percent_x)
        right_eye_y = int(actual_height * right_eye_percent_y)

        print(f"左眼位置: ({left_eye_x}, {left_eye_y})")
        print(f"右眼位置: ({right_eye_x}, {right_eye_y})")

        # 设置眼睛位置（使用计算出的实际位置）
        self.left_eye.original_pos = QPoint(left_eye_x - eye_size // 2, left_eye_y - eye_size // 2)
        self.right_eye.original_pos = QPoint(right_eye_x - eye_size // 2, right_eye_y - eye_size // 2)

        # 加载眼睛图片
        try:
            self.left_eye.set_eye_image(self.config['left_eye_img'])
        except:
            print("加载左眼图片失败，创建默认眼睛")
            self.create_default_eye(self.left_eye)

        try:
            self.right_eye.set_eye_image(self.config['right_eye_img'])
        except:
            print("加载右眼图片失败，创建默认眼睛")
            self.create_default_eye(self.right_eye)

        # 设置眼睛初始位置
        self.left_eye.move(self.left_eye.original_pos)
        self.right_eye.move(self.right_eye.original_pos)

        # ============ 创建白色背景层 ============
        self.white_background = QLabel(self)

        # 计算白色背景的位置和大小
        bg_x, bg_y, bg_width, bg_height = self.calculate_white_background_rect(actual_width, actual_height)

        # 设置白色背景的位置和大小
        self.white_background.setGeometry(int(bg_x), int(bg_y), int(bg_width), int(bg_height))

        # 创建白色背景图片
        r, g, b, a = self.config['white_bg_color']
        white_pixmap = QPixmap(int(bg_width), int(bg_height))
        white_pixmap.fill(QColor(r, g, b, a))
        self.white_background.setPixmap(white_pixmap)

        # ============ 设置Z轴顺序 ============
        # 图层顺序：白色背景层（最底层）-> 眼睛层 -> 人物背景层（最上层）
        self.white_background.lower()  # 白色背景放到最底层
        self.left_eye.raise_()  # 眼睛在白色背景之上
        self.right_eye.raise_()
        self.background_label.raise_()  # 人物背景在最上层

        # 创建对话气泡（带动画版本）
        self.speech_bubble = SpeechBubble(self)

        # 鼠标追踪定时器
        self.track_timer = QTimer()
        self.track_timer.timeout.connect(self.update_eyes)
        self.track_timer.start(self.config['track_interval'])

    def create_default_background(self, width, height):
        """创建默认背景"""
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算各部分大小
        head_radius = min(width, height) * 0.25
        head_x = (width - head_radius * 2) // 2
        head_y = height * 0.15

        body_width = width * 0.6
        body_height = height * 0.5
        body_x = (width - body_width) // 2
        body_y = head_y + head_radius * 2

        # 绘制人物
        painter.setBrush(QBrush(QColor(255, 218, 185)))
        painter.drawEllipse(int(head_x), int(head_y), int(head_radius * 2), int(head_radius * 2))

        painter.setBrush(QBrush(QColor(100, 149, 237)))
        painter.drawRoundedRect(int(body_x), int(body_y), int(body_width), int(body_height), 20, 20)

        # 眼眶（透明区域）
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)

        # 计算眼眶位置（百分比位置）
        left_eye_x = head_x + head_radius * 0.7
        left_eye_y = head_y + head_radius * 0.8
        right_eye_x = head_x + head_radius * 1.3
        right_eye_y = head_y + head_radius * 0.8
        eye_size = head_radius * 0.5

        painter.drawEllipse(int(left_eye_x), int(left_eye_y), int(eye_size), int(eye_size))
        painter.drawEllipse(int(right_eye_x), int(right_eye_y), int(eye_size), int(eye_size))

        painter.end()
        return pixmap

    def create_default_eye(self, eye_widget):
        """创建默认眼睛"""
        size = eye_widget.width()
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 创建带有白色背景的眼睛
        # 先绘制白色背景
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(0, 0, size, size)

        # 再绘制黑色眼球
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(size // 4, size // 4, size // 2, size // 2)

        # 最后绘制白色高光
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(size // 2, size // 2, size // 8, size // 8)

        painter.end()
        eye_widget.setPixmap(pixmap)

    def setup_timers(self):
        """设置定时器"""
        # 随机消息定时器
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.show_random_message)
        # 设置随机间隔：20秒-3分钟
        min_interval = self.config.get('min_message_interval', 20000)
        max_interval = self.config.get('max_message_interval', 180000)
        interval = random.randint(min_interval, max_interval)
        print(f"下一次气泡将在 {interval / 1000:.1f} 秒后出现")
        self.message_timer.start(interval)

        # 时间消息定时器（每分钟检查一次）
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.check_time_based_messages)
        self.time_timer.start(60000)  # 每分钟检查一次

        # 时间变化检查定时器（每分钟检查一次）
        self.time_change_timer = QTimer()
        self.time_change_timer.timeout.connect(self.check_time_change)
        self.time_change_timer.start(60000)  # 每分钟检查一次

        # 特殊日期检查定时器（每小时检查一次）
        self.date_timer = QTimer()
        self.date_timer.timeout.connect(self.check_special_dates)
        self.date_timer.start(3600000)  # 每小时检查一次

        # 立即检查特殊日期
        self.check_special_dates()

    def check_time_based_messages(self):
        """检查基于时间的消息"""
        current_time_category = self.get_time_category()

        # 检查是否需要显示夜间消息
        if current_time_category == 'night':
            if not self.has_shown_night_message:
                message = random.choice(self.messages_by_time['night'])
                self.speech_bubble.show_bubble(message, 4000)
                self.has_shown_night_message = True
        else:
            self.has_shown_night_message = False

    def check_special_dates(self):
        """检查特殊日期"""
        today = date.today()
        month_day = (today.month, today.day)

        if month_day in self.config['special_dates']:
            message = self.config['special_dates'][month_day]
            print(f"今天是特殊日期！显示消息: {message}")
            self.speech_bubble.show_bubble(message, 5000)

    def update_eyes(self):
        """更新眼睛位置"""
        mouse_pos = QCursor.pos()
        self.left_eye.track_mouse(mouse_pos)
        self.right_eye.track_mouse(mouse_pos)

    def show_random_message(self):
        """显示随机消息"""
        try:
            # 先检查特殊日期（优先级最高）
            self.check_special_dates()

            bubble_probability = self.config.get('bubble_probability', 0.95)

            if random.random() < (1 - bubble_probability):
                # 显示时间
                self.show_time_message()
            else:
                # 根据当前时间显示相应类型的消息
                current_time_category = self.get_time_category()

                # 从对应时间类别的消息中随机选择（包含原始消息）
                message = random.choice(self.messages_by_time[current_time_category])
                duration = self.config.get('bubble_duration', 3000)
                print(f"显示{current_time_category}消息: {message} (显示{duration / 1000}秒后消失)")
                self.speech_bubble.show_bubble(message, duration)
        except Exception as e:
            print(f"显示消息时出错: {e}")

        # 重置定时器，随机间隔：20秒-3分钟
        # TODO：可以根据希望显示消息的频率调整间隔时间
        min_interval = self.config.get('min_message_interval', 20000)
        max_interval = self.config.get('max_message_interval', 180000)
        interval = random.randint(min_interval, max_interval)
        print(f"下一次气泡将在 {interval / 1000:.1f} 秒后出现")
        self.message_timer.start(interval)

    def show_time_message(self):
        """显示当前时间"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            current_time_category = self.get_time_category()

            if current_time_category == 'morning':
                greeting = "早上"
            elif current_time_category == 'noon':
                greeting = "中午"
            elif current_time_category == 'afternoon':
                greeting = "下午"
            elif current_time_category == 'evening':
                greeting = "晚上"
            else:  # night
                greeting = "深夜"

            message = f"{greeting}{current_time}啦！"
            duration = self.config.get('bubble_duration', 3000)
            print(f"显示时间消息: {message} (显示{duration / 1000}秒后消失)")
            self.speech_bubble.show_bubble(message, duration)
        except Exception as e:
            print(f"显示时间消息时出错: {e}")

    # ============ 新增：互动区域检测方法 ============
    def get_body_part_at_position(self, pos):
        """检测点击位置对应的身体部位"""
        window_width = self.width()
        window_height = self.height()

        # 获取配置中的各个区域
        ear_percent = self.config['ear_area']
        head_percent = self.config['head_area']
        face_percent = self.config['face_area']
        body_percent = self.config['body_area']

        # 计算实际像素区域
        ear_rect = QRect(
            int(window_width * ear_percent[0]),
            int(window_height * ear_percent[1]),
            int(window_width * ear_percent[2]),
            int(window_height * ear_percent[3])
        )

        head_rect = QRect(
            int(window_width * head_percent[0]),
            int(window_height * head_percent[1]),
            int(window_width * head_percent[2]),
            int(window_height * head_percent[3])
        )

        face_rect = QRect(
            int(window_width * face_percent[0]),
            int(window_height * face_percent[1]),
            int(window_width * face_percent[2]),
            int(window_height * face_percent[3])
        )

        body_rect = QRect(
            int(window_width * body_percent[0]),
            int(window_height * body_percent[1]),
            int(window_width * body_percent[2]),
            int(window_height * body_percent[3])
        )

        # 检测点击位置（按优先级顺序）
        if ear_rect.contains(pos):
            return 'ear'
        elif head_rect.contains(pos):
            return 'head'
        elif face_rect.contains(pos):
            return 'face'
        elif body_rect.contains(pos):
            return 'body'

        return None

    def handle_body_part_interaction(self, body_part, pos=None):
        """处理身体部位互动"""
        if body_part in self.interaction_messages:
            message = random.choice(self.interaction_messages[body_part])
            # 显示气泡（带淡入动画）
            self.speech_bubble.show_bubble(message, 3000)

    def on_single_click_timeout(self):
        """单击超时处理（不是双击）"""
        if self.click_count == 1 and self.pending_click_pos:
            # 单击事件
            local_pos = self.pending_click_pos
            modifiers = QApplication.keyboardModifiers()

            if modifiers != Qt.KeyboardModifier.ControlModifier:
                body_part = self.get_body_part_at_position(local_pos)
                if body_part:
                    self.handle_body_part_interaction(body_part, local_pos)

        # 重置点击状态
        self.click_count = 0
        self.pending_click_pos = None

    # ============ 修改鼠标事件 ============
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            local_pos = event.position().toPoint()
            modifiers = QApplication.keyboardModifiers()

            # 记录鼠标按下的位置和窗口位置（用于拖动）
            self.mouse_press_pos = event.globalPosition().toPoint()
            self.is_dragging = False

            # 记录拖动起始位置
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.pre_drag_pos = self.pos()
            self.last_drag_time = datetime.now()

            current_time = datetime.now()

            if self.last_click_time and (current_time - self.last_click_time).total_seconds() < 0.2:
                # 200ms内的第二次点击，增加计数
                self.click_count += 1
            else:
                # 新的点击序列开始
                self.click_count = 1

            self.last_click_time = current_time
            self.pending_click_pos = local_pos

            # 启动/重启单击定时器
            self.double_click_timer.start()

            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽反馈"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            # 检查是否是第一次移动（从按下到移动）
            if not self.is_dragging and self.mouse_press_pos:
                # 计算移动距离
                current_pos = event.globalPosition().toPoint()
                distance = ((current_pos.x() - self.mouse_press_pos.x()) ** 2 +
                            (current_pos.y() - self.mouse_press_pos.y()) ** 2) ** 0.5

                # 如果移动距离超过阈值，认为是拖动而不是点击
                if distance > self.drag_threshold:
                    self.is_dragging = True
                    # 如果是拖动，取消单击/双击检测
                    self.double_click_timer.stop()
                    self.click_count = 0
                    self.pending_click_pos = None

                    # 每次开始拖动时显示拖动气泡（修复：每次拖动都显示）
                    drag_message = random.choice(self.drag_messages)
                    self.speech_bubble.show_bubble(drag_message, 2000)

            if self.is_dragging:
                # 检查是否是Ctrl键拖动（调试模式）
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.KeyboardModifier.ControlModifier:
                    # Ctrl键拖动时不移动窗口，只用于调试
                    return

                # 计算新的窗口位置
                new_pos = event.globalPosition().toPoint() - self.drag_pos

                # 移动窗口
                self.move(new_pos)

                # 更新气泡位置（如果正在显示）
                self.speech_bubble.update_position(self.pos())

                # 拖拽反馈（不再限制显示次数，每次拖动都有机会显示）
                current_time = datetime.now()
                if self.last_drag_time:
                    # 计算拖拽速度
                    time_diff = (current_time - self.last_drag_time).total_seconds()
                    distance = ((new_pos.x() - self.pre_drag_pos.x()) ** 2 +
                                (new_pos.y() - self.pre_drag_pos.y()) ** 2) ** 0.5

                    if time_diff > 0:
                        speed = distance / time_diff

                        # 快速拖动时随机显示反馈消息
                        if speed > 50 and random.random() < 0.3:  # 30%概率显示
                            drag_message = random.choice(self.drag_messages)
                            self.speech_bubble.show_bubble(drag_message, 2000)

                self.last_drag_time = current_time
                self.pre_drag_pos = new_pos

            event.accept()

    def mouseDoubleClickEvent(self, event):
        """双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 双击时取消单击定时器
            self.double_click_timer.stop()
            self.click_count = 0
            self.pending_click_pos = None

            # 双击显示随机消息
            self.show_random_message()

            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 如果不是拖动，重置拖动标志
            if not self.is_dragging:
                self.is_dragging = False
                self.mouse_press_pos = None

            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)

        menu.addSeparator()
        menu.addAction(quit_action)
        menu.exec(event.globalPos())

    def quit_application(self):
        """退出应用程序"""
        try:
            # 停止所有定时器
            if hasattr(self, 'track_timer'):
                self.track_timer.stop()
            if hasattr(self, 'message_timer'):
                self.message_timer.stop()
            if hasattr(self, 'time_timer'):
                self.time_timer.stop()
            if hasattr(self, 'time_change_timer'):
                self.time_change_timer.stop()
            if hasattr(self, 'date_timer'):
                self.date_timer.stop()
            if hasattr(self, 'double_click_timer'):
                self.double_click_timer.stop()

            # 清理气泡
            if hasattr(self, 'speech_bubble'):
                self.speech_bubble.cleanup_timers()

            # 关闭窗口
            self.close()

            # 退出应用程序
            QApplication.quit()
        except Exception as e:
            print(f"退出时出错: {e}")
            sys.exit(1)


def main():
    try:
        app = QApplication(sys.argv)
        pet = DesktopPet()
        pet.show()

        screen_geometry = app.primaryScreen().availableGeometry()
        initial_position = pet.config['initial_position']

        if initial_position:
            x, y = initial_position
            pet.move(x, y)
        else:
            pet.move(screen_geometry.width() - pet.width() - 20,
                     screen_geometry.height() - pet.height() - 50)

        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()