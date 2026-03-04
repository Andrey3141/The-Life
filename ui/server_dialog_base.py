"""
Базовые классы и вспомогательные диалоги для серверного режима
"""

import os
import sys
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QLineEdit, QTextEdit, QScrollArea, QWidget,
                               QMessageBox)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QPen

from config import THEMES


class AnimatedButton(QPushButton):
    """Кнопка с анимацией пульсации"""
    
    def __init__(self, text, parent=None, color="#10b981"):
        super().__init__(text, parent)
        self.color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50)
        self.setFont(QFont("Segoe UI", 12))
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        
    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        self.animation.start()
        super().leaveEvent(event)


class PlayerCard(QFrame):
    """Карточка подключенного игрока"""
    
    def __init__(self, player_name, player_id, connected_at, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.player_id = player_id
        self.connected_at = connected_at
        
        self.setObjectName("playerCard")
        self.setStyleSheet("""
            QFrame#playerCard {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QFrame#playerCard:hover {
                background-color: rgba(30, 41, 59, 0.9);
                border: 1px solid #3b82f6;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Аватар с цветом
        avatar = QLabel()
        avatar.setFixedSize(40, 40)
        
        # Генерируем цвет на основе имени
        colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#ef4444"]
        color_index = hash(player_name) % len(colors)
        
        pixmap = QPixmap(40, 40)
        pixmap.fill(QColor(colors[color_index]))
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.white, 2))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, player_name[0].upper())
        painter.end()
        
        avatar.setPixmap(pixmap)
        avatar.setStyleSheet("border-radius: 20px;")
        
        # Информация об игроке
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(player_name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_label.setStyleSheet("color: #f8fafc; background: transparent;")
        
        time_label = QLabel(f"Подключен: {connected_at.strftime('%H:%M:%S')}")
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: #94a3b8; background: transparent;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(time_label)
        
        # Статус (онлайн)
        status_label = QLabel("● ONLINE")
        status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        status_label.setStyleSheet("color: #10b981; background: transparent;")
        
        layout.addWidget(avatar)
        layout.addLayout(info_layout, 1)
        layout.addWidget(status_label)


class BaseDialog(QDialog):
    """Базовый класс для всех диалогов с общей стилизацией"""
    
    def __init__(self, parent=None, title="", current_theme="dark", width=500, height=400):
        super().__init__(parent)
        self.current_theme = current_theme
        self.theme = THEMES.get(current_theme, THEMES["dark"])
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setFixedSize(width, height)
        
        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme["bg_secondary"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 20px;
            }}
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_top_bar(title)
    
    def create_top_bar(self, title):
        """Создать верхнюю панель с заголовком и кнопкой закрытия"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme["bg_overlay"]};
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: 1px solid {self.theme["border"]};
            }}
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']};")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setFont(QFont("Segoe UI", 16))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.3);
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        self.main_layout.addWidget(top_bar)
    
    def add_content(self, content_widget):
        """Добавить контент в диалог"""
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme["bg_secondary"]};
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
            }}
        """)
        self.main_layout.addWidget(content_widget, 1)


class AddParticipantDialog(BaseDialog):
    """Диалог добавления участника"""
    
    def __init__(self, parent=None, current_theme="dark"):
        super().__init__(parent, "➕ ДОБАВЛЕНИЕ УЧАСТНИКА", current_theme, 500, 400)
        self.participant_name = ""
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Форма
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme["bg_card"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Поле для имени
        name_label = QLabel("Имя и фамилия участника:")
        name_label.setFont(QFont("Segoe UI", 11))
        name_label.setStyleSheet(f"color: {self.theme['text']};")
        form_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя и фамилию...")
        self.name_input.setFont(QFont("Segoe UI", 11))
        self.name_input.setMinimumHeight(40)
        # Сероватый фон для светлой темы
        if self.current_theme == "light":
            self.name_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #f1f5f9;
                    color: #0f172a;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 8px 12px;
                }}
                QLineEdit:focus {{
                    border: 2px solid #3b82f6;
                }}
            """)
        else:
            self.name_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.theme["bg_secondary"]};
                    color: {self.theme["text"]};
                    border: 1px solid {self.theme["border"]};
                    border-radius: 8px;
                    padding: 8px 12px;
                }}
                QLineEdit:focus {{
                    border: 2px solid #3b82f6;
                }}
            """)
        form_layout.addWidget(self.name_input)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setFont(QFont("Segoe UI", 11))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme["text_secondary"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 8px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: rgba(239, 68, 68, 0.1);
                border: 1px solid #ef4444;
                color: #ef4444;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton("✅ Добавить")
        add_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(45)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        self.add_content(content_widget)
    
    def accept(self):
        """Принять добавление"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Предупреждение", "Введите имя и фамилию участника!")
            return
        self.participant_name = name
        super().accept()


