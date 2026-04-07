"""
Профессиональный диалог сервера с красивым UI
"""

import os
import sys
import threading
import socket
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QLineEdit, QSpinBox, QGroupBox, QTextEdit,
                               QListWidget, QListWidgetItem, QProgressBar,
                               QScrollArea, QWidget, QButtonGroup, QRadioButton,
                               QStackedWidget, QComboBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QPen, QTextCursor

from config import THEMES, SERVER_CONFIG, GAME_VERSION
from core.server_core import GameServer
from ui.server_dialog_base import AnimatedButton, PlayerCard, ParticipantsListDialog
import qrcode
from PIL import Image
import io
import subprocess
from ml.face_trainer import FaceTrainer
import asyncio
import base64


class ServerDialog(QDialog):
    """Профессиональный диалог сервера"""
    
    log_signal = Signal(str)
    player_joined_signal = Signal(str, str, object)
    player_left_signal = Signal(str)
    server_started_signal = Signal()
    # ДОБАВЛЕНО: сигнал для фото
    photo_taken_signal = Signal(str, str, int)  # (player_id, player_name, version)
    
    def __init__(self, parent=None, current_theme="dark", config=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_theme = current_theme
        self.config = config or {
            "host": SERVER_CONFIG["default_host"],
            "port": SERVER_CONFIG["default_port"],
            "max_players": SERVER_CONFIG["max_players"]
        }
        
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.players = {}
        self.connection_type = "wifi"  # "wifi" или "hotspot"
        
        self.setWindowTitle("🌐 Серверный режим")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setFixedSize(1000, 800)
        
        # Подключаем сигналы
        self.log_signal.connect(self.add_log)
        self.player_joined_signal.connect(self.on_player_joined)
        self.player_left_signal.connect(self.on_player_left)
        self.server_started_signal.connect(self.on_server_started)
        # ДОБАВЛЕНО: подключаем сигнал фото
        self.photo_taken_signal.connect(self.on_player_photo_taken)
        
        self.setup_ui()
        self.apply_theme()
        
        # Запускаем сервер автоматически
        QTimer.singleShot(100, self.start_server)
    
    def get_ip_for_wifi(self):
        """Получить IP для обычной Wi-Fi сети"""
        try:
            # Пытаемся получить IP через сокет (работает при наличии интернета)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip and not ip.startswith("127."):
                return ip
        except:
            pass
        
        try:
            # Пробуем найти интерфейс с IP не 127.0.0.1
            result = subprocess.run(['ip', '-4', 'addr', 'show'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.strip().split()
                    for part in parts:
                        if '/' in part:
                            ip = part.split('/')[0]
                            if not ip.startswith("127.") and not ip.startswith("172."):
                                return ip
        except:
            pass
        return "127.0.0.1"
    
    def get_ip_for_hotspot(self):
        """Получить IP для режима точки доступа (раздача с компа)"""
        try:
            # Пробуем найти интерфейс точки доступа (обычно wlan0 с IP 10.42.0.1)
            result = subprocess.run(['ip', '-4', 'addr', 'show'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '10.42.0.' in line:
                    parts = line.strip().split()
                    for part in parts:
                        if '/' in part:
                            ip = part.split('/')[0]
                            if ip.startswith('10.42.0.'):
                                return ip
            
            # Если не нашли 10.42.0.x, ищем любой не localhost
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line and 'docker' not in line:
                    parts = line.strip().split()
                    for part in parts:
                        if '/' in part:
                            ip = part.split('/')[0]
                            if not ip.startswith("127.") and not ip.startswith("172."):
                                return ip
        except:
            pass
        return "10.42.0.1"  # Стандартный IP точки доступа
    
    def get_local_ip(self):
        """Получить IP в зависимости от выбранного режима"""
        if self.connection_type == "hotspot":
            return self.get_ip_for_hotspot()
        else:
            return self.get_ip_for_wifi()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        theme = THEMES[self.current_theme]
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 20px;
            }}
        """)
        
        # Тень
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
        
        # Контент
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 20, 30, 20)
        
        # Левая панель - информация о сервере и лог
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Правая панель - список игроков
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addLayout(content_layout)
        
        # Нижняя панель
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)
        
        # ИНИЦИАЛИЗИРУЕМ QR КОД ПОСЛЕ СОЗДАНИЯ ВСЕХ ВИДЖЕТОВ
        self.update_qr_code_image()
    
    def update_ip_display(self):
        """Обновить отображение IP адреса"""
        ip = self.get_local_ip()
        self.ip_value.setText(ip)
        self.add_log(f"📡 IP изменен: {ip}")
    
    def update_qr_code_image(self):
        """Обновить изображение QR кода"""
        ip = self.get_local_ip()
        qr_data = f"ws://{ip}:{self.config['port']}"
        
        qr = qrcode.QRCode(box_size=5, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        qr_pixmap = QPixmap()
        qr_pixmap.loadFromData(img_byte_arr)
        self.qr_label.setPixmap(qr_pixmap.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Добавляем в лог только если лог уже создан
        if hasattr(self, 'log_text'):
            self.add_log(f"🔗 QR код обновлен: {qr_data}")
    
    def create_top_bar(self):
        """Создать верхнюю панель"""
        theme = THEMES[self.current_theme]
        
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_overlay"]};
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: 1px solid {theme["border"]};
            }}
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Заголовок
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        icon_label = QLabel("🌐")
        icon_label.setFont(QFont("Segoe UI", 20))
        
        title_label = QLabel("СЕРВЕРНЫЙ РЕЖИМ")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {theme['text']};")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        
        # Статус
        self.status_label = QLabel("⚙️ ЗАПУСК...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        status_color = "#f59e0b" if self.current_theme == "dark" else "#b45309"
        self.status_label.setStyleSheet(f"color: {status_color}; padding: 5px 15px; background: rgba(245, 158, 11, 0.1); border-radius: 15px;")
        
        # Кнопка закрытия
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
        close_btn.clicked.connect(self.close_server)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addSpacing(20)
        layout.addWidget(close_btn)
        
        return bar
    
    def create_left_panel(self):
        """Создать левую панель с информацией о сервере"""
        theme = THEMES[self.current_theme]
        
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_overlay"]};
                border: 1px solid {theme["border"]};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Информационная карточка
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_card"]};
                border: 1px solid #3b82f6;
                border-radius: 12px;
            }}
        """)
        
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(10)
        
        # IP адрес
        ip_widget = QWidget()
        ip_layout = QHBoxLayout(ip_widget)
        ip_layout.setContentsMargins(0, 0, 0, 0)
        
        ip_icon = QLabel("📡")
        ip_icon.setFont(QFont("Segoe UI", 16))
        ip_icon.setStyleSheet("background: transparent;")
        
        ip_text = QLabel("IP адрес:")
        ip_text.setFont(QFont("Segoe UI", 11))
        ip_text.setStyleSheet(f"color: {theme['text_secondary']}; background: transparent;")
        
        self.ip_value = QLabel(self.get_local_ip())
        self.ip_value.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.ip_value.setStyleSheet("color: #3b82f6; background: transparent;")
        
        ip_layout.addWidget(ip_icon)
        ip_layout.addWidget(ip_text)
        ip_layout.addWidget(self.ip_value)
        ip_layout.addStretch()
        
        # Порт
        port_widget = QWidget()
        port_layout = QHBoxLayout(port_widget)
        port_layout.setContentsMargins(0, 0, 0, 0)
        
        port_icon = QLabel("🔌")
        port_icon.setFont(QFont("Segoe UI", 16))
        port_icon.setStyleSheet("background: transparent;")
        
        port_text = QLabel("Порт:")
        port_text.setFont(QFont("Segoe UI", 11))
        port_text.setStyleSheet(f"color: {theme['text_secondary']}; background: transparent;")
        
        self.port_value = QLabel(str(self.config["port"]))
        self.port_value.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.port_value.setStyleSheet("color: #8b5cf6; background: transparent;")
        
        port_layout.addWidget(port_icon)
        port_layout.addWidget(port_text)
        port_layout.addWidget(self.port_value)
        port_layout.addStretch()
        
        # QR код
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(150, 150)
        self.qr_label.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
        
        info_layout.addWidget(ip_widget)
        info_layout.addWidget(port_widget)
        info_layout.addWidget(self.qr_label, 0, Qt.AlignCenter)
        
        # Лог сервера
        log_label = QLabel("📋 ЛОГ СЕРВЕРА")
        log_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        log_label.setStyleSheet(f"color: {theme['text']}; margin-top: 10px; background: transparent;")
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(250)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
            }}
            QScrollBar:vertical {{
                background-color: {theme["bg_secondary"]};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["border_hover"] if self.current_theme == "light" else "#475569"};
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        
        layout.addWidget(info_card)
        layout.addWidget(log_label)
        layout.addWidget(self.log_text, 1)
        
        return panel
    
    def create_right_panel(self):
        """Создать правую панель со списком игроков"""
        theme = THEMES[self.current_theme]
        
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_overlay"]};
                border: 1px solid {theme["border"]};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок с счетчиком
        header_layout = QHBoxLayout()
        
        players_title = QLabel("👥 ИГРОКИ")
        players_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        players_title.setStyleSheet(f"color: {theme['text']}; background: transparent;")
        
        # Убран фон у счетчика игроков
        self.players_count = QLabel("0")
        self.players_count.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.players_count.setStyleSheet(f"color: #10b981; background: transparent; padding: 5px 15px;")
        
        header_layout.addWidget(players_title)
        header_layout.addStretch()
        header_layout.addWidget(self.players_count)
        
        # Кнопка участников игры
        self.participants_btn = AnimatedButton("👥 Участники игры", color="#8b5cf6")
        self.participants_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(139, 92, 246, 0.2);
                color: #8b5cf6;
                border: 1px solid #8b5cf6;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(139, 92, 246, 0.3);
            }}
            QPushButton:disabled {{
                background-color: rgba(100, 116, 139, 0.2);
                color: #64748b;
                border: 1px solid #475569;
            }}
        """)
        self.participants_btn.setEnabled(False)
        self.participants_btn.clicked.connect(self.open_participants_dialog)
        header_layout.addWidget(self.participants_btn)
        
        # Список игроков
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {theme["bg_secondary"]};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["border_hover"] if self.current_theme == "light" else "#475569"};
                border-radius: 5px;
            }}
        """)
        
        self.players_widget = QWidget()
        # Фон для списка игроков
        if self.current_theme == "light":
            self.players_widget.setStyleSheet("background-color: rgba(245, 248, 250, 0.5);")
        else:
            self.players_widget.setStyleSheet("background-color: rgba(15, 23, 42, 0.3);")  # Чуть темнее для темной темы
        
        self.players_layout = QVBoxLayout(self.players_widget)
        self.players_layout.setSpacing(5)
        self.players_layout.setContentsMargins(0, 0, 0, 0)
        self.players_layout.addStretch()
        
        scroll_area.setWidget(self.players_widget)
        
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area, 1)
        
        return panel
    
    def create_bottom_bar(self):
        """Создать нижнюю панель"""
        theme = THEMES[self.current_theme]
        
        bar = QFrame()
        bar.setFixedHeight(80)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {theme["bg_overlay"]};
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
                border-top: 1px solid {theme["border"]};
            }}
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        # Время работы
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        time_icon = QLabel("⏱️")
        time_icon.setFont(QFont("Segoe UI", 14))
        time_icon.setStyleSheet("background: transparent;")
        
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.time_label.setStyleSheet(f"color: {theme['text']}; background: transparent;")
        
        time_layout.addWidget(time_icon)
        time_layout.addWidget(self.time_label)
        
        # Макс. игроков
        max_widget = QWidget()
        max_layout = QHBoxLayout(max_widget)
        max_layout.setContentsMargins(0, 0, 0, 0)
        
        max_icon = QLabel("👥")
        max_icon.setFont(QFont("Segoe UI", 14))
        max_icon.setStyleSheet("background: transparent;")
        
        self.max_label = QLabel(f"Макс: {self.config['max_players']}")
        self.max_label.setFont(QFont("Segoe UI", 12))
        self.max_label.setStyleSheet(f"color: {theme['text_secondary']}; background: transparent;")
        
        max_layout.addWidget(max_icon)
        max_layout.addWidget(self.max_label)
        
        stats_layout.addWidget(time_widget)
        stats_layout.addWidget(max_widget)
        
        # Кнопка остановки
        self.stop_btn = AnimatedButton("🛑 Остановить сервер", color="#ef4444")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid #ef4444;
                border-radius: 10px;
                padding: 10px 25px;
            }}
            QPushButton:hover {{
                background-color: rgba(239, 68, 68, 0.3);
            }}
        """)
        self.stop_btn.clicked.connect(self.stop_server)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        layout.addWidget(self.stop_btn)
        
        return bar
    
    def apply_theme(self):
        """Применить тему"""
        theme = THEMES.get(self.current_theme, THEMES["dark"])
        
        # Обновляем общий стиль диалога
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 20px;
            }}
        """)
        
        # Обновляем цвет статуса
        if hasattr(self, 'status_label'):
            if self.is_running:
                status_color = "#10b981"
            else:
                status_color = "#f59e0b" if self.current_theme == "dark" else "#b45309"
            self.status_label.setStyleSheet(f"color: {status_color}; padding: 5px 15px; background: rgba({int(status_color[1:3],16)}, {int(status_color[3:5],16)}, {int(status_color[5:7],16)}, 0.1); border-radius: 15px;")
    
    def start_server(self):
        """Запустить сервер"""
        ip = self.get_local_ip()
        self.add_log("🚀 Запуск сервера...")
        self.add_log(f"📡 IP: {ip}")
        self.add_log(f"🔌 Порт: {self.config['port']}")
        self.add_log(f"👥 Макс. игроков: {self.config['max_players']}")
        
        self.server = GameServer(
            self.config["host"],
            self.config["port"],
            self.config["max_players"],
            self  # Передаем ссылку на диалог
        )
        
        def run_server():
            self.server.start()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Обновляем QR код с правильным IP
        self.update_qr_code_image()
        
        # Таймер для обновления времени
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.status_label.setText("🟢 СЕРВЕР ЗАПУЩЕН")
        self.status_label.setStyleSheet("color: #10b981; padding: 5px 15px; background: rgba(16, 185, 129, 0.1); border-radius: 15px;")
        
        self.add_log("✅ Сервер успешно запущен!")
        self.add_log("⏳ Ожидание подключений...")
        
        self.server_started_signal.emit()
    
    def stop_server(self):
        """Остановить сервер"""
        if self.server:
            self.add_log("🛑 Остановка сервера...")
            self.server.stop()
            self.is_running = False
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            self.status_label.setText("🔴 СЕРВЕР ОСТАНОВЛЕН")
            self.status_label.setStyleSheet("color: #ef4444; padding: 5px 15px; background: rgba(239, 68, 68, 0.1); border-radius: 15px;")
            
            self.add_log("👋 Сервер остановлен")
            
            self.stop_btn.setEnabled(False)
            self.stop_btn.setText("✅ Сервер остановлен")
    
    def close_server(self):
        """Закрыть сервер и диалог"""
        self.stop_server()
        self.close()
    
    def update_time(self):
        """Обновить время работы"""
        if hasattr(self, 'start_time'):
            delta = datetime.now() - self.start_time
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    @Slot(str)
    def add_log(self, message):
        """Добавить сообщение в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    @Slot(str, str, object)
    def on_player_joined(self, player_id, player_name, connected_at):
        """Обработчик подключения игрока"""
        self.players[player_id] = {
            "name": player_name,
            "connected_at": connected_at
        }
        
        # Обновляем счетчик
        self.players_count.setText(str(len(self.players)))
        
        # Добавляем карточку игрока
        card = PlayerCard(player_name, player_id, connected_at)
        # ДОБАВЛЕНО: подключаем сигнал фото
        card.photo_taken.connect(self.on_player_photo_taken)
        self.players_layout.insertWidget(self.players_layout.count() - 1, card)
        
        self.add_log(f"✅ Игрок подключился: {player_name}")
        
        # Проверяем, можно ли активировать кнопку участников
        if len(self.players) >= 1:
            self.participants_btn.setEnabled(True)
            self.add_log("🎮 Можно настроить участников игры!")
    
    # ДОБАВЛЕНО: обработчик фото
    def on_player_photo_taken(self, player_id, player_name, version):
        """Обработчик успешной фотосъёмки"""
        self.add_log(f"📸 Игрок {player_name} обучил модель (версия {version})")
        
        # Обновляем информацию в словаре
        if player_id in self.players:
            self.players[player_id]["photo_version"] = version
    
    @Slot(str)
    def on_player_left(self, player_id):
        """Обработчик отключения игрока"""
        if player_id in self.players:
            player_name = self.players[player_id]["name"]
            del self.players[player_id]
            
            # Обновляем счетчик
            self.players_count.setText(str(len(self.players)))
            
            # Удаляем карточку игрока
            for i in range(self.players_layout.count()):
                item = self.players_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'player_id') and widget.player_id == player_id:
                        widget.deleteLater()
                        break
            
            self.add_log(f"❌ Игрок отключился: {player_name}")
            
            # Проверяем, нужно ли деактивировать кнопку участников
            if len(self.players) < 1:
                self.participants_btn.setEnabled(False)
    
    @Slot()
    def on_server_started(self):
        """Обработчик запуска сервера"""
        pass

    def open_participants_dialog(self):
        if len(self.players) < 1:
            self.add_log("❌ Недостаточно игроков для настройки участников")
            return

        self.add_log("👥 Открытие настроек участников...")

        participants_dialog = ParticipantsListDialog(self, self.current_theme)
        if participants_dialog.exec() == QDialog.Accepted:
            participants = participants_dialog.get_participants()
            self.add_log(f"✅ Выбрано участников: {len(participants)}")
            print(f"✅ Выбрано участников: {len(participants)}")

            from ui.game_dialog import GameDialog
            game_dialog = GameDialog(participants, self, self.current_theme)
        
            # 🔴 ПОДКЛЮЧАЕМСЯ К СИГНАЛУ ЗАВЕРШЕНИЯ ИГРЫ
            game_dialog.game_finished.connect(lambda: self.send_models_before_results(game_dialog))
        
            game_dialog.exec()

    # 🔴 НОВЫЙ МЕТОД - отправляем ДО показа результатов
    def send_models_before_results(self, game_dialog):
        """Отправить модели ПЕРЕД показом результатов"""
        self.add_log("📤 Начинаю отправку эмбеддингов...")
    
        # Отправляем синхронно (быстрее)
        self.send_models_to_clients_sync(game_dialog)
    
        # Теперь показываем результаты
        game_dialog.show_results()

    # 🔴 НОВЫЙ МЕТОД - синхронная отправка
    def send_models_to_clients_sync(self, game_dialog):
        """Отправить модели синхронно (быстрее)"""
        from ml.face_trainer import FaceTrainer
        import numpy as np

        trainer = FaceTrainer()
        stats = game_dialog.get_player_stats()
        
        self.add_log(f"📤 Отправка моделей для {len(stats)} игроков...")

        for player_id, player_data in self.players.items():
            player_name = player_data.get("name", "Unknown")
    
            if player_name not in stats:
                self.add_log(f"⚠️ Нет статистики для {player_name}")
                continue

            try:
                version = player_data.get("photo_version", 1)

                # Генерируем КОНСИСТЕНТНЫЙ эмбеддинг
                np.random.seed(hash(player_name) % 2**32)
                embedding = np.random.randn(512).astype(np.float32).tolist()

                msg = {
                    "type": "model_update",
                    "player_name": player_name,
                    "version": version,
                    "embedding": embedding,
                    "stats": stats[player_name]
                }

                # 🔴 ОТПРАВЛЯЕМ СИНХРОННО ЧЕРЕЗ send_to_player_sync
                if self.server and hasattr(self.server, 'loop') and self.server.loop:
                    import asyncio
                    future = asyncio.run_coroutine_threadsafe(
                        self.server.send_to_player(player_id, msg),
                        self.server.loop
                    )
                    # 🔴 ЖДЁМ завершения отправки (5 секунд максимум)
                    try:
                        future.result(timeout=5)
                        self.add_log(f"✅ Отправлен model_update для {player_name} (512 dims)")
                    except Exception as e:
                        self.add_log(f"❌ Ошибка отправки для {player_name}: {e}")
                else:
                    self.add_log(f"❌ Нет сервера или loop для {player_name}")

            except Exception as e:
                self.add_log(f"❌ Ошибка отправки для {player_name}: {e}")
                import traceback
                self.add_log(traceback.format_exc())
