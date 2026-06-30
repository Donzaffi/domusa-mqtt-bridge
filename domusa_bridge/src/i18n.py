import json
import os

class I18n:
    def __init__(self, lang="de"):
        self.lang = lang
        self.data = {}
        # Pfad zum locales Ordner
        path = os.path.join(os.path.dirname(__file__), "locales", f"{lang}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            # Fallback auf de
            pass

    def t(self, key):
        return self.data.get(key, key)
