"""
Конфигурация игры
"""

import os
import json

# Версия игры
GAME_VERSION = "1.9.3"
GAME_YEAR = 2026

# Название игры
GAME_NAME = "Экономическая Симуляция: Путь к Успеху"
GAME_DESCRIPTION = "Симулятор для изучения экономики и менеджмента с современным интерфейсом"

# Полное название для заголовка окна
GAME_TITLE = f"💰 {GAME_NAME} v{GAME_VERSION}"

# Размеры окна
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Цветовая палитра (для обратной совместимости)
COLORS = {
    "primary": "#0f172a",
    "secondary": "#1e293b",
    "surface": "#334155",
    "accent_blue": "#3b82f6",
    "accent_purple": "#8b5cf6",
    "accent_green": "#10b981",
    "accent_yellow": "#f59e0b",
    "accent_pink": "#ec4899",
    "accent_red": "#ef4444",
    "text_primary": "#f8fafc",
    "text_secondary": "#cbd5e1",
    "text_muted": "#94a3b8",
    "text_disabled": "#64748b",
    "border_light": "rgba(255, 255, 255, 0.1)",
    "border_medium": "rgba(255, 255, 255, 0.2)",
    "border_heavy": "rgba(255, 255, 255, 0.3)",
    "bg_overlay": "rgba(15, 23, 42, 0.7)",
    "bg_card": "rgba(30, 41, 59, 0.7)",
    "bg_hover": "rgba(30, 41, 59, 0.9)",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "danger": "#ef4444",
    "border": "rgba(255, 255, 255, 0.2)",
}

# Настройки шрифтов (для обратной совместимости)
FONTS = {
    "display_large": ("Segoe UI", 48, "bold"),
    "display_medium": ("Segoe UI", 36, "bold"),
    "display_small": ("Segoe UI", 24, "bold"),
    "title_large": ("Segoe UI", 20, "bold"),
    "title_medium": ("Segoe UI", 16, "bold"),
    "title_small": ("Segoe UI", 14, "bold"),
    "body_large": ("Segoe UI", 16, "normal"),
    "body_medium": ("Segoe UI", 14, "normal"),
    "body_small": ("Segoe UI", 12, "normal"),
    "label_large": ("Segoe UI", 14, "medium"),
    "label_medium": ("Segoe UI", 12, "medium"),
    "label_small": ("Segoe UI", 11, "medium"),
    "emoji_large": ("Segoe UI Emoji", 32, "normal"),
    "emoji_medium": ("Segoe UI Emoji", 24, "normal"),
    "emoji_small": ("Segoe UI Emoji", 16, "normal"),
}

# Тексты интерфейса
TEXTS = {
    "welcome": "🚀 ДОБРО ПОЖАЛОВАТЬ В ЭКОНОМИЧЕСКУЮ СИМУЛЯЦИЮ!",
    "goal": "Принимайте стратегические решения и стройте карьеру мечты",
    "menu_new_game": "🚀 НОВАЯ ИГРА",
    "menu_load_game": "📂 ЗАГРУЗИТЬ ИГРУ",
    "menu_stats": "📊 СТАТИСТИКА",
    "menu_settings": "⚙️ НАСТРОЙКИ",
    "menu_tutorial": "📚 ОБУЧЕНИЕ",
    "menu_exit": "🚪 ВЫХОД",
    "player_creation": "👤 СОЗДАНИЕ ПЕРСОНАЖА",
    "enter_name": "Ваше имя:",
    "enter_age": "Возраст:",
    
    "stats_total_games": "Всего игр",
    "stats_wins": "Побед",
    "stats_losses": "Поражений",
    "stats_achievements": "Достижений",
    "stats_money_record": "Рекорд денег",
    "stats_endings_found": "Найденных финалов",
    
    "card_new_game": "Начните путь к финансовому успеху",
    "card_load_game": "Продолжите с сохранённой позиции",
    "card_stats": "Анализ достижений и результатов",
    "card_settings": "Настройка параметров игры",
    "card_tutorial": "Изучите основы экономики",
    "card_exit": "Завершить приложение",
    
    "copyright": f"© {GAME_YEAR} Экономическая Симуляция • Версия {GAME_VERSION}",
}

