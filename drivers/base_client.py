from abc import ABC, abstractmethod
from typing import Any

from utils.cache_service import CacheService


class BaseClient(ABC):
    def __init__(self, cache_service: CacheService | None = None):
        self.cache_service = cache_service

    @abstractmethod
    def start_client(self) -> Any:
        pass

    @abstractmethod
    def block_users(self) -> None:
        pass

    @staticmethod
    def get_usernames_from_file(file_path: str) -> list[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                print(f"Reading usernames from file: {file_path}")
                return file.read().splitlines()
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Error: {file_path} file not found.") from exc
