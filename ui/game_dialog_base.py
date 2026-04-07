"""
Базовые классы и виджеты для мультиплеерной игры
"""

import math
import logging
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QScrollArea, QWidget, QProgressBar, QGridLayout, QSizePolicy,
                               QMessageBox)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QPointF, QRectF
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPolygonF, QPixmap

from config import THEMES
from ui.camera_dialog import CameraDialog

logger = logging.getLogger("GameDialog")
logger.setLevel(logging.DEBUG)


class AnimatedButton(QPushButton):
    """Кнопка с анимацией пульсации"""
    
    def __init__(self, text, parent=None, color="#10b981", icon=""):
        super().__init__(text, parent)
        self.color = color
        self.icon = icon
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50)
        self.setFont(QFont("Segoe UI", 12))
        self._animation = None

    def enterEvent(self, event):
        if self._animation:
            self._animation.stop()
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(300)
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self._animation.setEasingCurve(QEasingCurve.OutBounce)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._animation:
            self._animation.stop()
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(300)
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        self._animation.setEasingCurve(QEasingCurve.OutBounce)
        self._animation.start()
        super().leaveEvent(event)


class SelfScoreButton(QPushButton):
    """Кнопка для самооценки"""
    
    def __init__(self, value, parent=None):
        super().__init__(str(value), parent)
        self.value = value
        self.is_selected = False
        self.setFixedSize(60, 60)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.update_style()
    
    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: 2px solid #2563eb;
                    border-radius: 30px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #94a3b8;
                    border: 2px solid #475569;
                    border-radius: 30px;
                }
                QPushButton:hover {
                    background-color: #334155;
                    border-color: #3b82f6;
                }
            """)
    
    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()


class ConnectedPlayerCard(QFrame):
    """Карточка подключенного клиента с возможностью фотосъёмки"""
    
    def __init__(self, player_name, player_id, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.player_id = player_id
        self.total_score = 0
        self.photo_version = 0
        self.has_photo = False
        self._animation = None

        self.setObjectName("connectedPlayerCard")
        self.setStyleSheet("""
            QFrame#connectedPlayerCard {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid #8b5cf6;
                border-radius: 10px;
                padding: 8px;
                margin: 3px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Иконка (фото или дефолтная)
        self.icon_label = QLabel("📱")
        self.icon_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(self.icon_label)

        name_label = QLabel(player_name)
        name_label.setFont(QFont("Segoe UI", 11))
        name_label.setStyleSheet("color: #f8fafc;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label, 1)

        # Квадратик для счета
        self.score_square = QFrame()
        self.score_square.setFixedSize(40, 40)
        self.score_square.setStyleSheet("background-color: #1e293b; border: 2px solid #8b5cf6; border-radius: 8px;")

        self.score_label = QLabel("0")
        self.score_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.score_label.setStyleSheet("color: #f8fafc; background: transparent;")
        self.score_label.setAlignment(Qt.AlignCenter)

        score_layout = QVBoxLayout(self.score_square)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.addWidget(self.score_label)

        layout.addWidget(self.score_square)

    def set_score(self, score):
        self.total_score = score
        self.score_label.setText(str(score))
        
        if self._animation:
            self._animation.stop()
        self._animation = QPropertyAnimation(self.score_square, b"geometry")
        self._animation.setDuration(200)
        self._animation.setKeyValueAt(0, self.score_square.geometry())
        self._animation.setKeyValueAt(0.5, self.score_square.geometry().adjusted(-5, -5, 5, 5))
        self._animation.setKeyValueAt(1, self.score_square.geometry())
        self._animation.setEasingCurve(QEasingCurve.OutBounce)
        self._animation.start()

    def set_photo_version(self, version):
        """Установить версию фото"""
        self.photo_version = version
        self.version_label.setText(str(version))
        
        if version > 0:
            self.has_photo = True
            self.icon_label.setText("✅")  # Меняем иконку на галочку
            self.camera_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
        else:
            self.has_photo = False
            self.icon_label.setText("📱")  # Возвращаем дефолтную иконку
            self.camera_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)

    def take_photos(self):
        """Открыть диалог фотосъёмки"""
        dialog = CameraDialog(self.player_name, self.window())
        if dialog.exec() == QDialog.Accepted and len(dialog.photos_taken) == 10:
            # Сохраняем фото
            self.save_photos(dialog.photos_taken)
            # Увеличиваем версию
            new_version = self.photo_version + 1
            self.set_photo_version(new_version)
            self.photo_version_updated.emit(self.player_id, new_version)

    def save_photos(self, photos):
        """Сохранить фотографии в файл"""
        try:
            # Создаём директорию для фото, если её нет
            photo_dir = "data/photos"
            os.makedirs(photo_dir, exist_ok=True)
            
            # Сохраняем фото с версией
            for i, photo in enumerate(photos):
                filename = f"{photo_dir}/{self.player_id}_v{self.photo_version + 1}_{i}.png"
                photo.save(filename)
            
            logger.info(f"Saved 10 photos for {self.player_name} (version {self.photo_version + 1})")
            
        except Exception as e:
            logger.error(f"Error saving photos: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить фото: {e}")


