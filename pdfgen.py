from dataclasses import dataclass
from fpdf import FPDF, Align, XPos, YPos
from file_sorter import AbsolutePath, Picture, Orientation
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

_ORIENTED = (Orientation.VERY_TALL, Orientation.VERTICAL, Orientation.HORIZONTAL)

# Column counts per page pattern, tried largest-first (like the old hard-coded
# table). Very tall pictures get their own dedicated pages rendered as 3-per-
# row grids; a 3-column row therefore never holds anything but very tall pics.
# The remaining vertical/horizontal stream uses the classic 2-per-row patterns
# (vertical pages hold 4, all-horizontal pages are denser at 6) and may mix
# orientations at the V*/H* boundary, exactly like the original layout.
_PATTERNS = {
    Orientation.VERY_TALL: ((3,), (2,), (1,)),
    Orientation.VERTICAL: ((2, 2), (2, 1), (1, 1), (1,)),
    Orientation.HORIZONTAL: ((2, 2, 2), (2, 2, 1), (2, 2), (2, 1), (1, 1), (1,)),
}

def plan_pages(counts : tp.Dict[Orientation, int]) -> tp.List[tp.Tuple[int, ...]]:
    """Folds the sorted VT* V* H* stream into page patterns of row column-counts."""
    pages : tp.List[tp.Tuple[int, ...]] = []

    vt = counts[Orientation.VERY_TALL]
    while vt:
        pattern = next(p for p in _PATTERNS[Orientation.VERY_TALL] if sum(p) <= vt)
        pages.append(pattern)
        vt -= sum(pattern)

    rem_v, rem_h = counts[Orientation.VERTICAL], counts[Orientation.HORIZONTAL]
    while rem_v or rem_h:
        total = rem_v + rem_h
        if rem_v:
            patterns = _PATTERNS[Orientation.VERTICAL]
        else:
            patterns = _PATTERNS[Orientation.HORIZONTAL]
        pattern = next(p for p in patterns if sum(p) <= total)
        pages.append(pattern)
        need = sum(pattern)
        take = min(rem_v, need)
        rem_v -= take
        rem_h -= need - take
    return pages

def rows_for_page(pattern : tp.Tuple[int, ...]) -> tp.List[Row]:
    rows = [Row(n_cols=c) for c in pattern]
    if sum(pattern) == 1:
        rows[0].extra_margin = 20
    return rows

class DefaultReportGen(ReportGenerator):
    def render(
        self,
        pics : tp.List[Picture],
        v_space_between : int = 10,
        v_offset : int = 3,
        heading : str | None = None,
        subheading : str | None = None
    ) -> None:
        # assume pics are sorted very tall first, then vertical, then horizontal
        counts = {o: sum(1 for p in pics if p.orientation == o) for o in _ORIENTED}
        for pattern in plan_pages(counts):
            rows = rows_for_page(pattern)

            self.pdf.add_page()
            if heading:
                self.pdf.cell(text=heading, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT, center=True)
            if subheading:
                self.pdf.cell(text=subheading, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT, center=True)

            y = self.pdf.get_y() + v_offset
            n_rows = len(rows)
            picture_height = (self.pdf.h - y - self.pdf.b_margin - n_rows * v_space_between - v_offset) / n_rows
            for row in rows:
                x = self.pdf.l_margin + row.extra_margin
                picture_width = (self.pdf.w - self.pdf.l_margin - self.pdf.r_margin - 
                    (row.n_cols - 1) * row.space_between - 2 * row.extra_margin) / row.n_cols
                for col in range(row.n_cols):
                    pic = pics.pop(0)
                    image = self.pdf.image(x=x, y=y, name=pic.path, h=picture_height, w=picture_width, keep_aspect_ratio=True)
                    if pic.name:
                        actual_y = y + image.rendered_height - (image.rendered_height - picture_height) / 2 + v_offset
                        self.pdf.set_xy(x, actual_y)
                        self.pdf.cell(text=pic.name, align=Align.C, w=picture_width)
                    x += picture_width + row.space_between
                y += v_space_between + picture_height
