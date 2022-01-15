import json
import os
from pathlib import Path

import fitz
import streamlit as st


class Aggregate:
    def __init__(self):
        self.path_store = Path("store")
        self.read_lists()
        self.set_list_pdfs()
        self.main()
        self.remove_registered_aggregations()

    def main(self):
        for f in self.list_files_pdf:
            self.name_doc = f
            self.read_file()
            self.modify_doc_all_pages()
            self.save()

    def read_file(self):
        self.doc = fitz.open(self.path_store / self.name_doc)

    def read_lists(self):
        with open(self.path_store / "aggregate.json") as reader:
            self.list_registered_aggregation = json.load(reader)
        with open(self.path_store / "nodes.json") as reader:
            self.list_nodes = json.load(reader)

    def set_list_pdfs(self):
        self.list_files_pdf: list[str] = [
            i for i in os.listdir(self.path_store) if i.endswith("pdf") and (not i.startswith("[A]"))
        ]

    def modify_doc_single_page(self, page: int):
        for i in self.doc[page].annots():
            for d in self.list_registered_aggregation:
                node_target: str = [i for i in self.list_nodes if i["frequency_id"] == d][0]["id"]
                content = self._extract_annot(annot=i, page=self.doc[page])
                info_annot = i.info

                if (
                    node_target in content
                    or (node_target.replace("-", " ") in content)
                    or (node_target.replace("_", " ") in content)
                    or (node_target.replace(" ", "-") in content)
                ) and ("".join(["[", node_target, "]"]) not in info_annot["content"]):
                    info_annot["content"] += "".join(["\n", "[", node_target, "]"])
                    i.set_info(info_annot)

    def modify_doc_all_pages(self):
        for i in range(self.doc.page_count):
            self.modify_doc_single_page(i)

    def save(self):
        os.remove(self.path_store / self.name_doc)
        self.doc.save(self.path_store / self.name_doc.replace("paper", "_paper"), garbage=1, deflate=True, clean=True)
        os.rename(self.path_store / self.name_doc.replace("paper", "_paper"), self.path_store / self.name_doc)

    def remove_registered_aggregations(self):
        os.remove(self.path_store / "aggregate.json")

    def _extract_annot(self, annot: fitz.Annot, page: fitz.Page):
        """Extract words in a given highlight.

        Args:
            annot (fitz.Annot): [description]
            words_on_page (list): [description]

        Returns:
            str: words in the entire highlight.
        """
        words_on_page = page.get_text("words")
        quad_points = annot.vertices
        try:
            quad_count = int(len(quad_points) / 4)
        except TypeError:
            st.write(f"Fail to identify {annot}")
        sentences = ["" for i in range(quad_count)]
        for i in range(quad_count):
            points = quad_points[i * 4 : i * 4 + 4]
            words = [w for w in words_on_page if self._check_contain(fitz.Rect(w[:4]), points)]
            sentences[i] = " ".join(w[4] for w in words)
        sentence = " ".join(sentences)
        return sentence

    def _check_contain(self, r_word, points: list, threshold_intersect: float = 0.65):
        """If `r_word` is contained in the rectangular area.

        The area of the intersection should be large enough compared to the
        area of the given word.

        Args:
            r_word (fitz.Rect): rectangular area of a single word.
            points (list): list of points in the rectangular area of the
                given part of a highlight.

        Returns:
            bool: whether `r_word` is contained in the rectangular area.
        """
        # `r` is mutable, so everytime a new `r` should be initiated.
        r = fitz.Quad(points).rect
        r.intersect(r_word)

        if r.get_area() >= r_word.get_area() * threshold_intersect:
            contain = True
        else:
            contain = False
        return contain


if __name__ == "__main__":
    Aggregate()