class ParticipantsListDialog(BaseDialog):
    """Диалог списка участников"""
    
    def __init__(self, parent=None, current_theme="dark"):
        super().__init__(parent, "👥 УЧАСТНИКИ ИГРЫ", current_theme, 1000, 800)
        self.participants = []
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Информация
        info_label = QLabel("Добавьте участников игры (минимум 1)")
        info_label.setFont(QFont("Segoe UI", 11))
        info_label.setStyleSheet(f"color: {self.theme['text_secondary']};")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Кнопка добавления
        self.add_btn = QPushButton("➕ Добавить участника")
        self.add_btn.setFont(QFont("Segoe UI", 11))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setMinimumHeight(50)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme["bg_card"]};
                color: {self.theme["text"]};
                border: 2px dashed #3b82f6;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(59, 130, 246, 0.1);
                border: 2px solid #3b82f6;
            }}
        """)
        self.add_btn.clicked.connect(self.add_participant)
        layout.addWidget(self.add_btn)
        
        # Список участников
        list_frame = QFrame()
        list_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme["bg_card"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        list_layout = QVBoxLayout(list_frame)
        
        list_title = QLabel("📋 СПИСОК УЧАСТНИКОВ")
        list_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        list_title.setStyleSheet(f"color: {self.theme['text']};")
        list_layout.addWidget(list_title)
        
        # Scroll area для списка
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e293b;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 5px;
            }
        """)
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(5)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addStretch()
        
        scroll_area.setWidget(self.list_widget)
        list_layout.addWidget(scroll_area)
        
        layout.addWidget(list_frame, 1)
        
        # Счетчик
        self.count_label = QLabel("Добавлено участников: 0")
        self.count_label.setFont(QFont("Segoe UI", 10))
        self.count_label.setStyleSheet(f"color: {self.theme['text_muted']};")
        self.count_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.count_label)
        
        # Кнопка продолжить
        self.continue_btn = QPushButton("▶ Продолжить")
        self.continue_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.continue_btn.setCursor(Qt.PointingHandCursor)
        self.continue_btn.setMinimumHeight(50)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #f1f5f9;
            }
        """)
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self.accept)
        layout.addWidget(self.continue_btn)
        
        self.add_content(content_widget)
    
    def add_participant(self):
        """Добавить нового участника"""
        dialog = AddParticipantDialog(self, self.current_theme)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.participant_name
            self.participants.append(name)
            self.update_list()
    
    def update_list(self):
        """Обновить список участников"""
        # Очищаем список
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Добавляем участников
        for i, name in enumerate(self.participants):
            item_widget = QFrame()
            item_widget.setStyleSheet("""
                QFrame {
                    background-color: rgba(59, 130, 246, 0.1);
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(10, 5, 10, 5)
            
            number_label = QLabel(f"{i+1}.")
            number_label.setStyleSheet("color: #3b82f6; font-weight: bold; background: transparent;")
            item_layout.addWidget(number_label)
            
            # ИЗМЕНЕНО: цвет текста зависит от темы
            text_color = "#0f172a" if self.current_theme == "light" else "#f8fafc"
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {text_color}; background: transparent;")
            name_label.setFont(QFont("Segoe UI", 11))
            item_layout.addWidget(name_label)
            item_layout.addStretch()
            
            self.list_layout.insertWidget(self.list_layout.count() - 1, item_widget)
        
        # Обновляем счетчик
        self.count_label.setText(f"Добавлено участников: {len(self.participants)}")
        
        # Активируем кнопку если есть хотя бы 1 участник
        self.continue_btn.setEnabled(len(self.participants) >= 1)
