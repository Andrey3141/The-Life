"""
Валидаторы для игры
"""

import re
from typing import Any


def validate_choice(choice_index: int, max_choices: int) -> bool:
    """Валидировать выбор игрока"""
    return 0 <= choice_index < max_choices


def validate_name(name: str) -> tuple[bool, str]:
    """Валидировать имя персонажа"""
    if not name or not name.strip():
        return False, "Имя не может быть пустым"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Имя должно содержать минимум 2 символа"
    
    if len(name) > 20:
        return False, "Имя не должно превышать 20 символов"
    
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', name):
        return False, "Имя может содержать только буквы, пробелы и дефисы"
    
    return True, ""


def validate_age(age: Any) -> tuple[bool, str]:
    """Валидировать возраст"""
    try:
        age_int = int(age)
        if age_int < 18:
            return False, "Возраст должен быть не менее 18 лет"
        if age_int > 100:
            return False, "Возраст должен быть не более 100 лет"
        return True, ""
    except (ValueError, TypeError):
        return False, "Возраст должен быть числом"


def validate_money(money: Any) -> tuple[bool, str]:
    """Валидировать сумму денег"""
    try:
        money_int = int(money)
        if money_int < 0:
            return False, "Сумма не может быть отрицательной"
        if money_int > 1000000000:  # 1 миллиард
            return False, "Сумма слишком большая"
        return True, ""
    except (ValueError, TypeError):
        return False, "Сумма должна быть числом"


def validate_save_name(name: str) -> tuple[bool, str]:
    """Валидировать название сохранения"""
    if not name or not name.strip():
        return False, "Название сохранения не может быть пустым"
    
    name = name.strip()
    
    if len(name) < 1:
        return False, "Название должно содержать минимум 1 символ"
    
    if len(name) > 50:
        return False, "Название не должно превышать 50 символов"
    
    # Запрещенные символы в именах файлов
    forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in forbidden_chars:
        if char in name:
            return False, f"Название содержит запрещенный символ: {char}"
    
    return True, ""


def validate_skill_value(value: Any) -> tuple[bool, str]:
    """Валидировать значение навыка"""
    try:
        value_int = int(value)
        if value_int < 0:
            return False, "Значение навыка не может быть отрицательным"
        if value_int > 100:
            return False, "Значение навыка не может превышать 100"
        return True, ""
    except (ValueError, TypeError):
        return False, "Значение навыка должно быть числом"
