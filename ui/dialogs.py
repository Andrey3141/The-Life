"""
Диалоговые окна для экономической симуляции
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QComboBox, QFrame,
                               QGraphicsDropShadowEffect, QWidget, QLineEdit,
                               QGridLayout, QMessageBox, QScrollArea)  # ДОБАВЛЕНО QLineEdit, QGridLayout, QMessageBox, QScrollArea
from PySide6.QtCore import Qt, Signal  # ДОБАВЛЕНО Signal
from PySide6.QtGui import QFont, QColor, QPixmap  # ДОБАВЛЕНО QPixmap

from config import THEMES


class ModernDialog(QDialog):
    """Современный стилизованный диалог"""
    
    def __init__(self, parent=None, title="", theme_name="dark"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        theme = THEMES[theme_name]
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 20px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
    
    def set_content(self, content_widget):
        """Установить контент диалога"""
        self.main_layout.addWidget(content_widget)


class ThemeSelectorDialog(QDialog):
    """Диалог выбора темы оформления"""
    
    def __init__(self, parent=None, current_theme="dark", current_image_path=""):
        super().__init__(parent)
        self.setWindowTitle("Выбор темы оформления")
        self.setFixedSize(500, 350)
        self.setModal(True)
        
        self.selected_theme = current_theme
        self.selected_image_path = current_image_path
        
        theme = THEMES[current_theme]
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 20px;
            }}
            QLabel {{
                color: {theme["text"]};
            }}
            QComboBox {{
                background-color: {theme["bg_card"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 10px;
                font-size: 12pt;
                min-height: 30px;
            }}
            QComboBox:hover {{
                border: 1px solid {theme["border_hover"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {theme["text"]};
                margin-right: 10px;
            }}
            QPushButton {{
                background-color: {theme["bg_card"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                min-height: 35px;
            }}
            QPushButton:hover {{
                background-color: rgba(59, 130, 246, 0.2);
                border: 1px solid #3b82f6;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("🎨 Настройка темы оформления")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Выбор темы
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Выберите тему:")
        theme_label.setFont(QFont("Segoe UI", 11))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌙 Темная", "dark")
        self.theme_combo.addItem("☀️ Светлая", "light")
        self.theme_combo.addItem("🖼️ Своя картинка", "custom")
        
        # Устанавливаем текущую тему
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo, 1)
        layout.addLayout(theme_layout)
        
        # ИЗМЕНЕНО: Контейнер для элементов выбора картинки
        self.image_container = QWidget()
        image_layout = QHBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_path_label = QLabel("Файл не выбран")
        self.image_path_label.setFont(QFont("Segoe UI", 10))
        self.image_path_label.setWordWrap(True)
        self.image_path_label.setStyleSheet(f"color: {theme['text_secondary']}; padding: 5px;")
        
        browse_btn = QPushButton("📁 Обзор...")
        browse_btn.clicked.connect(self.browse_image)
        
        image_layout.addWidget(self.image_path_label, 1)
        image_layout.addWidget(browse_btn)
        
        # ИЗМЕНЕНО: Добавляем контейнер в основной layout
        layout.addWidget(self.image_container)
        
        # ИЗМЕНЕНО: Управляем видимостью в зависимости от выбранной темы
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.on_theme_changed(self.theme_combo.currentIndex())
        
        # Если уже есть выбранная картинка
        if current_image_path and os.path.exists(current_image_path):
            self.image_path_label.setText(os.path.basename(current_image_path))
        
        layout.addStretch()
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Применить")
        apply_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)
        layout.addLayout(button_layout)
    
    def browse_image(self):
        """Выбрать изображение для фона"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фоновое изображение",
            os.path.expanduser("~"),
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.image_path_label.setText(os.path.basename(file_path))
            # Автоматически выбираем тему "custom"
            index = self.theme_combo.findData("custom")
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
    
    # ИЗМЕНЕНО: Новый метод для управления видимостью элементов выбора картинки
    def on_theme_changed(self, index):
        """Обработчик изменения выбранной темы"""
        theme_data = self.theme_combo.currentData()
        # Показываем контейнер только для темы "custom" (своя картинка)
        self.image_container.setVisible(theme_data == "custom")
    
    def accept(self):
        """Принять выбор"""
        self.selected_theme = self.theme_combo.currentData()
        if self.selected_theme == "custom" and not os.path.exists(self.selected_image_path):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Предупреждение", "Выберите изображение для фона!")
            return
        super().accept()


