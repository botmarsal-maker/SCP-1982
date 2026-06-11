import time

class SettingsCache:
    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        self._cache[key] = value

    def load_all(self, settings_dict):
        self._cache = settings_dict

settings_cache = SettingsCache()

class FSCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self._cache = {}

    def is_cached_valid(self, user_id: int) -> bool:
        expire_time = self._cache.get(user_id)
        if expire_time and time.time() < expire_time:
            return True
        return False

    def set_valid(self, user_id: int):
        self._cache[user_id] = time.time() + self.ttl

    def invalidate(self, user_id: int):
        if user_id in self._cache:
            del self._cache[user_id]

fs_cache = FSCache(ttl_seconds=300)
