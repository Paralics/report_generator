import os
from uuid import uuid4
from PIL import Image, ImageOps
from collections.abc import Callable
import typing as tp
from dataclasses import dataclass

type AbsolutePath = str

PICTURE_FORMATS = ['.png', '.jpg', '.jpeg']

@dataclass
class Picture:
    path : AbsolutePath
    name : str | None
    dimensions : tp.Tuple[int, int]
    is_horizontal : bool

def _is_pic(filename: AbsolutePath) -> bool:
    _, extension = os.path.splitext(filename)
    return extension in PICTURE_FORMATS

def get_pics(dir: AbsolutePath) -> tp.List[AbsolutePath]:
    # it seems like a good idea to throw if folder is not image-only
    # but I decided to extract only the pics instead 
    # because thumbs.db and maybe notes/other things
    return [os.path.join(dir, file) for file in os.listdir(dir) if _is_pic(file)]

def get_dirs(base_dir: AbsolutePath) -> tp.List[AbsolutePath]:
    return list(filter(os.path.isdir, [os.path.join(base_dir, dir) for dir in os.listdir(base_dir)]))

def _default_naming_pattern(id: int) -> str:
    return f"Фото {id}"

def process_dir(
    base_dir : AbsolutePath, 
    start_index : int = 1, 
    naming_pattern : Callable[[int], str] = _default_naming_pattern
) -> tp.List[Picture]:
    """
    Sorts pics in directory (first vertical, then horizontal)
    Renames them according to a naming pattern ("Фото n.extension" by default)
    Handles exif rotations (apparently fpdf2 does not)
    """
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"No such directory: {base_dir}")
    elif not os.path.isdir(base_dir):
        raise NotADirectoryError(f"Not a directory: {base_dir}")

    _, dir_name = os.path.split(base_dir)
    pics = get_pics(base_dir)

    n_pics = len(pics)
    horizontals = []
    verticals = []

    for pic_i, pic in enumerate(pics):
        if not os.path.exists(pic):
            raise FileNotFoundError(f"File deleted mid execution: {pic}")

        with Image.open(pic) as img:
            ImageOps.exif_transpose(img, in_place=True)

            _, extension = os.path.splitext(pic)
            if img.width < img.height:
                id = len(verticals) + start_index
                is_horizontal = False
            else:
                id = n_pics - len(horizontals) + start_index - 1
                is_horizontal=True
            new_name = naming_pattern(id)
            new_path = os.path.join(base_dir, new_name + extension)
            picture = Picture(
                path=new_path, 
                name=f"{dir_name}. {new_name}", 
                is_horizontal=is_horizontal, 
                dimensions=img.size
            )

            if is_horizontal:
                horizontals.insert(0, picture)
            else:
                verticals.append(picture)

            if os.path.exists(new_path):
                same_name_i = pics.index(new_path)
                swap_name = os.path.join(base_dir, f"{uuid4()}{extension}")
                if same_name_i == pic_i:
                    pic = swap_name
                pics[same_name_i] = swap_name
                os.rename(new_path, swap_name)
            img.save(new_path)
            os.remove(pic)

    return verticals + horizontals

