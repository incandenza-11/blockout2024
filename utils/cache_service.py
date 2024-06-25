import json
import os


class CacheService:
    def __init__(self, filename: str):
        self.filename = filename
        self.cache = self._load_cache()

    def _load_cache(self) -> dict[str, int]:
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}

    def _save(self) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=4)

    def get(self, key: str) -> int:
        return self.cache.get(key)

    def set(self, key: str, value: int) -> None:
        self.cache[key] = value
        self._save()
