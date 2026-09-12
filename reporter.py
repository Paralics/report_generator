from file_sorter import process_dir, AbsolutePath, get_dirs, get_pics
from pdfgen import DefaultReportGen
import os
import re
from collections.abc import Callable

def main(
    dir : AbsolutePath,
    output="picture.pdf",
    heading=None,
    subheading=None,
    progress : Callable[[int, int], None] | None = None
):
    gen = DefaultReportGen(os.path.join(dir, output))
    start_index = 1
    dirs = sorted(get_dirs(dir), key=lambda x: int(re.sub(r"\D", "", x)))
    weights = [len(get_pics(subdir)) for subdir in dirs]
    total = sum(weights)
    if progress is not None:
        progress(0, total)
    done = 0
    for w, subdir in zip(weights, dirs):
        pics = process_dir(subdir, start_index=start_index)
        start_index += len(pics)
        gen.render(pics, heading=heading, subheading=subheading)
        done += w
        if progress is not None:
            progress(done, total)
    gen.pdf.output(output)

if __name__ == "__main__":
    dir = input("Выбирете директорию: ")
    heading="Общество с ограниченной ответственностью «ПоморКом»" 
    subheading="163016, г. Архангельск, ул. Октябрьская, д.3, стр. 7, каб.1"
    main(dir, "pictures.pdf", heading, subheading)
