import itertools
import json
import os
import re
from itertools import product
from pathlib import Path
from re import findall

import fitz
import numpy as np
import streamlit as st
from Levenshtein import distance
from natsort import natsorted


class CreateDict:
    def __init__(self):
        self.path_store = Path("store")
        self.path_output_main = self.path_store / "dicts.json"
        self.path_output_node = self.path_store / "nodes.json"
        self.path_output_suggestion = self.path_store / "suggest.json"

        self.set_list_pdfs()
        self.make_dict_main()

        self.set_frequency_table_all_nodes()

        self.set_dict_suggestion()

        self.get_dict_ranked_time_creation()
        self.set_list_dict_node()
        self.save_list_dict_node()
        self.save_overall_keywords()

        self.set_frequency_id_in_list_dict_main()
        self.save_dict_main()

    def set_frequency_id_in_list_dict_main(self):
        for d in self.list_dict_main:
            d["nodes_frequency_id"] = [self.get_frequency_id(id) for id in d["nodes"] if type(d["nodes"]) is list]
            if type(d["nodes"]) is str:
                d["nodes_frequency_id"] = self.get_frequency_id(d["nodes"])

    def set_dict_suggestion(self):
        combinations: list[tuple] = list(product(*[self.frequencies.keys(), self.frequencies.keys()]))
        combinations = {frozenset(x) for x in combinations}
        combinations = (list(x) for x in combinations)
        combinations = (i for i in combinations if len(i) == 2)
        combinations: list[dict] = [
            {"pair": "".join([c[0], " / ", c[1]]), "distance": distance(c[0], c[1]) / (len(c[0]) + len(c[1]))}
            if c[0] in c[1] or c[1] in c[0]
            else {
                "pair": "".join([c[0], " / ", c[1]]),
                "distance": (distance(c[0], c[1]) * 2) / (len(c[0]) + len(c[1])),
            }
            for c in combinations
        ]
        combinations = [i for i in combinations if i["distance"] != 0]
        combinations: list[dict] = natsorted(combinations, key=lambda d: d["distance"])
        with open(self.path_output_suggestion, "w") as writer:
            json.dump(combinations, writer)

    def get_frequency_id(self, id) -> str:
        target: dict = [i for i in self.list_dict_node if i["id"] == id][0]
        return target["frequency_id"]

    def make_dict_main(self):
        list_dict_main = []
        append = list_dict_main.append
        for i in self.list_files_pdf:
            self.read_document(name_document=i)
            append(self.get_lists_dict_annot_all())

        self.list_dict_main = self.flatten(list_dict_main)

    def save_dict_main(self):
        with open(self.path_output_main, "w") as writer:
            json.dump(self.list_dict_main, writer)

    def set_list_pdfs(self) -> list[str]:
        self.list_files_pdf: list[str] = [
            i for i in os.listdir(self.path_store) if i.endswith("pdf") and (not i.startswith("[A]"))
        ]

    def read_document(self, name_document: str) -> "fitz.Doc":
        self.name_document: str = name_document
        self.doc = fitz.open(self.path_store / self.name_document)

    def get_lists_dict_annot_all(self) -> list[dict]:
        lists_dict_annot_all: list[list] = [self.get_list_dict_annot_from_page(i) for i in range(self.doc.page_count)]
        return self.flatten(lists_dict_annot_all)

    def get_list_dict_annot_from_page(self, index_page: int) -> list[dict]:
        page = self.doc[index_page]
        return [
            self.get_dict_from_annot(page, annot, index_page) for annot in page.annots() if annot.type[1] == "Highlight"
        ]

    def get_dict_from_annot(self, page: fitz.Page, annot: fitz.Annot, index_page: int) -> dict:
        text_annot: str = self._extract_annot(annot=annot, page=page)
        dict_annot: dict = {
            "content": text_annot,
            "note": self.filter_note(annot.info["content"]),
            "page": index_page,
            "nodes": self.get_nodes_from_note(annot.info["content"]),
            "source": self.name_document,
            "source_creation": self.doc.metadata["creationDate"],
        }

        return dict_annot

    def filter_note(self, content_annot: str) -> str:
        content_annot = content_annot.replace("\n", " ")
        content_annot = content_annot.replace("\r", " ")
        if content_annot == "":
            return "No comment."
        else:
            return content_annot

    def get_nodes_from_note(self, content_annot: str) -> str:
        """
        Extract node information from annotation content.
        Args:
            content_annot (str): entire annotation (note) content.
        Returns:
            str: string of node name.
        """
        nodes = findall(r"\[(.*?)\]", content_annot, re.DOTALL)
        if nodes:
            return [n.replace(" ", "-") for n in nodes]  # non greedy search
        else:
            return "None"

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

    def set_frequency_table_all_nodes(self):
        all_nodes: list = [i["nodes"] for i in self.list_dict_main]
        all_nodes: list = self.flatten(all_nodes)
        all_nodes: list = list(set(all_nodes))

        self.frequencies: dict = {i: self.get_node_frequency(i) for i in all_nodes}

        self.frequencies_manual = self.frequencies.copy()
        self.frequencies_auto = self.frequencies.copy()

        for key in self.frequencies.keys():
            self.frequencies[key] += self.get_num_unregistered_notes(key)

        for key in self.frequencies_auto.keys():
            self.frequencies_auto[key] = self.get_num_unregistered_notes(key)

    def get_node_frequency(self, node: str):
        return len([i for i in self.list_dict_main if node in i["nodes"]])

    def get_num_unregistered_notes(self, key):
        return len(
            [
                i
                for i in self.list_dict_main
                if key not in i["nodes"]
                and ((key.replace("-", " ").replace("_", " ") in i["content"]) or (key in i["content"]))
            ]
        )

    def set_list_dict_node(self) -> list[dict]:
        self.list_dict_node = [
            {
                "id": key,
                "frequency": float(self.frequencies[key]),
                "time_score": self.get_time_score(key),
                "frequency_id": "".join(
                    [
                        "[",
                        str(self.frequencies[key]),
                        "]",
                        "[",
                        str(self.frequencies_manual[key]),
                        ":",
                        str(self.frequencies_auto[key]),
                        "]",
                        "-",
                        "[",
                        key,
                        "]",
                    ]
                ),
            }
            for key in self.frequencies.keys()
        ]

    def save_list_dict_node(self):
        with open(self.path_output_node, "w") as writer:
            json.dump(self.list_dict_node, writer)

    def get_dict_ranked_time_creation(self) -> dict:
        list_time_creation: list[str] = list(set([i["source_creation"] for i in self.list_dict_main]))
        list_time_creation: list[str] = natsorted(list_time_creation)
        self.dict_ranked_time_creation: dict = {i: list_time_creation.index(i) for i in list_time_creation}

    def get_time_score(self, node: str) -> float:
        subset: list[dict] = [i for i in self.list_dict_main if node in i["nodes"]]
        scores = [self.dict_ranked_time_creation[i["source_creation"]] for i in subset]
        return np.mean(scores) / max(self.dict_ranked_time_creation.values())

    def save_overall_keywords(self) -> list[str]:
        keywords = self.flatten([i["id"].replace("-", " ").replace("_", " ") for i in self.list_dict_node])
        with open(self.path_store / "keywords.json", "w") as writer:
            for i in keywords:
                writer.write(i + "\n")

    def has_numbers(self, str: str):
        return any(char.isdigit() for char in str)

    def flatten(self, list_input) -> list:
        if len(list_input) == 0:
            return list_input
        if isinstance(list_input[0], list):
            return self.flatten(list_input[0]) + self.flatten(list_input[1:])
        return list_input[:1] + self.flatten(list_input[1:])


if __name__ == "__main__":
    CreateDict()
    with open(Path("store", "dicts.json")) as reader:
        data = json.load(reader)
    print(data)
