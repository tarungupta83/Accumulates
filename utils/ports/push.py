import os
import pickle
import shutil
from pathlib import Path

from dirsync import sync


class Push:
    def __init__(self):
        self.path_store = Path("store")
        self.path_cache = Path("cache")

    def forward(self):
        self.load_source()
        self.remove_dict()
        self.check_rename()
        self.sync()
        self.remove_cache()

    def remove_dict(self):
        self.list_json_in_store = [i for i in os.listdir(self.path_store) if i.endswith(".json")]
        for i in self.list_json_in_store:
            os.remove(self.path_store / i)

    def load_source(self):
        with open(self.path_store / ".source", "rb") as loader:
            self.path_source = pickle.load(loader)
        os.remove(self.path_store / ".source")

    def check_rename(self):
        if os.path.exists(self.path_store / "RENAMED"):
            for i in os.listdir(self.path_source):
                os.remove(self.path_source / i)
            os.remove(self.path_store / "RENAMED")

    def sync(self):
        sync(self.path_store, self.path_source, "sync")

    def remove_cache(self):
        if os.path.exists(self.path_cache):
            shutil.rmtree(self.path_cache)
        if os.path.exists(self.path_store):
            shutil.rmtree(self.path_store)


if __name__ == "__main__":
    Push().forward()
