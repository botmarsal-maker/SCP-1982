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
        self.last_cleanup = time.time()

    def _cleanup(self):
        now = time.time()
        if now - self.last_cleanup > 3600:
            self.last_cleanup = now
            to_delete = [uid for uid, expire_time in self._cache.items() if now > expire_time]
            for uid in to_delete:
                del self._cache[uid]

    def is_cached_valid(self, user_id: int) -> bool:
        self._cleanup()
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
