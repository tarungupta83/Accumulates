import os
import string
from math import dist as Mdist
from pathlib import Path

import fitz
from fitz.utils import getColor
from utils.documents.crop import Crop


class Annotator:
    def __init__(self):
        self.path_store = Path("store")
        self.path_cache = Path("cache")
        self.utilize_empty_right_margin = True
        self.sort_annots = True
        self.text_box_width_margin_ratio = 0.93
        self.space_between_text_boxes = 0.005

    def flatten(self, list_input):
        if len(list_input) == 0:
            return list_input
        if isinstance(list_input[0], list):
            return self.flatten(list_input[0]) + self.flatten(list_input[1:])
        return list_input[:1] + self.flatten(list_input[1:])

    def set_list_documents(self):
        list_files: list[str] = os.listdir(self.path_store)
        self.list_documents: list[str] = [i for i in list_files if i.endswith("pdf") and (not i.startswith("[A]"))]

    def forword(self):
        self.set_list_documents()
        for f in self.list_documents:
            self.annotate_file_by_name(f)

    def annotate_file_by_name(self, name_file: str):
        self.read_file(name_file)
        for i in range(self.doc.page_count):
            if list(self.doc[i].annots()):
                list_rects = self.get_rects_annots_by_page_index(i)
                list_rects.sort(key=lambda x: x[2], reverse=False)
                for rect in list_rects:
                    self.annotate_callout(list_rects=rect[0], index_page=i, text_input=rect[1])
        self.doc_cropped.save(self.path_save_output, garbage=1, deflate=True, clean=True)

    def read_file(self, name_file: str):
        path_doc_cropped: Path = self.path_cache / ("[Cropped]" + name_file)

        if not os.path.exists(path_doc_cropped):
            Crop(name_file=name_file).forward()

        self.doc = fitz.open(self.path_store / name_file)
        self.doc_cropped = fitz.open(path_doc_cropped)
        self.path_save_output = self.path_store / ("[A]" + name_file)

    def get_rects_annots_by_page_index(self, index_page: int):

        page = self.doc[index_page]
        rects = []
        append = rects.append
        for annot in list(page.annots()):
            if annot.type[0] == 8:  # highlight
                if len(annot.vertices) == 4:
                    r = [fitz.Quad(annot.vertices).rect]
                    distance_from_zero = min((self.get_distance_two_points([(i[0], i[1]), (0, 0)]) for i in r))
                    append([[fitz.Quad(annot.vertices).rect], annot.info["content"], distance_from_zero])
                else:
                    all_coordinates = [annot.vertices[x : x + 4] for x in range(0, len(annot.vertices), 4)]
                    r = [fitz.Quad(all_coordinates[i]).rect for i in range(len(all_coordinates))]
                    distance_from_zero = min((self.get_distance_two_points([(i[0], i[1]), (0, 0)]) for i in r))
                    append(
                        [
                            [fitz.Quad(all_coordinates[i]).rect for i in range(len(all_coordinates))],
                            annot.info["content"],
                            distance_from_zero
                        ]
                    )
        return rects

    def get_content_all_rects(self, page):
        content_all_rects: list = (
            page.search_for(i, quad=False) for i in "".join([string.ascii_lowercase, "1234567890"])
        )
        content_all_rects: list = list(filter(None, content_all_rects))
        return self.flatten(content_all_rects)

    def get_max_y_coord(self, page, rect_margin):
        rects_all_margin = (
            page.search_for(i, clip=rect_margin, quad=False) for i in "".join([string.ascii_lowercase, "1234567890"])
        )
        rects_all_margin = self.flatten(list(filter(None, rects_all_margin)))
        try:
            return max((i[3] for i in rects_all_margin if i in rect_margin))
        except ValueError:
            return 0

    def get_distance_two_points(self, points: "list[tuple]"):
        return Mdist(points[0], points[1])

    def check_value(self, value: float, origin: float, tolerance: float):
        if origin - tolerance <= value <= origin + tolerance:
            return True
        else:
            return False

    def draw_line(self, page, p1, p2, color):
        anno = page.add_line_annot(p1, p2)
        anno.set_colors(stroke=color)
        anno.set_opacity(0.25)
        anno.update()

    def insert_text(
        self,
        page,
        rect,
        text_input,
        size_font,
        fill,
    ):
        page.insert_textbox(
            rect,
            text_input,
            fontsize=size_font,
            fontname="helv",
            align=0,
            fill=fill,
            render_mode=0,
            stroke_opacity=1,
            fill_opacity=1,
        )

    def annotate_callout(self, list_rects: list[fitz.Rect], index_page: int, text_input: str):
        color = getColor("black")

        page_original = self.doc[index_page]
        page_cropped = self.doc_cropped[index_page]
        content_all_rects = self.get_content_all_rects(page=page_original)
        max_x_page_content = max((i[2] for i in content_all_rects)) + 6
        rect_page_margin: fitz.Rect = fitz.Rect(
            max_x_page_content, 0, page_cropped.rect.width, page_cropped.rect.height
        )
        max_y_page_content = self.get_max_y_coord(page=page_cropped, rect_margin=rect_page_margin)
        extend = (31.8, 0)
        size_font = 8

        if self.utilize_empty_right_margin:
            rect_text_box_margin = fitz.Rect(
                max_x_page_content
                + abs(page_original.rect.width - page_cropped.rect.width) * (1 - self.text_box_width_margin_ratio),
                max_y_page_content + (page_cropped.rect.height * self.space_between_text_boxes) + 15,
                page_original.rect.width
                + (page_cropped.rect.width - page_original.rect.width) * self.text_box_width_margin_ratio,
                page_cropped.rect.height,
            )
        else:
            rect_text_box_margin = fitz.Rect(
                page_original.rect.width
                + abs(page_original.rect.width - page_cropped.rect.width) * (1 - self.text_box_width_margin_ratio),
                max_y_page_content + (page_cropped.rect.height * self.space_between_text_boxes) + 15,
                page_original.rect.width
                + (page_cropped.rect.width - page_original.rect.width) * self.text_box_width_margin_ratio,
                page_cropped.rect.height,
            )

        point_text_box_margin = fitz.Point(rect_text_box_margin[0] - size_font / 2, rect_text_box_margin[1])
        list_points_all_content = [[(r[2], r[1]), (r[2], r[3])] for r in list_rects]
        list_points_all_content = self.flatten(list_points_all_content)
        list_dist_two_points = [
            self.get_distance_two_points(((point_text_box_margin), (i[0], i[1]))) for i in list_points_all_content
        ]
        point_nearest_to_point_text_box = list_points_all_content[list_dist_two_points.index(min(list_dist_two_points))]
        point_margin_border = fitz.Point(max_x_page_content, point_nearest_to_point_text_box[1])
        clip_secondary_search = fitz.Rect(
            point_nearest_to_point_text_box[0], 0, page_original.rect.width, page_original.rect.height
        )
        rects_secondary_search: list = [
            page_original.search_for(i, clip=clip_secondary_search, quad=False)
            for i in "".join([string.ascii_lowercase, "1234567890"])
        ]

        try:
            rects_inline = [i for i in rects_secondary_search if [i[1] for i in rects_secondary_search].count(i[1]) > 3]
            points_rects_inline = [(i[0], i[1]) for i in rects_inline]
            list_distance_rects_inline = [
                self.get_distance_two_points((point_nearest_to_point_text_box, p)) for p in points_rects_inline
            ]
            nearestPoint = points_rects_inline[list_distance_rects_inline.index(min(list_distance_rects_inline))]
            candidates = [
                i for i in points_rects_inline if self.check_value(value=i[0], origin=nearestPoint[0], tolerance=3)
            ]

            dict_point_zip = [
                (abs(abs(i[1] - point_text_box_margin[1]) - abs(i[1] - nearestPoint[1])), i) for i in candidates
            ]
            dict_point_zip.sort(key=lambda x: x[0], reverse=False)
            pointBridging = dict_point_zip[0][1]

            point_margin_border = (max_x_page_content, pointBridging[1])

            self.draw_line(page=page_cropped, p1=point_nearest_to_point_text_box, p2=pointBridging, color=color)
            self.draw_line(page=page_cropped, p1=pointBridging, p2=point_margin_border, color=color)
            self.draw_line(page=page_cropped, p1=point_margin_border, p2=point_text_box_margin, color=color)
            self.draw_line(page=page_cropped, p1=point_text_box_margin, p2=point_text_box_margin + extend, color=color)
        except IndexError:
            self.draw_line(page=page_cropped, p1=point_nearest_to_point_text_box, p2=point_margin_border, color=color)
            self.draw_line(page=page_cropped, p1=point_margin_border, p2=point_text_box_margin, color=color)
            self.draw_line(page=page_cropped, p1=point_text_box_margin, p2=point_text_box_margin + extend, color=color)

        self.insert_text(
            page=page_cropped,
            rect=rect_text_box_margin,
            text_input=text_input,
            size_font=size_font,
            fill=color,
        )

        try:
            while self.check_intersect(list_rects):
                list_rects = self.shrink_rects_in_list(list_rects)
        except IndexError:
            pass

        for r in list_rects:
            page_cropped.draw_rect(r, color=color, fill=color, stroke_opacity=0.2, fill_opacity=0.2)

    def check_intersect(self, list_rects: list[fitz.Rect]) -> bool:
        return list_rects[0].intersects(list_rects[1])

    def shrink_rects_in_list(self, list_rects: list[fitz.Rect]) -> bool:
        for i in range(len(list_rects)):
            list_rects[i] = fitz.Rect(list_rects[i][0], list_rects[i][1] + 1, list_rects[i][2], list_rects[i][3] - 1)
        return list_rects


if __name__ == "__main__":
    annotator = Annotator()
    annotator.forword()
