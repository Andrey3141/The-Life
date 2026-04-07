"""
Диалог для съёмки фотографий участников (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)
"""

import cv2
import logging
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QRect
from PySide6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor

from config import THEMES

logger = logging.getLogger("CameraDialog")
logger.setLevel(logging.DEBUG)


class CameraThread(QThread):
    """Поток для захвата кадров с камеры"""
    frame_ready = Signal(object)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.is_running = False
        self.camera_id = 0
        self.frame_skip = 2  # Пропускаем каждый 2-й кадр
        self.frame_count = 0
        
    def run(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            self.error_occurred.emit("Не удалось открыть камеру")
            return
            
        # Устанавливаем меньший размер для производительности
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)  # Ограничиваем FPS
            
        self.is_running = True
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # Пропускаем кадры для детекции
                self.frame_count += 1
                if self.frame_count % self.frame_skip == 0:
                    self.frame_ready.emit(frame)
            else:
                self.error_occurred.emit("Ошибка захвата кадра")
                break
            QThread.msleep(66)  # ~15 FPS
            
    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()


class FaceOverlayLabel(QLabel):
    """QLabel с отрисовкой квадрата вокруг лица"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.face_rect = None
        self.setMinimumSize(640, 480)
        self.setAlignment(Qt.AlignCenter)
        
    def set_face_rect(self, rect):
        self.face_rect = rect
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.face_rect and self.pixmap():
            painter = QPainter(self)
            
            # Масштабируем координаты
            pixmap = self.pixmap()
            scale_x = self.width() / pixmap.width()
            scale_y = self.height() / pixmap.height()
            
            x = int(self.face_rect.x() * scale_x)
            y = int(self.face_rect.y() * scale_y)
            w = int(self.face_rect.width() * scale_x)
            h = int(self.face_rect.height() * scale_y)
            
            # Рисуем зелёный квадрат
            pen = QPen(QColor(16, 185, 129))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRect(x, y, w, h)
            
            # Рисуем уголки
            corner_len = 30
            painter.drawLine(x, y, x + corner_len, y)
            painter.drawLine(x, y, x, y + corner_len)
            painter.drawLine(x + w - corner_len, y, x + w, y)
            painter.drawLine(x + w, y, x + w, y + corner_len)
            painter.drawLine(x, y + h - corner_len, x, y + h)
            painter.drawLine(x, y + h, x + corner_len, y + h)
            painter.drawLine(x + w - corner_len, y + h, x + w, y + h)
            painter.drawLine(x + w, y + h - corner_len, x + w, y + h)


class CameraDialog(QDialog):
    """Диалог для съёмки фотографий"""
    
    def __init__(self, player_name, parent=None, current_theme="dark"):
        super().__init__(parent)
        self.player_name = player_name
        self.current_theme = current_theme
        self.theme = THEMES.get(current_theme, THEMES["dark"])
        
        self.photos_taken = []
        self.current_photo_count = 0
        self.total_photos = 10
        self.face_detected = False
        self.face_rect = None
        self.last_detection_time = 0
        self.detection_interval = 3  # Детекция лица каждый 3-й кадр
        self.frame_counter = 0
        
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.error_occurred.connect(self.show_error)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.take_photo)
        
        self.setWindowTitle(f"📸 Фотосъёмка: {player_name}")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.resize(900, 700)
        
        self.setup_ui()
        self.camera_thread.start()
        
    def setup_ui(self):
        self.setStyleSheet(f"QDialog {{ background-color: {self.theme['bg']}; }}")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title_layout = QHBoxLayout()
        
        back_btn = QPushButton("◀ Назад")
        back_btn.setFont(QFont("Segoe UI", 12))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setMinimumHeight(40)
        back_btn.setMinimumWidth(100)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        back_btn.clicked.connect(self.reject)
        
        title_label = QLabel(f"📸 Фотосъёмка: {self.player_name}")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme['text']};")
        title_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(back_btn)
        title_layout.addWidget(title_label, 1)
        
        layout.addLayout(title_layout)
        
        # Область предпросмотра камеры
        self.preview_label = FaceOverlayLabel()
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                border: 2px solid #3b82f6;
                border-radius: 15px;
            }
        """)
        layout.addWidget(self.preview_label, 1)
        
        # Информационная панель
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['bg_overlay']};
                border: 1px solid {self.theme['border']};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        info_layout = QHBoxLayout(info_frame)
        
        self.count_label = QLabel(f"📸 Фото: 0/{self.total_photos}")
        self.count_label.setFont(QFont("Segoe UI", 14))
        self.count_label.setStyleSheet(f"color: {self.theme['text']}; padding: 10px; background: rgba(59,130,246,0.1); border-radius: 10px;")
        
        self.status_label = QLabel("👤 Ожидание лица...")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setStyleSheet("color: #f59e0b; padding: 10px; background: rgba(245,158,11,0.1); border-radius: 10px;")
        
        info_layout.addWidget(self.count_label)
        info_layout.addWidget(self.status_label)
        
        layout.addWidget(info_frame)
        
        # Кнопка съёмки
        self.capture_btn = QPushButton("📸 СФОТКАТЬ")
        self.capture_btn.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.capture_btn.setCursor(Qt.PointingHandCursor)
        self.capture_btn.setMinimumHeight(80)
        self.capture_btn.setEnabled(False)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #64748b;
            }
        """)
        self.capture_btn.clicked.connect(self.start_capture_sequence)
        
        layout.addWidget(self.capture_btn)
        
    def update_frame(self, frame):
        """Обновление кадра с камеры (оптимизированное)"""
        try:
            self.frame_counter += 1
            
            # Детекция лица только каждый detection_interval-й кадр
            if self.frame_counter % self.detection_interval == 0:
                # Уменьшаем разрешение для детекции (в 2 раза)
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                
                # Используем более быстрые параметры
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.2, 3, minSize=(50, 50))
                
                if len(faces) > 0:
                    # Масштабируем координаты обратно
                    x, y, w, h = faces[0]
                    x *= 2
                    y *= 2
                    w *= 2
                    h *= 2
                    
                    self.face_detected = True
                    self.face_rect = QRect(x, y, w, h)
                    
                    if not self.capture_btn.isEnabled():
                        self.capture_btn.setEnabled(True)
                        self.status_label.setText("✅ Лицо обнаружено!")
                        self.status_label.setStyleSheet("color: #10b981; padding: 10px; background: rgba(16,185,129,0.1); border-radius: 10px;")
                else:
                    self.face_detected = False
                    self.face_rect = None
                    self.capture_btn.setEnabled(False)
                    self.status_label.setText("👤 Лицо не найдено")
                    self.status_label.setStyleSheet("color: #f59e0b; padding: 10px; background: rgba(245,158,11,0.1); border-radius: 10px;")
            
            # Конвертируем и отображаем каждый кадр
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Быстрое масштабирование
            pixmap = QPixmap.fromImage(qt_image).scaled(
                self.preview_label.width(), self.preview_label.height(),
                Qt.KeepAspectRatio, Qt.FastTransformation
            )
            self.preview_label.setPixmap(pixmap)
            self.preview_label.set_face_rect(self.face_rect)
            
        except Exception as e:
            logger.error(f"Error updating frame: {e}")
    
    def start_capture_sequence(self):
        """Начать последовательную съёмку 10 фото"""
        self.current_photo_count = 0
        self.photos_taken = []
        self.capture_btn.setEnabled(False)
        self.status_label.setText("📸 Съёмка... 0/10")
        self.timer.start(200)  # Уменьшил интервал до 200мс
        
    def take_photo(self):
        """Сделать одно фото"""
        if self.current_photo_count < self.total_photos and hasattr(self, 'preview_label') and self.preview_label.pixmap():
            # Сохраняем фото (копируем, чтобы не зависеть от изменений)
            pixmap = self.preview_label.pixmap().copy()
            if pixmap:
                self.photos_taken.append(pixmap)
                self.current_photo_count += 1
                self.count_label.setText(f"📸 Фото: {self.current_photo_count}/{self.total_photos}")
                self.status_label.setText(f"📸 Съёмка... {self.current_photo_count}/{self.total_photos}")
        else:
            self.timer.stop()
            self.finish_capture()
    
    def finish_capture(self):
        """Завершить съёмку"""
        if len(self.photos_taken) == self.total_photos:
            self.status_label.setText("✅ Съёмка завершена!")
            # Небольшая задержка перед закрытием
            QTimer.singleShot(500, self.accept)
        else:
            self.status_label.setText("❌ Ошибка съёмки")
            self.capture_btn.setEnabled(True)
    
    def show_error(self, error_msg):
        """Показать ошибку"""
        QMessageBox.critical(self, "Ошибка камеры", error_msg)
        self.reject()
    
    def closeEvent(self, event):
        self.camera_thread.stop()
        self.camera_thread.wait()
        event.accept()