# Градиенты
GRADIENTS = {
    "primary": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #334155)",
    "title": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:0.5 #8b5cf6, stop:1 #ec4899)",
    "card_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(59, 130, 246, 0.1), stop:1 rgba(139, 92, 246, 0.1))",
}

# Настройки игры
GAME_SETTINGS = {
    "starting_money": 10000,
    "starting_age": 25,
    "min_age": 18,
    "max_age": 100,
    "max_skills": 100,
    "min_skills": 0,
    "total_scenes": 70,
    "total_endings": 12,
    "total_skills": 7,
    "career_paths": 3,
}

# Пути к файлам
PATHS = {
    "saves_dir": "data/saves",
    "config_file": "data/config.json",
    "results_file": "data/game_results.json",
    "stats_file": "data/player_stats.json",
    "theme_config": "data/theme_config.json",
}

# Настройки тем оформления
THEMES = {
    "dark": {
        "name": "🌙 Темная",
        "bg": "#0f172a",
        "bg_secondary": "#1e293b",
        "bg_card": "rgba(30, 41, 59, 0.85)",
        "bg_overlay": "rgba(15, 23, 42, 0.8)",
        "bg_hover": "rgba(30, 41, 59, 0.95)",
        "text": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "border": "rgba(255, 255, 255, 0.2)",
        "border_hover": "rgba(255, 255, 255, 0.4)",
        "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:0.5 #1e293b, stop:1 #334155)",
        "use_image": False,
        "image_path": ""
    },
    "light": {
        "name": "☀️ Светлая",
        "bg": "#f8fafc",
        "bg_secondary": "#ffffff",
        "bg_card": "rgba(255, 255, 255, 0.9)",
        "bg_overlay": "rgba(255, 255, 255, 0.85)",
        "bg_hover": "rgba(255, 255, 255, 0.95)",
        "text": "#0f172a",
        "text_secondary": "#1e293b",
        "text_muted": "#475569",
        "border": "#cbd5e1",
        "border_hover": "#94a3b8",
        "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fafc, stop:0.5 #ffffff, stop:1 #f1f5f9)",
        "use_image": False,
        "image_path": ""
    },
    "custom": {
        "name": "🖼️ Своя картинка",
        "bg": "rgba(15, 23, 42, 0.85)",
        "bg_secondary": "rgba(30, 41, 59, 0.8)",
        "bg_card": "rgba(30, 41, 59, 0.8)",
        "bg_overlay": "rgba(15, 23, 42, 0.75)",
        "bg_hover": "rgba(30, 41, 59, 0.9)",
        "text": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "border": "rgba(255, 255, 255, 0.2)",
        "border_hover": "rgba(255, 255, 255, 0.4)",
        "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(15, 23, 42, 0.85), stop:0.5 rgba(30, 41, 59, 0.8), stop:1 rgba(51, 65, 85, 0.75))",
        "use_image": True,
        "image_path": ""
    }
}

# Функции для сохранения и загрузки темы
def save_theme_config(theme_name, image_path=""):
    """Сохранить настройки темы"""
    try:
        os.makedirs("data", exist_ok=True)
        config = {
            "theme": theme_name,
            "image_path": image_path
        }
        with open(PATHS["theme_config"], 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения темы: {e}")
        return False

def load_theme_config():
    """Загрузить настройки темы"""
    try:
        if os.path.exists(PATHS["theme_config"]):
            with open(PATHS["theme_config"], 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("theme", "dark"), config.get("image_path", "")
    except Exception as e:
        print(f"Ошибка загрузки темы: {e}")
    return "dark", ""

# Загружаем сохраненную тему
CURRENT_THEME, CUSTOM_IMAGE_PATH = load_theme_config()
if CUSTOM_IMAGE_PATH and os.path.exists(CUSTOM_IMAGE_PATH):
    THEMES["custom"]["image_path"] = CUSTOM_IMAGE_PATH

# ============= ДОБАВЛЕНО (МИНИМУМ ИЗМЕНЕНИЙ) =============
# Режимы работы приложения
APP_MODES = {
    "single": {
        "name": "Одиночная игра",
        "icon": "🎮",
        "description": "Классический режим"
    },
    "server": {
        "name": "Серверный режим",
        "icon": "🌐",
        "description": "Режим с сервером для телефонов"
    }
}

# Настройки сервера
SERVER_CONFIG = {
    "default_host": "0.0.0.0",
    "default_port": 8888,
    "max_players": 10
}
