"""
Пользовательский интерфейс
"""

from .console_ui import ConsoleUI
from .menu_system import MainMenu
from .display_utils import clear_screen, print_colored, print_header
from .animations import typewriter_effect, loading_animation
from .stats_window import StatsWindow
from .game_ui import GameUI
from .dialogs import ModernDialog, ThemeSelectorDialog
from .game_ui_base import ImageWithBorderLabel, GameUIBase

__all__ = [
    'ConsoleUI',
    'MainMenu',
    'clear_screen',
    'print_colored',
    'print_header',
    'typewriter_effect',
    'loading_animation',
    'StatsWindow',
    'GameUI',
    'ModernDialog',
    'ThemeSelectorDialog',
    'ImageWithBorderLabel',
    'GameUIBase'
]
