from abc import ABC, abstractmethod
from typing import Any


class BaseClient(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def start_client() -> Any:
        pass

    @abstractmethod
    def block_users(self) -> None:
        pass
