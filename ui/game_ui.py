"""
Игровой интерфейс для экономической симуляции
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTextEdit, QFrame, QProgressBar, QSplitter,
                               QGroupBox, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from config import GAME_VERSION, THEMES
from ui.game_ui_base import ImageWithBorderLabel, GameUIBase, GraphWidget
from scenes.scenes_data import SCENES_DATA
import os


class GameUI(QWidget, GameUIBase):
    """Игровой интерфейс"""
    
    def __init__(self, game_engine, parent_window, current_theme="dark"):
        super().__init__()
        self.game_engine = game_engine
        self.parent_window = parent_window
        self.current_theme = current_theme
        self.scene_history = []  # История посещенных сцен
        self.setup_ui()
        self.load_current_scene()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        theme = THEMES[self.current_theme]
        
        if theme["use_image"] and theme.get("image_path") and os.path.exists(theme["image_path"]):
            self.setStyleSheet(f"""
                QWidget {{
                    background-image: url({theme["image_path"]});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme["bg"]};
                }}
            """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Панель навигации
        nav_bar = self.create_navigation_bar(theme)
        main_layout.addWidget(nav_bar)
        
        # Разделитель на три колонки
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {theme["border"]};
            }}
        """)
        
        # ЛЕВАЯ КОЛОНКА - Граф ветвления
        left_widget = self.create_graph_widget(theme)
        
        # ЦЕНТРАЛЬНАЯ КОЛОНКА - Игровой контент
        center_widget = self.create_center_column(theme)
        
        # ПРАВАЯ КОЛОНКА - Навыки и статистика
        right_widget = self.create_right_column(theme)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(center_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter, 1)
        
        # Статусная строка внизу
        self.status_label = QLabel("Готов к игре...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet(f"""
            color: {theme['text_secondary']}; 
            padding: 10px 40px; 
            background-color: {theme['bg_overlay']};
        """)
        main_layout.addWidget(self.status_label)
    
    def create_navigation_bar(self, theme):
        """Создать панель навигации"""
        nav_bar = QFrame()
        nav_bar.setFixedHeight(60)
        nav_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_overlay"]};
                border-bottom: 1px solid {theme["border"]};
            }}
        """)
        
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(30, 0, 30, 0)
        
        # Кнопка возврата
        back_btn = QPushButton("← Назад в меню")
        back_btn.setFont(QFont("Segoe UI", 11))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme["text_secondary"]};
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {theme["text"]};
            }}
        """)
        back_btn.clicked.connect(self.parent_window.return_to_main_menu)
        
        # Сохранить игру
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setFont(QFont("Segoe UI", 11))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(59, 130, 246, 0.3);
            }}
        """)
        save_btn.clicked.connect(self.save_game)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(save_btn)
        nav_layout.addStretch()
        
        # Статус игры
        self.game_status_label = QLabel("ИГРОВОЙ ПРОЦЕСС")
        self.game_status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.game_status_label.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        nav_layout.addWidget(self.game_status_label)
        nav_layout.addStretch()
        
        # Информация о дне и деньгах
        self.day_label = QLabel("День: 1")
        self.day_label.setFont(QFont("Segoe UI", 11))
        self.day_label.setStyleSheet(f"color: {theme['text_secondary']}; padding-right: 20px; background-color: transparent;")
        
        self.money_label = QLabel("💰 10,000 ₽")
        self.money_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.money_label.setStyleSheet("color: #10b981; background-color: transparent;")
        
        nav_layout.addWidget(self.day_label)
        nav_layout.addWidget(self.money_label)
        
        return nav_bar
    
    def create_graph_widget(self, theme):
        """Создать левую колонку с графом ветвления"""
        graph_widget = QWidget()
        graph_widget.setStyleSheet("background-color: transparent;")
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setSpacing(0)
        graph_layout.setContentsMargins(10, 5, 10, 10)
        
        # Заголовок
        title = QLabel("🌐 ГРАФ СЮЖЕТА")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {theme['text']}; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        graph_layout.addWidget(title)
        
        # Граф ветвления
        self.graph_widget = GraphWidget(theme)
        graph_layout.addWidget(self.graph_widget)
        
        return graph_widget
    
    def create_center_column(self, theme):
        """Создать центральную колонку с игровым контентом"""
        center_widget = QWidget()
        center_widget.setStyleSheet("background-color: transparent;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(0)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок сцены
        self.scene_title_label = QLabel()
        self.scene_title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.scene_title_label.setStyleSheet(f"""
            color: {theme['text']};
            padding: 30px 40px 10px 40px;
            background-color: transparent;
        """)
        self.scene_title_label.setWordWrap(True)
        
        # Текст сцены
        self.scene_text_edit = QTextEdit()
        self.scene_text_edit.setFont(QFont("Segoe UI", 18))
        self.scene_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme["bg_card"]};
                color: {theme["text_secondary"]};
                border: none;
                padding: 20px 40px;
                line-height: 1.6;
            }}
        """)
        self.scene_text_edit.setReadOnly(True)
        
        # Картинка с жирной черной рамкой
        self.image_frame = QFrame()
        self.image_frame.setFixedHeight(250)
        self.image_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                margin: 10px 40px;
            }
        """)
        
        image_layout = QHBoxLayout(self.image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene_image_label = ImageWithBorderLabel()
        self.scene_image_label.setAlignment(Qt.AlignCenter)
        self.scene_image_label.setStyleSheet("background-color: transparent;")
        self.scene_image_label.setText("🖼️")
        self.scene_image_label.setFont(QFont("Segoe UI", 24))
        
        image_layout.addWidget(self.scene_image_label)
        
        # Кнопки выбора вариантов ответа
        self.choices_widget = QWidget()
        self.choices_widget.setStyleSheet("background-color: transparent;")
        self.choices_layout = QVBoxLayout(self.choices_widget)
        self.choices_layout.setSpacing(4)
        self.choices_layout.setContentsMargins(40, 5, 40, 20)
        
        center_layout.addWidget(self.scene_title_label)
        center_layout.addWidget(self.scene_text_edit)
        center_layout.addWidget(self.image_frame)
        center_layout.addWidget(self.choices_widget, 1)
        
        return center_widget
    
    def create_right_column(self, theme):
        """Создать правую колонку с навыками и статистикой"""
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(20, 30, 20, 30)
        
        # Навыки игрока
        skills_group = QGroupBox("🎯 НАВЫКИ ПЕРСОНАЖА")
        skills_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        skills_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme['text']};
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {theme["bg_card"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {theme['text']};
            }}
        """)
        
        skills_layout = QVBoxLayout(skills_group)
        
        # Используем метод из базового класса для создания прогресс-баров
        self.skill_bars = self.setup_skill_bars(skills_group, theme)
        
        # Достижения
        self.achievements_label = QLabel("🏆 ДОСТИЖЕНИЙ: 0")
        self.achievements_label.setFont(QFont("Segoe UI", 11))
        self.achievements_label.setStyleSheet(f"""
            color: #f59e0b; 
            padding: 10px; 
            background-color: {theme['bg_card']}; 
            border-radius: 8px;
        """)
        
        # Имя игрока
        self.player_name_label = QLabel()
        self.player_name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.player_name_label.setStyleSheet(f"""
            color: {theme['text']}; 
            padding: 10px; 
            background-color: {theme['bg_card']}; 
            border-radius: 8px;
        """)
        
        right_layout.addWidget(skills_group)
        right_layout.addWidget(self.achievements_label)
        right_layout.addWidget(self.player_name_label)
        right_layout.addStretch()
        
        return right_widget
    
    def set_scene_image(self, image_path):
        """Установить изображение для текущей сцены"""
        if os.path.exists(image_path):
            return self.scene_image_label.set_image(image_path)
        return False
    
    def load_current_scene(self):
        """Загрузить текущую сцену в интерфейс"""
        if not self.game_engine.player:
            self.show_error_message(self, "Ошибка: игрок не найден!")
            QTimer.singleShot(1000, self.parent_window.return_to_main_menu)
            return
        
        self.update_player_info()
        
        scene = self.game_engine.get_current_scene()
        if not scene:
            self.show_error_message(self, "Ошибка: сцена не найдена!")
            self.status_label.setText(f"Сцена не найдена: {self.game_engine.player.current_scene_id}")
            self.show_scene_not_found()
            return
        
        self.scene_title_label.setText(f"📖 {scene.title}")
        
        scene_text = f"{scene.description}\n\n"
        if scene.is_ending:
            scene_text += "\n\n" + "═" * 50 + "\n🎮 ИГРА ЗАВЕРШЕНА!\n"
            if scene.game_over:
                scene_text += "❌ Вы не достигли успеха\n"
            else:
                scene_text += "✅ Поздравляем с успешным завершением!\n"
            scene_text += "═" * 50
        
        self.scene_text_edit.setHtml(f"""
            <div style="color: #cbd5e1; font-size: 18pt; line-height: 1.6;">
                {scene_text.replace('\n', '<br>')}
            </div>
        """)
        
        scene_image_path = os.path.join("assets", "scenes", f"{scene.scene_id}.jpg")
        if not self.set_scene_image(scene_image_path):
            default_image = os.path.join("assets", "scene_background.jpg")
            self.set_scene_image(default_image)
        
        self.clear_choices()
        
        # Построить граф при первой загрузке
        if not self.graph_widget.nodes:
            self.graph_widget.build_from_scenes(SCENES_DATA, scene.scene_id)
        else:
            # Обновить текущий узел
            self.graph_widget.set_current_node(scene.scene_id)
            # Сбрасываем флаг проигрыша
            self.graph_widget.set_game_over(False)
        
        if scene.is_ending:
            self.show_game_over(scene)
            return
        
        available_choices = self.game_engine.get_available_choices()
        if not available_choices:
            self.show_error_message(self, "Нет доступных выборов!")
            menu_btn = QPushButton("🏠 Вернуться в главное меню")
            menu_btn.clicked.connect(self.parent_window.return_to_main_menu)
            self.choices_layout.addWidget(menu_btn)
            return
        
        theme = THEMES[self.current_theme]
        
        for i, choice in enumerate(available_choices):
            choice_btn = QPushButton(choice.text)
            choice_btn.setFont(QFont("Segoe UI", 11))
            choice_btn.setCursor(Qt.PointingHandCursor)
            choice_btn.setMinimumHeight(60)
            
            is_available = choice.is_available(self.game_engine.player.skills)
            
            tooltip_text = ""
            if choice.required_skill:
                subject, level = choice.required_skill
                current = self.game_engine.player.skills.get_skill(subject)
                if current < level:
                    tooltip_text += f"Требуется {subject.value} {level}+ (у вас {current})\n"
            
            if choice.money_cost > 0:
                tooltip_text += f"Стоимость: {choice.money_cost} ₽\n"
            
            if tooltip_text:
                choice_btn.setToolTip(tooltip_text.strip())
            
            if is_available:
                choice_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(30, 41, 59, 0.7);
                        color: {theme['text']};
                        border: 1px solid {theme['border']};
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(30, 41, 59, 0.9);
                        border: 1px solid #3b82f6;
                    }}
                """)
                choice_btn.clicked.connect(lambda checked, idx=i: self.make_choice(idx))
            else:
                choice_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(30, 41, 59, 0.4);
                        color: {theme['text_secondary']};
                        border: 1px solid {theme['border']};
                        border-radius: 10px;
                        padding: 15px;
                        text-align: left;
                    }}
                """)
                choice_btn.setEnabled(False)
            
            self.choices_layout.addWidget(choice_btn)
        
        menu_btn = QPushButton("⚙️ Меню игры")
        menu_btn.setFont(QFont("Segoe UI", 11))
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(30, 41, 59, 0.7);
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(30, 41, 59, 0.9);
                border: 1px solid #3b82f6;
            }}
        """)
        menu_btn.clicked.connect(self.show_game_menu)
        self.choices_layout.addWidget(menu_btn)
    
    def make_choice(self, choice_index):
        """Сделать выбор"""
        if not self.game_engine.player:
            self.show_error_message(self, "Нет активного игрока!")
            return False
        
        old_skills = {}
        if self.game_engine.player.skills:
            old_skills = {
                'economics': self.game_engine.player.skills.economics,
                'management': self.game_engine.player.skills.management,
                'finance': self.game_engine.player.skills.finance,
                'marketing': self.game_engine.player.skills.marketing,
                'happiness': self.game_engine.player.skills.happiness,
                'health': self.game_engine.player.skills.health,
                'reputation': self.game_engine.player.skills.reputation,
                'money': self.game_engine.player.skills.money
            }
        
        success = self.game_engine.make_choice(choice_index)
        if not success:
            self.show_error_message(self, "Этот выбор недоступен!")
            return False
        
        if not self.game_engine.player:
            self.show_error_message(self, "Игровая сессия завершена!")
            QTimer.singleShot(2000, self.parent_window.return_to_main_menu)
            return True
        
        self.update_player_info()
        
        if self.game_engine.player and self.game_engine.player.skills:
            new_skills = {
                'economics': self.game_engine.player.skills.economics,
                'management': self.game_engine.player.skills.management,
                'finance': self.game_engine.player.skills.finance,
                'marketing': self.game_engine.player.skills.marketing,
                'happiness': self.game_engine.player.skills.happiness,
                'health': self.game_engine.player.skills.health,
                'reputation': self.game_engine.player.skills.reputation,
                'money': self.game_engine.player.skills.money
            }
            
            changes_text = "📊 Изменения навыков:\n"
            changes_found = False
            for skill_name in old_skills.keys():
                old_val = old_skills[skill_name]
                new_val = new_skills[skill_name]
                if old_val != new_val:
                    diff = new_val - old_val
                    sign = "+" if diff > 0 else ""
                    changes_text += f"  {self.get_skill_display_name(skill_name)}: {sign}{diff}\n"
                    changes_found = True
            
            if changes_found:
                self.show_info_message(self, "Результат выбора", changes_text)
        
        if self.game_engine.player:
            self.status_label.setText(f"Выбор сделан. День {self.game_engine.player.day}")
        
        QTimer.singleShot(100, self.load_current_scene)
        return True
    
    def show_scene_not_found(self):
        """Показать экран при отсутствии сцены"""
        self.clear_choices()
        
        theme = THEMES[self.current_theme]
        
        error_widget = QWidget()
        error_widget.setStyleSheet("background-color: transparent;")
        error_layout = QVBoxLayout(error_widget)
        error_layout.setSpacing(20)
        error_layout.setContentsMargins(40, 40, 40, 40)
        
        error_title = QLabel("❌ Сцена не найдена")
        error_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        error_title.setStyleSheet("color: #ef4444; background-color: transparent;")
        error_title.setAlignment(Qt.AlignCenter)
        
        scene_id = self.game_engine.player.current_scene_id if self.game_engine.player else "unknown"
        message = QLabel(f"Сцена с ID '{scene_id}' не существует в базе данных.")
        message.setFont(QFont("Segoe UI", 14))
        message.setStyleSheet(f"color: {theme['text_secondary']}; background-color: transparent;")
        message.setWordWrap(True)
        
        button_layout = QHBoxLayout()
        
        restart_btn = QPushButton("🔄 Начать новую игру")
        restart_btn.setFont(QFont("Segoe UI", 12))
        restart_btn.setMinimumHeight(50)
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        restart_btn.clicked.connect(self.parent_window.return_to_main_menu)
        
        menu_btn = QPushButton("🏠 В главное меню")
        menu_btn.setFont(QFont("Segoe UI", 12))
        menu_btn.setMinimumHeight(50)
        menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        menu_btn.clicked.connect(self.parent_window.return_to_main_menu)
        
        button_layout.addWidget(restart_btn)
        button_layout.addWidget(menu_btn)
        
        error_layout.addWidget(error_title)
        error_layout.addWidget(message)
        error_layout.addLayout(button_layout)
        
        self.choices_layout.addWidget(error_widget)
    
    def update_player_info(self):
        """Обновить информацию о игроке в интерфейсе"""
        theme = THEMES[self.current_theme]
        
        if not self.game_engine.player:
            self.player_name_label.setText("Игрок не найден")
            self.day_label.setText("День: ?")
            self.money_label.setText("💰 0 ₽")
            return
        
        player = self.game_engine.player
        
        self.day_label.setText(f"📅 День: {player.day}")
        self.money_label.setText(f"💰 {player.skills.money:,} ₽")
        
        for skill_key, progress_bar in self.skill_bars.items():
            skill_value = getattr(player.skills, skill_key)
            progress_bar.setValue(skill_value)
            
            color = self.get_skill_color(skill_value)
            
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                    text-align: center;
                    background-color: rgba(255, 255, 255, 0.05);
                    color: #f8fafc;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 5px;
                }}
            """)
        
        achievements_count = len(player.achievements)
        self.achievements_label.setText(f"🏆 ДОСТИЖЕНИЙ: {achievements_count}")
        self.player_name_label.setText(f"👤 {player.name}, {player.age} лет")
    
    def clear_choices(self):
        """Очистить кнопки выбора"""
        while self.choices_layout.count():
            item = self.choices_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_game_over(self, scene):
        """Показать экран завершения игры"""
        self.clear_choices()
        
        theme = THEMES[self.current_theme]
        
        # Устанавливаем красный цвет для графа при проигрыше
        if scene.game_over:
            self.graph_widget.set_game_over(True)
        
        result_widget = QWidget()
        result_widget.setStyleSheet(f"background-color: {theme['bg_card']}; border-radius: 10px;")
        result_layout = QVBoxLayout(result_widget)
        result_layout.setSpacing(20)
        result_layout.setContentsMargins(40, 40, 40, 40)
        
        if scene.game_over:
            result_title = QLabel("❌ ИГРА ЗАВЕРШЕНА - ПОРАЖЕНИЕ")
            result_title.setStyleSheet("color: #ef4444; background-color: transparent;")
        else:
            result_title = QLabel("✅ ИГРА ЗАВЕРШЕНА - ПОБЕДА!")
            result_title.setStyleSheet("color: #10b981; background-color: transparent;")
        
        result_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        result_title.setAlignment(Qt.AlignCenter)
        
        stats_text = ""
        if self.game_engine.player:
            stats_text = f"""
            <div style='color: {theme["text_secondary"]}; font-size: 14pt;'>
                <p><b>📊 Результат:</b> {'✅ Победа!' if not scene.game_over else '❌ Поражение'}</p>
                <p><b>👤 Игрок:</b> {self.game_engine.player.name}</p>
                <p><b>📅 Дней игры:</b> {self.game_engine.player.day}</p>
                <p><b>💰 Финальные деньги:</b> {self.game_engine.player.skills.money:,} ₽</p>
                <p><b>🏆 Достижений:</b> {len(self.game_engine.player.achievements)}</p>
            </div>
            """
        
        stats_label = QLabel()
        stats_label.setTextFormat(Qt.RichText)
        stats_label.setText(stats_text)
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet("background-color: transparent;")
        
        button_layout = QHBoxLayout()
        
        restart_btn = QPushButton("🔄 Новая игра")
        restart_btn.setFont(QFont("Segoe UI", 12))
        restart_btn.setMinimumHeight(50)
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        restart_btn.clicked.connect(self.parent_window.return_to_main_menu)
        
        stats_btn = QPushButton("📊 Статистика")
        stats_btn.setFont(QFont("Segoe UI", 12))
        stats_btn.setMinimumHeight(50)
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        stats_btn.clicked.connect(self.parent_window.show_stats)
        
        menu_btn = QPushButton("🏠 В главное меню")
        menu_btn.setFont(QFont("Segoe UI", 12))
        menu_btn.setMinimumHeight(50)
        menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        menu_btn.clicked.connect(self.parent_window.return_to_main_menu)
        
        button_layout.addWidget(restart_btn)
        button_layout.addWidget(stats_btn)
        button_layout.addWidget(menu_btn)
        
        result_layout.addWidget(result_title)
        result_layout.addWidget(stats_label)
        result_layout.addLayout(button_layout)
        
        self.choices_layout.addWidget(result_widget)
        
        if scene.game_over:
            self.game_status_label.setText("❌ ИГРА ОКОНЧЕНА - ПОРАЖЕНИЕ")
            self.status_label.setText("Игра завершена с поражением")
        else:
            self.game_status_label.setText("✅ ИГРА ОКОНЧЕНА - ПОБЕДА!")
            self.status_label.setText("Игра успешно завершена!")
        
        if self.game_engine.player:
            self.game_engine.save_game_result(not scene.game_over)
    
    def show_game_menu(self):
        """Показать меню игры"""
        try:
            from ui.dialogs import ModernDialog
        except ImportError:
            self.show_simple_game_menu()
            return
        
        dialog = ModernDialog(self.parent_window, "Меню игры", self.current_theme)
        dialog.setFixedSize(600, 500)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        theme = THEMES[self.current_theme]
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel("⚙️ МЕНЮ ИГРЫ")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"""
            color: {theme['text']};
            padding: 15px;
            background-color: {theme['bg_card']};
            border: 1px solid {theme['border']};
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопки
        button_style = f"""
            QPushButton {{
                background-color: {theme['bg_card']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 20px 25px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_hover']};
                border: 1px solid #3b82f6;
            }}
            QPushButton:pressed {{
                background-color: {theme['bg_card']};
            }}
        """
        
        # Кнопка сохранения
        save_btn = QPushButton("💾   СОХРАНИТЬ ИГРУ")
        save_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        save_btn.setMinimumHeight(70)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(button_style)
        save_btn.clicked.connect(lambda: (self.save_game(), dialog.accept()))
        layout.addWidget(save_btn)
        
        # Кнопка статистики
        stats_btn = QPushButton("📊   СТАТИСТИКА")
        stats_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        stats_btn.setMinimumHeight(70)
        stats_btn.setCursor(Qt.PointingHandCursor)
        stats_btn.setStyleSheet(button_style)
        stats_btn.clicked.connect(lambda: (self.parent_window.show_stats(), dialog.accept()))
        layout.addWidget(stats_btn)
        
        # Кнопка возврата в главное меню
        menu_btn = QPushButton("🏠   ГЛАВНОЕ МЕНЮ")
        menu_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        menu_btn.setMinimumHeight(70)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet(button_style)
        menu_btn.clicked.connect(lambda: (self.parent_window.return_to_main_menu(), dialog.accept()))
        layout.addWidget(menu_btn)
        
        # Кнопка отмены
        cancel_btn = QPushButton("✕   ОТМЕНА")
        cancel_btn.setFont(QFont("Segoe UI", 12))
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid #ef4444;
                color: #ef4444;
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)
        
        dialog.set_content(content)
        dialog.exec()
    
    def show_simple_game_menu(self):
        """Показать простое меню игры (fallback)"""
        self.clear_choices()
        
        theme = THEMES[self.current_theme]
        
        menu_widget = QWidget()
        menu_widget.setStyleSheet(f"background-color: {theme['bg_card']}; border-radius: 10px;")
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setSpacing(15)
        menu_layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("⚙️ МЕНЮ ИГРЫ")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        title.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(title)
        
        buttons = [
            ("💾 Сохранить игру", self.save_game, "#10b981"),
            ("📊 Статистика", self.parent_window.show_stats, "#8b5cf6"),
            ("🏠 В главное меню", self.parent_window.return_to_main_menu, "#64748b"),
        ]
        
        for text, action, color in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Segoe UI", 12))
            btn.setMinimumHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(action)
            menu_layout.addWidget(btn)
        
        back_btn = QPushButton("← Вернуться к игре")
        back_btn.setFont(QFont("Segoe UI", 12))
        back_btn.setMinimumHeight(50)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #64748b;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: #475569;
            }}
        """)
        back_btn.clicked.connect(lambda: self.load_current_scene())
        menu_layout.addWidget(back_btn)
        
        self.choices_layout.addWidget(menu_widget)
    
    def save_game(self):
        """Сохранить игру"""
        if not self.game_engine.player:
            self.show_error_message(self, "Нет активной игры для сохранения")
            return
        
        try:
            from core.models import GameSave
            game_save = GameSave(
                player=self.game_engine.player,
                game_version=GAME_VERSION
            )
            
            result = self.game_engine.save_manager.save_game(game_save, f"manual_{self.game_engine.player.name}")
            if result:
                self.status_label.setText(f"✅ Игра сохранена: {self.game_engine.player.name}")
                self.show_info_message(self, "Сохранение", "Игра успешно сохранена!")
            else:
                self.show_error_message(self, "Ошибка при сохранении игры")
        except Exception as e:
            self.show_error_message(self, f"Ошибка сохранения: {str(e)}")
