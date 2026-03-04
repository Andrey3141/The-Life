"""
Базовые классы для игрового интерфейса
"""

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QPolygon
from PySide6.QtCore import QPoint

from config import GAME_VERSION, THEMES
import os


class ImageWithBorderLabel(QLabel):
    """QLabel с жирной черной рамкой для эффекта каньона"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap_data = None
        self.border_color = QColor(0, 0, 0)
        self.border_width = 8
        self.secondary_border_width = 4
        self.margin = 4
    
    def set_image(self, image_path):
        """Установить изображение"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.pixmap_data = pixmap
            self.update()
            return True
        return False
    
    def set_border_color(self, color):
        """Установить цвет рамки"""
        self.border_color = color
        self.update()
    
    def set_border_width(self, width):
        """Установить толщину рамки"""
        self.border_width = width
        self.update()
    
    def paintEvent(self, event):
        """Отрисовка с жирной черной рамкой"""
        if self.pixmap_data and not self.pixmap_data.isNull():
            painter = QPainter(self)
            
            scaled_pixmap = self.pixmap_data.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            
            painter.drawPixmap(x, y, scaled_pixmap)
            
            pen = QPen(self.border_color, self.border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            painter.drawRect(
                self.margin, self.margin,
                self.width() - 2 * self.margin,
                self.height() - 2 * self.margin
            )
            
            pen.setWidth(self.secondary_border_width)
            painter.setPen(pen)
            painter.drawRect(
                self.margin + self.border_width, self.margin + self.border_width,
                self.width() - 2 * (self.margin + self.border_width),
                self.height() - 2 * (self.margin + self.border_width)
            )
        else:
            super().paintEvent(event)


class GraphNode:
    """Узел графа ветвления"""
    
    def __init__(self, x, y, node_id="", scene_id=""):
        self.x = x
        self.y = y
        self.id = node_id
        self.scene_id = scene_id
        self.state = "future"  # future, past, current
        self.connections = []  # Список связанных узлов (id узлов)


class GraphWidget(QWidget):
    """Виджет для отображения графа ветвления"""
    
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.nodes = {}  # Словарь узлов по id
        self.current_node_id = None
        self.is_game_over = False  # Флаг проигрыша
        self.setMinimumWidth(350)
        self.setMinimumHeight(600)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['bg_card']};
                border: 1px solid {self.theme['border']};
                border-radius: 10px;
            }}
        """)
    
    def build_from_scenes(self, scenes_data, current_scene_id="start"):
        """Построить граф на основе данных сцен"""
        self.nodes.clear()
        self.is_game_over = False
        
        # Сначала создадим все узлы
        node_positions = self.calculate_node_positions(scenes_data)
        
        for scene in scenes_data:
            if scene.scene_id in node_positions:
                x, y = node_positions[scene.scene_id]
                node = GraphNode(x, y, scene.scene_id, scene.scene_id)
                self.nodes[scene.scene_id] = node
        
        # Теперь добавим связи
        for scene in scenes_data:
            if scene.scene_id in self.nodes:
                node = self.nodes[scene.scene_id]
                for choice in scene.choices:
                    if choice.next_scene_id in self.nodes:
                        if choice.next_scene_id not in node.connections:
                            node.connections.append(choice.next_scene_id)
        
        # Установим текущий узел
        if current_scene_id in self.nodes:
            self.set_current_node(current_scene_id)
        
        self.update()
    
    def calculate_node_positions(self, scenes_data):
        """Рассчитать позиции узлов для красивого отображения"""
        positions = {}
        
        # Создадим карту уровней на основе BFS
        levels = {}
        queue = [("start", 0)]
        visited = set()
        
        while queue:
            scene_id, level = queue.pop(0)
            if scene_id in visited:
                continue
            
            visited.add(scene_id)
            levels[scene_id] = level
            
            # Найдем сцену
            scene = None
            for s in scenes_data:
                if s.scene_id == scene_id:
                    scene = s
                    break
            
            if scene:
                for choice in scene.choices:
                    if choice.next_scene_id not in visited:
                        queue.append((choice.next_scene_id, level + 1))
        
        # Группируем узлы по уровням
        level_nodes = {}
        for scene_id, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(scene_id)
        
        # Рассчитываем позиции - РАСТЯНУТЫЕ ПО ШИРИНЕ
        start_y = 30
        level_height = 60
        total_width = 300
        
        for level, nodes in level_nodes.items():
            y = start_y + level * level_height
            count = len(nodes)
            
            if count == 1:
                x = 150
            elif count == 2:
                x_positions = [80, 220]
            elif count == 3:
                x_positions = [50, 150, 250]
            elif count == 4:
                x_positions = [40, 110, 190, 260]
            else:
                step = total_width // (count - 1) if count > 1 else 0
                x_positions = [30 + i * step for i in range(count)]
            
            for i, node_id in enumerate(nodes):
                if count == 1:
                    x = 150
                else:
                    x = x_positions[i] if i < len(x_positions) else 150
                positions[node_id] = (x, y)
        
        return positions
    
    def set_game_over(self, is_game_over):
        """Установить состояние проигрыша"""
        self.is_game_over = is_game_over
        self.update()
    
    def set_current_node(self, node_id):
        """Установить текущий узел"""
        if node_id not in self.nodes:
            return
        
        # Сбрасываем состояния всех узлов
        for node in self.nodes.values():
            node.state = "future"
        
        # Отмечаем путь от старта до текущего узла
        self.mark_path_to_node("start", node_id)
        
        self.current_node_id = node_id
        self.update()
    
    def mark_path_to_node(self, start_id, target_id):
        """Отметить путь от start_id до target_id без рекурсии"""
        if start_id not in self.nodes or target_id not in self.nodes:
            return False
        
        # Используем BFS для поиска пути
        queue = [(start_id, [])]
        visited = set()
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_id == target_id:
                # Нашли путь - отмечаем все узлы
                for node_id in path + [target_id]:
                    if node_id in self.nodes:
                        if node_id == target_id:
                            self.nodes[node_id].state = "current"
                        else:
                            self.nodes[node_id].state = "past"
                return True
            
            # Добавляем соседей в очередь
            for next_id in self.nodes[current_id].connections:
                if next_id not in visited:
                    queue.append((next_id, path + [current_id]))
        
        return False
    
    def paintEvent(self, event):
        """Отрисовка графа"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Сначала рисуем все соединения
        for node_id, node in self.nodes.items():
            for connected_id in node.connections:
                if connected_id in self.nodes:
                    connected_node = self.nodes[connected_id]
                    
                    # Определяем цвет линии
                    if self.is_game_over:
                        # При проигрыше все линии красные
                        color = QColor(239, 68, 68)  # Красный
                    else:
                        if (node.state == "past" and connected_node.state == "past") or \
                           (node.state == "past" and connected_node.state == "current") or \
                           (node.state == "current" and connected_node.state == "past"):
                            color = QColor(34, 197, 94)  # Зеленый для пройденных путей
                        elif node.state == "current" or connected_node.state == "current":
                            color = QColor(250, 204, 21)  # Желтый для текущего пути
                        else:
                            color = QColor(156, 163, 175)  # Серый для непройденных
                    
                    pen = QPen(color, 2)
                    painter.setPen(pen)
                    
                    # Рисуем линию
                    painter.drawLine(node.x, node.y, connected_node.x, connected_node.y)
        
        # Затем рисуем узлы (кружочки)
        for node_id, node in self.nodes.items():
            # Определяем цвет узла
            if self.is_game_over:
                # При проигрыше все узлы красные
                color = QColor(239, 68, 68)  # Красный
                border_color = QColor(220, 38, 38)
            else:
                if node.state == "current":
                    color = QColor(250, 204, 21)  # Желтый
                    border_color = QColor(234, 179, 8)
                elif node.state == "past":
                    color = QColor(34, 197, 94)  # Зеленый
                    border_color = QColor(22, 163, 74)
                else:
                    color = QColor(156, 163, 175)  # Серый
                    border_color = QColor(107, 114, 128)
            
            # Рисуем круг
            painter.setBrush(color)
            painter.setPen(QPen(border_color, 2))
            painter.drawEllipse(node.x - 10, node.y - 10, 20, 20)
    
    def update_node_state(self, node_id, state):
        """Обновить состояние узла"""
        if node_id in self.nodes:
            self.nodes[node_id].state = state
            self.update()
    
    def clear_graph(self):
        """Очистить граф"""
        self.nodes.clear()
        self.current_node_id = None
        self.is_game_over = False
        self.update()


