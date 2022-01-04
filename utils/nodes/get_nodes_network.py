import colorsys
import itertools
import json
import webbrowser
from pathlib import Path

import pandas
from pyvis.network import Network
from utils.nodes.jaal_logo_removed import JaalLogoRemoved


class GetNodesNetwork:
    def __init__(self, whether_manual_adjust: bool = False):
        self.options_network = open(Path("assets", "options_network")).read()
        self.whether_manual_adjust = whether_manual_adjust
        self.path_store = Path("store")
        self.read_dicts()
        self.set_edge_map()

        if whether_manual_adjust:
            self.set_network_pyvis()
        else:
            self.set_network()

    def read_dicts(self) -> list[dict]:
        """Read the main dictionary from store folder.
        Returns:
            list[dict]: a list of dictionaries that contains all annotation information.
        """
        with open(self.path_store / "dicts.json") as reader:
            self.data_list_dicts = json.load(reader)
        with open(self.path_store / "nodes.json") as reader:
            self.list_node_stats_dict = json.load(reader)

    def set_edge_map(self) -> dict:

        combinations: list = [
            [i["id"] for i in self.list_node_stats_dict],
            [i["id"] for i in self.list_node_stats_dict],
        ]
        combinations: list = list(itertools.product(*combinations))
        combinations: list = [i for i in combinations if i[0] != i[1]]

        edges: dict = {key: None for key in combinations}
        for key in edges.keys():
            edges[key] = self.get_num_connections_by_key(key)
        self.edges = {key: value for key, value in edges.items() if value != 0}

    def get_num_connections_by_key(self, key: tuple) -> int:
        """Get number of connections between the two given nodes (a key as tuple): (node_1, node_2).
        1. filter out all the annotations where the first node takes the first place.
        2. check whether the second node is one of the remaining. If true, add 1 connection.
        Args:
            key (tuple): (node_1, node_2)
        Returns:
            int: the total number of connections.
        """
        subset: list[dict] = [i for i in self.data_list_dicts if i["nodes"][0] == key[0]]
        subset: list[dict] = [i for i in subset if key[1] in i["nodes"][1:]]
        return len(subset)

    def get_hex_from_hsv(self, hsv: tuple) -> str:
        # rgb = tuple(int(i * 255) for i in colorsys.hsv_to_rgb())
        try:
            rgb = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(*hsv))
        except ValueError:
            rgb = (3, 136, 252)
        hex = "#%02x%02x%02x" % rgb
        return hex

    def set_network(self):
        df_node = pandas.DataFrame(columns=["id", "frequency", "time_score"])
        for i in self.list_node_stats_dict:
            df_node = df_node.append(pandas.Series(i, name=self.list_node_stats_dict.index(i)))

        df_edge = pandas.DataFrame(columns=["from", "to", "weight", "strength"])
        list_edges: list[dict] = [
            {"from": key[0], "to": key[1], "weight": float(self.edges[key]), "strength": "medium"}
            for key in self.edges.keys()
        ]
        for i in list_edges:
            df_edge = df_edge.append(pandas.Series(i, name=list_edges.index(i)))

        webbrowser.open("http://127.0.0.1:8050/")

        JaalLogoRemoved(df_edge, df_node).plot(
            vis_opts={
                "nodes": {
                    "color": {"highlight": {"border": "rgba(179,0,233,1)", "background": "rgba(194,0,255,0.76)"}}
                },
                "edges": {
                    "color": {"color": "rgba(0,75,255,0.76)", "highlight": "rgba(255,0,0,1)"},
                    "smooth": False,
                },
                # "interaction": {"hideEdgesOnDrag": false},
                "physics": {
                    "repulsion": {"springLength": 70, "nodeDistance": 300},
                    "minVelocity": 0.75,
                    "solver": "repulsion",
                },
            }
        )

    def set_network_pyvis(self):
        net = Network(height="100%", width="100%")
        net.add_nodes(
            [i["id"] for i in self.list_node_stats_dict],
            value=[i["frequency"] for i in self.list_node_stats_dict],
            title=[f"Size: {i}" for i in [i["frequency"] for i in self.list_node_stats_dict]],
            color=[self.get_hex_from_hsv((200 / 360, 1, i["time_score"])) for i in self.list_node_stats_dict],
        )

        for key in self.edges.keys():
            net.add_edge(
                key[0],
                key[1],
                weight=self.edges[key],
                # weight=0.01,
                title=f"Connections: {self.edges[key]}",
                physics=True,
                # value=self.edges[key],
            )
        net.show_buttons()
        net.show(str(Path("assets", "network.html")))

    def flatten(self, list_input) -> list:
        if len(list_input) == 0:
            return list_input
        if isinstance(list_input[0], list):
            return self.flatten(list_input[0]) + self.flatten(list_input[1:])
        return list_input[:1] + self.flatten(list_input[1:])


if __name__ == "__main__":
    pass
