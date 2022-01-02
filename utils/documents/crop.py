import json
import os
from pathlib import Path

import fitz


class Crop:
    def __init__(self, name_file):
        self.name_file: str = name_file
        self.path_file: Path = Path("store", self.name_file)
        self.src = fitz.open(self.path_file)
        self.doc = fitz.open(self.src.name)
        self.configuration = json.loads(open(Path("assets", "configuration.json")).read())
        self.page_expand_ratio = self.configuration["page_expand_ratio"]

    def forward(self):
        self.create_dir_cache()
        self.expand_all_pages()
        self.doc.save(Path("cache", "[Cropped]" + self.name_file), garbage=1, deflate=True, clean=True)

    def create_dir_cache(self):
        if not os.path.exists(Path("cache")):
            os.mkdir(Path("cache"))

    def expand_all_pages(self):
        for i in range(self.src.page_count):
            rect = self.doc[i].rect
            page_new = self.doc.new_page(i + 1, width=rect.width * float(self.page_expand_ratio), height=rect.height)
            page_new.show_pdf_page(rect, self.src, i, clip=rect)
            self.doc.delete_page(i)


if __name__ == "__main__":
    Crop(name_file="example.pdf").forward()
