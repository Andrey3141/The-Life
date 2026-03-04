# core/models.py
"""
Модели данных игры
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class Subject(Enum):
    """Предметы/навыки"""
    ECONOMICS = "Экономика"
    MANAGEMENT = "Менеджмент"
    FINANCE = "Финансы"
    MARKETING = "Маркетинг"
    HAPPINESS = "Счастье"
    HEALTH = "Здоровье"
    REPUTATION = "Репутация"


class GameState(Enum):
    """Состояния игры"""
    MENU = "menu"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Skill:
    """Навыки персонажа"""
    economics: int = 50
    management: int = 50
    finance: int = 50
    marketing: int = 50
    happiness: int = 70
    health: int = 80
    reputation: int = 50
    money: int = 10000  # Начальные деньги
    
    def to_dict(self) -> Dict[str, int]:
        """Преобразовать в словарь"""
        return {
            'economics': self.economics,
            'management': self.management,
            'finance': self.finance,
            'marketing': self.marketing,
            'happiness': self.happiness,
            'health': self.health,
            'reputation': self.reputation,
            'money': self.money
        }
    
    def get_skill(self, subject: Subject) -> int:
        """Получить значение навыка по предмету"""
        skill_map = {
            Subject.ECONOMICS: self.economics,
            Subject.MANAGEMENT: self.management,
            Subject.FINANCE: self.finance,
            Subject.MARKETING: self.marketing,
            Subject.HAPPINESS: self.happiness,
            Subject.HEALTH: self.health,
            Subject.REPUTATION: self.reputation
        }
        return skill_map.get(subject, 0)


@dataclass
class Choice:
    """Выбор в сцене"""
    text: str
    next_scene_id: str
    effects: Dict[str, int]
    money_cost: int = 0
    required_skill: Optional[Tuple[Subject, int]] = None
    
    def is_available(self, skills: Skill) -> bool:
        """Проверить доступность выбора"""
        if self.required_skill:
            subject, required_level = self.required_skill
            current_level = skills.get_skill(subject)
            if current_level < required_level:
                return False
        
        # Проверка денег
        if self.money_cost > skills.money:
            return False
        
        return True


@dataclass
class Scene:
    """Игровая сцена"""
    scene_id: str
    title: str
    description: str
    choices: List[Choice]
    is_ending: bool = False
    game_over: bool = False


@dataclass
class Player:
    """Игрок"""
    name: str
    age: int
    profession: str
    skills: Skill
    day: int = 1
    achievements: List[str] = field(default_factory=list)
    current_scene_id: str = "start"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'name': self.name,
            'age': self.age,
            'profession': self.profession,
            'skills': self.skills.to_dict(),
            'day': self.day,
            'achievements': self.achievements,
            'current_scene_id': self.current_scene_id
        }


@dataclass
class GameSave:
    """Сохранение игры"""
    player: Player
    game_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'player': self.player.to_dict(),
            'game_version': self.game_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSave':
        """Создать из словаря"""
        skills_data = data['player']['skills']
        skills = Skill(
            economics=skills_data.get('economics', 50),
            management=skills_data.get('management', 50),
            finance=skills_data.get('finance', 50),
            marketing=skills_data.get('marketing', 50),
            happiness=skills_data.get('happiness', 70),
            health=skills_data.get('health', 80),
            reputation=skills_data.get('reputation', 50),
            money=skills_data.get('money', 10000)
        )
        
        player = Player(
            name=data['player']['name'],
            age=data['player']['age'],
            profession=data['player'].get('profession', 'Начинающий специалист'),
            skills=skills,
            day=data['player']['day'],
            achievements=data['player'].get('achievements', []),
            current_scene_id=data['player']['current_scene_id']
        )
        
        return cls(
            player=player,
            game_version=data['game_version']
        )
