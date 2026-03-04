"""
Экономическая Симуляция - Графическая версия на PySide6
Основной класс приложения и точка входа
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame, QGridLayout,
                               QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget,
                               QLineEdit, QMessageBox, QDialog)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap

from core.game_engine import GameEngine
from scenes.scene_manager import SceneManager
from ui.stats_window import StatsWindow
from config import GAME_TITLE, GAME_VERSION, THEMES, PATHS, save_theme_config, CUSTOM_IMAGE_PATH
from ui.game_ui import GameUI
from ui.dialogs import ModernDialog, ThemeSelectorDialog

# ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
from ui.mode_selector_dialog import ModeSelectorDialog
from core.server_core import GameServer
import threading


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_engine = GameEngine()
        self.scene_manager = SceneManager()
        self.game_engine.scene_manager = self.scene_manager
        
        # НАСТРОЙКА ОКНА
        self.setWindowTitle(GAME_TITLE)
        # ИЗМЕНЕНО: возвращаем Qt.FramelessWindowHint
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showMaximized()
        
        # Флаги
        self.is_fullscreen = False
        self.current_theme = "dark"
        self.custom_image_path = CUSTOM_IMAGE_PATH
        
        # Загружаем сохраненную тему
        from config import load_theme_config
        self.current_theme, self.custom_image_path = load_theme_config()
        if self.custom_image_path and os.path.exists(self.custom_image_path):
            THEMES["custom"]["image_path"] = self.custom_image_path
        
        # Устанавливаем тему
        self.apply_theme(self.current_theme)
        
        # Создаем центральный виджет
        self.central_stacked = QStackedWidget()
        self.setCentralWidget(self.central_stacked)
        
        # Создаем главное меню
        self.main_menu_widget = self.create_main_menu()
        self.central_stacked.addWidget(self.main_menu_widget)
        
        # Игровой виджет
        self.game_widget = None
        
        self.central_stacked.setCurrentWidget(self.main_menu_widget)
        
        # ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
        self.game_server = None
    
    def apply_theme(self, theme_name):
        """Применить тему оформления"""
        self.current_theme = theme_name
        theme = THEMES[theme_name]
        
        # Сохраняем тему
        image_path = theme.get("image_path", "")
        save_theme_config(theme_name, image_path)
        
        # Основной стиль окна
        if theme["use_image"] and theme["image_path"] and os.path.exists(theme["image_path"]):
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-image: url({theme["image_path"]});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {theme["bg"]};
                }}
            """)
    
    def show_theme_selector(self):
        """Показать диалог выбора темы"""
        dialog = ThemeSelectorDialog(self, self.current_theme, self.custom_image_path)
        if dialog.exec():
            self.current_theme = dialog.selected_theme
            self.custom_image_path = dialog.selected_image_path
            
            if self.custom_image_path and os.path.exists(self.custom_image_path):
                THEMES["custom"]["image_path"] = self.custom_image_path
            
            self.apply_theme(self.current_theme)
            
            # Обновляем главное меню
            self.central_stacked.removeWidget(self.main_menu_widget)
            self.main_menu_widget.deleteLater()
            self.main_menu_widget = self.create_main_menu()
            self.central_stacked.addWidget(self.main_menu_widget)
            self.central_stacked.setCurrentWidget(self.main_menu_widget)
            
            # Показываем уведомление
            theme_name = THEMES[self.current_theme]["name"]
            self.show_info_message("Тема оформления", f"Установлена тема: {theme_name}")
    
    def get_scene_statistics(self):
        """Получить реальную статистику сцен"""
        try:
            if not hasattr(self.scene_manager, 'scenes') or not self.scene_manager.scenes:
                return self.get_default_statistics()
            
            total_scenes = len(self.scene_manager.scenes)
            
            total_endings = 0
            success_endings = 0
            failure_endings = 0
            
            for scene in self.scene_manager.scenes.values():
                if hasattr(scene, 'is_ending') and scene.is_ending:
                    total_endings += 1
                    if hasattr(scene, 'game_over'):
                        if scene.game_over:
                            failure_endings += 1
                        else:
                            success_endings += 1
            
            if total_endings == 0:
                return self.get_default_statistics()
                
            return {
                "total_scenes": total_scenes,
                "total_endings": total_endings,
                "success_endings": success_endings,
                "failure_endings": failure_endings,
                "total_skills": 7,
                "career_paths": 3
            }
            
        except Exception as e:
            print(f"Ошибка при получении статистики сцен: {e}")
            return self.get_default_statistics()
    
    def get_default_statistics(self):
        """Получить статистику по умолчанию"""
        return {
            "total_scenes": 70,
            "total_endings": 12,
            "success_endings": 6,
            "failure_endings": 6,
            "total_skills": 7,
            "career_paths": 3
        }
    
    def create_main_menu(self):
        """Создать современное главное меню"""
        container = QWidget()
        container.setObjectName("mainMenuContainer")
        
        theme = THEMES[self.current_theme]
        
        if theme["use_image"] and theme["image_path"] and os.path.exists(theme["image_path"]):
            container.setStyleSheet(f"""
                QWidget#mainMenuContainer {{
                    background-image: url({theme["image_path"]});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """)
        else:
            container.setStyleSheet(f"""
                QWidget#mainMenuContainer {{
                    background: {theme["gradient"]};
                }}
            """)
        
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(40, 20, 40, 40)
        
        title_section = self.create_title_section()
        content_layout.addWidget(title_section)
        
        actions_section = self.create_actions_section()
        content_layout.addWidget(actions_section, 1)
        
        info_section = self.create_info_section()
        content_layout.addWidget(info_section)
        
        main_layout.addWidget(content_widget, 1)
        
        return container
    
    def create_top_bar(self):
        """Создать верхнюю панель с кнопками управления окном"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        
        theme = THEMES[self.current_theme]
        
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_overlay"]};
                border-bottom: 1px solid {theme["border"]};
            }}
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(20)
        
        # Логотип и название
        logo_label = QLabel("💰")
        logo_label.setFont(QFont("Segoe UI", 24))
        logo_label.setStyleSheet("color: #3b82f6;")
        logo_label.setToolTip("")  # Убираем подсказку
        
        title_label = QLabel("ЭКОНОМИЧЕСКАЯ СИМУЛЯЦИЯ")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {theme['text']};")
        title_label.setToolTip("")  # Убираем подсказку
        
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Версия
        version_label = QLabel(f"v{GAME_VERSION} Professional")
        version_label.setFont(QFont("Segoe UI", 10))
        version_label.setStyleSheet(f"color: {theme['text_secondary']};")
        version_label.setToolTip("")  # Убираем подсказку
        layout.addWidget(version_label)
        
        # Кнопка выбора темы
        theme_btn = QPushButton("🎨 Тема")
        theme_btn.setFont(QFont("Segoe UI", 11))
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setToolTip("")  # Убираем подсказку
        theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(139, 92, 246, 0.2);
                color: #8b5cf6;
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: rgba(139, 92, 246, 0.3);
                border: 1px solid rgba(139, 92, 246, 0.5);
            }}
        """)
        theme_btn.clicked.connect(self.show_theme_selector)
        layout.addWidget(theme_btn)
        
        # ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
        # Кнопка выбора режима
        mode_btn = QPushButton("🎮 Режим")
        mode_btn.setFont(QFont("Segoe UI", 11))
        mode_btn.setCursor(Qt.PointingHandCursor)
        mode_btn.setToolTip("")  # Убираем подсказку
        mode_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 8px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: rgba(16, 185, 129, 0.3);
                border: 1px solid rgba(16, 185, 129, 0.5);
            }}
        """)
        mode_btn.clicked.connect(self.show_mode_selector)
        layout.addWidget(mode_btn)
        
        # Кнопка полноэкранного режима
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFont(QFont("Segoe UI", 16))
        self.fullscreen_btn.setFixedSize(40, 40)
        self.fullscreen_btn.setCursor(Qt.PointingHandCursor)
        self.fullscreen_btn.setToolTip("")  # Убираем подсказку
        self.fullscreen_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(59, 130, 246, 0.3);
                border: 1px solid rgba(59, 130, 246, 0.5);
            }}
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        layout.addWidget(self.fullscreen_btn)
        
        # Кнопка ВЫХОДА
        exit_btn = QPushButton("✕")
        exit_btn.setFont(QFont("Segoe UI", 16))
        exit_btn.setFixedSize(40, 40)
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.setToolTip("")  # Убираем подсказку
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(239, 68, 68, 0.3);
                border: 1px solid rgba(239, 68, 68, 0.5);
            }}
        """)
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)
        
        return top_bar
    
    # ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
    def show_mode_selector(self):
        """Показать диалог выбора режима"""
        dialog = ModeSelectorDialog(self, self.current_theme)
        
        if dialog.exec() == QDialog.Accepted:
            if dialog.selected_mode == "server":
                # Запускаем серверный режим
                self.start_server_mode(dialog.server_config)
            else:
                # Обычный режим - показываем создание персонажа
                self.show_new_game_dialog()
    
    # ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
    def start_server_mode(self, config):
        """Запустить серверный режим с профессиональным UI"""
        from ui.server_dialog import ServerDialog
    
        dialog = ServerDialog(self, self.current_theme, config)
        dialog.exec()
    
    def toggle_fullscreen(self):
        """Переключить полноэкранный режим"""
        if self.is_fullscreen:
            self.showNormal()
            self.showMaximized()
            self.fullscreen_btn.setText("⛶")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("⧉")
        
        self.is_fullscreen = not self.is_fullscreen
    
    def create_title_section(self):
        """Создать секцию с заголовком"""
        widget = QWidget()
        widget.setFixedHeight(200)
        
        theme = THEMES[self.current_theme]
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 40)
        layout.setSpacing(15)
        
        # Главный заголовок
        main_title = QLabel("ПУТЬ К ФИНАНСОВОМУ УСПЕХУ")
        main_title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        main_title.setStyleSheet(f"""
            color: {theme['text']};
        """)
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setToolTip("")  # Убираем подсказку
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(59, 130, 246, 100))
        shadow.setOffset(0, 0)
        main_title.setGraphicsEffect(shadow)
        
        # Подзаголовок
        subtitle = QLabel("Принимайте стратегические решения и стройте карьеру мечты")
        subtitle.setFont(QFont("Segoe UI", 16))
        subtitle.setStyleSheet(f"color: {theme['text_secondary']};")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setToolTip("")  # Убираем подсказку
        
        layout.addWidget(main_title)
        layout.addWidget(subtitle)
        
        return widget
    
    def create_actions_section(self):
        """Создать секцию с карточками действий"""
        widget = QWidget()
        
        layout = QGridLayout(widget)
        layout.setSpacing(25)
        layout.setContentsMargins(0, 0, 0, 30)
        
        cards = [
            {
                "icon": "🚀",
                "title": "Новая игра",
                "description": "Начните свой путь к финансовому успеху",
                "color": "#3b82f6",
                "hover_color": "#2563eb",
                "action": self.show_new_game_dialog
            },
            {
                "icon": "📂",
                "title": "Загрузить игру",
                "description": "Продолжите с сохранённой позиции",
                "color": "#8b5cf6",
                "hover_color": "#7c3aed",
                "action": self.show_load_dialog
            },
            {
                "icon": "📊",
                "title": "Статистика",
                "description": "Анализ ваших достижений и результатов",
                "color": "#10b981",
                "hover_color": "#059669",
                "action": self.show_stats
            },
            {
                "icon": "🎨",
                "title": "Оформление",
                "description": "Настройте тему и фоновое изображение",
                "color": "#8b5cf6",
                "hover_color": "#7c3aed",
                "action": self.show_theme_selector
            },
            {
                "icon": "📚",
                "title": "Обучение",
                "description": "Изучите основы экономики и менеджмента",
                "color": "#ec4899",
                "hover_color": "#db2777",
                "action": self.show_tutorial
            },
            {
                "icon": "🚪",
                "title": "Выход",
                "description": "Завершить работу с приложением",
                "color": "#ef4444",
                "hover_color": "#dc2626",
                "action": self.close
            }
        ]
        
        for i, card_data in enumerate(cards):
            row = i // 3
            col = i % 3
            card = self.create_action_card(card_data)
            layout.addWidget(card, row, col)
        
        return widget
    
    def create_action_card(self, card_data):
        """Создать карточку действия"""
        card = QFrame()
        card.setMinimumSize(300, 170)
        card.setMaximumSize(400, 200)
        card.setCursor(Qt.PointingHandCursor)
        card.setObjectName("actionCard")
        card.setToolTip("")  # Убираем подсказку
        
        theme = THEMES[self.current_theme]
        
        if self.current_theme == "light":
            card.setStyleSheet(f"""
                QFrame#actionCard {{
                    background-color: rgba(245, 248, 250, 0.95);
                    border: 1px solid #e2e8f0;
                    border-radius: 18px;
                    padding: 20px;
                }}
                QFrame#actionCard:hover {{
                    background-color: rgba(235, 245, 255, 0.98);
                    border: 1px solid {card_data['color']};
                }}
            """)
        else:
            card.setStyleSheet(f"""
                QFrame#actionCard {{
                    background-color: {theme["bg_card"]};
                    border: 1px solid {theme["border"]};
                    border-radius: 18px;
                    padding: 20px;
                }}
                QFrame#actionCard:hover {{
                    background-color: {theme["bg_hover"]};
                    border: 1px solid {card_data['color']};
                }}
            """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Верхняя часть с иконкой и заголовком
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(card_data["icon"])
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setStyleSheet(f"color: {card_data['color']}; background-color: transparent;")
        icon_label.setMinimumWidth(40)
        icon_label.setToolTip("")  # Убираем подсказку
        
        title_label = QLabel(card_data["title"])
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        title_label.setWordWrap(True)
        title_label.setToolTip("")  # Убираем подсказку
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label, 1)
        
        # Описание
        desc_label = QLabel(card_data["description"])
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet(f"color: {theme['text_secondary']}; background-color: transparent;")
        desc_label.setWordWrap(True)
        desc_label.setToolTip("")  # Убираем подсказку
        
        # Индикатор наведения
        hover_indicator = QFrame()
        hover_indicator.setFixedHeight(3)
        hover_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {card_data['color']};
                border-radius: 1.5px;
            }}
        """)
        hover_indicator.setToolTip("")  # Убираем подсказку
        
        layout.addLayout(top_layout)
        layout.addWidget(desc_label, 1)
        layout.addWidget(hover_indicator)
        
        def on_click():
            self.animate_card_click(card)
            QTimer.singleShot(150, card_data["action"])
        
        overlay_btn = QPushButton(card)
        overlay_btn.setGeometry(card.rect())
        overlay_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)
        overlay_btn.setToolTip("")  # Убираем подсказку
        overlay_btn.clicked.connect(on_click)
        
        return card
    
    def animate_card_click(self, card):
        """Анимация нажатия карточки"""
        animation = QPropertyAnimation(card, b"geometry")
        animation.setDuration(100)
        animation.setStartValue(card.geometry())
        animation.setEndValue(card.geometry().adjusted(0, 2, 0, 2))
        animation.setEasingCurve(QEasingCurve.OutQuad)
        
        animation2 = QPropertyAnimation(card, b"geometry")
        animation2.setDuration(100)
        animation2.setStartValue(card.geometry().adjusted(0, 2, 0, 2))
        animation2.setEndValue(card.geometry())
        animation2.setEasingCurve(QEasingCurve.InQuad)
        
        animation.finished.connect(lambda: animation2.start())
        animation.start()
    
    def create_info_section(self):
        """Создать информационную секцию"""
        widget = QFrame()
        widget.setFixedHeight(100)
        
        theme = THEMES[self.current_theme]
        
        if self.current_theme == "light":
            widget.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(245, 248, 250, 0.95);
                    border-radius: 15px;
                    border: 1px solid #e2e8f0;
                }}
            """)
        else:
            widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme["bg_overlay"]};
                    border-radius: 15px;
                    border: 1px solid {theme["border"]};
                }}
            """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(40)
        
        stats = self.get_scene_statistics()
        
        stats_items = [
            ("🎮", f"{stats['total_scenes']} сцен", "#3b82f6"),
            ("🏆", f"{stats['total_endings']} концовок", "#8b5cf6"),
            ("📈", f"{stats['total_skills']} навыков", "#10b981"),
            ("👥", f"{stats['career_paths']} путей", "#ec4899"),
        ]
        
        for icon, text, color in stats_items:
            item_widget = QWidget()
            item_widget.setStyleSheet("background-color: transparent;")
            item_widget.setToolTip("")  # Убираем подсказку
            item_layout = QHBoxLayout(item_widget)
            item_layout.setSpacing(10)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 16))
            icon_label.setStyleSheet(f"color: {color}; background-color: transparent;")
            icon_label.setToolTip("")  # Убираем подсказку
            
            text_label = QLabel(text)
            text_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
            text_label.setStyleSheet(f"color: {theme['text_secondary']}; background-color: transparent;")
            text_label.setToolTip("")  # Убираем подсказку
            
            item_layout.addWidget(icon_label)
            item_layout.addWidget(text_label)
            item_layout.addStretch()
            
            layout.addWidget(item_widget)
        
        layout.addStretch()
        
        from config import TEXTS
        copyright_label = QLabel(TEXTS["copyright"])
        copyright_label.setFont(QFont("Segoe UI", 10))
        copyright_label.setStyleSheet(f"color: {theme.get('text_muted', '#64748b')}; background-color: transparent;")
        copyright_label.setToolTip("")  # Убираем подсказку
        layout.addWidget(copyright_label)
        
        return widget
    
    def show_stats(self):
        """Показать окно статистики"""
        stats_window = StatsWindow(self.game_engine, self)
        stats_window.setWindowModality(Qt.WindowModal)
        stats_window.exec()
    
    def show_new_game_dialog(self):
        """Показать современный диалог создания новой игры"""
        dialog = ModernDialog(self, "Создание персонажа", self.current_theme)
        dialog.setFixedSize(500, 400)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        theme = THEMES[self.current_theme]
        
        # Заголовок
        title = QLabel("👤 СОЗДАНИЕ ПЕРСОНАЖА")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        title.setAlignment(Qt.AlignCenter)
        title.setToolTip("")  # Убираем подсказку
        layout.addWidget(title)
        
        # Поле для имени
        name_group = self.create_input_group("Ваше имя:", "Введите имя персонажа...")
        layout.addWidget(name_group)
        
        # Поле для возраста
        age_group = self.create_input_group("Возраст:", "25", True)
        layout.addWidget(age_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        create_btn = self.create_dialog_button("Создать и начать", "#10b981", "#059669")
        cancel_btn = self.create_dialog_button("Отмена", "#64748b", "#475569")
        
        create_btn.setToolTip("")  # Убираем подсказку
        cancel_btn.setToolTip("")  # Убираем подсказку
        
        create_btn.clicked.connect(lambda: self.create_character(dialog, name_group.findChild(QLineEdit), age_group.findChild(QLineEdit)))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        dialog.set_content(content)
        
        if dialog.exec() == QDialog.Accepted:
            self.start_game_session()
    
    def create_input_group(self, label_text, placeholder, is_age=False):
        """Создать группу ввода"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        theme = THEMES[self.current_theme]
        widget.setStyleSheet(f"background-color: transparent;")
        widget.setToolTip("")  # Убираем подсказку
        
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 12))
        label.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        label.setToolTip("")  # Убираем подсказку
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFont(QFont("Segoe UI", 12))
        line_edit.setMinimumHeight(45)
        line_edit.setToolTip("")  # Убираем подсказку
        
        if is_age:
            line_edit.setText("25")
        
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme["bg_card"]};
                border: 2px solid {theme["border"]};
                border-radius: 10px;
                padding: 10px 15px;
                color: {theme["text"]};
                selection-background-color: #3b82f6;
            }}
            QLineEdit:focus {{
                border-color: #3b82f6;
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(line_edit)
        
        return widget
    
    def create_dialog_button(self, text, color, hover_color):
        """Создать кнопку для диалога"""
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setMinimumWidth(120)
        btn.setFont(QFont("Segoe UI", 11, QFont.Medium))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("")  # Убираем подсказку
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 25px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
        """)
        btn.setAutoDefault(False)
        return btn
    
    def create_character(self, dialog, name_input, age_input):
        """Создать персонажа"""
        name = name_input.text().strip()
        age_text = age_input.text().strip()
        
        if not name:
            self.show_error_message("Введите имя персонажа")
            return
        
        try:
            age = int(age_text) if age_text else 25
            if age < 18 or age > 100:
                self.show_error_message("Возраст должен быть от 18 до 100 лет")
                return
        except ValueError:
            self.show_error_message("Возраст должен быть числом")
            return
        
        if self.game_engine.new_game(name, age):
            dialog.accept()
        else:
            self.show_error_message("Не удалось создать игру")
    
    def show_error_message(self, message):
        """Показать сообщение об ошибке"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QMessageBox QLabel {
                color: #f8fafc;
            }
            QMessageBox QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        msg_box.exec()
    
    def show_load_dialog(self):
        """Показать диалог загрузки (заглушка)"""
        self.show_info_message("Функция загрузки", "Система загрузки игр в разработке")
    
    def show_tutorial(self):
        """Показать обучение (заглушка)"""
        self.show_info_message("Обучение", "Раздел обучения в разработке")
    
    def show_info_message(self, title, message):
        """Показать информационное сообщение"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QMessageBox QLabel {
                color: #f8fafc;
            }
            QMessageBox QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        msg_box.exec()
    
    def start_game_session(self):
        """Начать игровую сессию"""
        self.game_widget = GameUI(self.game_engine, self, self.current_theme)
        self.central_stacked.addWidget(self.game_widget)
        self.central_stacked.setCurrentWidget(self.game_widget)
    
    def return_to_main_menu(self):
        """Вернуться в главное меню"""
        if self.game_engine.player and self.game_engine.state.value == "playing":
            reply = QMessageBox.question(
                self,
                "Выход в меню",
                "Текущий прогресс будет потерян. Продолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.game_engine.state = self.game_engine.state.MENU
        self.game_engine.player = None
        
        if self.game_widget:
            self.central_stacked.removeWidget(self.game_widget)
            self.game_widget.deleteLater()
            self.game_widget = None
        
        self.central_stacked.setCurrentWidget(self.main_menu_widget)


def main():
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 23, 42))
    palette.setColor(QPalette.WindowText, QColor(248, 250, 252))
    palette.setColor(QPalette.Base, QColor(30, 41, 59))
    palette.setColor(QPalette.AlternateBase, QColor(15, 23, 42))
    palette.setColor(QPalette.ToolTipBase, QColor(248, 250, 252))
    palette.setColor(QPalette.ToolTipText, QColor(15, 23, 42))
    palette.setColor(QPalette.Text, QColor(248, 250, 252))
    palette.setColor(QPalette.Button, QColor(30, 41, 59))
    palette.setColor(QPalette.ButtonText, QColor(248, 250, 252))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
