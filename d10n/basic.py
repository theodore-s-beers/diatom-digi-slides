import os
import shutil
import json
from datetime import datetime
from .classes import DigiSlide
from . import metadata, dij

def setup(arg):
    if os.path.isdir(arg):
        ap = os.path.abspath(arg)
        if ap.endswith('/'):
            ap = os.path.dirname(ap)

        dn = os.path.dirname(ap)
        bn = os.path.basename(ap)
        meta = bn.split('_')
        slide = meta.pop(0)
        return DigiSlide(dn, slide, meta)

def metadata_prep(ds : DigiSlide):
    metadata.make_tile_config(ds)
    metadata.make_new_dir(ds)

def convert(ds : DigiSlide):
    for z in range(ds.min_z, ds.max_z + 1):
        print(f'pane {z}: {datetime.now()}')
        dij.stitch(ds, z)
        dij.con_ome_tif(ds, z)
        dij.last_clean(ds, z)

    dij.move_metadata(ds)

def archive(ds : DigiSlide):
    shutil.make_archive(ds.new_dir, 'zip', ds.dir_name, ds.new_meta_str)
    with open(f"{ds.new_dir}.json", 'w') as f:
        json.dump(ds.simple_dict(), f)