# ============= НОВЫЙ КЛАСС: Диалог ввода имён участников с кнопками камеры =============

class ParticipantInputDialog(QDialog):
    """Диалог для ввода имён участников с возможностью фотосъёмки"""
    
    # Сигналы для обновления версий фото
    photo_taken = Signal(str, int)  # (participant_name, version)
    
    def __init__(self, parent=None, theme_name="dark"):
        super().__init__(parent)
        self.setWindowTitle("👥 Ввод участников")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        
        self.participants = []
        self.participant_widgets = []  # Список (line_edit, camera_btn, version_label)
        self.photo_versions = {}  # Словарь {имя: версия}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme["bg_secondary"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 20px;
            }}
            QLabel {{
                color: {self.theme["text"]};
                font-size: 12pt;
            }}
            QLineEdit {{
                background-color: {self.theme["bg_card"]};
                color: {self.theme["text"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 8px;
                padding: 10px;
                font-size: 12pt;
                min-height: 30px;
            }}
            QLineEdit:focus {{
                border: 2px solid #3b82f6;
            }}
            QPushButton {{
                border-radius: 8px;
                padding: 8px;
                font-size: 14pt;
                min-width: 40px;
                min-height: 40px;
            }}
            QPushButton#cameraBtn {{
                background-color: #3b82f6;
                color: white;
                border: none;
            }}
            QPushButton#cameraBtn:hover {{
                background-color: #2563eb;
            }}
            QPushButton#cameraBtn:checked {{
                background-color: #10b981;
            }}
            QPushButton#addBtn {{
                background-color: #10b981;
                color: white;
                border: none;
                font-size: 12pt;
                min-width: 100px;
                padding: 10px;
            }}
            QPushButton#addBtn:hover {{
                background-color: #059669;
            }}
            QPushButton#startBtn {{
                background-color: #8b5cf6;
                color: white;
                border: none;
                font-size: 14pt;
                font-weight: bold;
                min-width: 200px;
                min-height: 50px;
                padding: 10px 20px;
            }}
            QPushButton#startBtn:hover {{
                background-color: #7c3aed;
            }}
            QPushButton#startBtn:disabled {{
                background-color: #64748b;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("👥 Введите имена участников")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Область прокрутки для списка участников
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {self.theme["border"]};
                border-radius: 10px;
                background-color: {self.theme["bg_card"]};
            }}
            QScrollBar:vertical {{
                background: {self.theme["bg"]};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme["border"]};
                border-radius: 4px;
            }}
        """)
        
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)
        
        # Кнопка добавления участника
        add_btn = QPushButton("➕ Добавить участника")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self.add_participant)
        layout.addWidget(add_btn)
        
        # Кнопка начала игры
        self.start_btn = QPushButton("▶ НАЧАТЬ ИГРУ")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.accept)
        layout.addWidget(self.start_btn)
        
        # Добавляем первого участника по умолчанию
        self.add_participant()
    
    def add_participant(self):
        """Добавить поле для ввода имени нового участника"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Поле ввода имени
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(f"Участник {len(self.participant_widgets) + 1}")
        line_edit.textChanged.connect(self.check_start_button)
        layout.addWidget(line_edit, 1)
        
        # Метка для отображения версии фото
        version_label = QLabel("0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFixedSize(30, 40)
        version_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme["bg"]};
                color: #10b981;
                border: 2px solid #10b981;
                border-radius: 8px;
                font-size: 12pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(version_label)
        
        # Кнопка камеры
        camera_btn = QPushButton("📷")
        camera_btn.setObjectName("cameraBtn")
        camera_btn.setFixedSize(50, 40)
        camera_btn.clicked.connect(lambda: self.take_photos(line_edit, version_label))
        layout.addWidget(camera_btn)
        
        # Кнопка удаления (если не первый)
        if len(self.participant_widgets) > 0:
            remove_btn = QPushButton("❌")
            remove_btn.setFixedSize(40, 40)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12pt;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_participant(widget))
            layout.addWidget(remove_btn)
        
        # Добавляем в список
        self.participant_widgets.append((line_edit, camera_btn, version_label))
        
        # Вставляем перед stretch
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, widget)
        
        self.check_start_button()
    
    def remove_participant(self, widget):
        """Удалить участника"""
        # Находим индекс виджета
        for i, (line_edit, camera_btn, version_label) in enumerate(self.participant_widgets):
            if line_edit.parent() == widget:
                # Удаляем из списка
                self.participant_widgets.pop(i)
                # Удаляем из словаря версий
                name = line_edit.text().strip()
                if name and name in self.photo_versions:
                    del self.photo_versions[name]
                break
        
        # Удаляем виджет
        widget.deleteLater()
        self.check_start_button()
    
    def take_photos(self, line_edit, version_label):
        """Открыть диалог фотосъёмки для участника"""
        name = line_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Предупреждение", "Сначала введите имя!")
            return
        
        # Импортируем здесь, чтобы избежать циклических импортов
        from ui.camera_dialog import CameraDialog
        
        dialog = CameraDialog(name, self, self.theme_name)
        if dialog.exec() == QDialog.Accepted and hasattr(dialog, 'photos_taken') and len(dialog.photos_taken) == 10:
            # Сохраняем фото
            self.save_photos(name, dialog.photos_taken)
            
            # Увеличиваем версию
            current_version = self.photo_versions.get(name, 0)
            new_version = current_version + 1
            self.photo_versions[name] = new_version
            
            # Обновляем метку
            version_label.setText(str(new_version))
            
            # Меняем цвет кнопки камеры на зелёный
            camera_btn = line_edit.parent().findChild(QPushButton, "cameraBtn")
            if camera_btn:
                camera_btn.setStyleSheet("""
                    QPushButton#cameraBtn {
                        background-color: #10b981;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 14pt;
                    }
                    QPushButton#cameraBtn:hover {
                        background-color: #059669;
                    }
                """)
            
            # Отправляем сигнал
            self.photo_taken.emit(name, new_version)
            
            QMessageBox.information(self, "Успех", f"Фото для {name} сохранены! Версия: {new_version}")
    
    def save_photos(self, name, photos):
        """Сохранить фотографии"""
        try:
            # Создаём директорию для фото
            photo_dir = "data/photos"
            os.makedirs(photo_dir, exist_ok=True)
            
            # Получаем текущую версию
            version = self.photo_versions.get(name, 0) + 1
            
            # Сохраняем фото
            for i, photo in enumerate(photos):
                filename = f"{photo_dir}/{name}_v{version}_{i}.png"
                photo.save(filename)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить фото: {e}")
    
    def check_start_button(self):
        """Проверить, можно ли активировать кнопку старта"""
        # Проверяем, что все поля заполнены
        all_filled = True
        for line_edit, _, _ in self.participant_widgets:
            if not line_edit.text().strip():
                all_filled = False
                break
        
        # Активируем кнопку, если есть хотя бы один участник и все поля заполнены
        self.start_btn.setEnabled(len(self.participant_widgets) > 0 and all_filled)
    
    def get_participants(self):
        """Получить список участников"""
        participants = []
        for line_edit, _, version_label in self.participant_widgets:
            name = line_edit.text().strip()
            if name:
                participants.append(name)
        return participants
    
    def get_photo_versions(self):
        """Получить словарь версий фото"""
        return self.photo_versions.copy()


# ============= СТАРЫЙ КОД =============
from .mode_selector_dialog import ModeSelectorDialog
