"""
Окно статистики с историей игр
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QPushButton, 
                               QHeaderView, QTabWidget, QWidget, QFrame,
                               QScrollArea, QGridLayout, QProgressBar, QScrollBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

from core.game_engine import GameEngine
from core.save_manager import SaveManager
from config import GAME_NAME, GAME_VERSION, THEMES  # ИЗМЕНЕНО: убрали COLORS, FONTS, добавили THEMES


class StatsWindow(QDialog):
    """Расширенное окно статистики с историей игр"""
    
    def __init__(self, game_engine: GameEngine, parent=None):
        super().__init__(parent)
        self.game_engine = game_engine
        self.save_manager = SaveManager()
        self.setWindowTitle(f"📊 Статистика и история игр - v{GAME_VERSION}")
        self.setFixedSize(900, 700)
        
        # ДОБАВЛЕНО: получаем тему из родительского окна
        self.current_theme = "dark"
        if parent and hasattr(parent, 'current_theme'):
            self.current_theme = parent.current_theme
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        theme = THEMES[self.current_theme]
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        title = QLabel(f"📊 СТАТИСТИКА И ИСТОРИЯ ИГР (v{GAME_VERSION})")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"""
            color: white;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #8b5cf6);
            border-radius: 10px;
        """)
        main_layout.addWidget(title)
        
        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 11))
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["bg_secondary"]};
            }}
            QTabBar::tab {{
                background-color: {theme["bg_card"]};
                color: {theme["text"]};
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid {theme["border"]};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {theme["bg_secondary"]};
                border-bottom: 2px solid #3b82f6;
            }}
            QTabBar::tab:hover {{
                background-color: {theme["bg_hover"] if "bg_hover" in theme else theme["bg_card"]};
            }}
        """)
        
        # Вкладка текущего игрока
        current_player_tab = self.create_current_player_tab()
        self.tabs.addTab(current_player_tab, "👤 Текущий игрок")
        
        # Вкладка истории игр
        history_tab = self.create_history_tab()
        self.tabs.addTab(history_tab, "📜 История игр")
        
        # Вкладка общей статистики
        overall_stats_tab = self.create_overall_stats_tab()
        self.tabs.addTab(overall_stats_tab, "🏆 Общая статистика")
        
        # Вкладка рекордов
        records_tab = self.create_records_tab()
        self.tabs.addTab(records_tab, "⭐ Рекорды")
        
        main_layout.addWidget(self.tabs)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFont(QFont("Arial", 11, QFont.Bold))
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #3b82f6;
                color: white;
                border-radius: 8px;
                padding: 8px 20px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
        """)
        refresh_btn.clicked.connect(self.refresh_stats)
        
        close_btn = QPushButton("✖ Закрыть")
        close_btn.setFixedHeight(40)
        close_btn.setFont(QFont("Arial", 11, QFont.Bold))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #ef4444;
                color: white;
                border-radius: 8px;
                padding: 8px 20px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def create_current_player_tab(self):
        """Создать вкладку текущего игрока"""
        theme = THEMES[self.current_theme]
        
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        if not self.game_engine.player:
            no_data = QLabel("Нет активного игрока.\nНачните новую игру!")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setFont(QFont("Arial", 14))
            no_data.setStyleSheet(f"""
                color: {theme['text_secondary']};
                padding: 40px;
                background-color: {theme['bg_card']};
                border-radius: 10px;
            """)
            layout.addWidget(no_data)
            return widget
        
        player = self.game_engine.player
        player_stats = self.save_manager.get_player_stats(player.name)
        
        # Информация об игроке
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['bg_card']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
            }}
        """)
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        
        name_label = QLabel(f"👤 <b>{player.name}</b>, {player.age} лет")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        stats_info = [
            ("📅 Игровой день", str(player.day), "#3b82f6"),
            ("💰 Деньги", f"{player.skills.money} ₽", "#10b981"),
            ("🎮 Всего игр", str(player_stats.get('total_games', 1)), "#8b5cf6"),
            ("✅ Побед", str(player_stats.get('wins', 0)), "#10b981"),
            ("❌ Поражений", str(player_stats.get('losses', 0)), "#ef4444"),
            ("🏆 Достижений", str(len(player.achievements)), "#f59e0b"),
            ("⭐ Лучшие деньги", f"{player_stats.get('best_money', player.skills.money)} ₽", "#8b5cf6"),
            ("📊 Найденных финалов", f"{len(player_stats.get('endings_found', []))}/5", "#10b981")
        ]
        
        for i, (label_text, value, color) in enumerate(stats_info):
            row = i // 2
            col = i % 2
            
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10))
            label.setStyleSheet(f"color: {theme['text_secondary']}; background-color: transparent;")
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 11, QFont.Bold))
            value_label.setStyleSheet(f"color: {color}; background-color: transparent;")
            
            stats_grid.addWidget(label, row, col*2)
            stats_grid.addWidget(value_label, row, col*2+1)
        
        info_layout.addWidget(name_label)
        info_layout.addLayout(stats_grid)
        layout.addWidget(info_frame)
        
        # Навыки с прогресс-барами
        skills_frame = QFrame()
        skills_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['bg_card']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
            }}
        """)
        
        skills_layout = QVBoxLayout(skills_frame)
        skills_title = QLabel("📈 НАВЫКИ")
        skills_title.setFont(QFont("Arial", 12, QFont.Bold))
        skills_title.setStyleSheet(f"color: {theme['text']}; padding-bottom: 10px; background-color: transparent;")
        skills_layout.addWidget(skills_title)
        
        skill_names = {
            "economics": "📊 Экономика",
            "management": "👨‍💼 Менеджмент", 
            "finance": "💳 Финансы",
            "marketing": "📢 Маркетинг",
            "happiness": "😊 Счастье",
            "health": "❤️ Здоровье",
            "reputation": "⭐ Репутация"
        }
        
        for skill_key, skill_name in skill_names.items():
            skill_value = getattr(player.skills, skill_key)
            
            skill_layout = QHBoxLayout()
            
            name_label = QLabel(skill_name)
            name_label.setFont(QFont("Arial", 10))
            name_label.setFixedWidth(120)
            name_label.setStyleSheet(f"color: {theme['text_secondary']}; background-color: transparent;")
            
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(skill_value)
            progress.setTextVisible(True)
            progress.setFormat(f"{skill_value}/100")
            
            color = self.get_skill_color(skill_value)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {theme['border']};
                    border-radius: 5px;
                    text-align: center;
                    background-color: rgba(255, 255, 255, 0.05);
                    color: {theme['text']};
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 5px;
                }}
            """)
            
            skill_layout.addWidget(name_label)
            skill_layout.addWidget(progress)
            skills_layout.addLayout(skill_layout)
        
        layout.addWidget(skills_frame)
        
        # Достижения
        if player.achievements:
            achievements_frame = QFrame()
            achievements_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme['bg_card']};
                    border: 1px solid {theme['border']};
                    border-radius: 10px;
                }}
            """)
            
            ach_layout = QVBoxLayout(achievements_frame)
            ach_title = QLabel("🏆 ДОСТИЖЕНИЯ")
            ach_title.setFont(QFont("Arial", 12, QFont.Bold))
            ach_title.setStyleSheet(f"color: {theme['text']}; padding-bottom: 10px; background-color: transparent;")
            ach_layout.addWidget(ach_title)
            
            for achievement in player.achievements:
                ach_label = QLabel(f"✓ {achievement}")
                ach_label.setFont(QFont("Arial", 10))
                ach_label.setStyleSheet(f"""
                    color: #10b981;
                    background-color: rgba(16, 185, 129, 0.1);
                    padding: 5px 10px;
                    border-radius: 5px;
                    margin: 2px;
                """)
                ach_layout.addWidget(ach_label)
            
            layout.addWidget(achievements_frame)
        
        layout.addStretch()
        return widget
    
    def create_history_tab(self):
        """Создать вкладку истории игр"""
        theme = THEMES[self.current_theme]
        
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        game_history = self.save_manager.get_all_game_results()
        
        if not game_history:
            no_data = QLabel("История игр пуста.\nСыграйте несколько игр!")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setFont(QFont("Arial", 14))
            no_data.setStyleSheet(f"""
                color: {theme['text_secondary']};
                padding: 40px;
                background-color: {theme['bg_card']};
                border-radius: 10px;
            """)
            layout.addWidget(no_data)
            return widget
        
        table = QTableWidget()
        table.setRowCount(len(game_history))
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Игрок", "Возраст", "День", "Деньги", "Финал", 
            "Результат", "Достижений", "Дата"
        ])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['bg_card']};
                alternate-background-color: {theme['bg_secondary']};
                color: {theme['text']};
                gridline-color: {theme['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {theme['text']};
            }}
            QHeaderView::section {{
                background-color: #3b82f6;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
        """)
        
        for i, game in enumerate(reversed(game_history[-50:])):
            player_item = QTableWidgetItem(game['player_name'])
            player_item.setFont(QFont("Arial", 10, QFont.Bold))
            player_item.setForeground(QColor(theme['text']))
            
            age_item = QTableWidgetItem(str(game['age']))
            age_item.setTextAlignment(Qt.AlignCenter)
            age_item.setForeground(QColor(theme['text']))
            
            day_item = QTableWidgetItem(str(game['day']))
            day_item.setTextAlignment(Qt.AlignCenter)
            day_item.setForeground(QColor(theme['text']))
            
            money_item = QTableWidgetItem(f"{game['money']} ₽")
            money_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if game['money'] >= 50000:
                money_item.setForeground(QColor("#10b981"))
            elif game['money'] <= 0:
                money_item.setForeground(QColor("#ef4444"))
            else:
                money_item.setForeground(QColor(theme['text']))
            
            scene_item = QTableWidgetItem(game['final_scene'])
            scene_item.setTextAlignment(Qt.AlignCenter)
            scene_item.setForeground(QColor(theme['text']))
            
            if game['is_ending']:
                if game['is_game_over']:
                    result_item = QTableWidgetItem("❌ Поражение")
                    result_item.setForeground(QColor("#ef4444"))
                else:
                    result_item = QTableWidgetItem("✅ Победа")
                    result_item.setForeground(QColor("#10b981"))
            else:
                result_item = QTableWidgetItem("➤ В процессе")
                result_item.setForeground(QColor("#3b82f6"))
            
            achievements_item = QTableWidgetItem(str(len(game['achievements'])))
            achievements_item.setTextAlignment(Qt.AlignCenter)
            if len(game['achievements']) >= 3:
                achievements_item.setForeground(QColor("#8b5cf6"))
            else:
                achievements_item.setForeground(QColor(theme['text']))
            
            timestamp = game['timestamp'].split('T')[0]
            date_item = QTableWidgetItem(timestamp)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setForeground(QColor(theme['text']))
            
            table.setItem(i, 0, player_item)
            table.setItem(i, 1, age_item)
            table.setItem(i, 2, day_item)
            table.setItem(i, 3, money_item)
            table.setItem(i, 4, scene_item)
            table.setItem(i, 5, result_item)
            table.setItem(i, 6, achievements_item)
            table.setItem(i, 7, date_item)
        
        table.setMinimumHeight(400)
        layout.addWidget(table)
        
        total_games = len(game_history)
        wins = sum(1 for g in game_history if g['is_ending'] and not g['is_game_over'])
        losses = sum(1 for g in game_history if g['is_ending'] and g['is_game_over'])
        
        stats_label = QLabel(
            f"📊 Всего игр: {total_games} | "
            f"✅ Побед: {wins} ({wins/total_games*100:.1f}%) | "
            f"❌ Поражений: {losses} ({losses/total_games*100:.1f}%)"
        )
        stats_label.setFont(QFont("Arial", 11))
        stats_label.setStyleSheet(f"""
            color: {theme['text']};
            background-color: {theme['bg_card']};
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """)
        layout.addWidget(stats_label)
        
        return widget
    
    def create_overall_stats_tab(self):
        """Создать вкладку общей статистики"""
        theme = THEMES[self.current_theme]
        
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        overall_stats = self.save_manager.get_player_stats()
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        stat_cards = [
            ("👥 Игроков", str(overall_stats.get('total_players', 0)), "#3b82f6", theme['bg_card']),
            ("🎮 Всего игр", str(overall_stats.get('total_games', 0)), "#8b5cf6", theme['bg_card']),
            ("✅ Всего побед", str(overall_stats.get('total_wins', 0)), "#10b981", theme['bg_card']),
            ("❌ Всего поражений", str(overall_stats.get('total_losses', 0)), "#ef4444", theme['bg_card']),
            ("💰 Макс. деньги", f"{overall_stats.get('best_money', 0)} ₽", "#8b5cf6", theme['bg_card']),
            ("📅 Макс. день", str(overall_stats.get('best_day', 0)), "#10b981", theme['bg_card']),
            ("🏆 Макс. достижений", str(overall_stats.get('most_achievements', 0)), "#f59e0b", theme['bg_card']),
        ]
        
        for i, (title, value, color, bg_color) in enumerate(stat_cards):
            row = i // 2
            col = i % 2
            
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {theme['border']};
                    border-radius: 15px;
                    padding: 15px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 11, QFont.Bold))
            title_label.setStyleSheet(f"color: {color}; background-color: transparent;")
            title_label.setAlignment(Qt.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 16, QFont.Bold))
            value_label.setStyleSheet(f"color: {color}; background-color: transparent;")
            value_label.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            stats_grid.addWidget(card, row, col)
        
        layout.addLayout(stats_grid)
        
        player_stats = self.save_manager.load_player_stats()
        if player_stats:
            most_active = overall_stats.get('most_active_player', '')
            most_wins = overall_stats.get('most_wins_player', '')
            
            if most_active or most_wins:
                best_players_frame = QFrame()
                best_players_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {theme['bg_card']};
                        border: 1px solid {theme['border']};
                        border-radius: 10px;
                    }}
                """)
                
                best_layout = QVBoxLayout(best_players_frame)
                
                best_title = QLabel("🏅 ЛУЧШИЕ ИГРОКИ")
                best_title.setFont(QFont("Arial", 14, QFont.Bold))
                best_title.setStyleSheet(f"color: {theme['text']}; padding-bottom: 15px; background-color: transparent;")
                best_title.setAlignment(Qt.AlignCenter)
                best_layout.addWidget(best_title)
                
                if most_active:
                    active_stats = player_stats[most_active]
                    active_label = QLabel(
                        f"🎮 <b>Самый активный:</b> {most_active}<br>"
                        f"   Всего игр: {active_stats.get('total_games', 0)}"
                    )
                    active_label.setFont(QFont("Arial", 11))
                    active_label.setStyleSheet(f"color: {theme['text_secondary']}; padding: 5px; background-color: transparent;")
                    best_layout.addWidget(active_label)
                
                if most_wins:
                    wins_stats = player_stats[most_wins]
                    wins_label = QLabel(
                        f"✅ <b>Больше всего побед:</b> {most_wins}<br>"
                        f"   Побед: {wins_stats.get('wins', 0)}"
                    )
                    wins_label.setFont(QFont("Arial", 11))
                    wins_label.setStyleSheet(f"color: {theme['text_secondary']}; padding: 5px; background-color: transparent;")
                    best_layout.addWidget(wins_label)
                
                layout.addWidget(best_players_frame)
        
        return widget
    
    def create_records_tab(self):
        """Создать вкладку рекордов"""
        theme = THEMES[self.current_theme]
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {theme['bg_secondary']};
            }}
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        scroll.setWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        all_games = self.save_manager.get_all_game_results()
        
        if not all_games:
            no_data = QLabel("Рекордов пока нет!\nСыграйте несколько игр.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setFont(QFont("Arial", 14))
            no_data.setStyleSheet(f"""
                color: {theme['text_secondary']};
                padding: 40px;
                background-color: {theme['bg_card']};
                border-radius: 10px;
            """)
            layout.addWidget(no_data)
            return scroll
        
        record_games = {
            "💰 Самые богатые": max(all_games, key=lambda x: x['money']),
            "📅 Самые долгие": max(all_games, key=lambda x: x['day']),
            "🏆 Больше всего достижений": max(all_games, key=lambda x: len(x['achievements'])),
        }
        
        for record_title, record_game in record_games.items():
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3b82f6, stop:1 #8b5cf6);
                    border-radius: 15px;
                    padding: 20px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            title_label = QLabel(f"⭐ {record_title}")
            title_label.setFont(QFont("Arial", 14, QFont.Bold))
            title_label.setStyleSheet("color: white; background-color: transparent;")
            title_label.setAlignment(Qt.AlignCenter)
            
            player_info = QLabel(
                f"👤 <b>{record_game['player_name']}</b> ({record_game['age']} лет)<br>"
                f"📅 День: {record_game['day']} | 💰 {record_game['money']} ₽<br>"
                f"🏆 Достижений: {len(record_game['achievements'])}<br>"
                f"📊 Результат: {'Победа' if record_game['is_ending'] and not record_game['is_game_over'] else 'Поражение'}"
            )
            player_info.setFont(QFont("Arial", 11))
            player_info.setStyleSheet("color: white; background-color: transparent;")
            player_info.setWordWrap(True)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(player_info)
            
            layout.addWidget(card)
        
        endings_frame = QFrame()
        endings_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['bg_card']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        endings_layout = QVBoxLayout(endings_frame)
        endings_layout.setSpacing(10)
        
        endings_title = QLabel("🏁 НАЙДЕННЫЕ ФИНАЛЫ")
        endings_title.setFont(QFont("Arial", 14, QFont.Bold))
        endings_title.setStyleSheet(f"color: {theme['text']}; background-color: transparent;")
        endings_title.setAlignment(Qt.AlignCenter)
        endings_layout.addWidget(endings_title)
        
        found_endings = set()
        for game in all_games:
            if game['is_ending']:
                found_endings.add(game['final_scene'])
        
        total_endings = 12
        found_count = len(found_endings)
        
        progress_label = QLabel(f"Найдено {found_count} из {total_endings} финалов")
        progress_label.setFont(QFont("Arial", 12, QFont.Bold))
        progress_label.setStyleSheet(f"color: {theme['text_secondary']}; background-color: transparent;")
        progress_label.setAlignment(Qt.AlignCenter)
        endings_layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, total_endings)
        progress_bar.setValue(found_count)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat(f"{found_count}/{total_endings}")
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme['border']};
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 0.05);
                height: 25px;
                color: {theme['text']};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 8px;
            }}
        """)
        endings_layout.addWidget(progress_bar)
        
        if found_endings:
            endings_list_label = QLabel("Найденные финалы:")
            endings_list_label.setFont(QFont("Arial", 11, QFont.Bold))
            endings_list_label.setStyleSheet(f"color: {theme['text']}; margin-top: 10px; background-color: transparent;")
            endings_layout.addWidget(endings_list_label)
            
            for ending in sorted(found_endings):
                ending_label = QLabel(f"• {self.get_ending_name(ending)}")
                ending_label.setFont(QFont("Arial", 10))
                ending_label.setStyleSheet(f"color: #10b981; padding-left: 10px; background-color: transparent;")
                endings_layout.addWidget(ending_label)
        
        layout.addWidget(endings_frame)
        layout.addStretch()
        
        return scroll
    
    def get_ending_name(self, ending_id):
        """Получить читаемое название финала"""
        endings_map = {
            "ceo_success": "Генеральный директор",
            "startup_exit_success": "Успешный выход из стартапа",
            "government_minister": "Министр",
            "balance_success": "Гармоничная жизнь",
            "consultant_success": "Эксперт-консультант",
            "investor_success": "Успешный инвестор",
            "burnout_failure": "Профессиональное выгорание",
            "bankruptcy_failure": "Банкротство",
            "health_failure": "Потеря здоровья",
            "corruption_failure": "Коррупционный скандал",
            "family_failure": "Потеря семьи",
            "stagnation_failure": "Карьерный застой"
        }
        return endings_map.get(ending_id, ending_id)
    
    def get_skill_color(self, value):
        """Получить цвет для значения навыка"""
        if value >= 80:
            return "#10b981"
        elif value >= 60:
            return "#3b82f6"
        elif value >= 40:
            return "#f59e0b"
        elif value >= 20:
            return "#ef4444"
        else:
            return "#dc2626"
    
    def refresh_stats(self):
        """Обновить статистика"""
        self.close()
        new_window = StatsWindow(self.game_engine, self.parent())
        new_window.exec()
