"""
Серверная часть для мультиплеерного режима с поддержкой UI
"""

import asyncio
import json
import logging
import threading
import socket
from datetime import datetime
from typing import Dict, Set, Optional
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.asyncio.server import ServerConnection
from PySide6.QtCore import QTimer, QObject, Signal


class GameState(Enum):
    WAITING = "waiting"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class PlayerConnection:
    def __init__(self, player_id: str, websocket, name: str = None):
        self.player_id = player_id
        self.websocket = websocket
        self.name = name or f"Player_{player_id[:4]}"
        self.connected_at = datetime.now()
        self.score = 0
        self.current_scene = None
        self.answers = []


class GameServer(QObject):
    """Сервер с поддержкой UI обратных вызовов"""
    
    log_signal = Signal(str)
    player_joined_signal = Signal(str, str, object)
    player_left_signal = Signal(str)
    vote_received_signal = Signal(str, int)
    
    def __init__(self, host="0.0.0.0", port=8888, max_players=10, ui_callback=None):
        super().__init__()
        self.host = host
        self.port = port
        self.max_players = max_players
        self.ui_callback = ui_callback
        self.game_dialog = None
        self.instance_id = id(self)
        
        self.players: Dict[str, PlayerConnection] = {}
        self.game_state = GameState.WAITING
        self.current_scene_index = 0
        self.scenes = []
        self.results = {}
        self.is_running = False
        self.loop = None
        self.server = None
        self.server_task = None
        self._cleanup_task = None
        
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("GameServer")
    
    def log(self, message):
        self.logger.info(message)
        try:
            if self.ui_callback and hasattr(self.ui_callback, 'log_signal'):
                if self.ui_callback.log_signal is not None:
                    self.ui_callback.log_signal.emit(message)
        except RuntimeError:
            pass
    
    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    async def register_player(self, websocket: ServerConnection, name: str = None) -> str:
        if len(self.players) >= self.max_players:
            try:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Сервер заполнен"
                }))
                await websocket.close()
            except:
                pass
            return None
        
        player_id = f"player_{len(self.players) + 1}_{int(datetime.now().timestamp())}"
        
        if name is None:
            name = f"Игрок {len(self.players) + 1}"
        
        player = PlayerConnection(player_id, websocket, name)
        self.players[player_id] = player
        
        self.log(f"✅ Игрок подключился: {name} (ID: {player_id})")
        self.log(f"👥 Всего игроков: {len(self.players)}")
        
        try:
            if self.ui_callback and hasattr(self.ui_callback, 'player_joined_signal'):
                if self.ui_callback.player_joined_signal is not None:
                    self.ui_callback.player_joined_signal.emit(player_id, name, player.connected_at)
        except RuntimeError:
            pass
        
        try:
            await self.send_to_player(player_id, {
                "type": "welcome",
                "player_id": player_id,
                "message": f"Добро пожаловать, {name}!",
                "players_connected": len(self.players)
            })
            
            await self.broadcast({
                "type": "player_joined",
                "player_id": player_id,
                "player_name": name,
                "players_connected": len(self.players)
            }, exclude={player_id})
        except:
            pass
        
        return player_id
    
    async def unregister_player(self, player_id: str):
        if player_id in self.players:
            player = self.players[player_id]
            self.log(f"❌ Игрок отключился: {player.name}")
            
            try:
                if self.ui_callback and hasattr(self.ui_callback, 'player_left_signal'):
                    if self.ui_callback.player_left_signal is not None:
                        self.ui_callback.player_left_signal.emit(player_id)
            except RuntimeError:
                pass
            
            del self.players[player_id]
            
            try:
                await self.broadcast({
                    "type": "player_left",
                    "player_id": player_id,
                    "players_connected": len(self.players)
                })
            except:
                pass
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        if exclude is None:
            exclude = set()
        
        disconnected = []
        
        for player_id, player in self.players.items():
            if player_id in exclude:
                continue
            
            try:
                await player.websocket.send(json.dumps(message, ensure_ascii=False))
            except (websockets.exceptions.ConnectionClosed, ConnectionError):
                disconnected.append(player_id)
            except Exception as e:
                self.log(f"Ошибка отправки игроку {player_id}: {e}")
                disconnected.append(player_id)
        
        for player_id in disconnected:
            await self.unregister_player(player_id)
    
    async def send_to_player(self, player_id: str, message: dict):
        """Отправить сообщение и дождаться подтверждения"""
        if player_id in self.players:
            try:
                await self.players[player_id].websocket.send(
                    json.dumps(message, ensure_ascii=False)
                )
                self.log(f"📤 Отправлено {message.get('type', 'unknown')} игроку {player_id}")
            except (websockets.exceptions.ConnectionClosed, ConnectionError):
                await self.unregister_player(player_id)
            except Exception as e:
                self.log(f"Ошибка отправки игроку {player_id}: {e}")
                await self.unregister_player(player_id)
    
    async def handle_message(self, player_id: str, data: dict):
        message_type = data.get("type", "")
        
        if message_type == "answer":
            answer = data.get("answer", "")
            scene_id = data.get("scene_id", "")
            
            player = self.players.get(player_id)
            if player:
                player.answers.append({
                    "scene_id": scene_id,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat()
                })
                
                self.log(f"📝 Игрок {player.name} ответил на {scene_id}: {answer}")
                
                await self.send_to_player(player_id, {
                    "type": "answer_received",
                    "message": "Ответ получен"
                })
        
        elif message_type == "ready":
            player = self.players.get(player_id)
            if player:
                self.log(f"🎮 Игрок {player.name} готов")
        
        elif message_type == "get_players":
            players_list = [
                {"id": pid, "name": p.name, "score": p.score}
                for pid, p in self.players.items()
            ]
            await self.send_to_player(player_id, {
                "type": "players_list",
                "players": players_list
            })
        
        elif message_type == "vote":
            vote = data.get("vote", 0)
            question_index = data.get("question_index", 0)
            
            player = self.players.get(player_id)
            if player:
                self.log(f"🗳️ Игрок {player.name} поставил оценку {vote} на вопрос {question_index}")
                
                if self.game_dialog:
                    self.vote_received_signal.emit(player_id, vote)
                
                await self.send_to_player(player_id, {
                    "type": "vote_received",
                    "message": "Оценка получена"
                })
    
    async def player_handler(self, websocket: ServerConnection):
        path = websocket.request.path if hasattr(websocket, 'request') else "/"
        name = None
        
        if "?" in path:
            try:
                query = path.split("?")[1]
                params = dict(param.split("=") for param in query.split("&") if "=" in param)
                name = params.get("name")
            except:
                pass
        
        player_id = await self.register_player(websocket, name)
        if not player_id:
            return
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(player_id, data)
                except json.JSONDecodeError:
                    self.log(f"Получен некорректный JSON от {player_id}")
                except Exception as e:
                    self.log(f"Ошибка обработки сообщения: {e}")
        
        except (websockets.exceptions.ConnectionClosed, ConnectionError):
            self.log(f"Соединение с {player_id} закрыто")
        except asyncio.CancelledError:
            self.log(f"Задача обработки игрока {player_id} отменена")
        except Exception as e:
            self.log(f"Неожиданная ошибка в обработчике игрока {player_id}: {e}")
        finally:
            await self.unregister_player(player_id)
    
    async def start_server_async(self):
        self.server = await websockets.serve(
            self.player_handler,
            self.host,
            self.port
        )
        
        local_ip = self.get_local_ip()
        self.log("=" * 50)
        self.log("🚀 СЕРВЕР ЗАПУЩЕН!")
        self.log(f"📡 IP адрес: {local_ip}")
        self.log(f"🔌 Порт: {self.port}")
        self.log(f"👥 Макс. игроков: {self.max_players}")
        self.log("=" * 50)
        self.log(f"🔗 Адрес для подключения: ws://{local_ip}:{self.port}")
        self.log("=" * 50)
        
        try:
            await self.server.wait_closed()
        except asyncio.CancelledError:
            self.log("Сервер остановлен")
        except Exception as e:
            self.log(f"Ошибка сервера: {e}")
        finally:
            self.server = None
    
    async def cleanup(self):
        tasks = []
        for player_id in list(self.players.keys()):
            tasks.append(self.unregister_player(player_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
    
    def start(self):
        self.is_running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.server_task = self.loop.create_task(self.start_server_async())
            self.loop.run_until_complete(self.server_task)
        except KeyboardInterrupt:
            self.log("Сервер остановлен по запросу")
        except asyncio.CancelledError:
            self.log("Сервер остановлен")
        except Exception as e:
            self.log(f"Ошибка сервера: {e}")
        finally:
            if self.loop and self.loop.is_running():
                self._cleanup_task = self.loop.create_task(self.cleanup())
                self.loop.run_until_complete(self._cleanup_task)
            
            if self.server_task and not self.server_task.done():
                self.server_task.cancel()
            
            if self.loop and self.loop.is_running():
                self.loop.stop()
            
            if self.loop:
                self.loop.close()
            
            self.is_running = False
            self.log("Сервер остановлен")
    
    def stop(self):
        self.is_running = False
        if self.server:
            self.server.close()
        
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()
        
        self.log("Сервер остановлен")
    
    async def send_file_to_player(self, player_id, file_path, metadata):
        """Отправить файл модели клиенту"""
        if player_id in self.players:
            try:
                # Сначала отправляем метаданные
                await self.send_to_player(player_id, metadata)
            
                # Отправляем файл частями
                with open(file_path, 'rb') as f:
                    chunk_size = 4096
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        # Здесь нужно реализовать протокол передачи файлов
                        # Можно использовать отдельный тип сообщения "file_chunk"
                        await self.send_to_player(player_id, {
                            "type": "file_chunk",
                            "data": chunk.hex()
                        })
            except Exception as e:
                self.log(f"Ошибка отправки файла: {e}")
