"""
Модуль статистики для мультиплеерной игры
"""

import asyncio
import logging
import math
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QScrollArea, QWidget, QTabWidget, QGridLayout,
                               QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush

from config import THEMES
from ui.game_dialog_base import RadarChartWidget, BarChartWidget, AnimatedButton

logger = logging.getLogger("GameDialog")
logger.setLevel(logging.DEBUG)


class StatsCard(QFrame):
    """Карточка статистики для одного качества"""
    
    def __init__(self, category, self_score, other_avg, diff, parent=None):
        super().__init__(parent)
        self.category = category
        self.self_score = self_score
        self.other_avg = other_avg
        self.diff = diff
        
        self.setObjectName("statsCard")
        self.setFixedHeight(200)
        self.setStyleSheet("""
            QFrame#statsCard {
                background-color: rgba(30, 41, 59, 0.9);
                border: 1px solid #3b82f6;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Заголовок категории
        title_label = QLabel(category.upper())
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #3b82f6; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Значения
        values_layout = QHBoxLayout()
        
        self_val = QLabel(f"Я: {self_score}")
        self_val.setFont(QFont("Segoe UI", 11))
        self_val.setStyleSheet("color: #10b981; background: transparent;")
        self_val.setAlignment(Qt.AlignCenter)
        
        other_val = QLabel(f"Др: {other_avg:.1f}")
        other_val.setFont(QFont("Segoe UI", 11))
        other_val.setStyleSheet("color: #f59e0b; background: transparent;")
        other_val.setAlignment(Qt.AlignCenter)
        
        diff_val = QLabel(f"{diff:+.1f}")
        diff_val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        diff_color = "#10b981" if diff >= 0 else "#ef4444"
        diff_val.setStyleSheet(f"color: {diff_color}; background: transparent;")
        diff_val.setAlignment(Qt.AlignCenter)
        
        values_layout.addWidget(self_val)
        values_layout.addWidget(other_val)
        values_layout.addWidget(diff_val)
        
        layout.addLayout(values_layout)
        
        # Прогресс-бары
        self_bar = QProgressBar()
        self_bar.setRange(0, 5)
        self_bar.setValue(int(self_score))
        self_bar.setTextVisible(False)
        self_bar.setFixedHeight(15)
        self_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 7px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 7px;
            }
        """)
        layout.addWidget(self_bar)
        
        other_bar = QProgressBar()
        other_bar.setRange(0, 5)
        other_bar.setValue(int(other_avg))
        other_bar.setTextVisible(False)
        other_bar.setFixedHeight(15)
        other_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 7px;
            }
            QProgressBar::chunk {
                background-color: #f59e0b;
                border-radius: 7px;
            }
        """)
        layout.addWidget(other_bar)


class StatsTab(QWidget):
    """Вкладка со статистикой участника"""
    
    def __init__(self, participant_name, data, parent=None):
        super().__init__(parent)
        self.participant_name = participant_name
        self.data = data
        self.setup_ui()
    
    def setup_ui(self):
        # Основной layout с прокруткой
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
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(20, 20, 20, 40)
        
        # Заголовок с именем
        title_frame = QFrame()
        title_frame.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_frame)
        
        icon_label = QLabel("👤")
        icon_label.setFont(QFont("Segoe UI", 32))
        icon_label.setStyleSheet("color: #3b82f6; background: transparent;")
        
        name_label = QLabel(self.participant_name)
        name_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        name_label.setStyleSheet("color: #f8fafc; background: transparent;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(name_label)
        title_layout.addStretch()
        
        content_layout.addWidget(title_frame)
        
        # Данные
        self_scores = self.data.get("self_scores", [])
        other_scores = self.data.get("other_scores", [])
        
        # Вычисляем средние оценки других
        other_averages = []
        for scores in other_scores:
            avg = sum(scores) / len(scores) if scores else 0
            other_averages.append(avg)
        
        # Общий счет
        total_self = sum(self_scores)
        total_other = sum(other_averages)
        total = total_self + total_other
        
        total_frame = QFrame()
        total_frame.setStyleSheet("background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 15px; padding: 15px;")
        total_layout = QHBoxLayout(total_frame)
        
        total_label = QLabel("ОБЩИЙ СЧЕТ:")
        total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        total_label.setStyleSheet("color: #f8fafc; background: transparent;")
        
        total_value = QLabel(f"{total:.0f}")
        total_value.setFont(QFont("Segoe UI", 20, QFont.Bold))
        total_value.setStyleSheet("color: #10b981; background: transparent;")
        total_value.setAlignment(Qt.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        
        content_layout.addWidget(total_frame)
        
        # Графики
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        categories = ["Трудолюбие", "Ответственность", "Креативность", "Командность", "Стрессоустойчивость"]
        radar_chart = RadarChartWidget(categories, self_scores, other_averages)
        charts_layout.addWidget(radar_chart)
        
        bar_chart = BarChartWidget(categories, self_scores, other_averages)
        charts_layout.addWidget(bar_chart)
        
        content_layout.addLayout(charts_layout)
        
        # Аналитический блок
        analysis_frame = QFrame()
        analysis_frame.setStyleSheet("background: rgba(30, 41, 59, 0.7); border: 1px solid #3b82f6; border-radius: 15px; padding: 20px;")
        analysis_layout = QVBoxLayout(analysis_frame)
        
        analysis_title = QLabel("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
        analysis_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        analysis_title.setStyleSheet("color: #3b82f6; background: transparent;")
        analysis_layout.addWidget(analysis_title)
        
        # Находим сильные и слабые стороны
        strengths = []
        weaknesses = []
        discrepancies = []
        
        for i, category in enumerate(categories):
            self_score = self_scores[i]
            other_avg = other_averages[i]
            diff = self_score - other_avg
            
            if self_score >= 4:
                strengths.append(f"• {category}: {self_score}/5")
            elif self_score <= 2:
                weaknesses.append(f"• {category}: {self_score}/5")
            
            if abs(diff) >= 1.5:
                if diff > 0:
                    discrepancies.append(f"• {category}: вы выше на {diff:.1f} (вы: {self_score}, др: {other_avg:.1f})")
                else:
                    discrepancies.append(f"• {category}: вас выше на {abs(diff):.1f} (вы: {self_score}, др: {other_avg:.1f})")
        
        # Сильные стороны
        if strengths:
            strength_label = QLabel("💪 СИЛЬНЫЕ СТОРОНЫ:")
            strength_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            strength_label.setStyleSheet("color: #10b981; background: transparent; margin-top: 10px;")
            analysis_layout.addWidget(strength_label)
            
            for s in strengths:
                s_label = QLabel(s)
                s_label.setFont(QFont("Segoe UI", 11))
                s_label.setStyleSheet("color: #f8fafc; background: transparent; padding-left: 10px;")
                analysis_layout.addWidget(s_label)
        
        # Слабые стороны
        if weaknesses:
            weakness_label = QLabel("🎯 ЗОНЫ РАЗВИТИЯ:")
            weakness_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            weakness_label.setStyleSheet("color: #f59e0b; background: transparent; margin-top: 10px;")
            analysis_layout.addWidget(weakness_label)
            
            for w in weaknesses:
                w_label = QLabel(w)
                w_label.setFont(QFont("Segoe UI", 11))
                w_label.setStyleSheet("color: #f8fafc; background: transparent; padding-left: 10px;")
                analysis_layout.addWidget(w_label)
        
        # Расхождения
        if discrepancies:
            disc_label = QLabel("⚠️ РАСХОЖДЕНИЯ:")
            disc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            disc_label.setStyleSheet("color: #ef4444; background: transparent; margin-top: 10px;")
            analysis_layout.addWidget(disc_label)
            
            for d in discrepancies:
                d_label = QLabel(d)
                d_label.setFont(QFont("Segoe UI", 11))
                d_label.setStyleSheet("color: #f8fafc; background: transparent; padding-left: 10px;")
                analysis_layout.addWidget(d_label)
        
        # Общая рекомендация
        if total_self > total_other + 3:
            recommendation = "Вы склонны переоценивать себя. Постарайтесь быть более объективным."
        elif total_other > total_self + 3:
            recommendation = "Окружающие ценят вас выше, чем вы сами. Больше верьте в свои силы!"
        else:
            recommendation = "У вас здоровое восприятие себя. Продолжайте в том же духе!"
        
        recommendation_label = QLabel(f"💡 {recommendation}")
        recommendation_label.setFont(QFont("Segoe UI", 11))
        recommendation_label.setWordWrap(True)
        recommendation_label.setStyleSheet("color: #94a3b8; background: transparent; margin-top: 15px; padding: 10px; border-top: 1px solid #334155;")
        analysis_layout.addWidget(recommendation_label)
        
        content_layout.addWidget(analysis_frame)
        
        # Карточки качеств
        cards_label = QLabel("📋 ДЕТАЛЬНАЯ СТАТИСТИКА")
        cards_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cards_label.setStyleSheet("color: #f8fafc; background: transparent; margin-top: 20px;")
        content_layout.addWidget(cards_label)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        for i, category in enumerate(categories):
            self_score = self_scores[i] if i < len(self_scores) else 0
            other_avg = other_averages[i] if i < len(other_averages) else 0
            diff = self_score - other_avg
            
            card = StatsCard(category, self_score, other_avg, diff)
            grid.addWidget(card, i // 2, i % 2)
        
        content_layout.addLayout(grid)
        
        scroll_area.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)


class ResultsDialog(QDialog):
    """Диалог с результатами"""
    
    def __init__(self, participants, results_data, parent=None, current_theme="dark"):
        super().__init__(parent)
        self.participants = participants
        self.results_data = results_data
        self.current_theme = current_theme
        self.theme = THEMES.get(current_theme, THEMES["dark"])
        
        self.setWindowTitle("📊 РЕЗУЛЬТАТЫ")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.showMaximized()
        
        self.setup_ui()
        self.send_results_to_clients()
    
    def send_results_to_clients(self):
        """Отправить результаты на клиенты"""
        if hasattr(self.parent(), 'server') and self.parent().server:
            server = self.parent().server
            
            results_for_clients = []
            for participant in self.participants:
                data = self.results_data.get(participant, {})
                self_scores = data.get("self_scores", [])
                other_scores = data.get("other_scores", [])
                
                other_averages = []
                for scores in other_scores:
                    avg = sum(scores) / len(scores) if scores else 0
                    other_averages.append(avg)
                
                results_for_clients.append({
                    "name": participant,
                    "self_scores": self_scores,
                    "other_averages": other_averages,
                    "total_self": sum(self_scores),
                    "total_other": sum(other_averages),
                    "total": sum(self_scores) + sum(other_averages)
                })
            
            message = {
                "type": "game_results",
                "results": results_for_clients
            }
            
            for player_id in self.parent().connected_players:
                if hasattr(server, 'loop') and server.loop:
                    asyncio.run_coroutine_threadsafe(
                        server.send_to_player(player_id, message),
                        server.loop
                    )
    
    def setup_ui(self):
        self.setStyleSheet(f"QDialog {{ background-color: {self.theme['bg']}; }}")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя панель
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Контент с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme['bg_secondary']};
            }}
            QScrollBar:vertical {{
                background-color: #1e293b;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #475569;
                border-radius: 5px;
            }}
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {self.theme['bg_secondary']};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 50)
        
        title_label = QLabel("ИТОГОВАЯ СТАТИСТИКА")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']}; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Табы
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {self.theme['bg_secondary']};
                border: 1px solid {self.theme['border']};
                border-radius: 15px;
                padding: 20px;
            }}
            QTabBar::tab {{
                background-color: {self.theme['bg_card']};
                color: {self.theme['text']};
                padding: 15px 30px;
                margin-right: 5px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border: 1px solid {self.theme['border']};
                border-bottom: none;
                font-size: 14px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {self.theme['bg_secondary']};
                color: #3b82f6;
                border-bottom: 3px solid #3b82f6;
            }}
            QTabBar::tab:hover {{
                background-color: {self.theme['bg_hover']};
            }}
        """)
        
        for participant in self.participants:
            data = self.results_data.get(participant, {})
            tab = StatsTab(participant, data)
            tabs.addTab(tab, f"👤 {participant}")
        
        content_layout.addWidget(tabs)
        
        # Кнопка закрытия
        close_btn = QPushButton("📋 ЗАВЕРШИТЬ")
        close_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setMinimumHeight(60)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 30px;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area, 1)
    
    def create_top_bar(self):
        bar = QFrame()
        bar.setFixedHeight(70)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['bg_overlay']};
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: 2px solid {self.theme['border']};
            }}
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(15)
        
        icon_label = QLabel("📊")
        icon_label.setFont(QFont("Segoe UI", 28))
        
        title_label = QLabel("РЕЗУЛЬТАТЫ")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']};")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        
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
        close_btn.clicked.connect(self.accept)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        return bar
