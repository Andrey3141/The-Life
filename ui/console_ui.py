"""
Консольный интерфейс игры
"""

import time
from typing import Optional

from core.game_engine import GameEngine
from core.models import GameState
from ui.display_utils import (
    clear_screen,
    print_header,
    print_menu,
    print_status_bar,
    print_skills,
    print_achievements,
    print_choice_result,
    print_game_over
)
from ui.animations import (
    typewriter_effect,
    loading_animation,
    print_colored
)


class ConsoleUI:
    """Консольный интерфейс пользователя"""
    
    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine
        self.last_update = time.time()
    
    def display_main_menu(self):
        """Отобразить главное меню"""
        clear_screen()
        print_header("ЭКОНОМИЧЕСКАЯ СИМУЛЯЦИЯ")
        
        menu_items = [
            ("1", "Новая игра", "Начать новую игру"),
            ("2", "Загрузить игру", "Продолжить сохраненную игру"),
            ("3", "Статистика", "Показать статистику игры"),
            ("4", "Об игре", "Информация об игре"),
            ("5", "Выход", "Выйти из игры")
        ]
        
        print_menu("ГЛАВНОЕ МЕНЮ", menu_items)
    
    def display_game(self):
        """Отобразить игровое состояние"""
        clear_screen()
        
        # Заголовок и статус
        print_header("ИГРАЕМ")
        print_status_bar(
            day=self.game_engine.player.day if self.game_engine.player else 1,
            money=self.game_engine.player.skills.money if self.game_engine.player else 0,
            state=self.game_engine.state.value
        )
        
        # Текущая сцена
        scene = self.game_engine.get_current_scene()
        if scene:
            print_colored(f"\n📖 {scene.title}", "yellow")
            typewriter_effect(scene.description, delay=0.02)
            print()
        
        # Навыки
        if self.game_engine.player:
            progress = self.game_engine.get_skill_progress()
            print_skills(self.game_engine.player.skills, progress)
        
        # Достижения
        if self.game_engine.player and self.game_engine.player.achievements:
            print_achievements(self.game_engine.player.achievements)
        
        # Выборы
        available_choices = self.game_engine.get_available_choices()
        if available_choices:
            print_colored("\n🎯 ВАРИАНТЫ ДЕЙСТВИЙ:", "cyan")
            for i, choice in enumerate(available_choices, 1):
                status = ""
                if not choice.is_available(self.game_engine.player.skills):
                    if choice.money_cost > self.game_engine.player.skills.money:
                        status = f" [💰 Не хватает {choice.money_cost} ₽]"
                    elif choice.required_skill:
                        subject, level = choice.required_skill
                        current = self.game_engine.player.skills.get_skill(subject)
                        status = f" [📚 {subject.value} {level}+ (у вас {current})]"
                
                choice_text = f"{i}. {choice.text}{status}"
                if status:
                    print_colored(choice_text, "red")
                else:
                    print_colored(choice_text, "green")
        
        # Подсказка
        if scene and scene.is_ending:
            print_colored("\n🎮 Игра завершена! Нажмите Enter для выхода в меню.", "magenta")
        elif available_choices:
            print_colored(f"\n⌨️  Введите номер выбора (1-{len(available_choices)}): ", "yellow", end="")
        else:
            print_colored("\n⚠️  Нет доступных выборов. Нажмите Enter для продолжения...", "red")
    
    def display_pause_menu(self):
        """Отобразить меню паузы"""
        clear_screen()
        print_header("ПАУЗА")
        
        menu_items = [
            ("1", "Продолжить", "Вернуться к игре"),
            ("2", "Сохранить игру", "Сохранить текущий прогресс"),
            ("3", "Загрузить игру", "Загрузить сохранение"),
            ("4", "Главное меню", "Выйти в главное меню")
        ]
        
        print_menu("МЕНЮ ПАУЗЫ", menu_items)
    
    def display_load_menu(self, saves):
        """Отобразить меню загрузки"""
        clear_screen()
        print_header("ЗАГРУЗКА ИГРЫ")
        
        if not saves:
            print_colored("\n⚠️  Сохранений не найдено!", "red")
            print_colored("\nНажмите Enter для возврата...", "yellow")
            return
        
        print_colored("\n📂 ДОСТУПНЫЕ СОХРАНЕНИЯ:", "cyan")
        for i, save in enumerate(saves, 1):
            timestamp = save['timestamp'][:19].replace('T', ' ')
            print_colored(f"\n{i}. {save['player_name']} - День {save['day']}", "green")
            print_colored(f"   💰 {save['money']} ₽ | 📅 {timestamp}", "white")
        
        print_colored(f"\n\n⌨️  Выберите сохранение (1-{len(saves)}) или '0' для отмены: ", "yellow", end="")
    
    def display_save_menu(self):
        """Отобразить меню сохранения"""
        clear_screen()
        print_header("СОХРАНЕНИЕ ИГРЫ")
        
        menu_items = [
            ("1", "Быстрое сохранение", "Сохранить в автоматический слот"),
            ("2", "Именованное сохранение", "Создать именованное сохранение"),
            ("3", "Назад", "Вернуться в игру")
        ]
        
        print_menu("МЕНЮ СОХРАНЕНИЯ", menu_items)
    
    def display_stats(self):
        """Отобразить статистику игры"""
        clear_screen()
        print_header("СТАТИСТИКА")
        
        stats = self.game_engine.get_game_stats()
        
        if not stats:
            print_colored("\n⚠️  Статистика недоступна!", "red")
            return
        
        print_colored("\n📊 ОБЩАЯ СТАТИСТИКА:", "cyan")
        print_colored(f"👤 Игрок: {stats['player_name']}", "green")
        print_colored(f"📅 День: {stats['day']}", "green")
        print_colored(f"💰 Деньги: {stats['money']} ₽", "green")
        print_colored(f"🏆 Достижений: {stats['achievements']}", "green")
        print_colored(f"⏱️  Время игры: {stats['play_time']} сек", "green")
        print_colored(f"🎮 Статус: {stats['state']}", "green")
        
        if self.game_engine.player:
            print_colored("\n🎯 НАВЫКИ ИГРОКА:", "cyan")
            progress = self.game_engine.get_skill_progress()
            for skill_name, (value, status) in progress.items():
                print_colored(f"   {skill_name}: {value}/100 ({status})", "white")
        
        print_colored("\n\nНажмите Enter для возврата...", "yellow")
    
    def display_about(self):
        """Отобразить информацию об игре"""
        clear_screen()
        print_header("ОБ ИГРЕ")
        
        about_text = """
🎮 ЭКОНОМИЧЕСКАЯ СИМУЛЯЦИЯ: ПУТЬ К УСПЕХУ

📚 ОПИСАНИЕ:
Это текстовая игра-симулятор, которая демонстрирует важность 
знаний в экономике и менеджменте для принятия жизненных решений.

🎯 ЦЕЛЬ ИГРЫ:
Принимая различные решения, вы будете развивать навыки персонажа
и строить успешную карьеру, учитывая баланс между работой и личной жизнью.

📊 КЛЮЧЕВЫЕ НАВЫКИ:
• 📊 Экономика - анализ рынков и финансовых потоков
• 👨‍💼 Менеджмент - управление командами и проектами
• 💳 Финансы - управление личными и корпоративными финансами
• 😊 Счастье - баланс между работой и личной жизнью

🏆 ДОСТИЖЕНИЯ:
Игра содержит систему достижений, которые можно получить,
развивая различные навыки и принимая правильные решения.

🔄 ВАРИАНТЫ РАЗВИТИЯ:
• Корпоративная карьера
• Собственный стартап
• Государственная служба

👨‍💻 РАЗРАБОТЧИК:
Игра создана для демонстрации важности экономических знаний
в современном мире.

Версия: 1.0.0
"""
        
        typewriter_effect(about_text, delay=0.01)
        print_colored("\n\nНажмите Enter для возврата...", "yellow")
    
    def display_loading(self, message="Загрузка..."):
        """Показать анимацию загрузки"""
        loading_animation(message)
    
    def display_choice_result(self, choice, old_skills, new_skills):
        """Показать результат выбора"""
        print_choice_result(choice, old_skills, new_skills)
    
    def display_game_over(self, scene):
        """Показать экран окончания игры"""
        print_game_over(scene)
    
    def get_input(self, prompt=""):
        """Получить ввод от пользователя"""
        if prompt:
            print_colored(prompt, "yellow", end="")
        return input().strip()
    
    def wait_for_enter(self, message="Нажмите Enter для продолжения..."):
        """Ожидать нажатия Enter"""
        print_colored(f"\n{message}", "yellow", end="")
        input()
    
    def show_message(self, message, message_type="info"):
        """Показать сообщение"""
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        color = colors.get(message_type, "white")
        print_colored(f"\n{message}", color)
        time.sleep(1.5)
