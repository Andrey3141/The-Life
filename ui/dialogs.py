"""
Диалоговые окна для экономической симуляции
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QComboBox, QFrame,
                               QGraphicsDropShadowEffect, QWidget)  # ДОБАВЛЕНО QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

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

# ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
from .mode_selector_dialog import ModeSelectorDialog
