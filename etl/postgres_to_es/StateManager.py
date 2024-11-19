import json
import abc
from typing import Any, Dict
import os
import datetime


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
        with open(self.file_path, "w") as file:
            json.dump(state, file)

    def load_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return json.load(file)
        return (
            datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"),
        )


class StateManager:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self.state = self.storage.load_state()
        self.listeners = []

    def add_listener(self, listener: Any) -> None:
        self.listeners.append(listener)

    def notify(self, table) -> None:
        for listener in self.listeners:
            listener(self.state, table)

    def change_state(self, time, table_data, table) -> None:
        self.state = time
        self.storage.save_state(self.state)
        ids = list([i["id"] for i in table_data])
        self.notify(ids, table)

    def get_state(self):
        return self.state

    # def set_state(self, key: str, value: Any) -> None:
    #     """Установить состояние для определённого ключа."""
    #     self._state[key] = value
    #     self.storage.save_state(self._state)

    # def get_state(self, key: str) -> Any:
    #     """Получить состояние по определённому ключу."""
    #     return self._state.get(key)


# TODO: переделать
# class StateManager:
#     def __init__(self):
#         self.state = {'Films': {},
#                       'Janres': {},
#                       'Persons': {}}
#         self.listeners = []

#     @state.setter
#     def change_state(self, state):
#         if state != self.state:
#             self.state = state
#             self.notify()

#     def add_listener(self, listener):
#         ...

#     def notify(self):
#         for listener in self.listeners:
#             listener(self.state)

# manager = StateManager()
# def


# class StateManager:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.state = self.load_state()

#     def load_state(self):
#         try:
#             with open(self.file_path, "r") as file:
#                 return json.load(file)
#         except FileNotFoundError:
#             return {}

#     def save_state(self, key, value):
#         self.state[key] = value
#         with open(self.file_path, "w") as file:
#             json.dump(self.state, file)

#     def get_state(self, key, default=None):
#         return self.state.get(key, default)
