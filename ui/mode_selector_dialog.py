"""
Диалог выбора режима игры
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QLineEdit, QSpinBox, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from config import THEMES, APP_MODES, SERVER_CONFIG


class ModeSelectorDialog(QDialog):
    """Диалог выбора режима игры"""
    
    def __init__(self, parent=None, current_theme="dark"):
        super().__init__(parent)
        self.setWindowTitle("Выбор режима игры")
        self.setFixedSize(750, 550)
        self.setModal(True)
        
        # Убираем стандартную панель окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        self.selected_mode = None
        self.current_theme = current_theme
        self.server_config = {
            "host": SERVER_CONFIG["default_host"],
            "port": SERVER_CONFIG["default_port"],
            "max_players": 30
        }
        
        theme = THEMES[current_theme]
        
        # Черная граница
        border_color = "#000000"
        border_width = "3px"
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme["bg_secondary"]};
                border: {border_width} solid {border_color};
                border-radius: 0px;
            }}
            QLabel {{
                color: {theme["text"]};
                background-color: transparent;
            }}
            QLineEdit, QSpinBox {{
                background-color: {theme["bg_card"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 0px;
                padding: 8px;
                font-size: 11pt;
                min-height: 30px;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 2px solid #3b82f6;
            }}
            QFrame#modeCard {{
                background-color: transparent;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Заголовок
        title = QLabel("🎮 ВЫБОР РЕЖИМА ИГРЫ")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Карточки режимов
        modes_layout = QHBoxLayout()
        modes_layout.setSpacing(25)
        
        # Одиночный режим
        self.single_card = self.create_mode_card(
            "🎮", 
            "Одиночная игра",
            "Классический режим",
            "#3b82f6"
        )
        self.single_card.mousePressEvent = lambda e: self.select_mode("single")
        # Убираем всплывающую подсказку
        self.single_card.setToolTip("")
        modes_layout.addWidget(self.single_card)
        
        # Серверный режим
        self.server_card = self.create_mode_card(
            "🌐", 
            "Серверный режим",
            "Игра с телефонов (до 30 игроков)",
            "#8b5cf6"
        )
        self.server_card.mousePressEvent = lambda e: self.select_mode("server")
        # Убираем всплывающую подсказку
        self.server_card.setToolTip("")
        modes_layout.addWidget(self.server_card)
        
        layout.addLayout(modes_layout)
        
        # Растяжка
        layout.addStretch(1)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        self.start_btn = QPushButton("✅ Начать игру")
        self.start_btn.setFixedHeight(45)
        self.start_btn.setMinimumWidth(170)
        self.start_btn.setFont(QFont("Segoe UI", 11, QFont.Normal))  # Уменьшен с 12 до 11
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setEnabled(False)
        self.start_btn.setToolTip("")  # Убираем всплывающую подсказку
        
        # Стиль кнопки "Начать"
        if current_theme == "light":
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(16, 185, 129, 0.8);
                    color: #0f172a;
                    border: 1px solid #cbd5e1;
                    border-radius: 10px;
                    padding: 10px 25px;
                }}
                QPushButton:hover {{
                    background-color: rgba(16, 185, 129, 0.95);
                    border: 1px solid #10b981;
                }}
                QPushButton:disabled {{
                    background-color: rgba(100, 116, 139, 0.3);
                    color: #64748b;
                    border: 1px solid #cbd5e1;
                }}
            """)
        else:
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(16, 185, 129, 0.2);
                    color: #10b981;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 10px;
                    padding: 10px 25px;
                }}
                QPushButton:hover {{
                    background-color: rgba(16, 185, 129, 0.3);
                    border: 1px solid rgba(16, 185, 129, 0.5);
                }}
                QPushButton:disabled {{
                    background-color: rgba(100, 116, 139, 0.1);
                    color: #64748b;
                    border: 1px solid rgba(100, 116, 139, 0.2);
                }}
            """)
        self.start_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setMinimumWidth(170)
        cancel_btn.setFont(QFont("Segoe UI", 11))  # Уменьшен с 12 до 11
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setToolTip("")  # Убираем всплывающую подсказку
        
        if current_theme == "light":
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(239, 68, 68, 0.8);
                    color: #0f172a;
                    border: 1px solid #cbd5e1;
                    border-radius: 10px;
                    padding: 10px 25px;
                }}
                QPushButton:hover {{
                    background-color: rgba(239, 68, 68, 0.95);
                    border: 1px solid #ef4444;
                }}
            """)
        else:
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(239, 68, 68, 0.2);
                    color: #ef4444;
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    border-radius: 10px;
                    padding: 10px 25px;
                }}
                QPushButton:hover {{
                    background-color: rgba(239, 68, 68, 0.3);
                    border: 1px solid rgba(239, 68, 68, 0.5);
                }}
            """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.start_btn)
        
        layout.addLayout(button_layout)
        
        # Ничего не выбрано по умолчанию
        self.reset_styles()
    
    def reset_styles(self):
        """Сбросить стили карточек к исходным"""
        theme = THEMES[self.current_theme]
        
        if self.current_theme == "light":
            self.single_card.setStyleSheet(f"""
                QFrame#modeCard {{
                    background-color: rgba(245, 248, 250, 0.8);
                    border: 2px solid #e2e8f0;
                    border-radius: 0px;
                    padding: 15px;
                }}
                QFrame#modeCard:hover {{
                    border: 4px solid #3b82f6;
                    background-color: rgba(235, 245, 255, 0.9);
                }}
            """)
            self.server_card.setStyleSheet(f"""
                QFrame#modeCard {{
                    background-color: rgba(245, 248, 250, 0.8);
                    border: 2px solid #e2e8f0;
                    border-radius: 0px;
                    padding: 15px;
                }}
                QFrame#modeCard:hover {{
                    border: 4px solid #8b5cf6;
                    background-color: rgba(235, 245, 255, 0.9);
                }}
            """)
        else:
            self.single_card.setStyleSheet(f"""
                QFrame#modeCard {{
                    background-color: rgba(30, 41, 59, 0.7);
                    border: 3px solid #334155;
                    border-radius: 0px;
                    padding: 15px;
                }}
                QFrame#modeCard:hover {{
                    border: 4px solid #3b82f6;
                }}
            """)
            self.server_card.setStyleSheet(f"""
                QFrame#modeCard {{
                    background-color: rgba(30, 41, 59, 0.7);
                    border: 3px solid #334155;
                    border-radius: 0px;
                    padding: 15px;
                }}
                QFrame#modeCard:hover {{
                    border: 4px solid #8b5cf6;
                }}
            """)
    
    def create_mode_card(self, icon, title, description, color):
        """Создать карточку режима"""
        card = QFrame()
        card.setFixedSize(260, 190)
        card.setCursor(Qt.PointingHandCursor)
        card.setObjectName("modeCard")
        card.setToolTip("")  # Убираем всплывающую подсказку
        
        theme = THEMES[self.current_theme]
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {color}; background: transparent;")
        icon_label.setToolTip("")  # Убираем всплывающую подсказку
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))  # Уменьшен с 16 до 15
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {theme['text']}; background: transparent;")
        title_label.setToolTip("")  # Убираем всплывающую подсказку
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 9))  # Уменьшен с 10 до 9
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {theme['text_secondary']}; background: transparent;")
        desc_label.setToolTip("")  # Убираем всплывающую подсказку
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        return card
    
    def select_mode(self, mode):
        """Выбрать режим"""
        self.selected_mode = mode
        
        # Сбрасываем стили для обеих карточек
        self.reset_styles()
        
        # Черная граница
        if mode == "single":
            if self.current_theme == "light":
                self.single_card.setStyleSheet(f"""
                    QFrame#modeCard {{
                        background-color: rgba(245, 248, 250, 0.8);
                        border: 2px solid #000000;
                        border-radius: 0px;
                        padding: 15px;
                    }}
                    QFrame#modeCard:hover {{
                        border: 4px solid #3b82f6;
                        background-color: rgba(235, 245, 255, 0.9);
                    }}
                """)
            else:
                self.single_card.setStyleSheet(f"""
                    QFrame#modeCard {{
                        background-color: rgba(30, 41, 59, 0.7);
                        border: 2px solid #000000;
                        border-radius: 0px;
                        padding: 15px;
                    }}
                    QFrame#modeCard:hover {{
                        border: 4px solid #3b82f6;
                    }}
                """)
        else:  # server mode
            if self.current_theme == "light":
                self.server_card.setStyleSheet(f"""
                    QFrame#modeCard {{
                        background-color: rgba(245, 248, 250, 0.8);
                        border: 2px solid #000000;
                        border-radius: 0px;
                        padding: 15px;
                    }}
                    QFrame#modeCard:hover {{
                        border: 4px solid #8b5cf6;
                        background-color: rgba(235, 245, 255, 0.9);
                    }}
                """)
            else:
                self.server_card.setStyleSheet(f"""
                    QFrame#modeCard {{
                        background-color: rgba(30, 41, 59, 0.7);
                        border: 2px solid #000000;
                        border-radius: 0px;
                        padding: 15px;
                    }}
                    QFrame#modeCard:hover {{
                        border: 4px solid #8b5cf6;
                    }}
                """)
        
        # Включаем кнопку "Начать игру"
        self.start_btn.setEnabled(True)
    
    def accept(self):
        """Принять выбор"""
        if self.selected_mode is None:
            return
            
        if self.selected_mode == "server":
            self.server_config = {
                "host": SERVER_CONFIG["default_host"],
                "port": SERVER_CONFIG["default_port"],
                "max_players": 30
            }
        super().accept()