class ParticipantScoreCard(QFrame):
    """Карточка участника (вручную добавленного)"""
    
    def __init__(self, participant_name, participant_index, parent=None):
        super().__init__(parent)
        self.participant_name = participant_name
        self.participant_index = participant_index
        self.self_scores = []  # Самооценка
        self.other_scores = []  # Оценки окружающих
        self._animation = None
        
        self.setObjectName("participantCard")
        self.setStyleSheet("""
            QFrame#participantCard {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid #3b82f6;
                border-radius: 10px;
                padding: 8px;
                margin: 3px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        index_label = QLabel(f"{participant_index}.")
        index_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        index_label.setStyleSheet("color: #3b82f6; min-width: 25px;")
        layout.addWidget(index_label)
        
        name_label = QLabel(participant_name)
        name_label.setFont(QFont("Segoe UI", 11))
        name_label.setStyleSheet("color: #f8fafc;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label, 1)
        
        # Квадратик для текущей оценки
        self.score_square = QFrame()
        self.score_square.setFixedSize(40, 40)
        self.score_square.setStyleSheet("background-color: #1e293b; border: 2px solid #3b82f6; border-radius: 8px;")
        
        self.score_label = QLabel("0")
        self.score_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.score_label.setStyleSheet("color: #f8fafc; background: transparent;")
        self.score_label.setAlignment(Qt.AlignCenter)
        
        score_layout = QVBoxLayout(self.score_square)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.addWidget(self.score_label)
        
        layout.addWidget(self.score_square)
    
    def set_current_score(self, score):
        """Установить текущую оценку (сумму самооценки и оценок других)"""
        self.score_label.setText(str(score))
        
        if self._animation:
            self._animation.stop()
        self._animation = QPropertyAnimation(self.score_square, b"geometry")
        self._animation.setDuration(200)
        self._animation.setKeyValueAt(0, self.score_square.geometry())
        self._animation.setKeyValueAt(0.5, self.score_square.geometry().adjusted(-5, -5, 5, 5))
        self._animation.setKeyValueAt(1, self.score_square.geometry())
        self._animation.setEasingCurve(QEasingCurve.OutBounce)
        self._animation.start()
    
    def add_self_score(self, score):
        """Добавить самооценку"""
        self.self_scores.append(score)
    
    def add_other_score(self, score):
        """Добавить оценку от другого"""
        self.other_scores.append(score)
    
    def get_total_score(self):
        """Получить сумму всех оценок"""
        return sum(self.self_scores) + sum(self.other_scores)


class QuestionCard(QFrame):
    """Карточка с вопросом и самооценкой"""
    
    def __init__(self, category, question, parent=None):
        super().__init__(parent)
        self.category = category
        self.question = question
        self.selected_self_score = None
        self.confirm_button = None
        self.self_score_buttons = []
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.8);
                border: 2px solid #3b82f6;
                border-radius: 20px;
                padding: 30px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(59, 130, 246, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Категория
        category_frame = QFrame()
        category_frame.setStyleSheet("background-color: #3b82f620; border-radius: 15px; padding: 10px;")
        cat_layout = QHBoxLayout(category_frame)
        cat_layout.setContentsMargins(15, 10, 15, 10)
        cat_icon = QLabel("📊")
        cat_icon.setFont(QFont("Segoe UI", 20))
        cat_layout.addWidget(cat_icon)
        self.category_label = QLabel(category.upper())
        self.category_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.category_label.setStyleSheet("color: #3b82f6;")
        cat_layout.addWidget(self.category_label)
        cat_layout.addStretch()
        layout.addWidget(category_frame)

        # Вопрос
        self.question_label = QLabel(question)
        self.question_label.setFont(QFont("Segoe UI", 20))
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("color: #f8fafc; padding: 20px 0;")
        layout.addWidget(self.question_label)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #334155; max-height: 1px;")
        layout.addWidget(separator)

        # Самооценка
        self_score_label = QLabel("🗳️ Оцените свой ответ:")
        self_score_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self_score_label.setStyleSheet("color: #f8fafc; padding: 10px 0;")
        layout.addWidget(self_score_label)

        # Кнопки для самооценки 0-5
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)

        for i in range(6):
            btn = SelfScoreButton(i)
            btn.clicked.connect(lambda checked, val=i: self.select_score(val))
            self.self_score_buttons.append(btn)
            buttons_layout.addWidget(btn)

        layout.addLayout(buttons_layout)

        # Кнопка подтверждения
        confirm_layout = QHBoxLayout()
        confirm_layout.setAlignment(Qt.AlignCenter)
        
        self.confirm_button = QPushButton("✅ Подтвердить оценку")
        self.confirm_button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.confirm_button.setCursor(Qt.PointingHandCursor)
        self.confirm_button.setMinimumHeight(50)
        self.confirm_button.setMinimumWidth(200)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border: 2px solid #10b981;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(16, 185, 129, 0.3);
            }
            QPushButton:disabled {
                background-color: rgba(100, 116, 139, 0.1);
                color: #64748b;
                border: 2px solid #475569;
            }
        """)
        
        confirm_layout.addWidget(self.confirm_button)
        layout.addLayout(confirm_layout)
        layout.addStretch()

    def set_question(self, category, question):
        self.category_label.setText(category.upper())
        self.question_label.setText(question)
        self.selected_self_score = None
        for btn in self.self_score_buttons:
            btn.set_selected(False)
        self.confirm_button.setEnabled(False)
    
    def select_score(self, score):
        self.selected_self_score = score
        for i, btn in enumerate(self.self_score_buttons):
            btn.set_selected(i == score)
        self.confirm_button.setEnabled(True)


