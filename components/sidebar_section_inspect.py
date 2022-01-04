import json
import multiprocessing
import os
from pathlib import Path

import fitz
import pyperclip
import streamlit as st
from functions.modify_meta_subject import ModifyDocSubject
from functions.modify_node import ModifyNode
from functions.set_language import set_language
from functions.string_parser import string_parser
from natsort import natsorted
from utils.documents.get_note_proportion import GetNoteProportion
from utils.nodes.get_nodes_network import GetNodesNetwork

from components.section_push import SectionPush


class SidebarSectionInspect:
    def __init__(self, main_c1):
        self.dict_language = set_language()
        self.options_network = open(Path("assets") / "options_network").read()
        self.path_store = Path("store")

        if "network_running" not in st.session_state:
            st.session_state["network_running"] = "STATE_UNINIT"

        try:
            self.read_dicts_data()
            self.set_list_node_frequency_id()
            self.set_list_unique_pdfs()

        except FileNotFoundError:
            pass

        st.markdown(f"> ## 「{self.dict_language['title_expander_nodes_inspect']}」")
        self.sidebar_expander_inspect(main_c1)
        SectionPush()

    def read_dicts_data(self) -> list[dict]:
        """Read the main dictionary from store folder.
        Returns:
            list[dict]: a list of dictionaries that contains all annotation information.
        """
        with open(self.path_store / "dicts.json") as reader:
            self.data_list_dicts = json.load(reader)
        with open(self.path_store / "nodes.json") as reader:
            self.list_dict_node: list[dict] = json.load(reader)

    def set_list_node_frequency_id(self) -> list[str]:
        self.list_node_frequency_id = natsorted([i["frequency_id"] for i in self.list_dict_node], reverse=True)

    def set_list_unique_pdfs(self) -> list[str]:
        all_pdfs: list = self.flatten([i["source"] for i in self.data_list_dicts])
        self.all_pdfs: list = list(set(all_pdfs))

    def sidebar_expander_inspect(self, main_c1):
        if os.path.exists(self.path_store / "dicts.json"):
            select_box_which_stats = st.radio(
                "",
                (
                    self.dict_language["button_show_file_stats_unfinished"],
                    self.dict_language["button_show_file_stats_finished"],
                    self.dict_language["button_show_file_stats_by_subject"],
                    self.dict_language["button_produce_nodes_network"],
                    self.dict_language["multiselect_inspect_nodes"],
                    self.dict_language["node_translate"],
                ),
            )
        else:
            select_box_which_stats = st.radio(
                "",
                (
                    self.dict_language["button_show_file_stats_unfinished"],
                    self.dict_language["button_show_file_stats_finished"],
                    self.dict_language["button_show_file_stats_by_subject"],
                ),
            )

        if select_box_which_stats == self.dict_language["button_produce_nodes_network"]:
            button_show_network = st.button(self.dict_language["button_produce_nodes_network"])
            checkbox_manual_adjust = st.checkbox(
                self.dict_language["whether_manual_settings"],
                value=False,
                help=self.dict_language["help_whether_manual_settings_overview"],
            )

            if button_show_network and not checkbox_manual_adjust:
                if st.session_state.network_running == "STATE_UNINIT":
                    st.session_state.network_running = multiprocessing.Process(target=GetNodesNetwork)
                    st.session_state.network_running.start()

                else:
                    st.session_state.network_running.terminate()
                    st.session_state.network_running = multiprocessing.Process(target=GetNodesNetwork)
                    st.session_state.network_running.start()

            elif button_show_network and checkbox_manual_adjust:
                GetNodesNetwork(checkbox_manual_adjust)
                os.system("open assets/network.html")

        elif select_box_which_stats == self.dict_language["multiselect_inspect_nodes"]:
            with main_c1:
                multiselect_nodes = st.multiselect(
                    self.dict_language["multiselect_inspect_nodes"], options=self.list_node_frequency_id + ["[ALL]"]
                )
                nodes_secondary = st.multiselect(
                    self.dict_language["secondary_inspect_nodes"], options=self.get_coexist_nodes(multiselect_nodes)
                )

                nodes_combined = multiselect_nodes + nodes_secondary

                keywords: list[str] = open(Path("store", "keywords.json")).read().split("\n")
                if nodes_combined and "[ALL]" not in nodes_combined:
                    subset: list[dict] = [
                        i for i in self.data_list_dicts if set(nodes_combined).issubset(i["nodes_frequency_id"])
                    ]
                elif "[ALL]" in nodes_combined:
                    subset: list[dict] = self.data_list_dicts
                else:
                    subset = []
                for i in subset:
                    st.markdown(
                        string_parser.get_card_html(i, [i for i in keywords if i]),
                        unsafe_allow_html=True,
                    )
            pyperclip.copy(" ".join([i["content"] for i in subset]))

        elif select_box_which_stats == self.dict_language["button_show_file_stats_unfinished"]:
            list_dict_notes_stats = GetNoteProportion().list_dict_notes_stats
            list_dict_notes_stats = [i for i in list_dict_notes_stats if i["latest_note_page"] != 100.0]
            list_subjects = [fitz.open(Path("store") / i["file"]).metadata["subject"] for i in list_dict_notes_stats]
            list_subjects = natsorted(list(set(list_subjects)))
            subjects_to_include = st.multiselect(self.dict_language["metadata_subject_include"], options=list_subjects)
            if "revisit" in list_subjects:
                subjects_to_exclude = st.multiselect(
                    self.dict_language["metadata_subject_exclude"], options=list_subjects, default="revisit"
                )
            else:
                subjects_to_exclude = st.multiselect(
                    self.dict_language["metadata_subject_exclude"], options=list_subjects
                )
            if subjects_to_include:
                list_dict_notes_stats = [
                    i
                    for i in list_dict_notes_stats
                    if fitz.open(Path("store") / i["file"]).metadata["subject"] in subjects_to_include
                ]
            if subjects_to_exclude:
                list_dict_notes_stats = [
                    i
                    for i in list_dict_notes_stats
                    if fitz.open(Path("store") / i["file"]).metadata["subject"] not in subjects_to_exclude
                ]

            self.get_cards(main_c1=main_c1, list_dict_notes_stats=list_dict_notes_stats)

        elif select_box_which_stats == self.dict_language["button_show_file_stats_finished"]:
            list_dict_notes_stats = GetNoteProportion().list_dict_notes_stats
            list_dict_notes_stats = [i for i in list_dict_notes_stats if i["latest_note_page"] == 100.0]
            list_subjects = [fitz.open(Path("store") / i["file"]).metadata["subject"] for i in list_dict_notes_stats]
            list_subjects = list(set(list_subjects))
            list_subjects = natsorted(list(set(list_subjects)))
            subjects_to_include = st.multiselect(self.dict_language["metadata_subject_include"], options=list_subjects)
            if "revisit" in list_subjects:
                subjects_to_exclude = st.multiselect(
                    self.dict_language["metadata_subject_exclude"], options=list_subjects, default="revisit"
                )
            else:
                subjects_to_exclude = st.multiselect(
                    self.dict_language["metadata_subject_exclude"], options=list_subjects
                )
            if subjects_to_include:
                list_dict_notes_stats = [
                    i
                    for i in list_dict_notes_stats
                    if fitz.open(Path("store") / i["file"]).metadata["subject"] in subjects_to_include
                ]
            if subjects_to_exclude:
                list_dict_notes_stats = [
                    i
                    for i in list_dict_notes_stats
                    if fitz.open(Path("store") / i["file"]).metadata["subject"] not in subjects_to_exclude
                ]

            self.get_cards(main_c1=main_c1, list_dict_notes_stats=list_dict_notes_stats)

        elif select_box_which_stats == self.dict_language["button_show_file_stats_by_subject"]:
            list_dict_notes_stats = GetNoteProportion().list_dict_notes_stats
            list_subjects = [fitz.open(Path("store") / i["file"]).metadata["subject"] for i in list_dict_notes_stats]
            list_subjects = list(set(list_subjects))
            list_subjects = natsorted(list(set(list_subjects)))
            subjects_selected = st.multiselect(self.dict_language["metadata_subject"], options=list_subjects)
            list_dict_notes_stats = [
                i
                for i in list_dict_notes_stats
                if fitz.open(Path("store") / i["file"]).metadata["subject"] in subjects_selected
            ]
            self.get_cards(main_c1=main_c1, list_dict_notes_stats=list_dict_notes_stats)

        elif select_box_which_stats == self.dict_language["node_translate"]:
            with main_c1:
                list_node_frequency_id_reversed = self.list_node_frequency_id
                list_node_frequency_id_reversed.reverse()
                if os.path.exists(self.path_store / "translate.json"):
                    with open(self.path_store / "translate.json") as reader:
                        list_registered_translations = json.load(reader)
                    list_node_frequency_id_reversed = [
                        i
                        for i in list_node_frequency_id_reversed
                        if i not in [[k for k in i.keys()][0] for i in list_registered_translations]
                    ]
                nodes_to_translate = st.multiselect(
                    self.dict_language["nodes_to_translate"], options=list_node_frequency_id_reversed
                )
                nodes_translate_to = st.text_input(self.dict_language["nodes_translate_to"])
                button_register = st.button(self.dict_language["nodes_register"])
                if nodes_to_translate:
                    subset: list[dict] = [
                        i for i in self.data_list_dicts if set(nodes_to_translate).intersection(i["nodes_frequency_id"])
                    ]
                else:
                    subset = []

                if (
                    nodes_to_translate
                    and nodes_translate_to
                    and button_register
                    and not os.path.exists(self.path_store / "translate.json")
                ):
                    with open(self.path_store / "translate.json", "w") as writer:
                        json.dump([{i: nodes_translate_to} for i in nodes_to_translate], writer)
                    st.experimental_rerun()

                elif os.path.exists(self.path_store / "translate.json"):
                    with open(self.path_store / "translate.json") as reader:
                        list_registered_translations = json.load(reader)
                    button_apply_registration = st.button(self.dict_language["nodes_apply_registration"])
                    button_clear_registration = st.button(self.dict_language["nodes_clear_registration"])

                    if nodes_to_translate and nodes_translate_to and button_register:
                        list_registered_translations += [{i: nodes_translate_to} for i in nodes_to_translate]
                        list_registered_translations = [
                            dict(s) for s in set(frozenset(d.items()) for d in list_registered_translations)
                        ]
                        with open(self.path_store / "translate.json", "w") as writer:
                            json.dump(list_registered_translations, writer)
                        st.experimental_rerun()

                    if button_apply_registration:
                        ModifyNode()
                        st.experimental_rerun()

                    if button_clear_registration:
                        os.remove(self.path_store / "translate.json")
                        st.experimental_rerun()

                for i in subset:
                    st.markdown(
                        string_parser.get_card_html(
                            i, [i for i in open(Path("store", "keywords.json")).read().split("\n") if i]
                        ),
                        unsafe_allow_html=True,
                    )

                if os.path.exists(self.path_store / "translate.json"):
                    st.write(list_registered_translations)

    def flatten(self, list_input) -> list:
        if len(list_input) == 0:
            return list_input
        if isinstance(list_input[0], list):
            return self.flatten(list_input[0]) + self.flatten(list_input[1:])
        return list_input[:1] + self.flatten(list_input[1:])

    def get_coexist_nodes(self, list_input: list[str]) -> list:
        subset: list[dict] = [i for i in self.data_list_dicts if set(list_input).issubset(i["nodes_frequency_id"])]
        if list_input:
            return [i for i in self.flatten([i["nodes_frequency_id"] for i in subset]) if i not in list_input]
        else:
            return []

    def get_cards(self, main_c1, list_dict_notes_stats):
        input_subject = []
        buttons_open = []
        with main_c1:
            for i in list_dict_notes_stats:
                st.markdown(string_parser.get_html_card_pdf_stat(i), unsafe_allow_html=True)
                input_subject.append(
                    st.text_input(
                        self.dict_language["metadata_subject"],
                        key=(i["file"].split(".")[0] + "." + self.dict_language["metadata_subject"]),
                    )
                )
                buttons_open.append(st.button(i["file"][:19]))
                st.markdown("\n")

            for i, input in enumerate(input_subject):
                if input and input != fitz.open(Path("store") / list_dict_notes_stats[i]["file"]).metadata["subject"]:
                    ModifyDocSubject(doc=list_dict_notes_stats[i]["file"], subject=input)
                    st.experimental_rerun()

            for i, button in enumerate(buttons_open):
                if button:
                    os.system(f"open {self.path_store / list_dict_notes_stats[i]['file']}")
