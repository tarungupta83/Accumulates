import collections
import json
from collections import Counter as counter
from pathlib import Path

import numpy as np
from natsort import natsorted
from utils.nodes.get_keywords import get_keywords


class CreateNodesStats:
    def __init__(self, whether_get_keywords: bool):
        self.path_store = Path("store")
        self.path_output = self.path_store / "nodes.json"
        self.read_dict_main()
        self.set_frequency_table_all_nodes()
        self.get_dict_ranked_time_creation()
        self.set_list_node_stats_dicts()
        self.get_overall_keywords(whether_get_keywords)

    def read_dict_main(self) -> list[dict]:
        with open(self.path_store / "dicts.json") as reader:
            self.data_list_dicts = json.load(reader)

    def set_frequency_table_all_nodes(self):
        all_nodes: list = [i["nodes"] for i in self.data_list_dicts]
        all_nodes: list = self.flatten(all_nodes)
        self.frequencies: collections.Counter = counter(all_nodes)
        self.frequencies: dict = dict(self.frequencies)

    def set_list_node_stats_dicts(self) -> list[dict]:
        self.list_node_stats_dict = [
            {
                "id": key,
                "frequency": float(self.frequencies[key]),
                "time_score": self.get_time_score(key),
                "frequency_id": "".join(["[", str(self.frequencies[key]), "]", key]),
            }
            for key in self.frequencies.keys()
        ]
        with open(self.path_output, "w") as writer:
            json.dump(self.list_node_stats_dict, writer)

    def get_dict_ranked_time_creation(self) -> dict:
        list_time_creation: list[str] = list(set([i["source_creation"] for i in self.data_list_dicts]))
        list_time_creation: list[str] = natsorted(list_time_creation)
        self.dict_ranked_time_creation: dict = {i: list_time_creation.index(i) for i in list_time_creation}

    def get_time_score(self, node: str) -> float:
        subset: list[dict] = [i for i in self.data_list_dicts if node in i["nodes"]]
        scores = [self.dict_ranked_time_creation[i["source_creation"]] for i in subset]
        return np.mean(scores) / max(self.dict_ranked_time_creation.values())

    def get_overall_keywords(self, whether_get_keywords: bool, quantity_each_node: int = 6) -> list[str]:
        content: str = " ".join([i["content"] for i in self.data_list_dicts])
        if whether_get_keywords:
            keywords: list[str] = get_keywords(
                text=content, quantity=len(self.list_node_stats_dict) * quantity_each_node
            )
        else:
            keywords: list[str] = [""]
        keywords: list[str] = [i for i in keywords if not self.has_numbers(i)]
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
    pass
