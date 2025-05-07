import json
import os
import shutil
from datetime import datetime

from . import dij, metadata
from .classes.digislide import DigiSlide


def setup(args: list[str]) -> DigiSlide:
    if not os.path.isdir(args[0]):
        raise ValueError(f"{args[0]} is not a directory")

    ap = os.path.abspath(args[0])
    dn, bn = os.path.split(ap)
    meta = bn.split("_")
    slide = meta.pop(0)

    ext = "tiff" if len(args) > 1 and args[1] == "--tiff" else "tif"

    return DigiSlide(dn, slide, meta, ext)


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
    # Zip output
    shutil.make_archive(ds.new_dir, "zip", ds.dir_name, ds.new_meta_str)

    # Generate JSON metadata
    with open(f"{ds.new_dir}.json", "w") as f:
        json.dump(ds.simple_dict(), f)

    # Delete output directory (not needed once zipped)
    shutil.rmtree(ds.new_dir)
