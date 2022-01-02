import argparse
import os
import pickle
from pathlib import Path

from dirsync import sync


class Pull:
    def __init__(self):
        self.pathStore = Path("store")

    def forward(self, *args):
        self.make_dir()
        self.sync(args[0])
        self.pickle_path()

    def make_dir(self):
        if not os.path.exists(self.pathStore):
            os.mkdir(self.pathStore)

    def sync(self, arg):
        self.path_unit = Path("..", open(Path("assets", "path.pth"), "r").read(), arg)
        sync(self.path_unit, self.pathStore, "sync")

    def pickle_path(self):
        with open(self.pathStore / ".source", "wb") as dumper:
            pickle.dump(self.path_unit, dumper)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Input unit name")
    parser.add_argument("unit_name", metavar="N", type=str)
    parser.add_argument("pdf_type", metavar="N", type=str)
    args = parser.parse_args()

    Pull().forward(args.unit_name, args.pdf_type)
