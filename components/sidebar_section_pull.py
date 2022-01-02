import os
from pathlib import Path

import streamlit as st
from functions.set_language import set_language
from utils.ports.pull import Pull


class SidebarSectionPull:
    def __init__(self):
        self.dict_language = set_language()
        self.path_store: Path = Path("store")
        self.sidebar_section()

    def sidebar_section(self):
        whether_manual_input = st.checkbox(
            self.dict_language["whether_manual_input_path"],
            value=False,
            help=self.dict_language["help_whether_manual_input_path"],
        )
        if whether_manual_input:
            arg = st.text_input(self.dict_language["name_folder"])
        else:
            path_unit = Path("..", open(Path("assets", "path.pth"), "r").read())
            list_all_files = os.listdir(path_unit)
            list_all_files = [f for f in list_all_files if not os.path.isfile(str(path_unit / f))]
            list_all_files = [f for f in list_all_files if not f.startswith(".")]
            arg = st.selectbox(self.dict_language["name_folder"], options=list_all_files)
        button_pull = st.button(self.dict_language["pull"])
        button_reset_path = st.button(
            self.dict_language["button_reset_path_and_language"],
            help=self.dict_language["help_button_reset_path_and_language"],
        )

        if button_pull:
            Pull().forward(arg)
            st.session_state["PDFs_IMPORTED"] = True
            st.experimental_rerun()

        if button_reset_path:
            os.remove(Path("assets", "path.pth"))
            os.remove(Path("assets", "language.set"))
            st.experimental_rerun()
