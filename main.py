import os
from pathlib import Path

import streamlit as st

from components.sidebar_section_document import sidebar_section_document
from components.sidebar_section_inspect import SidebarSectionInspect
from components.sidebar_section_pull import SidebarSectionPull
from functions.set_language import set_language
from functions.string_parser import string_parser
from pages.create_log_path import CreateLogPath


class Main:
    def __init__(self):
        self.dict_language = set_language()
        st.set_page_config(layout="wide")
        # self.init_session_state()
        self.set_width()
        self.area_main()
        self.area_sidebar()

    # def init_session_state(self):
    #     if "PDFs_IMPORTED" not in st.session_state:
    #         st.session_state["PDFs_IMPORTED"] = False

    def set_width(self):
        st.markdown(
            string_parser.get_style(),
            unsafe_allow_html=True,
        )

    def area_main(self):
        self.main_c1 = st.container()
        st.markdown("""
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>""", unsafe_allow_html=True)

    def area_sidebar(self):
        with st.sidebar:
            # if not st.session_state["PDFs_IMPORTED"]:
            if not os.path.exists(Path("store")):
                SidebarSectionPull()
            else:
                st.title(f"「{self.dict_language['title_expander_documents']}」")
                sidebar_section_document()
                st.title(f"「{self.dict_language['title_expander_nodes_inspect']}」")
                SidebarSectionInspect(self.main_c1)


if __name__ == "__main__":
    if os.path.exists(Path("assets", "path.pth")) and os.path.exists(Path("assets", "language.set")):
        Main()

    else:
        CreateLogPath().forward()
