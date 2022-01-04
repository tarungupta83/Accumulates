import json
import os
from pathlib import Path

import fitz


class ModifyNode:
    def __init__(self):
        self.path_store = Path("store")
        self.read_lists()
        self.set_list_pdfs()
        self.main()
        self.remove_registered_translations()

    def main(self):
        for f in self.list_files_pdf:
            self.name_doc = f
            self.read_file()
            self.modify_doc_all_pages()
            self.save()

    def read_file(self):
        self.doc = fitz.open(self.path_store / self.name_doc)

    def read_lists(self):
        with open(self.path_store / "translate.json") as reader:
            self.list_registered_translations = json.load(reader)
        with open(self.path_store / "nodes.json") as reader:
            self.list_nodes = json.load(reader)

    def set_list_pdfs(self):
        self.list_files_pdf: list[str] = [
            i for i in os.listdir(self.path_store) if i.endswith("pdf") and (not i.startswith("[A]"))
        ]

    def modify_doc_single_page(self, page: int):
        for i in self.doc[page].annots():
            for d in self.list_registered_translations:
                node_target: str = self.wrap(
                    [i for i in self.list_nodes if i["frequency_id"] == [i for i in d.keys()][0]][0]["id"]
                )
                translate_to: str = self.wrap([i for i in d.values()][0])
                if translate_to == "[delete]":
                    translate_to = ""
                elif translate_to == "[keep]":
                    translate_to = node_target
                info_annot = i.info
                info_annot["content"] = info_annot["content"].replace(node_target, translate_to)
                i.set_info(info_annot)

    def modify_doc_all_pages(self):
        for i in range(self.doc.page_count):
            self.modify_doc_single_page(i)

    def wrap(self, string) -> str:
        return "".join(["[", string, "]"])

    def save(self):
        os.remove(self.path_store / self.name_doc)
        self.doc.save(self.path_store / self.name_doc.replace("paper", "_paper"), garbage=1, deflate=True, clean=True)
        os.rename(self.path_store / self.name_doc.replace("paper", "_paper"), self.path_store / self.name_doc)

    def remove_registered_translations(self):
        os.remove(self.path_store / "translate.json")


if __name__ == "__main__":
    ModifyNode()
