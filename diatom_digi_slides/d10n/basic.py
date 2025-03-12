import json
import os
import shutil
from datetime import datetime

from . import dij, metadata
from .classes.digislide import DigiSlide


def setup(arg: str) -> DigiSlide:
    if not os.path.isdir(arg):
        raise ValueError(f"{arg} is not a directory")

    ap = os.path.abspath(arg)
    if ap.endswith("/"):
        ap = os.path.dirname(ap)

    dn = os.path.dirname(ap)
    bn = os.path.basename(ap)
    meta = bn.split("_")
    slide = meta.pop(0)
    return DigiSlide(dn, slide, meta)


def metadata_prep(ds: DigiSlide) -> None:
    metadata.make_tile_config(ds)
    metadata.make_new_dir(ds)


def convert(ds: DigiSlide) -> None:
    for z in range(ds.min_z, ds.max_z + 1):
        print(f"pane {z}: {datetime.now()}")
        dij.stitch(ds, z)
        dij.con_ome_tif(ds, z)
        dij.last_clean(ds, z)

    dij.move_metadata(ds)


def archive(ds: DigiSlide) -> None:
    shutil.make_archive(ds.new_dir, "zip", ds.dir_name, ds.new_meta_str)
    with open(f"{ds.new_dir}.json", "w") as f:
        json.dump(ds.simple_dict(), f)
