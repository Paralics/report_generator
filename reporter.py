from file_sorter import process_dir, AbsolutePath, get_dirs
from pdfgen import DefaultReportGen
import os
import re
def main(dir : AbsolutePath, output="picture.pdf", heading=None, subheading=None):
    gen = DefaultReportGen(os.path.join(dir, output))
    start_index = 1
    dirs = get_dirs(dir)
    for subdir in sorted(dirs, key=lambda x: int(re.sub(r"\D", "", x))):
        pics = process_dir(subdir, start_index=start_index)
        start_index += len(pics)
        gen.render(pics, heading=heading, subheading=subheading)
    gen.pdf.output(output)

if __name__ == "__main__":
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_dir")
    heading="Общество с ограниченной ответственностью «ПоморКом»" 
    subheading="163016, г. Архангельск, ул. Октябрьская, д.3, стр. 7, каб.1"
    main(dir, "pictures.pdf", heading, subheading)
