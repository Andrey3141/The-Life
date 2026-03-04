"""
Основной диалог мультиплеерной игры
"""

import asyncio
import logging
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QSplitter, QScrollArea,
                               QMessageBox, QApplication, QWidget)  # ДОБАВЛЕНО QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Slot, Signal
from PySide6.QtGui import QFont, QColor

from config import THEMES
from ui.game_dialog_base import (AnimatedButton, ConnectedPlayerCard, 
                                 ParticipantScoreCard, QuestionCard)
from ui.game_dialog_stats import ResultsDialog

logger = logging.getLogger("GameDialog")
logger.setLevel(logging.DEBUG)


class GameDialog(QDialog):
    vote_received = Signal(str, int)
    self_score_confirmed = Signal(int)
    
    def __init__(self, participants, parent=None, current_theme="dark"):
        super().__init__(parent)
        self.participants = participants
        self.current_participant_index = 0
        self.current_theme = current_theme
        self.theme = THEMES.get(current_theme, THEMES["dark"])
        self.connected_players = parent.players if parent else {}
        self.server = parent.server if parent else None
        self._question_anim = None

        if self.server:
            self.server.game_dialog = self
            self.server.vote_received_signal.connect(self.receive_vote, Qt.QueuedConnection)

        self.vote_received.connect(self._on_vote_received, Qt.QueuedConnection)
        self.self_score_confirmed.connect(self._on_self_score_confirmed, Qt.QueuedConnection)

        self.questions = [
            {"category": "Трудолюбие", "question": "Как вы относитесь к работе в выходные дни?"},
            {"category": "Ответственность", "question": "Как часто вы сдаете проекты в срок?"},
            {"category": "Креативность", "question": "Как часто вы предлагаете нестандартные решения?"},
            {"category": "Командность", "question": "Как вы предпочитаете работать?"},
            {"category": "Стрессоустойчивость", "question": "Как вы реагируете на критику?"}
        ]
        
        self.current_question_index = 0
        self.participant_cards = []
        self.connected_player_cards = {}
        
        self.participant_data = {}
        for p in participants:
            self.participant_data[p] = {
                "self_scores": [0] * len(self.questions),
                "other_scores": [[] for _ in range(len(self.questions))]
            }
        
        self.votes_for_current = {}
        self.waiting_for = set()
        self.self_score_selected = False

        self.setWindowTitle("🎮 Мультиплеерная игра")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.showMaximized()

        self.setup_ui()
        
        # Подключаем кнопку подтверждения
        self.question_card.confirm_button.clicked.connect(self.confirm_self_score)
        
        QTimer.singleShot(500, self.start_current_participant)

    def setup_ui(self):
        self.setStyleSheet(f"QDialog {{ background-color: {self.theme['bg']}; }}")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Основной сплиттер
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {self.theme['border']}; }}")

        # Левая панель - участники
        left_panel = self.create_participants_panel()
        splitter.addWidget(left_panel)

        # Центральная панель - вопросы
        center_panel = self.create_questions_panel()
        splitter.addWidget(center_panel)

        # Правая панель - клиенты
        right_panel = self.create_clients_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter, 1)

        # Нижняя панель
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)

    def create_top_bar(self):
        bar = QFrame()
        bar.setFixedHeight(70)
        bar.setStyleSheet(f"background-color: {self.theme['bg_overlay']}; border-bottom: 2px solid {self.theme['border']};")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(15)
        
        icon_label = QLabel("🎮")
        icon_label.setFont(QFont("Segoe UI", 28))
        
        title_label = QLabel("ОЦЕНКА КАЧЕСТВ")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']};")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        
        self.progress_label = QLabel(f"Вопрос 1/{len(self.questions)} • Уч. 1/{len(self.participants)}")
        self.progress_label.setFont(QFont("Segoe UI", 14))
        self.progress_label.setStyleSheet(f"color: {self.theme['text_secondary']}; padding: 8px 20px; background: rgba(59, 130, 246, 0.1); border-radius: 20px;")
        
        self.abort_btn = AnimatedButton("⛔ Прервать", color="#ef4444")
        self.abort_btn.clicked.connect(self.abort_game)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(self.progress_label)
        layout.addSpacing(30)
        layout.addWidget(self.abort_btn)
        
        return bar

    def create_participants_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {self.theme['bg_card']}; border-right: 1px solid {self.theme['border']};")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_layout = QHBoxLayout()
        title_label = QLabel("👥 УЧАСТНИКИ")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']};")
        
        self.participants_count = QLabel(str(len(self.participants)))
        self.participants_count.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.participants_count.setStyleSheet("color: #10b981; background: rgba(16,185,129,0.1); padding:5px 15px; border-radius:20px;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.participants_count)
        layout.addLayout(title_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background:#1e293b; width:8px; border-radius:4px; } QScrollBar::handle:vertical { background:#475569; border-radius:4px; }")
        
        # ИСПРАВЛЕНО: здесь используется QWidget, теперь импорт есть
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.setSpacing(8)
        widget_layout.setContentsMargins(0,0,0,0)
        
        for i, name in enumerate(self.participants):
            card = ParticipantScoreCard(name, i + 1)
            self.participant_cards.append(card)
            widget_layout.addWidget(card)
        
        widget_layout.addStretch()
        scroll.setWidget(widget)
        layout.addWidget(scroll)
        
        return panel

    def create_questions_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {self.theme['bg_secondary']};")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 30, 40, 30)
        
        self.current_participant_label = QLabel(f"👤 Отвечает: {self.participants[0]}")
        self.current_participant_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.current_participant_label.setStyleSheet("color: #3b82f6; background: rgba(59,130,246,0.1); padding:15px; border-radius:15px;")
        self.current_participant_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_participant_label)
        
        self.question_card = QuestionCard(self.questions[0]["category"], self.questions[0]["question"])
        layout.addWidget(self.question_card, 1)
        
        return panel

    def create_clients_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {self.theme['bg_card']}; border-left: 1px solid {self.theme['border']};")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_layout = QHBoxLayout()
        title_label = QLabel("📱 КЛИЕНТЫ")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']};")
        
        self.clients_count = QLabel(str(len(self.connected_players)))
        self.clients_count.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.clients_count.setStyleSheet("color: #8b5cf6; background: rgba(139,92,246,0.1); padding:5px 15px; border-radius:20px;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.clients_count)
        layout.addLayout(title_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background:#1e293b; width:8px; border-radius:4px; } QScrollBar::handle:vertical { background:#475569; border-radius:4px; }")
        
        # ИСПРАВЛЕНО: здесь используется QWidget, теперь импорт есть
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.setSpacing(8)
        widget_layout.setContentsMargins(0,0,0,0)

        self.connected_player_cards.clear()
        for pid, pdata in self.connected_players.items():
            name = pdata.get("name", "Неизвестный")
            card = ConnectedPlayerCard(name, pid)
            self.connected_player_cards[pid] = card
            widget_layout.addWidget(card)

        widget_layout.addStretch()
        scroll.setWidget(widget)
        layout.addWidget(scroll)
        
        return panel

    def create_bottom_bar(self):
        bar = QFrame()
        bar.setFixedHeight(100)
        bar.setStyleSheet(f"background-color: {self.theme['bg_overlay']}; border-top: 2px solid {self.theme['border']};")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(40, 0, 40, 0)

        self.prev_btn = AnimatedButton("◀ Предыдущий", color="#8b5cf6")
        self.prev_btn.setMinimumWidth(200)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.previous_participant)

        self.vote_status_label = QLabel("⏳ Ожидание...")
        self.vote_status_label.setFont(QFont("Segoe UI", 14))
        self.vote_status_label.setStyleSheet("color: #f59e0b; padding: 8px 20px; background: rgba(245,158,11,0.1); border-radius:20px;")
        self.vote_status_label.setAlignment(Qt.AlignCenter)

        self.question_indicator = QLabel(f"⚪ 1/{len(self.questions)} • Уч. 1/{len(self.participants)}")
        self.question_indicator.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.question_indicator.setStyleSheet("color: #3b82f6;")
        self.question_indicator.setAlignment(Qt.AlignCenter)

        self.next_btn = AnimatedButton("Следующий ▶", color="#10b981")
        self.next_btn.setMinimumWidth(200)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_participant)

        layout.addWidget(self.prev_btn)
        layout.addWidget(self.vote_status_label)
        layout.addWidget(self.question_indicator)
        layout.addWidget(self.next_btn)

        return bar

    def start_current_participant(self):
        participant = self.participants[self.current_participant_index]
        self.current_participant_label.setText(f"👤 Отвечает: {participant}")
        
        self.votes_for_current.clear()
        self.waiting_for = set(self.connected_players.keys())
        self.waiting_for.add("self")
        self.self_score_selected = False
        
        self.vote_status_label.setText(f"⏳ Ожидание ({len(self.waiting_for)})")
        self.next_btn.setEnabled(False)
        
        self.send_question_to_players()

    def send_question_to_players(self):
        q = self.questions[self.current_question_index]
        participant = self.participants[self.current_participant_index]

        for pid in self.connected_players:
            if self.server:
                msg = {
                    "type": "new_question",
                    "question_index": self.current_question_index,
                    "category": q["category"],
                    "question": q["question"],
                    "participant": participant
                }
                if hasattr(self.server, 'loop') and self.server.loop:
                    asyncio.run_coroutine_threadsafe(
                        self.server.send_to_player(pid, msg),
                        self.server.loop
                    )

    def receive_vote(self, player_id: str, vote: int):
        self.vote_received.emit(player_id, vote)

    @Slot(str, int)
    def _on_vote_received(self, player_id: str, vote: int):
        if player_id not in self.votes_for_current:
            self.votes_for_current[player_id] = vote
            self.waiting_for.discard(player_id)
            
            participant = self.participants[self.current_participant_index]
            self.participant_data[participant]["other_scores"][self.current_question_index].append(vote)
            
            if player_id in self.connected_player_cards:
                card = self.connected_player_cards[player_id]
                total = sum(v for v in self.votes_for_current.values() if v != "self")
                card.set_score(total)
        
        self.check_votes_complete()

    def confirm_self_score(self):
        if self.question_card.selected_self_score is not None and not self.self_score_selected:
            self.self_score_selected = True
            score = self.question_card.selected_self_score
            self.self_score_confirmed.emit(score)

    @Slot(int)
    def _on_self_score_confirmed(self, score):
        self.votes_for_current["self"] = score
        self.waiting_for.discard("self")
        
        participant = self.participants[self.current_participant_index]
        self.participant_data[participant]["self_scores"][self.current_question_index] = score
        
        if self.current_participant_index < len(self.participant_cards):
            card = self.participant_cards[self.current_participant_index]
            total = (sum(self.participant_data[participant]["self_scores"]) + 
                    sum(sum(scores) for scores in self.participant_data[participant]["other_scores"]))
            card.set_current_score(total)
        
        self.check_votes_complete()

    def check_votes_complete(self):
        if not self.waiting_for:
            self.vote_status_label.setText("✅ Все оценили!")
            self.vote_status_label.setStyleSheet("color: #10b981; padding:8px 20px; background:rgba(16,185,129,0.1); border-radius:20px;")
            self.next_btn.setEnabled(True)
        else:
            self.vote_status_label.setText(f"⏳ Ожидание ({len(self.waiting_for)})")

    def next_participant(self):
        if self.current_participant_index < len(self.participants) - 1:
            self.current_participant_index += 1
            self.start_current_participant()
            self.update_progress()
        else:
            if self.current_question_index < len(self.questions) - 1:
                self.current_question_index += 1
                self.current_participant_index = 0
                self.update_question()
                self.start_current_participant()
                self.update_progress()
                
                if self.current_question_index == len(self.questions) - 1:
                    self.next_btn.setText("Завершить ▶")
            else:
                self.show_results()

    def previous_participant(self):
        if self.current_participant_index > 0:
            self.current_participant_index -= 1
            self.start_current_participant()
            self.update_progress()
        
        if self.current_participant_index == 0:
            self.prev_btn.setEnabled(False)

    def update_question(self):
        q = self.questions[self.current_question_index]
        self.question_card.set_question(q["category"], q["question"])
        
        self._question_anim = QPropertyAnimation(self.question_card, b"geometry")
        self._question_anim.setDuration(400)
        self._question_anim.setKeyValueAt(0, self.question_card.geometry())
        self._question_anim.setKeyValueAt(0.2, self.question_card.geometry().adjusted(-10, -5, 10, 5))
        self._question_anim.setKeyValueAt(0.8, self.question_card.geometry().adjusted(5, 3, -5, -3))
        self._question_anim.setKeyValueAt(1, self.question_card.geometry())
        self._question_anim.setEasingCurve(QEasingCurve.OutElastic)
        self._question_anim.start()

    def update_progress(self):
        self.progress_label.setText(
            f"Вопрос {self.current_question_index + 1}/{len(self.questions)} • "
            f"Уч. {self.current_participant_index + 1}/{len(self.participants)}"
        )
        self.question_indicator.setText(
            f"⚪ {self.current_question_index + 1}/{len(self.questions)} • "
            f"Уч. {self.current_participant_index + 1}/{len(self.participants)}"
        )

    def show_results(self):
        results_dialog = ResultsDialog(self.participants, self.participant_data, self, self.current_theme)
        results_dialog.exec()

    def abort_game(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Прерывание")
        msg.setText("Прервать игру?")
        msg.setInformativeText("Все результаты будут потеряны.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.theme["bg_secondary"]};
                color: {self.theme["text"]};
                border: 2px solid {self.theme["border"]};
                border-radius: 15px;
            }}
            QMessageBox QLabel {{
                color: {self.theme["text"]};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {self.theme["bg_card"]};
                color: {self.theme["text"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 100px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme["bg_hover"]};
                border: 1px solid #3b82f6;
            }}
        """)
        if msg.exec() == QMessageBox.Yes:
            self.reject()
