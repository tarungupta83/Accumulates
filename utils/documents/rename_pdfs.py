import os
from pathlib import Path

import fitz
from natsort import natsorted


class RenamePDFs:
    def __init__(self):
        self.path_store: Path = Path("store")
        self.set_list_pdf_in_store()
        self.get_list_dict_metadata()
        self.register_renamed()

    def set_list_pdf_in_store(self):
        try:
            self.list_all_names_pdf_document = [
                i for i in os.listdir(self.path_store) if (not i.startswith("[A]") and i.endswith(".pdf"))
            ]
        except FileNotFoundError:
            self.list_all_names_pdf_document = []

    def get_list_dict_metadata(self):
        list_dict_metadata: list[dict] = []
        append = list_dict_metadata.append
        for i in self.list_all_names_pdf_document:
            doc = fitz.open(self.path_store / i)
            append(
                {
                    "name": i,
                    "title": doc.metadata["title"],
                    "author": doc.metadata["author"],
                    "time_created": doc.metadata["creationDate"],
                }
            )
        list_dict_metadata = natsorted(list_dict_metadata, key=lambda d: d["time_created"])
        for i in list_dict_metadata:
            if i["time_created"][0].isdigit():
                i["time_created"] = "D:" + i["time_created"]
            name_author: str = i["author"].split(" ")[-1].lower() if i["author"] else "unknown"
            i["index"] = list_dict_metadata.index(i) + 1
            i["name_new"] = f"paper{i['index']}.{i['time_created'][2:6]}_{i['time_created'][6:12]}_{name_author}.pdf"
            os.rename(self.path_store / i["name"], self.path_store / i["name_new"])

    def register_renamed(self):
        with open(self.path_store / "RENAMED", "w") as writer:
            writer.write("RENAMED")
