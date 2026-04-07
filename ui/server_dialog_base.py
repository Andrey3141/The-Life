"""
Базовые классы для серверного диалога
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QLineEdit, QListWidgetItem, QScrollArea, QWidget,
                               QMessageBox)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap

from config import THEMES
import os


class AnimatedButton(QPushButton):
    """Кнопка с анимацией при наведении"""
    
    def __init__(self, text, parent=None, color="#3b82f6"):
        super().__init__(text, parent)
        self.color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        
    def enterEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()
        super().leaveEvent(event)


class PlayerCard(QFrame):
    """Карточка игрока в списке"""
    
    # ДОБАВЛЕНО: сигнал для фото
    photo_taken = Signal(str, str, int)  # (player_id, player_name, version)
    
    def __init__(self, player_name, player_id, connected_at, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.player_id = player_id
        self.connected_at = connected_at
        self.photo_version = 0
        self.has_photo = False
        
        self.setObjectName("playerCard")
        self.setFixedHeight(70)
        self.setStyleSheet("""
            QFrame#playerCard {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid #3b82f6;
                border-radius: 10px;
                margin: 2px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Аватар
        avatar = QLabel("👤")
        avatar.setFont(QFont("Segoe UI", 20))
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background-color: #3b82f6; border-radius: 20px; color: white;")
        layout.addWidget(avatar)
        
        # Информация
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(player_name)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_label.setStyleSheet("color: #f8fafc; background: transparent;")
        
        time_label = QLabel(connected_at.strftime("%H:%M:%S"))
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: #94a3b8; background: transparent;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout, 1)
        
        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(59, 130, 246, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def take_photo(self):
        """Открыть диалог фотосъёмки"""
        from ui.camera_dialog import CameraDialog
        from ml.face_trainer import FaceTrainer
        
        dialog = CameraDialog(self.player_name, self.window())
        if dialog.exec() == QDialog.Accepted and hasattr(dialog, 'photos_taken') and len(dialog.photos_taken) == 10:
            # Обучаем модель
            trainer = FaceTrainer()
            new_version = trainer.train_new_face(self.player_name, dialog.photos_taken)
            
            if new_version > 0:
                # Обновляем отображение
                self.photo_version = new_version
                self.has_photo = True
                self.version_label.setText(str(new_version))
                
                # Меняем иконку на птичку (НЕ фон кнопки)
                self.camera_btn.setText("✅")
                
                # Отключаем кнопку
                self.camera_btn.setEnabled(False)
                
                # ДОБАВЛЕНО: испускаем сигнал
                self.photo_taken.emit(self.player_id, self.player_name, new_version)
    
    def set_photo_version(self, version):
        """Установить версию фото"""
        self.photo_version = version
        self.has_photo = version > 0
        self.version_label.setText(str(version))
        
        if version > 0:
            self.camera_btn.setText("✅")
            self.camera_btn.setEnabled(False)
        else:
            self.camera_btn.setText("📷")
            self.camera_btn.setEnabled(True)


class ParticipantsListDialog(QDialog):
    """Диалог для ввода имён участников"""
    
    def __init__(self, parent=None, current_theme="dark"):
        super().__init__(parent)
        self.current_theme = current_theme
        self.theme = THEMES.get(current_theme, THEMES["dark"])
        self.participants = []
        self.photo_versions = {}  # {имя: версия}
        
        self.setWindowTitle("👥 Участники игры")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("👥 Введите имена участников")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Контейнер для полей ввода
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setSpacing(10)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавляем первое поле
        self.add_participant_field()
        
        scroll.setWidget(self.fields_container)
        layout.addWidget(scroll, 1)
        
        # Кнопка добавления
        add_btn = QPushButton("➕ Добавить участника")
        add_btn.setFont(QFont("Segoe UI", 12))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.add_participant_field)
        layout.addWidget(add_btn)
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setFont(QFont("Segoe UI", 12))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        
        self.start_btn = QPushButton("✅ Начать игру")
        self.start_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.start_btn)
        
        layout.addLayout(button_layout)
    
    def add_participant_field(self):
        """Добавить поле для ввода имени участника"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Поле ввода имени
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Участник {self.fields_layout.count() + 1}")
        line_edit.setFont(QFont("Segoe UI", 11))
        line_edit.setMinimumHeight(35)
        line_edit.textChanged.connect(self.check_fields)
        layout.addWidget(line_edit, 1)
        
        # ============= ДОБАВЛЕНО: метка версии фото =============
        version_label = QLabel("0")
        version_label.setFixedSize(35, 35)
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                color: #10b981;
                border: 2px solid #10b981;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(version_label)
        
        # ============= ДОБАВЛЕНО: кнопка камеры =============
        camera_btn = QPushButton("📷")
        camera_btn.setFixedSize(35, 35)
        camera_btn.setFont(QFont("Segoe UI", 12))
        camera_btn.setCursor(Qt.PointingHandCursor)
        camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #64748b;
            }
        """)
        # Привязываем обработчик с передачей line_edit, version_label и camera_btn
        camera_btn.clicked.connect(lambda: self.take_photos(line_edit, version_label, camera_btn))
        layout.addWidget(camera_btn)
        
        # Кнопка удаления (только если не первое поле)
        if self.fields_layout.count() > 0:
            remove_btn = QPushButton("❌")
            remove_btn.setFixedSize(35, 35)
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_field(widget))
            layout.addWidget(remove_btn)
        
        self.fields_layout.addWidget(widget)
    
    # ============= ДОБАВЛЕНО: новый метод для фотосъёмки =============
    def take_photos(self, line_edit, version_label, camera_btn):
        """Открыть диалог фотосъёмки для участника"""
        name = line_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Предупреждение", "Сначала введите имя!")
            return
    
        from ui.camera_dialog import CameraDialog
        from ml.face_trainer import FaceTrainer
    
        dialog = CameraDialog(name, self)
        if dialog.exec() == QDialog.Accepted and hasattr(dialog, 'photos_taken') and len(dialog.photos_taken) == 10:
            # Обучаем модель (пока без статистики, передаём пустой словарь)
            trainer = FaceTrainer()
            # ИСПРАВЛЕНО: добавляем пустой словарь для stats
            new_version = trainer.train_new_face(name, dialog.photos_taken, {})
        
            if new_version > 0:
                # Обновляем отображение
                version_label.setText(str(new_version))
                self.photo_versions[name] = new_version
            
                # Меняем иконку на птичку
                camera_btn.setText("✅")
                camera_btn.setEnabled(False)
            
                QMessageBox.information(self, "Успех", f"Фото для {name} сохранены! Версия: {new_version}")
    
    def remove_field(self, widget):
        """Удалить поле"""
        widget.deleteLater()
        self.check_fields()
    
    def check_fields(self):
        """Проверить заполненность полей"""
        all_filled = True
        for i in range(self.fields_layout.count()):
            item = self.fields_layout.itemAt(i)
            if item and item.widget():
                line_edit = item.widget().findChild(QLineEdit)
                if not line_edit or not line_edit.text().strip():
                    all_filled = False
                    break
        
        self.start_btn.setEnabled(self.fields_layout.count() > 0 and all_filled)
    
    def get_participants(self):
        """Получить список участников"""
        participants = []
        for i in range(self.fields_layout.count()):
            item = self.fields_layout.itemAt(i)
            if item and item.widget():
                line_edit = item.widget().findChild(QLineEdit)
                if line_edit:
                    name = line_edit.text().strip()
                    if name:
                        participants.append(name)
        return participants
    
    def get_photo_versions(self):
        """Получить словарь версий фото"""
        return self.photo_versions.copy()
    
    def apply_theme(self):
        """Применить тему"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme["bg_secondary"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 20px;
            }}
            QLabel {{
                color: {self.theme["text"]};
            }}
            QLineEdit {{
                background-color: {self.theme["bg_card"]};
                color: {self.theme["text"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 5px;
                padding: 5px 10px;
            }}
            QLineEdit:focus {{
                border: 2px solid #3b82f6;
            }}
        """)
