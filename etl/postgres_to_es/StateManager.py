import json
import abc
import os
from typing import Any, Dict, List, Optional
from logging_config import logger


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния."""

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def load_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.
    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        try:
            with open(self.file_path, "w") as file:
                json.dump(state, file)
        except (OSError, IOError) as e:
            logger.error(f"Ошибка при сохранении состояния: {e}")

    def load_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        if os.path.exists(self.file_path):
            logger.info(f"Загрузка состояния из {self.file_path}")
            with open(self.file_path, "r") as file:
                try:
                    data = json.load(file)
                    return data if isinstance(data, dict) else {}
                except json.JSONDecodeError:
                    return {}
        return {}


class StateManager:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self.state = self.storage.load_state()
        self.listeners = []

    def add_listener(self, listener: Any) -> None:
        """Добавить слушателя изменений состояния"""
        self.listeners.append(listener)

    def notify(self, ids, table) -> None:
        """Уведомить слушателей об изменениях"""
        if not ids:
            logger.info(f"Нет обновлений в таблице {table}, пропускаем загрузку в Elasticsearch")
            return
        for listener in self.listeners:
            listener(ids, table)

    def change_state(
        self, time: Any, table_data: List[Dict[str, Any]], table: str
    ) -> None:
        """Обновить состояние и уведомить слушателей об изменениях"""
        if self.state is None:
            self.state = {}

        self.state[table] = time.isoformat()
        self.storage.save_state(self.state)
        ids = [id["id"] for id in table_data]
        logger.info(f"Количество обновленных записей: {len(ids)}")
        self.notify(ids, table)

    def get_state(self, table: str) -> Optional[str]:
        """Получить последнее сохраненное состояние для таблицы"""
        state = self.storage.load_state()
        return state.get(table)
