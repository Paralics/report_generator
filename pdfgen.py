from dataclasses import dataclass
from fpdf import FPDF, Align, XPos, YPos
from file_sorter import AbsolutePath, Picture
from math import ceil
from abc import ABC, abstractmethod
import typing as tp
import os

class ReportGenerator(ABC):
    def __init__(
        self,
        output : AbsolutePath,
        font_path: AbsolutePath | None = None,
        font_name : None | str = None
    ):
        self.output = output

        if not font_name:
            font_name = "FontName"

        if not font_path:
            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts/times.ttf")

        self.pdf = FPDF()
        self.pdf.add_font(font_name, fname=font_path)
        self.pdf.set_font(font_name)

    @abstractmethod
    def render(self, pics : tp.List[Picture]) -> None:
        pass

    def finish(self):
        self.pdf.output(self.output)

@dataclass
class Row:
    n_cols : int
    space_between : int = 10
    extra_margin : int = 0

@dataclass
class Testlation:
    n_pics : int
    n_vertical : int | None
    rows : tp.List[Row]

ALL_HORIZONTAL = Testlation(6, 0, [Row(n_cols=2) for _ in range(3)])
INCOMPLETE_HORIZONTAL = Testlation(5, 0, [Row(n_cols=2), Row(n_cols=2), Row(n_cols=1)])
DEFAULT = Testlation(4, None, [Row(n_cols=2) for _ in range(2)])
TWO_PICS = Testlation(2, None, [Row(n_cols=1) for _ in range(2)])
SINGLE_PIC = Testlation(1, None, [Row(n_cols=1, extra_margin=20)])


class DefaultReportGen(ReportGenerator):
    def render(
        self, 
        pics : tp.List[Picture], 
        patterns : tp.List[Testlation]=[ALL_HORIZONTAL, INCOMPLETE_HORIZONTAL, DEFAULT, TWO_PICS, SINGLE_PIC], 
        v_space_between : int = 10,
        heading : str | None = None,
        subheading : str | None = None
    ) -> None:
        while pics:
            # select pattern for the page
            rows = None
            for pattern in patterns:
                # assume list to be sorted vertical first then horizontal
                if len(pics) < pattern.n_pics:
                    continue
                if pattern.n_vertical is not None:
                    right_check = pattern.n_vertical
                    left_check = right_check - 1
                    if not (right_check >= len(pics) or pics[right_check].is_horizontal):
                        continue
                    if not (left_check < 0 or not pics[left_check].is_horizontal):
                        continue
                rows = pattern.rows
                break

            if not rows:
                raise ValueError(f"No pattern fits: {pics} {patterns}")

            self.pdf.add_page()
            if heading:
                self.pdf.cell(text=heading, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT, center=True)
            if subheading:
                self.pdf.cell(text=subheading, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT, center=True)

            y = self.pdf.get_y()
            n_rows = len(rows)
            picture_height = (self.pdf.h - y - self.pdf.b_margin - n_rows * v_space_between) / n_rows
            for row in rows:
                x = self.pdf.l_margin + row.extra_margin
                picture_width = (self.pdf.w - self.pdf.l_margin - self.pdf.r_margin - 
                    (row.n_cols - 1) * row.space_between - 2 * row.extra_margin) / row.n_cols
                for col in range(row.n_cols):
                    pic = pics.pop(0)
                    image = self.pdf.image(x=x, y=y, name=pic.path, h=picture_height, w=picture_width, keep_aspect_ratio=True)
                    if pic.name:
                        actual_y = y + image.rendered_height - (image.rendered_height - picture_height) / 2 
                        self.pdf.set_xy(x, actual_y)
                        self.pdf.cell(text=pic.name, align=Align.C, w=picture_width)
                    x += picture_width + row.space_between
                y += v_space_between + picture_height

if __name__ == "__main__":
    from file_sorter import process_dir
    pics = process_dir("/home/ivan/projects/pdf_generator/test_dir/03.Фундамент АМС")
    gen1 = DefaultReportGen("test.pdf")
    gen1.render(
        pics,
        heading="Общество с ограниченной ответственностью «ПоморКом»", 
        subheading="163016, г. Архангельск, ул. Октябрьская, д.3, стр. 7, каб.1",
    )
    gen1.finish()

            
