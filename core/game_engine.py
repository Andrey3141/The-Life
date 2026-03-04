"""
Игровой движок - управление состоянием игры
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

from core.models import Player, Scene, GameSave, GameState, Subject, Skill
from core.save_manager import SaveManager
from scenes.scene_manager import SceneManager


class GameEngine:
    """Игровой движок - управление состоянием игры"""
    
    def __init__(self):
        self.player: Optional[Player] = None
        self.scene_manager: Optional[SceneManager] = None
        self.save_manager = SaveManager()
        self.state = GameState.MENU
        
        # Загружаем статистику
        self.load_stats()
    
    def new_game(self, name: str, age: int = 25) -> bool:
        """Создать новую игру"""
        try:
            self.player = Player(
                name=name,
                age=age,
                profession="Начинающий специалист",
                skills=Skill(),
                day=1,
                achievements=[],
                current_scene_id="start"
            )
            
            self.state = GameState.PLAYING
            return True
        except Exception as e:
            print(f"Ошибка создания игры: {e}")
            return False
    
    def make_choice(self, choice_index: int) -> bool:
        """Сделать выбор в текущей сцене"""
        if not self.player or not self.scene_manager:
            return False
        
        scene = self.get_current_scene()
        if not scene:
            return False
        
        if choice_index < 0 or choice_index >= len(scene.choices):
            return False
        
        choice = scene.choices[choice_index]
        
        # Проверяем доступность выбора
        if not choice.is_available(self.player.skills):
            return False
        
        # Проверяем достаточно ли денег
        if choice.money_cost > self.player.skills.money:
            return False
        
        # Применяем эффекты
        for skill, value in choice.effects.items():
            if hasattr(self.player.skills, skill):
                current = getattr(self.player.skills, skill)
                setattr(self.player.skills, skill, max(0, min(100, current + value)))
        
        # Вычитаем стоимость
        if choice.money_cost > 0:
            self.player.skills.money -= choice.money_cost
        
        # Переходим к следующей сцене
        self.player.current_scene_id = choice.next_scene_id
        self.player.day += 1
        
        # Проверяем, не достиг ли игрок конца игры
        next_scene = self.get_current_scene()
        if next_scene and next_scene.is_ending:
            # Сохраняем результат игры
            self.save_game_result(next_scene.game_over)
            self.state = GameState.FINISHED
        
        return True
    
    def get_current_scene(self) -> Optional[Scene]:
        """Получить текущую сцену"""
        if not self.player or not self.scene_manager:
            return None
        
        return self.scene_manager.get_scene(self.player.current_scene_id)
    
    def get_available_choices(self) -> List:
        """Получить доступные выборы для текущей сцены"""
        scene = self.get_current_scene()
        if not scene:
            return []
        
        return scene.choices
    
    def save_game_result(self, is_loss: bool = False) -> bool:
        """Сохранить результат игры в статистику"""
        if not self.player:
            return False
        
        try:
            # Создаем запись о результате игры
            game_result = {
                'player_name': self.player.name,
                'date': datetime.now().isoformat(),
                'days_played': self.player.day,
                'final_money': self.player.skills.money,
                'achievements_count': len(self.player.achievements),
                'is_loss': is_loss,
                'skills': self.player.skills.to_dict()
            }
            
            # Загружаем текущую статистику
            stats_file = "data/game_results.json"
            os.makedirs(os.path.dirname(stats_file), exist_ok=True)
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            else:
                stats = {'games': []}
            
            # Добавляем результат
            stats['games'].append(game_result)
            
            # Сохраняем
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            # Также обновляем статистику игрока
            self.update_player_stats(is_loss)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения результата: {e}")
            return False
    
    def update_player_stats(self, is_loss: bool) -> bool:
        """Обновить статистику игрока"""
        if not self.player:
            return False
        
        try:
            stats_file = "data/player_stats.json"
            os.makedirs(os.path.dirname(stats_file), exist_ok=True)
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            else:
                all_stats = {}
            
            player_name = self.player.name
            
            if player_name not in all_stats:
                all_stats[player_name] = {
                    'total_games': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_days': 0,
                    'total_money': 0,
                    'achievements': [],
                    'games': []
                }
            
            player_stats = all_stats[player_name]
            player_stats['total_games'] += 1
            
            if is_loss:
                player_stats['losses'] += 1
            else:
                player_stats['wins'] += 1
            
            player_stats['total_days'] += self.player.day
            player_stats['total_money'] += self.player.skills.money
            
            # Добавляем достижения
            for achievement in self.player.achievements:
                if achievement not in player_stats['achievements']:
                    player_stats['achievements'].append(achievement)
            
            # Добавляем информацию об игре
            game_info = {
                'date': datetime.now().isoformat(),
                'days': self.player.day,
                'money': self.player.skills.money,
                'is_loss': is_loss
            }
            player_stats['games'].append(game_info)
            
            # Сохраняем
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка обновления статистики игрока: {e}")
            return False
    
    def load_stats(self):
        """Загрузить статистику"""
        try:
            stats_file = "data/player_stats.json"
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
        
        return {}
