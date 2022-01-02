import os
from pathlib import Path

import streamlit as st
from functions.set_language import set_language
from utils.ports.push import Push


class SectionPush:
    def __init__(self):
        self.dict_language = set_language()
        self.path_store: Path = Path("store")
        self.sidebar_section_push()

    def sidebar_section_push(self):
        path_unit = Path("..", open(Path("assets", "path.pth"), "r").read())
        list_all_files = os.listdir(path_unit)
        list_all_files = [f for f in list_all_files if not os.path.isfile(str(path_unit / f))]
        list_all_files = [f for f in list_all_files if not f.startswith(".")]

        button_push = st.button(self.dict_language["push"])

        if button_push:
            Push().forward()
            st.session_state["PDFs_IMPORTED"] = False
            st.experimental_rerun()
