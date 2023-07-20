import extra_streamlit_components as stx
import uuid


class CookieManager:
    def __init__(self):
        self._manager = stx.CookieManager(key=str(uuid.uuid4()))

    def get_all(self):
        return self._manager.get_all()

    def get(self, cookie):
        return self._manager.get(cookie)

    def set(self, cookie, value, expires_at):
        self._manager.set(cookie, value, expires_at)

    def delete(self, cookie):
        self._manager.delete(cookie)
