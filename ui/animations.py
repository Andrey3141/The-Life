"""
Анимации для игры
"""

import time
import sys
from typing import Optional

from ui.display_utils import print_colored


def typewriter_effect(text: str, delay: float = 0.03, end: str = "\n"):
    """Эффект печатной машинки"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print(end=end)


def loading_animation(message: str = "Загрузка", duration: float = 1.5):
    """Анимация загрузки"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    start_time = time.time()
    frame_idx = 0
    
    while time.time() - start_time < duration:
        frame = frames[frame_idx % len(frames)]
        sys.stdout.write(f"\r{frame} {message}...")
        sys.stdout.flush()
        frame_idx += 1
        time.sleep(0.1)
    
    sys.stdout.write(f"\r{' ' * (len(message) + 10)}\r")


def countdown_animation(seconds: int, message: str = "Начинаем через"):
    """Анимация обратного отсчета"""
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{message} {i}...")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")


def progress_bar(progress: float, width: int = 40, label: str = ""):
    """Прогресс бар"""
    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int(progress * 100)
    
    if label:
        print_colored(f"{label}: [{bar}] {percentage}%", "cyan")
    else:
        print_colored(f"[{bar}] {percentage}%", "cyan")


def flash_message(message: str, color: str = "yellow", times: int = 3):
    """Мигающее сообщение"""
    for _ in range(times):
        print(f"\r{message}", end='')
        time.sleep(0.3)
        print(f"\r{' ' * len(message)}", end='')
        time.sleep(0.3)
    print(f"\r{message}")


def print_ascii_art():
    """Показать ASCII арт"""
    art = """
    ╔═══════════════════════════════════════════════════════╗
    ║  ███████╗ ██████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗║
    ║  ██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║║
    ║  █████╗  ██║     ██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║║
    ║  ██╔══╝  ██║     ██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║║
    ║  ███████╗╚██████╗╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║║
    ║  ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝║
    ║                                                           ║
    ║         ЭКОНОМИЧЕСКАЯ СИМУЛЯЦИЯ: ПУТЬ К УСПЕХУ           ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print_colored(art, "cyan")
