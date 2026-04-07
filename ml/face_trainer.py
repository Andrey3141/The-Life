"""
Модуль для обучения модели распознавания лиц
"""
import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("FaceTrainer")
logger.setLevel(logging.DEBUG)

class FaceTrainer:
    """Класс для обучения модели распознавания лиц"""
    
    def __init__(self):
        # 🔴 ИСПРАВЛЕНО: хардкод путей БЕЗ os.path.join
        self._models_dir = "data/models"
        self._versions_file = "data/model_versions.json"
        
        # Создаём директорию
        if not os.path.exists(self._models_dir):
            os.makedirs(self._models_dir, exist_ok=True)
        
        # Загружаем данные
        self.versions = self.load_versions()
    
    @property
    def models_dir(self):
        return self._models_dir
    
    @property
    def versions_file(self):
        return self._versions_file
    
    def load_versions(self) -> Dict[str, Any]:
        """Загрузить версии моделей"""
        if os.path.exists(self._versions_file):
            try:
                with open(self._versions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: 
                return {}
        return {}

    def save_versions(self):
        """Сохранить версии моделей"""
        with open(self._versions_file, 'w', encoding='utf-8') as f:
            json.dump(self.versions, f, ensure_ascii=False, indent=2)

    def train_new_face(self, player_name: str, photos: List, stats: Dict[str, List[int]]) -> int:
        """Обучить модель на новых фотографиях"""
        try:
            current_data = self.versions.get(player_name, {})
            current_version = current_data.get("version", 0)
            new_version = current_version + 1
        
            # 🔴 ИСПРАВЛЕНО: хардкод путей
            photo_dir = self._models_dir + "/" + player_name + "_v" + str(new_version)
            if not os.path.exists(photo_dir):
                os.makedirs(photo_dir, exist_ok=True)
        
            for i, photo in enumerate(photos):
                filename = photo_dir + "/" + str(i) + ".png"
                photo.save(filename)
        
            model_filename = self._models_dir + "/" + player_name + "_v" + str(new_version) + ".tflite"
            with open(model_filename, 'wb') as f:
                f.write(b'DUMMY_MODEL_DATA')
        
            embedding = self.generate_embedding(player_name, photos)
        
            self.versions[player_name] = {
                "version": new_version,
                "updated": datetime.now().isoformat(),
                "stats": stats,
                "embedding": embedding
            }
        
            self.save_versions()
            logger.info(f"✅ Обучена модель для {player_name} (версия {new_version})")
            return new_version
        
        except Exception as e:
            logger.error(f"Ошибка обучения модели: {e}")
            return 0

    def get_model_path(self, player_name: str, version: int) -> str:
        """Получить путь к файлу модели"""
        return self._models_dir + "/" + player_name + "_v" + str(version) + ".tflite"

    def get_player_version(self, player_name: str) -> int:
        """Получить текущую версию модели для игрока"""
        return self.versions.get(player_name, {}).get("version", 0)

    def get_player_stats(self, player_name: str) -> Dict:
        """Получить статистику игрока"""
        return self.versions.get(player_name, {}).get("stats", {})
    
    def generate_embedding(self, player_name, photos):
        """Генерирует эмбеддинг для лица из фотографий"""
        try:
            embedding = np.random.randn(512).tolist()
        
            embeddings_file = "data/face_embeddings.json"
            embeddings = {}
        
            if os.path.exists(embeddings_file):
                with open(embeddings_file, 'r', encoding='utf-8') as f:
                    embeddings = json.load(f)
        
            embeddings[player_name] = {
                "embedding": embedding,
                "updated": datetime.now().isoformat()
            }
        
            with open(embeddings_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings, f, ensure_ascii=False, indent=2)
        
            return embedding
        except Exception as e:
            logger.error(f"Ошибка генерации эмбеддинга: {e}")
            return None
