"""
Синхронизация моделей распознавания лиц между сервером и клиентами
"""

import json
import os
import shutil
from datetime import datetime


class ModelSync:
    """Класс для синхронизации моделей"""
    
    def __init__(self):
        self.models_dir = "data/models"
        self.versions_file = "data/model_versions.json"
        os.makedirs(self.models_dir, exist_ok=True)
        
    def get_versions(self):
        """Получить словарь версий моделей для всех игроков"""
        if os.path.exists(self.versions_file):
            try:
                with open(self.versions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_version(self, player_name, version, stats):
        """Сохранить версию модели для игрока"""
        versions = self.get_versions()
        versions[player_name] = {
            "version": version,
            "updated": datetime.now().isoformat(),
            "stats": stats  # {"Трудолюбие": [5,3], ...}
        }
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
    
    def get_model_path(self, player_name, version):
        """Получить путь к файлу модели"""
        return f"{self.models_dir}/{player_name}_v{version}.tflite"
    
    def save_model_file(self, player_name, version, model_data):
        """Сохранить файл модели"""
        path = self.get_model_path(player_name, version)
        with open(path, 'wb') as f:
            f.write(model_data)
        return path