class RadarChartWidget(QFrame):
    """Виджет для отображения радарного графика"""
    
    def __init__(self, categories, self_scores, other_scores, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.self_scores = self_scores
        self.other_scores = other_scores
        self.setMinimumSize(300, 300)
        self.setMaximumSize(400, 400)
        self.setStyleSheet("background-color: transparent;")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) * 0.4
        
        # Рисуем сетку
        painter.setPen(QPen(QColor(75, 85, 99), 1))
        for i in range(1, 6):
            r = radius * i / 5
            painter.drawEllipse(QPointF(center_x, center_y), r, r)
        
        # Рисуем оси
        num_categories = len(self.categories)
        for i in range(num_categories):
            angle = 2 * math.pi * i / num_categories - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            painter.drawLine(center_x, center_y, x, y)
        
        # Рисуем данные самооценки
        points_self = []
        for i, score in enumerate(self.self_scores):
            angle = 2 * math.pi * i / num_categories - math.pi / 2
            r = radius * score / 5
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points_self.append(QPointF(x, y))
        
        if points_self:
            painter.setBrush(QBrush(QColor(16, 185, 129, 80)))
            painter.setPen(QPen(QColor(16, 185, 129), 2))
            painter.drawPolygon(QPolygonF(points_self))
        
        # Рисуем данные оценок других
        points_other = []
        for i, score in enumerate(self.other_scores):
            angle = 2 * math.pi * i / num_categories - math.pi / 2
            r = radius * score / 5
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points_other.append(QPointF(x, y))
        
        if points_other:
            painter.setBrush(QBrush(QColor(245, 158, 11, 80)))
            painter.setPen(QPen(QColor(245, 158, 11), 2))
            painter.drawPolygon(QPolygonF(points_other))
        
        # Легенда
        painter.setPen(QPen(QColor(248, 250, 252), 1))
        painter.setFont(QFont("Segoe UI", 9))
        
        painter.setBrush(QBrush(QColor(16, 185, 129)))
        painter.drawRect(10, 10, 12, 12)
        painter.setPen(QPen(QColor(248, 250, 252)))
        painter.drawText(30, 22, "Самооценка")
        
        painter.setBrush(QBrush(QColor(245, 158, 11)))
        painter.drawRect(10, 30, 12, 12)
        painter.setPen(QPen(QColor(248, 250, 252)))
        painter.drawText(30, 42, "Оценка других")


class BarChartWidget(QFrame):
    """Виджет для отображения столбчатой диаграммы"""
    
    def __init__(self, categories, self_scores, other_scores, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.self_scores = self_scores
        self.other_scores = other_scores
        self.setMinimumSize(300, 200)
        self.setMaximumHeight(250)
        self.setStyleSheet("background-color: transparent;")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height() - 50
        margin = 50
        bar_width = (width - 2 * margin) / (len(self.categories) * 2) - 5
        
        # Рисуем оси
        painter.setPen(QPen(QColor(100, 116, 139), 1))
        painter.drawLine(margin, height - 30, width - margin, height - 30)
        painter.drawLine(margin, 10, margin, height - 30)
        
        # Рисуем деления по Y
        for i in range(6):
            y = height - 30 - (i * (height - 60) / 5)
            painter.setPen(QPen(QColor(75, 85, 99), 1))
            painter.drawLine(margin - 5, y, margin, y)
            painter.setPen(QPen(QColor(248, 250, 252)))
            painter.drawText(10, y + 5, str(i))
        
        # Рисуем столбцы
        for i, category in enumerate(self.categories):
            x_self = margin + i * 2 * bar_width + 15
            x_other = x_self + bar_width
            
            # Самооценка
            self_height = (height - 60) * self.self_scores[i] / 5
            painter.setBrush(QBrush(QColor(16, 185, 129)))
            painter.setPen(QPen(QColor(16, 185, 129)))
            painter.drawRect(x_self, height - 30 - self_height, bar_width - 5, self_height)
            
            # Оценка других
            other_height = (height - 60) * self.other_scores[i] / 5
            painter.setBrush(QBrush(QColor(245, 158, 11)))
            painter.setPen(QPen(QColor(245, 158, 11)))
            painter.drawRect(x_other, height - 30 - other_height, bar_width - 5, other_height)
            
            # Подпись категории
            painter.setPen(QPen(QColor(248, 250, 252)))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(x_self, height - 10, category[:10])
