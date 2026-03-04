"""
Сервер для мультиплеерного режима
Запускается на компьютере, к нему подключаются телефоны
"""

import asyncio
import json
import logging
import socket
import threading
from datetime import datetime
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
import qrcode
from PIL import Image
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GameServer")


class GameState(Enum):
    WAITING = "waiting"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass
class Player:
    """Класс игрока на сервере"""
    id: str
    name: str
    websocket: Any
    connected_at: datetime
    score: int = 0
    current_scene: str = "start"
    answers: list = None
    
    def __post_init__(self):
        if self.answers is None:
            self.answers = []


class GameServer:
    """Основной класс сервера"""
    
    def __init__(self, host="0.0.0.0", port=8888, max_players=10):
        self.host = host
        self.port = port
        self.max_players = max_players
        self.players: Dict[str, Player] = {}
        self.game_state = GameState.WAITING
        self.current_scene_index = 0
        self.scenes = []  # Будут загружены из scenes_data.py
        self.results = {}
        self.loop = None
        self.server = None
        
    def get_local_ip(self) -> str:
        """Получить локальный IP адрес компьютера"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def generate_qr_code(self, data: str, filename: str = "qr_code.png") -> str:
        """Сгенерировать QR код для подключения"""
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return os.path.abspath(filename)
    
    async def register_player(self, websocket: WebSocketServerProtocol, name: str = None) -> Player:
        """Зарегистрировать нового игрока"""
        player_id = f"player_{len(self.players) + 1}_{datetime.now().timestamp()}"
        
        if name is None:
            name = f"Игрок {len(self.players) + 1}"
        
        player = Player(
            id=player_id,
            name=name,
            websocket=websocket,
            connected_at=datetime.now()
        )
        
        self.players[player_id] = player
        logger.info(f"Игрок подключился: {name} (ID: {player_id})")
        logger.info(f"Всего игроков: {len(self.players)}")
        
        # Отправляем приветственное сообщение
        await self.send_to_player(player_id, {
            "type": "welcome",
            "player_id": player_id,
            "message": f"Добро пожаловать, {name}!",
            "players_connected": len(self.players)
        })
        
        # Оповещаем всех о новом игроке
        await self.broadcast({
            "type": "player_joined",
            "player_id": player_id,
            "player_name": name,
            "players_connected": len(self.players)
        }, exclude={player_id})
        
        return player
    
    async def unregister_player(self, player_id: str):
        """Отключить игрока"""
        if player_id in self.players:
            player = self.players[player_id]
            logger.info(f"Игрок отключился: {player.name}")
            del self.players[player_id]
            
            # Оповещаем всех об отключении
            await self.broadcast({
                "type": "player_left",
                "player_id": player_id,
                "players_connected": len(self.players)
            })
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        """Отправить сообщение всем игрокам"""
        if exclude is None:
            exclude = set()
        
        disconnected = []
        
        for player_id, player in self.players.items():
            if player_id in exclude:
                continue
            
            try:
                await player.websocket.send(json.dumps(message, ensure_ascii=False))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(player_id)
            except Exception as e:
                logger.error(f"Ошибка отправки игроку {player_id}: {e}")
                disconnected.append(player_id)
        
        # Удаляем отключившихся игроков
        for player_id in disconnected:
            await self.unregister_player(player_id)
    
    async def send_to_player(self, player_id: str, message: dict):
        """Отправить сообщение конкретному игроку"""
        if player_id in self.players:
            try:
                await self.players[player_id].websocket.send(
                    json.dumps(message, ensure_ascii=False)
                )
            except Exception as e:
                logger.error(f"Ошибка отправки игроку {player_id}: {e}")
                await self.unregister_player(player_id)
    
    async def handle_message(self, player_id: str, data: dict):
        """Обработать сообщение от игрока"""
        message_type = data.get("type", "")
        
        if message_type == "answer":
            # Игрок отправил ответ на задание
            answer = data.get("answer", "")
            scene_id = data.get("scene_id", "")
            
            player = self.players.get(player_id)
            if player:
                player.answers.append({
                    "scene_id": scene_id,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Игрок {player.name} ответил на {scene_id}: {answer}")
                
                # Отправляем подтверждение
                await self.send_to_player(player_id, {
                    "type": "answer_received",
                    "message": "Ответ получен"
                })
        
        elif message_type == "ready":
            # Игрок готов начать
            await self.send_to_player(player_id, {
                "type": "waiting",
                "message": "Ожидание начала игры..."
            })
        
        elif message_type == "get_players":
            # Запрос списка игроков
            players_list = [
                {"id": pid, "name": p.name, "score": p.score}
                for pid, p in self.players.items()
            ]
            await self.send_to_player(player_id, {
                "type": "players_list",
                "players": players_list
            })
    
    async def send_scene_to_all(self, scene_data: dict):
        """Отправить сцену всем игрокам"""
        await self.broadcast({
            "type": "new_scene",
            "scene": scene_data
        })
    
    async def player_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Обработчик подключения игрока"""
        # Регистрируем игрока
        player = await self.register_player(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(player.id, data)
                except json.JSONDecodeError:
                    logger.error(f"Получен некорректный JSON от {player.id}")
                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Соединение с {player.id} закрыто")
        finally:
            await self.unregister_player(player.id)
    
    async def start_server(self):
        """Запустить WebSocket сервер"""
        self.server = await websockets.serve(
            self.player_handler,
            self.host,
            self.port
        )
        
        local_ip = self.get_local_ip()
        logger.info("=" * 50)
        logger.info(f"🚀 СЕРВЕР ЗАПУЩЕН!")
        logger.info(f"📡 IP адрес: {local_ip}")
        logger.info(f"🔌 Порт: {self.port}")
        logger.info(f"👥 Макс. игроков: {self.max_players}")
        logger.info("=" * 50)
        logger.info(f"🔗 Адрес для подключения: ws://{local_ip}:{self.port}")
        
        # Генерируем QR код
        qr_file = self.generate_qr_code(f"ws://{local_ip}:{self.port}")
        logger.info(f"📱 QR код сохранен: {qr_file}")
        logger.info("=" * 50)
        
        await self.server.wait_closed()
    
    def start(self):
        """Запустить сервер (синхронная обертка)"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.start_server())
        except KeyboardInterrupt:
            logger.info("Сервер остановлен")
        finally:
            self.loop.close()
    
    def stop(self):
        """Остановить сервер"""
        if self.server:
            self.server.close()
        
        if self.loop:
            self.loop.stop()


def run_server(host="0.0.0.0", port=8888, max_players=10):
    """Функция для запуска сервера в отдельном потоке"""
    server = GameServer(host, port, max_players)
    server.start()


if __name__ == "__main__":
    # Запуск сервера напрямую
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск игрового сервера")
    parser.add_argument("--host", default="0.0.0.0", help="Хост для прослушивания")
    parser.add_argument("--port", type=int, default=8888, help="Порт")
    parser.add_argument("--max-players", type=int, default=10, help="Максимум игроков")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🎮 ЗАПУСК СЕРВЕРА ЭКОНОМИЧЕСКОЙ СИМУЛЯЦИИ")
    print("=" * 50)
    
    server = GameServer(args.host, args.port, args.max_players)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
