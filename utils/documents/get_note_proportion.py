import os
from pathlib import Path

import fitz
import pandas
from natsort import natsorted


class GetNoteProportion:
    def __init__(self):
        self.path_store: Path = Path("store")
        self.set_list_documents()
        self.set_dataframes()

    def set_list_documents(self) -> list[str]:
        list_files_all: list[str] = os.listdir(self.path_store)
        self.list_files_document: list[str] = [
            i for i in list_files_all if i.endswith("pdf") and (not i.startswith("[A]"))
        ]
        self.list_files_document.sort()

    def set_dataframes(self):
        dataframe_count_notes = pandas.DataFrame(
            index=pandas.Index(["count"], name="count"),
            columns=pandas.Index(self.list_files_document, name="document"),
        )

        dataframe_percentage_noted = pandas.DataFrame(
            index=pandas.Index(["percentage"], name="percentage"),
            columns=pandas.Index(self.list_files_document, name="document"),
        )

        dataframe_location_max_page = pandas.DataFrame(
            index=pandas.Index(["percentage"], name="percentage"),
            columns=pandas.Index(self.list_files_document, name="document"),
        )

        for d in self.list_files_document:
            dataframe_count_notes.at["count", d] = self.get_count_notes_total_by_name(d)
            dataframe_percentage_noted.at["percentage", d] = self.get_percentage_pages_noted_by_name(d)
            dataframe_location_max_page.at["percentage", d] = self.get_location_page_last_note_by_name(d)

        dataframe_count_notes = self.reindex(dataframe_count_notes.transpose())
        dataframe_percentage_noted = self.reindex(dataframe_percentage_noted.transpose())
        dataframe_location_max_page = self.reindex(dataframe_location_max_page.transpose())

        self.list_dict_notes_stats: list[dict] = [
            {
                "file": i,
                "count_note": dataframe_count_notes.at[i, "count"],
                "percentage_page_noted": dataframe_percentage_noted.at[i, "percentage"],
                "latest_note_page": dataframe_location_max_page.at[i, "percentage"],
            }
            for i in self.list_files_document
        ]
        self.list_dict_notes_stats = natsorted(self.list_dict_notes_stats, key=lambda d: d["file"])

    def reindex(self, df: pandas.DataFrame) -> pandas.DataFrame:
        return df.reindex(index=[x for _, x in natsorted(zip([i for i in df.index], df.index))])

    def get_count_notes_total_by_name(self, name_document: str):
        doc = fitz.open(self.path_store / name_document)
        list_count_notes_all_pages = ((lambda i: len(list(doc[i].annots())))(i) for i in range(doc.page_count))
        return sum(list_count_notes_all_pages)

    def get_percentage_pages_noted_by_name(self, name_document: str):
        doc = fitz.open(self.path_store / name_document)
        list_bool_noted: list[bool] = [(lambda i: not list(doc[i].annots()))(i) for i in range(doc.page_count)]
        count_pages_noted: int = doc.page_count - sum(list_bool_noted)
        return round(count_pages_noted * 100 / doc.page_count, 2)

    def get_location_page_last_note_by_name(self, name_document: str):
        doc = fitz.open(self.path_store / name_document)
        list_bool_noted: list[bool] = [(lambda i: not list(doc[i].annots()))(i) for i in range(doc.page_count)]
        list_bool_noted = [not i for i in list_bool_noted]
        index_last_true = [i for i, x in enumerate(list_bool_noted) if x]
        if index_last_true == []:
            index_last_true = 0
        else:
            index_last_true = max(index_last_true) + 1
        return round(index_last_true * 100 / doc.page_count, 2)


if __name__ == "__main__":
    get_note_proportion = GetNoteProportion()
    print(get_note_proportion.dataframe_location_max_page)
