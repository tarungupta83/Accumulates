import json
import os
from pathlib import Path

import streamlit as st


class CreateLogPath:
    def __init__(self):
        pass

    def forward(self):
        self.get_path_input()

    def get_path_input(self):
        option_language = st.selectbox("", options=["English", "中文"])

        if option_language == "English":
            self.dict_language = json.loads(open(Path("assets", "language", "en.json")).read())
        elif option_language == "中文":
            self.dict_language = json.loads(open(Path("assets", "language", "zh.json")).read())

        path_input = st.selectbox(
            self.dict_language["register_root_directory_title"],
            options=os.listdir(".."),
            help=self.dict_language["register_root_directory_help"],
        )

        button_confirm = st.button(self.dict_language["confirm"])

        if button_confirm:
            with open(Path("assets", "path.pth"), "w") as writer:
                writer.write(path_input)
            with open(Path("assets", "language.set"), "w") as writer:
                writer.write(option_language)
            st.experimental_rerun()
