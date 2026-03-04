"""
Менеджер сохранений игры
"""

import os
import json
import pickle
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.models import GameSave, Player, Skill


class SaveManager:
    """Менеджер сохранений"""
    
    def __init__(self, saves_dir: str = "data/saves"):
        self.saves_dir = saves_dir
        self.results_file = os.path.join("data", "game_results.json")
        self.stats_file = os.path.join("data", "player_stats.json")
        
        # Создаем директории если их нет
        os.makedirs(self.saves_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Загружаем историю результатов
        self.game_history = self.load_game_history()
    
    def save_game(self, game_save: GameSave, filename: str) -> bool:
        """Сохранить игру"""
        try:
            filepath = os.path.join(self.saves_dir, f"{filename}.save")
            
            # Сохраняем в бинарном формате
            with open(filepath, 'wb') as f:
                pickle.dump(game_save.to_dict(), f)
            
            # Также сохраняем результат игры в историю
            self._save_to_history(game_save, filename)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении игры: {e}")
            return False
    
    def _save_to_history(self, game_save: GameSave, filename: str):
        """Сохранить результат игры в историю"""
        try:
            # Получаем текущую сцену для определения результата
            if not self.scene_manager:
                from scenes.scene_manager import SceneManager
                self.scene_manager = SceneManager()
            
            current_scene = self.scene_manager.get_scene(game_save.player.current_scene_id)
            
            is_ending = current_scene.is_ending if current_scene else False
            is_game_over = current_scene.game_over if current_scene and is_ending else False
            
            result_entry = {
                "player_name": game_save.player.name,
                "age": game_save.player.age,
                "day": game_save.player.day,
                "money": game_save.player.skills.money,
                "skills": game_save.player.skills.to_dict(),
                "achievements": game_save.player.achievements,
                "final_scene": game_save.player.current_scene_id,
                "is_ending": is_ending,
                "is_game_over": is_game_over,
                "timestamp": datetime.now().isoformat(),
                "save_name": filename,
                "game_version": game_save.game_version
            }
            
            # ВАЖНО: Загружаем существующую историю
            game_history = self.load_game_history()
            game_history.append(result_entry)
            
            # Сохраняем историю в файл
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(game_history, f, ensure_ascii=False, indent=2)
            
            # Обновляем статистику игрока
            self._update_player_stats(game_save.player.name, result_entry)
            
        except Exception as e:
            print(f"Ошибка при сохранении в историю: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_player_stats(self, player_name: str, result_entry: dict):
        """Обновить статистику игрока"""
        try:
            # Загружаем существующую статистику
            player_stats = self.load_player_stats()
            
            if player_name not in player_stats:
                player_stats[player_name] = {
                    "total_games": 0,
                    "wins": 0,
                    "losses": 0,
                    "best_money": 0,
                    "best_day": 0,
                    "endings_found": [],  # ИЗМЕНЕНО: был set, стал list
                    "total_achievements": 0,
                    "games": []
                }
            
            stats = player_stats[player_name]
            stats["total_games"] += 1
            
            if result_entry["is_ending"] and not result_entry["is_game_over"]:
                stats["wins"] += 1
            elif result_entry["is_ending"] and result_entry["is_game_over"]:
                stats["losses"] += 1
            
            # Обновляем лучшие показатели
            if result_entry["money"] > stats["best_money"]:
                stats["best_money"] = result_entry["money"]
            
            if result_entry["day"] > stats["best_day"]:
                stats["best_day"] = result_entry["day"]
            
            # Добавляем найденные финалы (ИСПРАВЛЕНО)
            if result_entry["is_ending"]:
                ending_id = result_entry["final_scene"]
                if ending_id not in stats["endings_found"]:
                    stats["endings_found"].append(ending_id)
            
            # Подсчитываем достижения
            stats["total_achievements"] = max(stats["total_achievements"], 
                                            len(result_entry["achievements"]))
            
            # Добавляем игру в историю
            game_summary = {
                "day": result_entry["day"],
                "money": result_entry["money"],
                "result": "win" if result_entry["is_ending"] and not result_entry["is_game_over"] else "loss",
                "timestamp": result_entry["timestamp"],
                "final_scene": result_entry["final_scene"]
            }
            stats["games"].append(game_summary)
            
            # Ограничиваем историю последними 20 играми
            stats["games"] = stats["games"][-20:]
            
            # Сохраняем статистику
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(player_stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")
    
    def load_game_history(self) -> List[Dict]:
        """Загрузить историю игр"""
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке истории игр: {e}")
        return []
    
    def load_player_stats(self) -> Dict:
        """Загрузить статистику игроков"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке статистики игроков: {e}")
        return {}
    
    def get_all_game_results(self) -> List[Dict]:
        """Получить все результаты игр"""
        return self.game_history
    
    def get_player_stats(self, player_name: str = None) -> Dict:
        """Получить статистику игрока или общую статистику"""
        all_stats = self.load_player_stats()
        
        if player_name:
            return all_stats.get(player_name, {})
        
        # Общая статистика
        total_stats = {
            "total_players": len(all_stats),
            "total_games": 0,
            "total_wins": 0,
            "total_losses": 0,
            "best_money": 0,
            "best_day": 0,
            "most_achievements": 0,
            "most_active_player": "",
            "most_wins_player": ""
        }
        
        max_games = 0
        max_wins = 0
        
        for player_name, stats in all_stats.items():
            total_stats["total_games"] += stats.get("total_games", 0)
            total_stats["total_wins"] += stats.get("wins", 0)
            total_stats["total_losses"] += stats.get("losses", 0)
            total_stats["best_money"] = max(total_stats["best_money"], stats.get("best_money", 0))
            total_stats["best_day"] = max(total_stats["best_day"], stats.get("best_day", 0))
            total_stats["most_achievements"] = max(total_stats["most_achievements"], 
                                                  stats.get("total_achievements", 0))
            
            if stats.get("total_games", 0) > max_games:
                max_games = stats["total_games"]
                total_stats["most_active_player"] = player_name
            
            if stats.get("wins", 0) > max_wins:
                max_wins = stats["wins"]
                total_stats["most_wins_player"] = player_name
        
        return total_stats
    
    def list_saves(self) -> List[Dict]:
        """Получить список сохранений"""
        saves = []
        
        try:
            for filename in os.listdir(self.saves_dir):
                if filename.endswith('.save'):
                    filepath = os.path.join(self.saves_dir, filename)
                    try:
                        with open(filepath, 'rb') as f:
                            save_data = pickle.load(f)
                            save_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                            
                            saves.append({
                                'filename': filename,
                                'player_name': save_data['player']['name'],
                                'day': save_data['player']['day'],
                                'money': save_data['player']['skills']['money'],
                                'timestamp': save_time.strftime('%Y-%m-%d %H:%M')
                            })
                    except Exception as e:
                        print(f"Ошибка при загрузке сохранения {filename}: {e}")
                        
            # Сортируем по времени (сначала новые)
            saves.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Ошибка при получении списка сохранений: {e}")
        
        return saves
    
    def load_game(self, filename: str) -> Optional[GameSave]:
        """Загрузить игру"""
        try:
            filepath = os.path.join(self.saves_dir, filename)
            
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            return GameSave.from_dict(save_data)
        except Exception as e:
            print(f"Ошибка при загрузке игры: {e}")
            return None
