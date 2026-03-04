"""
Система меню игры
"""

import os
import sys
from typing import Optional

from core.game_engine import GameEngine
from core.save_manager import SaveManager
from ui.console_ui import ConsoleUI
from ui.display_utils import (
    clear_screen,
    print_header,
    print_menu,
    print_colored
)
from ui.animations import typewriter_effect, loading_animation


class MainMenu:
    """Главное меню игры"""
    
    def __init__(self, game_engine: GameEngine, console_ui: ConsoleUI):
        self.game_engine = game_engine
        self.console_ui = console_ui
        self.save_manager = SaveManager()
        self.running = True
    
    def run(self):
        """Запустить главное меню"""
        while self.running:
            self.console_ui.display_main_menu()
            choice = self.console_ui.get_input("Выберите пункт меню: ")
            
            if choice == "1":
                self.start_new_game()
            elif choice == "2":
                self.load_game_menu()
            elif choice == "3":
                self.show_stats()
            elif choice == "4":
                self.show_about()
            elif choice == "5":
                self.exit_game()
            else:
                self.console_ui.show_message("Неверный выбор!", "error")
    
    def start_new_game(self):
        """Начать новую игру"""
        clear_screen()
        print_header("НОВАЯ ИГРА")
        
        print_colored("\n👤 СОЗДАНИЕ ПЕРСОНАЖА", "cyan")
        
        # Имя персонажа
        player_name = ""
        while not player_name.strip():
            player_name = self.console_ui.get_input("Введите имя персонажа: ")
            if not player_name.strip():
                self.console_ui.show_message("Имя не может быть пустым!", "error")
        
        # Возраст
        age = 25
        try:
            age_input = self.console_ui.get_input("Введите возраст персонажа [25]: ")
            if age_input.strip():
                age = int(age_input)
                age = max(18, min(60, age))  # Ограничение от 18 до 60
        except ValueError:
            self.console_ui.show_message("Используется возраст по умолчанию (25)", "warning")
        
        # Создание игры
        self.console_ui.display_loading("Создание новой игры...")
        
        if self.game_engine.new_game(player_name):
            self.game_engine.player.age = age
            self.console_ui.show_message(f"Игра создана! Добро пожаловать, {player_name}!", "success")
            self.run_game()
        else:
            self.console_ui.show_message("Ошибка при создании игры!", "error")
    
    def load_game_menu(self):
        """Меню загрузки игры"""
        saves = self.save_manager.list_saves()
        self.console_ui.display_load_menu(saves)
        
        if not saves:
            self.console_ui.wait_for_enter()
            return
        
        choice = self.console_ui.get_input()
        
        if choice == "0":
            return
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(saves):
                selected_save = saves[choice_idx]
                self.load_game(selected_save['filename'])
            else:
                self.console_ui.show_message("Неверный выбор!", "error")
        except ValueError:
            self.console_ui.show_message("Пожалуйста, введите номер!", "error")
    
    def load_game(self, filename: str):
        """Загрузить игру"""
        self.console_ui.display_loading("Загрузка игры...")
        
        save = self.save_manager.load_game(filename)
        if save and self.game_engine.load_game(save.to_dict()):
            self.console_ui.show_message(f"Игра загружена! Добро пожаловать обратно, {save.player.name}!", "success")
            self.run_game()
        else:
            self.console_ui.show_message("Ошибка при загрузке игры!", "error")
    
    def save_game_menu(self):
        """Меню сохранения игры"""
        self.console_ui.display_save_menu()
        choice = self.console_ui.get_input("Выберите действие: ")
        
        if choice == "1":
            self.quick_save()
        elif choice == "2":
            self.named_save()
        elif choice == "3":
            return
        else:
            self.console_ui.show_message("Неверный выбор!", "error")
    
    def quick_save(self):
        """Быстрое сохранение"""
        if self.game_engine.state.value not in ["playing", "paused"]:
            self.console_ui.show_message("Нельзя сохранить игру в текущем состоянии!", "error")
            return
        
        save_data = self.game_engine.save_game()
        if save_data:
            from core.models import GameSave
            game_save = GameSave.from_dict(save_data)
            
            if self.save_manager.save_game(game_save, "auto"):
                self.console_ui.show_message("Игра успешно сохранена!", "success")
            else:
                self.console_ui.show_message("Ошибка при сохранении игры!", "error")
        else:
            self.console_ui.show_message("Нет данных для сохранения!", "error")
    
    def named_save(self):
        """Именованное сохранение"""
        if self.game_engine.state.value not in ["playing", "paused"]:
            self.console_ui.show_message("Нельзя сохранить игру в текущем состоянии!", "error")
            return
        
        clear_screen()
        print_header("ИМЕНОВАННОЕ СОХРАНЕНИЕ")
        
        slot_name = self.console_ui.get_input("Введите название сохранения: ")
        
        if not slot_name.strip():
            self.console_ui.show_message("Название не может быть пустым!", "error")
            return
        
        save_data = self.game_engine.save_game()
        if save_data:
            from core.models import GameSave
            game_save = GameSave.from_dict(save_data)
            
            if self.save_manager.save_game(game_save, slot_name):
                self.console_ui.show_message(f"Игра сохранена как '{slot_name}'!", "success")
            else:
                self.console_ui.show_message("Ошибка при сохранении игры!", "error")
        else:
            self.console_ui.show_message("Нет данных для сохранения!", "error")
    
    def show_stats(self):
        """Показать статистику"""
        self.console_ui.display_stats()
        self.console_ui.wait_for_enter()
    
    def show_about(self):
        """Показать информацию об игре"""
        self.console_ui.display_about()
        self.console_ui.wait_for_enter()
    
    def run_game(self):
        """Запустить игровой цикл"""
        while self.game_engine.state in [self.game_engine.state.PLAYING, self.game_engine.state.PAUSED]:
            
            if self.game_engine.state == self.game_engine.state.PLAYING:
                self.game_loop()
            elif self.game_engine.state == self.game_engine.state.PAUSED:
                self.pause_loop()
            
            # Проверка окончания игры
            if self.game_engine.state in [self.game_engine.state.FINISHED, self.game_engine.state.GAME_OVER]:
                self.game_over()
                break
    
    def game_loop(self):
        """Основной игровой цикл"""
        self.console_ui.display_game()
        
        scene = self.game_engine.get_current_scene()
        if not scene:
            self.console_ui.show_message("Ошибка: сцена не найдена!", "error")
            self.game_engine.state = self.game_engine.state.GAME_OVER
            return
        
        # Если это финальная сцена
        if scene.is_ending:
            self.console_ui.wait_for_enter("Нажмите Enter для выхода в меню...")
            self.game_engine.state = self.game_engine.state.FINISHED
            return
        
        available_choices = self.game_engine.get_available_choices()
        
        if not available_choices:
            self.console_ui.wait_for_enter()
            return
        
        # Обработка ввода игрока
        while True:
            try:
                choice_input = self.console_ui.get_input()
                
                # Специальные команды
                if choice_input.lower() == "меню":
                    self.game_engine.state = self.game_engine.state.PAUSED
                    return
                elif choice_input.lower() == "сохранить":
                    self.quick_save()
                    self.console_ui.display_game()
                    continue
                elif choice_input.lower() == "статистика":
                    self.show_stats()
                    self.console_ui.display_game()
                    continue
                
                # Обычный выбор
                choice_idx = int(choice_input) - 1
                
                if 0 <= choice_idx < len(available_choices):
                    # Сохраняем старые навыки для отображения изменений
                    old_skills = self.game_engine.player.skills.__dict__.copy() if self.game_engine.player else {}
                    
                    if self.game_engine.make_choice(choice_idx):
                        # Показываем результат выбора
                        if self.game_engine.player:
                            new_skills = self.game_engine.player.skills.__dict__.copy()
                            self.console_ui.display_choice_result(
                                available_choices[choice_idx],
                                old_skills,
                                new_skills
                            )
                            self.console_ui.wait_for_enter("Нажмите Enter для продолжения...")
                        break
                    else:
                        self.console_ui.show_message("Этот выбор недоступен!", "error")
                        self.console_ui.display_game()
                else:
                    self.console_ui.show_message("Неверный номер выбора!", "error")
                    self.console_ui.display_game()
                    
            except ValueError:
                self.console_ui.show_message("Пожалуйста, введите номер!", "error")
                self.console_ui.display_game()
            except KeyboardInterrupt:
                self.game_engine.state = self.game_engine.state.PAUSED
                return
    
    def pause_loop(self):
        """Цикл меню паузы"""
        self.console_ui.display_pause_menu()
        choice = self.console_ui.get_input("Выберите пункт меню: ")
        
        if choice == "1":
            self.game_engine.state = self.game_engine.state.PLAYING
        elif choice == "2":
            self.save_game_menu()
        elif choice == "3":
            self.load_game_menu()
        elif choice == "4":
            self.game_engine.state = self.game_engine.state.MENU
        else:
            self.console_ui.show_message("Неверный выбор!", "error")
    
    def game_over(self):
        """Обработка окончания игры"""
        scene = self.game_engine.get_current_scene()
        if scene:
            self.console_ui.display_game_over(scene)
        
        # Предложение сохранить результат
        if self.game_engine.state == self.game_engine.state.FINISHED:
            save_result = self.console_ui.get_input("\nСохранить результат игры? (да/нет): ")
            if save_result.lower() in ["да", "д", "yes", "y"]:
                save_name = self.console_ui.get_input("Введите название сохранения: ")
                if save_name.strip():
                    save_data = self.game_engine.save_game()
                    if save_data:
                        from core.models import GameSave
                        game_save = GameSave.from_dict(save_data)
                        self.save_manager.save_game(game_save, f"result_{save_name}")
                        self.console_ui.show_message("Результат сохранен!", "success")
        
        self.console_ui.wait_for_enter("Нажмите Enter для возврата в главное меню...")
        self.game_engine.state = self.game_engine.state.MENU
    
    def exit_game(self):
        """Выйти из игры"""
        clear_screen()
        print_header("ВЫХОД ИЗ ИГРЫ")
        
        print_colored("\nСпасибо за игру!", "green")
        print_colored("До новых встреч!", "yellow")
        
        self.running = False
