import base64
import re
from pathlib import Path

import fitz
from screeninfo import get_monitors

from functions.set_language import set_language


class string_parser:
    def get_style(
        percentageButtonWidth: float = 0.68,
        percentWidthPdf: int = 100,
        sidebarWidth: int = int(get_monitors()[0].width * 0.25),
    ):
        strMaxWidth = f"max-width: {percentWidthPdf}%;"
        return f"""
<style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {{
            width: {sidebarWidth}px;
        }}
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {{
            width: {sidebarWidth}px;
            margin-left: -{sidebarWidth}px;
        }}

        .stButton>button {{
            color: #4F8BF9;
            border-radius: 0%;
            height: 38px;
            width: {(sidebarWidth-40)*percentageButtonWidth}px;
    }}
        .reportview-container .main .block-container{{{strMaxWidth}padding-top: {1}rem;}}

        .uploadedFile {{display: none}}

        # MainMenu {{visibility: hidden;}}

        .reportview-container .main footer {{visibility: hidden;}}

        # div.row-widget.stRadio > div{{flex-direction:row;}}
</style>
"""

    def wrap_in_code_block(text: str, level: str):
        return f"""<kbd class="alert alert-{level} p-1">{text}</kbd>"""

    def wrap_braces_in_color_span(text: str, color: str):
        return text.replace("(", f"<span style='color:{color};font-weight:bold'>(").replace(")", ")</span>")

    def wrap_content_in_color_span(text: str, color: str):
        return f"<span style='color:{color};font-weight:bold'>{text}</span>"

    def get_card_html(dict: dict, keywords: list[str], selected_keywords: list[str], options: list):
        content = dict["content"]
        keywords = [i for i in keywords if i in content and i not in selected_keywords]
        selected_keywords = [i for i in selected_keywords if i in content]

        for i in selected_keywords:
            compiler = re.compile(re.escape(i), re.IGNORECASE)
            content = compiler.sub(string_parser.wrap_content_in_color_span(text=i, color="Gold"), content)
            compiler_ = re.compile(re.escape(i.replace(" ", "-")), re.IGNORECASE)
            content = compiler_.sub(
                string_parser.wrap_content_in_color_span(text=i.replace(" ", "-"), color="Gold"), content
            )

            # content = content.replace(i, string_parser.wrap_content_in_color_span(text=i, color="Gold"))

        for i in keywords:
            compiler = re.compile(re.escape(i), re.IGNORECASE)
            content = compiler.sub(string_parser.wrap_content_in_color_span(text=i, color="Tomato"), content)
            compiler = re.compile(re.escape(i.replace(" ", "-")), re.IGNORECASE)
            content = compiler.sub(
                string_parser.wrap_content_in_color_span(text=i.replace(" ", "-"), color="Tomato"), content
            )

        source = string_parser.wrap_in_code_block(dict["source"], level="primary")
        content = string_parser.wrap_braces_in_color_span(content, color="LightSkyBlue")
        page = string_parser.wrap_in_code_block("Page: " + str(dict["page"]), level="primary")
        note = re.sub("[\[].*?[\]]", "", dict["note"])
        note = "No comments" if note.replace(" ", "") == "" else note

        if type(dict["nodes_frequency_id"]) == list:
            node_primary = string_parser.wrap_in_code_block(dict["nodes_frequency_id"][0], level="teal-bg")
            nodes_secondary = " ".join(
                [string_parser.wrap_in_code_block(i, level="city") for i in dict["nodes_frequency_id"][1:]]
            )

            for i in options:
                node_primary = node_primary.replace(
                    i, string_parser.wrap_content_in_color_span(text=i, color="Gold")
                )
                nodes_secondary = nodes_secondary.replace(
                    i, string_parser.wrap_content_in_color_span(text=i, color="Gold")
                )

        elif type(dict["nodes_frequency_id"]) == str:
            node_primary = string_parser.wrap_in_code_block(dict["nodes_frequency_id"], level="teal-bg")
            nodes_secondary = " "

            for i in options:
                node_primary = node_primary.replace(
                    i, string_parser.wrap_content_in_color_span(text=i, color="Gold")
                )

        return f"""
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
<div class="card text-white bg-dark mb-3">
    <div class="card-header">
    {source} {page}
    </div>
    <div class="card-body">
    <blockquote class="blockquote mb-0">
        <h5 style="line-height: 160%;">{content}</h5>
    </blockquote>
    <p style="line-height: 160%;">{note}</p>
    </div>
    <div class="card-footer text-muted" style="line-height: 200%;">
    {node_primary}  {nodes_secondary}
    </div>
</div>
<br>
"""

    def get_card_html_doc_info(image_data_bytes, title, authors, time_created, time_modified) -> str:
        if title.replace(" ", "") != "":
            content_title = f"""<div class="card-footer" style="line-height: 200%;">{title}</div>"""
        else:
            content_title = "<br>"

        return f"""
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>

<div class="card text-white bg-dark mb-3">
    <img src="data:image/png;base64,{image_data_bytes}" alt="cat png">
    {content_title}
    <div class="card-footer" style="line-height: 200%;">
    {authors}
    </div>
    <div class="card-footer" style="line-height: 200%;">
    {time_created}
    </div>
    <div class="card-footer" style="line-height: 200%;">
    {time_modified}
    </div>
</div>"""

    def get_html_card_pdf_stat(dict_file: dict):
        # print(dict_file["file"])
        doc = fitz.open(Path("store") / dict_file["file"])
        image_data_bytes = base64.b64encode(doc[0].get_pixmap().tobytes("format")).decode("utf-8")
        dict_language = set_language()
        return f"""
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
<div class="card flex-row flex-wrap">
<img style="width:25%" src="data:image/png;base64,{image_data_bytes}" alt="cover">
<div style="width:75%" class="card text-white bg-dark mb-3">
    <div class="card-body">
    {string_parser.wrap_in_code_block(text=dict_file['file'], level='primary')}
    </div>
    <div class="card-body" style="line-height: 200%;">
    {dict_language['metadata_subject']} {string_parser.wrap_in_code_block(text=str(doc.metadata['subject']), level='secondary')}
    </div>
    <div class="card-body" style="line-height: 200%;">
    {dict_language['note_count']} {string_parser.wrap_in_code_block(text=str(dict_file['count_note']), level='secondary')}
    </div>
    <div class="card-body" style="line-height: 200%;">
    {dict_language['percentage_pages_noted']}
    <div class="progress">
        <div class="progress-bar bg-success" role="progressbar" style="width: {dict_file['percentage_page_noted']}%;" aria-valuenow="{dict_file['percentage_page_noted']}" aria-valuemin="0" aria-valuemax="100">{dict_file['percentage_page_noted']}%</div>
    </div>
    </div>
    <div class="card-body" style="line-height: 200%;">
    {dict_language['latest_note_location_in_percentage']}
    <div class="progress">
        <div class="progress-bar bg-info" role="progressbar" style="width: {dict_file['latest_note_page']}%;" aria-valuenow="{dict_file['latest_note_page']}" aria-valuemin="0" aria-valuemax="100">{dict_file['latest_note_page']}%</div>
    </div>
    </div>
</div>
</div>
<br>
"""
