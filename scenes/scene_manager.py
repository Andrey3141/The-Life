# scenes/scene_manager.py
"""
Менеджер загрузки сцен - проверяет все переходы
"""

from typing import Dict, Optional, List
from core.models import Scene
from .scenes_data import SCENES_DATA


class SceneManager:
    """Менеджер загрузки и управления сценами"""
    
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.load_all_scenes()
        self.validate_all_transitions()
    
    def load_all_scenes(self):
        """Загрузить все сцены из данных"""
        for scene in SCENES_DATA:
            self.scenes[scene.scene_id] = scene
        
        total_scenes = len(self.scenes)
        endings = [s for s in self.scenes.values() if s.is_ending]
        success_endings = [s for s in endings if not s.game_over]
        failure_endings = [s for s in endings if s.game_over]
        
        print(f"✅ Всего загружено сцен: {total_scenes}")
        print(f"✅ Концовок: {len(endings)}")
        print(f"✅ Успешных концовок: {len(success_endings)}")
        print(f"✅ Неудачных концовок: {len(failure_endings)}")
    
    def validate_all_transitions(self):
        """Проверить все переходы между сценами"""
        existing_ids = set(self.scenes.keys())
        broken_transitions = []
        
        for scene_id, scene in self.scenes.items():
            if not scene.is_ending:  # Только для неконечных сцен
                for i, choice in enumerate(scene.choices):
                    if choice.next_scene_id not in existing_ids:
                        broken_transitions.append((scene_id, i, choice.next_scene_id))
        
        if broken_transitions:
            print(f"\n⚠️  Обнаружены некорректные переходы: {len(broken_transitions)}")
            for scene_id, choice_idx, broken_id in broken_transitions[:10]:
                scene = self.scenes[scene_id]
                choice_text = scene.choices[choice_idx].text[:50] + "..." if len(scene.choices[choice_idx].text) > 50 else scene.choices[choice_idx].text
                print(f"   Сцена '{scene_id}': выбор '{choice_text}' -> '{broken_id}' (не найдено)")
            
            # Автоматически исправляем
            self.fix_broken_transitions(broken_transitions, existing_ids)
        else:
            print(f"✅ Все переходы корректны!")
    
    def fix_broken_transitions(self, broken_transitions: List[tuple], existing_ids: set):
        """Исправить некорректные переходы"""
        print("\n🔧 Исправляю переходы...")
        
        # Получаем список всех концовок
        success_endings = [scene_id for scene_id, scene in self.scenes.items() 
                          if scene.is_ending and not scene.game_over]
        failure_endings = [scene_id for scene_id, scene in self.scenes.items() 
                          if scene.is_ending and scene.game_over]
        
        if not success_endings and not failure_endings:
            print("❌ Нет доступных концовок для исправления!")
            return
        
        for scene_id, choice_idx, broken_id in broken_transitions:
            scene = self.scenes.get(scene_id)
            if not scene or choice_idx >= len(scene.choices):
                continue
            
            # Определяем тип концовки по названию или случайно
            broken_lower = broken_id.lower()
            
            if any(word in broken_lower for word in ['fail', 'loss', 'bankrupt', 'corrupt', 'scandal', 'burnout', 'stagnation']):
                # Неудачная концовка
                if failure_endings:
                    replacement = failure_endings[0]
                else:
                    replacement = success_endings[0] if success_endings else list(existing_ids)[0]
            else:
                # Успешная концовка
                if success_endings:
                    replacement = success_endings[0]
                else:
                    replacement = failure_endings[0] if failure_endings else list(existing_ids)[0]
            
            scene.choices[choice_idx].next_scene_id = replacement
            print(f"   {scene_id}: выбор {choice_idx+1} -> {replacement}")
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Получить сцену по ID"""
        scene = self.scenes.get(scene_id)
        if not scene:
            print(f"⚠️  Сцена не найдена: {scene_id}")
            # Возвращаем случайную концовку вместо ошибки
            endings = [s for s in self.scenes.values() if s.is_ending]
            if endings:
                import random
                return random.choice(endings)
            else:
                # Возвращаем первую сцену
                return list(self.scenes.values())[0] if self.scenes else None
        return scene
    
    def get_all_scenes(self):
        """Получить все сцены"""
        return list(self.scenes.values())
    
    def scene_exists(self, scene_id: str) -> bool:
        """Проверить существование сцены"""
        return scene_id in self.scenes
