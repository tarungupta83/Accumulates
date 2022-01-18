# import os

import streamlit as st
from functions.set_language import set_language
from utils.documents.rename_pdfs import RenamePDFs

# from utils.documents.annotator import Annotator


def sidebar_section_document():
    dict_language = set_language()

    # button_create_documents_callout = st.button(dict_language["button_apply_callout"])
    # button_create_json = st.button(dict_language["button_produce_dict_main"])
    button_rename_documents = st.button(dict_language["rename"], help=dict_language["rename_help"])

    # if button_create_documents_callout:
    #     Annotator().forword()
    #     os.system("open store")
    #     st.success(dict_language["done"])

    if button_rename_documents:
        RenamePDFs()
        st.experimental_rerun()
