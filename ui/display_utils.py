"""
Утилиты для отображения
"""

import os
import sys
from typing import List, Tuple, Dict

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


def clear_screen():
    """Очистить экран"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Напечатать заголовок"""
    width = 60
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)


def print_menu(title: str, items: List[Tuple[str, str, str]]):
    """Напечатать меню"""
    print_colored(f"\n{title}", "cyan")
    print("-" * 60)
    
    for number, item, description in items:
        print_colored(f"{number}. {item}", "green")
        print_colored(f"   {description}", "white")
        print()


def print_status_bar(day: int, money: int, state: str):
    """Напечатать статус бар"""
    print_colored(f"📅 День: {day} | 💰 Деньги: {money} ₽ | 🎮 Статус: {state}", "yellow")


def print_skills(skills, progress: Dict[str, tuple]):
    """Напечатать навыки"""
    print_colored("\n📊 НАВЫКИ ПЕРСОНАЖА:", "cyan")
    
    skill_names_ru = {
        "economics": "📊 Экономика",
        "management": "👨‍💼 Менеджмент",
        "finance": "💳 Финансы",
        "marketing": "📢 Маркетинг",
        "happiness": "😊 Счастье",
        "health": "❤️ Здоровье",
        "reputation": "⭐ Репутация"
    }
    
    for skill_name, (value, status) in progress.items():
        display_name = skill_names_ru.get(skill_name, skill_name)
        bar_length = 20
        filled = int(value / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Цвет в зависимости от значения
        if value >= 80:
            color = "green"
        elif value >= 60:
            color = "cyan"
        elif value >= 40:
            color = "yellow"
        elif value >= 20:
            color = "magenta"
        else:
            color = "red"
        
        print_colored(f"  {display_name}:", "white", end=" ")
        print_colored(f"{bar} {value:3d}/100", color, end=" ")
        print_colored(f"({status})", "white")


def print_achievements(achievements: List[str]):
    """Напечатать достижения"""
    print_colored("\n🏆 ДОСТИЖЕНИЯ:", "cyan")
    for achievement in achievements:
        print_colored(f"  ✓ {achievement}", "green")


def print_choice_result(choice, old_skills: Dict, new_skills: Dict):
    """Показать результат выбора"""
    print_colored("\n" + "─" * 60, "cyan")
    print_colored("📝 РЕЗУЛЬТАТ ВЫБОРА:", "yellow")
    print_colored(f"«{choice.text}»", "green")
    print()
    
    # Показать изменения
    changes = []
    
    # Изменение денег
    if "money" in choice.effects:
        old_money = old_skills.get("money", 0)
        new_money = new_skills.get("money", 0)
        diff = new_money - old_money
        if diff != 0:
            sign = "+" if diff > 0 else ""
            changes.append(f"💰 Деньги: {old_money} → {new_money} ({sign}{diff} ₽)")
    
    # Изменения навыков
    for skill_name in ["economics", "management", "finance", "marketing", "happiness", "health", "reputation"]:
        if skill_name in choice.effects:
            old_value = old_skills.get(skill_name, 0)
            new_value = new_skills.get(skill_name, 0)
            diff = new_value - old_value
            if diff != 0:
                skill_names_ru = {
                    "economics": "📊 Экономика",
                    "management": "👨‍💼 Менеджмент",
                    "finance": "💳 Финансы",
                    "marketing": "📢 Маркетинг",
                    "happiness": "😊 Счастье",
                    "health": "❤️ Здоровье",
                    "reputation": "⭐ Репутация"
                }
                display_name = skill_names_ru.get(skill_name, skill_name)
                sign = "+" if diff > 0 else ""
                changes.append(f"{display_name}: {old_value} → {new_value} ({sign}{diff})")
    
    if changes:
        for change in changes:
            print_colored(f"  {change}", "white")
    else:
        print_colored("  Нет изменений", "white")


def print_game_over(scene):
    """Показать экран окончания игры"""
    clear_screen()
    
    if scene.game_over:
        print_colored("\n" + "█" * 60, "red")
        print_colored("GAME OVER".center(60), "red")
        print_colored("█" * 60, "red")
    else:
        print_colored("\n" + "★" * 60, "yellow")
        print_colored("ИГРА ЗАВЕРШЕНА".center(60), "yellow")
        print_colored("★" * 60, "yellow")
    
    print()
    print_colored(scene.title, "cyan")
    print()
    
    # Разбиваем описание на строки
    lines = scene.description.split('\n')
    for line in lines:
        print_colored(f"  {line}", "white")
    
    print()


def print_colored(text: str, color: str = "white", end: str = "\n"):
    """Напечатать цветной текст"""
    if not COLORAMA_AVAILABLE:
        print(text, end=end)
        return
    
    color_map = {
        "black": Fore.BLACK,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "bright_black": Fore.LIGHTBLACK_EX,
        "bright_red": Fore.LIGHTRED_EX,
        "bright_green": Fore.LIGHTGREEN_EX,
        "bright_yellow": Fore.LIGHTYELLOW_EX,
        "bright_blue": Fore.LIGHTBLUE_EX,
        "bright_magenta": Fore.LIGHTMAGENTA_EX,
        "bright_cyan": Fore.LIGHTCYAN_EX,
        "bright_white": Fore.LIGHTWHITE_EX,
    }
    
    color_code = color_map.get(color.lower(), Fore.WHITE)
    print(f"{color_code}{text}{Style.RESET_ALL}", end=end)
