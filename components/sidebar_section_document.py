import os

import streamlit as st
from functions.set_language import set_language
from utils.documents.annotator import Annotator
from utils.documents.create_dict import CreateDict
from utils.documents.rename_pdfs import RenamePDFs


def sidebar_section_document():
    dict_language = set_language()

    button_create_documents_callout = st.button(dict_language["button_apply_callout"])
    button_create_json = st.button(dict_language["button_produce_dict_main"])
    check_box_get_keywords: bool = st.checkbox("GET_KEYWORDS", help="EXPERIMENTAL", value=False)
    button_rename_documents = st.button(dict_language["rename"], help=dict_language["rename_help"])

    if button_create_json:
        CreateDict(check_box_get_keywords)
        st.experimental_rerun()

    if button_create_documents_callout:
        Annotator().forword()
        os.system("open store")
        st.success(dict_language["done"])

    if button_rename_documents:
        RenamePDFs()
        st.experimental_rerun()
