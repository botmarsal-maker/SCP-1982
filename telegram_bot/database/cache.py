import time
from globals import current_bot_id

class BotAwareCache:
    def __init__(self):
        # { bot_id: { key: value } }
        self._cache = {}

    def _get_bot_cache(self):
        bot_id = current_bot_id.get("main")
        if bot_id not in self._cache:
            self._cache[bot_id] = {}
        return self._cache[bot_id]

class SettingsCache(BotAwareCache):
    def get(self, key):
        return self._get_bot_cache().get(key)

    def set(self, key, value):
        self._get_bot_cache()[key] = value

    def load_all(self, settings_dict):
        bot_id = current_bot_id.get("main")
        self._cache[bot_id] = settings_dict

settings_cache = SettingsCache()

class FSCache(BotAwareCache):
    def __init__(self, ttl_seconds=300):
        super().__init__()
        self.ttl = ttl_seconds

    def is_cached_valid(self, user_id: int) -> bool:
        expire_time = self._get_bot_cache().get(user_id)
        if expire_time and time.time() < expire_time:
            return True
        return False

    def set_valid(self, user_id: int):
        self._get_bot_cache()[user_id] = time.time() + self.ttl

    def invalidate(self, user_id: int):
        if user_id in self._get_bot_cache():
            del self._get_bot_cache()[user_id]

fs_cache = FSCache(ttl_seconds=300)
