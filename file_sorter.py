import os
from uuid import uuid4
from PIL import Image, ImageOps
from collections.abc import Callable
import typing as tp
from dataclasses import dataclass
from enum import Enum, auto

type AbsolutePath = str

PICTURE_FORMATS = ['.png', '.jpg', '.jpeg']
VERY_TALL_ASPECT_RATIO = 2.0

class Orientation(Enum):
    VERY_TALL = auto()
    VERTICAL = auto()
    HORIZONTAL = auto()

@dataclass
class Picture:
    path : AbsolutePath
    name : str | None
    dimensions : tp.Tuple[int, int]
    orientation : Orientation

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

def classify(width: int, height: int) -> Orientation:
    if width >= height:
        return Orientation.HORIZONTAL
    if height / width >= VERY_TALL_ASPECT_RATIO:
        return Orientation.VERY_TALL
    return Orientation.VERTICAL

def process_dir(
    base_dir : AbsolutePath, 
    start_index : int = 1, 
    naming_pattern : Callable[[int], str] = _default_naming_pattern
) -> tp.List[Picture]:
    """
    Sorts pics in directory (very tall first, then vertical, then horizontal)
    Renames them according to a naming pattern ("Фото n.extension" by default)
    Handles exif rotations (apparently fpdf2 does not)
    """
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"No such directory: {base_dir}")
    elif not os.path.isdir(base_dir):
        raise NotADirectoryError(f"Not a directory: {base_dir}")

    _, dir_name = os.path.split(base_dir)
    source = get_pics(base_dir)

    groups : tp.Dict[Orientation, tp.List[AbsolutePath]] = {
        o: [] for o in (Orientation)
    }
    for pic in source:
        if not os.path.exists(pic):
            raise FileNotFoundError(f"File deleted mid execution: {pic}")
        with Image.open(pic) as img:
            ImageOps.exif_transpose(img, in_place=True)
            groups[classify(*img.size)].append(pic)

    ordered = sum([groups[i] for i in Orientation], start=[])

    pictures : tp.List[Picture] = []
    for pos, pic in enumerate(ordered):
        with Image.open(pic) as img:
            ImageOps.exif_transpose(img, in_place=True)

            _, extension = os.path.splitext(pic)
            new_name = naming_pattern(start_index + pos)
            new_path = os.path.join(base_dir, new_name + extension)
            pictures.append(Picture(
                path=new_path, 
                name=f"{dir_name}. {new_name}", 
                orientation=classify(*img.size), 
                dimensions=img.size
            ))

            if os.path.exists(new_path):
                same_name_i = ordered.index(new_path)
                swap_name = os.path.join(base_dir, f"{uuid4()}{extension}")
                if same_name_i == pos:
                    pic = swap_name
                ordered[same_name_i] = swap_name
                os.rename(new_path, swap_name)
            img.save(new_path)
            os.remove(pic)

    return pictures

