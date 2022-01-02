import fitz


class Debugger:
    def __init__(self):
        self.read_file()
        self.print_annots(1)
        # self.check_page(0)
        self.process_and_save()

    def read_file(self):
        self.doc = fitz.open("example.pdf")

    def print_annots(self, page: int):
        for i in self.doc[page].annots():
            info = i.info
            info["content"] = "test"
            i.set_info(info)
            print(i.info["content"])

    def check_page(self, num_page: int):
        self.page = self.doc[num_page]
        self.all_words_on_page: list[tuple] = self.page.get_text("words")
        self.rects_all_words_on_page: list[tuple] = [i[:4] for i in self.all_words_on_page]
        for r in self.rects_all_words_on_page:
            self.page.draw_rect(r, color=(0, 0, 0), fill=(0, 0, 0), overlay=True)

    def process_and_save(self):
        self.doc.save("marked_example.pdf", garbage=1, deflate=True, clean=True)


if __name__ == "__main__":
    Debugger()
