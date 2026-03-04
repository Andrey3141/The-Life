"""
Вспомогательные функции
"""

import os
import json
import random
from datetime import datetime
from typing import Any, Dict, List, Optional


def clear_screen():
    """Очистить экран"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_timestamp() -> str:
    """Получить текущую временную метку"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_money(amount: int) -> str:
    """Форматировать сумму денег"""
    if amount >= 1000000:
        return f"{amount / 1000000:.1f}M ₽"
    elif amount >= 1000:
        return f"{amount / 1000:.1f}K ₽"
    else:
        return f"{amount} ₽"


def calculate_success_probability(skill_value: int, difficulty: int = 50) -> float:
    """Рассчитать вероятность успеха"""
    diff = skill_value - difficulty
    probability = 50 + diff  # Базовый 50% + разница
    return max(10, min(90, probability)) / 100


def random_event(chance: float) -> bool:
    """Случайное событие с заданной вероятностью"""
    return random.random() < chance


def get_random_lesson(subject_type: Optional[str] = None) -> str:
    """Получить случайный урок"""
    lessons = {
        "economics": [
            "📊 Экономика: Спрос и предложение определяют цены на рынке.",
            "📊 Экономика: Инфляция снижает покупательную способность денег.",
            "📊 Экономика: Диверсификация снижает инвестиционные риски.",
            "📊 Экономика: Кривая спроса обычно имеет отрицательный наклон.",
            "📊 Экономика: ВВП измеряет общую экономическую активность страны."
        ],
        "management": [
            "👨‍💼 Менеджмент: Правильная постановка целей - ключ к успеху проекта.",
            "👨‍💼 Менеджмент: Эффективная коммуникация в команде повышает продуктивность.",
            "👨‍💼 Менеджмент: Делегирование задач освобождает время для стратегических решений.",
            "👨‍💼 Менеджмент: Обратная связь помогает сотрудникам развиваться.",
            "👨‍💼 Менеджмент: Управление временем критически важно для успеха проекта."
        ],
        "finance": [
            "💳 Финансы: Составление бюджета помогает контролировать расходы.",
            "💳 Финансы: Инвестирование требует понимания рисков и доходности.",
            "💳 Финансы: Сложные проценты могут значительно увеличить капитал со временем.",
            "💳 Финансы: Финансовая подушка безопасности должна составлять 3-6 месячных доходов.",
            "💳 Финансы: Диверсификация портфеля снижает общий риск."
        ],
        "life": [
            "😊 Жизнь: Баланс между работой и отдыхом повышает общую эффективность.",
            "😊 Жизнь: Здоровый образ жизни увеличивает продуктивность и долголетие.",
            "😊 Жизнь: Постоянное обучение - ключ к профессиональному росту.",
            "😊 Жизнь: Сетевые связи часто открывают новые возможности.",
            "😊 Жизнь: Умение говорить 'нет' сохраняет время и энергию."
        ]
    }
    
    if subject_type and subject_type in lessons:
        return random.choice(lessons[subject_type])
    else:
        all_lessons = []
        for category in lessons.values():
            all_lessons.extend(category)
        return random.choice(all_lessons)


def calculate_game_score(player_data: Dict[str, Any]) -> int:
    """Рассчитать итоговый счет игры"""
    score = 0
    
    # Баллы за деньги
    money = player_data.get('skills', {}).get('money', 0)
    score += money // 100  # 1 балл за каждые 100 рублей
    
    # Баллы за навыки
    skills = ['economics', 'management', 'finance', 'marketing', 'happiness', 'health', 'reputation']
    for skill in skills:
        value = player_data.get('skills', {}).get(skill, 0)
        score += value  # 1 балл за каждый пункт навыка
    
    # Бонус за достижения
    achievements = player_data.get('achievements', [])
    score += len(achievements) * 100
    
    # Бонус за дни выживания
    days = player_data.get('day', 1)
    score += days * 10
    
    return score


def save_to_json(data: Dict[str, Any], filename: str) -> bool:
    """Сохранить данные в JSON файл"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_from_json(filename: str) -> Optional[Dict[str, Any]]:
    """Загрузить данные из JSON файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def print_header(text: str, width: int = 60):
    """Напечатать заголовок"""
    print("\n" + "=" * width)
    print(f"{text:^{width}}")
    print("=" * width)
