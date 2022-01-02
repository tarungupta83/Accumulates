import os
from pathlib import Path

import fitz


class ModifyDocSubject:
    def __init__(self, doc: str, subject: str):
        self.path_store = Path("store")
        self.name_doc = doc
        self.read_doc()
        self.modify(subject)
        self.save()

    def read_doc(self):
        self.doc = fitz.open(self.path_store / self.name_doc)

    def modify(self, subject: str):
        metadata = self.doc.metadata
        metadata["subject"] = subject
        self.doc.set_metadata(metadata)

    def save(self):
        os.remove(self.path_store / self.name_doc)
        self.doc.save(self.path_store / self.name_doc.replace("paper", "_paper"), garbage=1, deflate=True, clean=True)
        os.rename(self.path_store / self.name_doc.replace("paper", "_paper"), self.path_store / self.name_doc)


if __name__ == "__main__":
    pass