class GameUIBase:
    """Базовый класс с общими методами для игрового интерфейса"""
    
    @staticmethod
    def get_skill_display_name(skill_key):
        """Получить отображаемое имя навыка"""
        skill_names = {
            "economics": "Экономика",
            "management": "Менеджмент",
            "finance": "Финансы",
            "marketing": "Маркетинг",
            "happiness": "Счастье",
            "health": "Здоровье",
            "reputation": "Репутация",
            "money": "Деньги"
        }
        return skill_names.get(skill_key, skill_key)
    
    @staticmethod
    def darken_color(color):
        """Затемнить цвет для эффекта hover"""
        if color.startswith("#") and len(color) == 7:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    @staticmethod
    def get_skill_color(value):
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
    
    def setup_skill_bars(self, skills_group, theme):
        """Настройка прогресс-баров навыков"""
        from PySide6.QtWidgets import QProgressBar
        
        skill_bars = {}
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
            skill_widget = QWidget()
            skill_widget.setStyleSheet("background-color: transparent;")
            skill_h_layout = QHBoxLayout(skill_widget)
            skill_h_layout.setContentsMargins(0, 5, 0, 5)
            
            label = QLabel(skill_name)
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet(f"color: {theme['text_secondary']}; min-width: 120px; background-color: transparent;")
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setTextVisible(True)
            progress_bar.setFormat("%v/100")
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                    text-align: center;
                    background-color: rgba(255, 255, 255, 0.05);
                    color: #f8fafc;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #3b82f6;
                    border-radius: 5px;
                }
            """)
            
            skill_h_layout.addWidget(label)
            skill_h_layout.addWidget(progress_bar, 1)
            
            skills_group.layout().addWidget(skill_widget)
            skill_bars[skill_key] = progress_bar
        
        return skill_bars
    
    def show_error_message(self, parent, message):
        """Показать сообщение об ошибке"""
        msg_box = QMessageBox(parent)
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
    
    def show_info_message(self, parent, title, message):
        """Показать информационное сообщение"""
        msg_box = QMessageBox(parent)
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
