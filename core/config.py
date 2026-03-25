# -*- coding: utf-8 -*-
import json
from pathlib import Path

class Config:
    def __init__(self):
        self.config_path = Path.home() / ".joman_gis" / "config.json"
        self.config = self.load()
    
    def load(self):
        default = {
            "language": "fr",
            "theme": "dark",
            "crs": "EPSG:4326",
            "recent_projects": []
        }
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                default.update(data)
        return default
    
    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None): return self.config.get(key, default)
    def set(self, key, value): self.config[key] = value; self.save()

config = Config()
