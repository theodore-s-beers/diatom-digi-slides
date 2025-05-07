import csv
import os
from typing import Optional

from .classes.digislide import DigiSlide


def make_tile_config(ds: DigiSlide) -> None:
    layers: dict[int, list[tuple[str, float, float]]] = {}

    x_min: Optional[float] = None
    y_min: Optional[float] = None

    w_scale: Optional[float] = None
    h_scale: Optional[float] = None

    with open(ds.xy_path, newline="", encoding="utf_16_le") as csvfile:
        r = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
        next(r)

        for row in r:
            x_curr = float(row[1])
            y_curr = float(row[2])
            z_curr = int(row[7])

            if not w_scale:
                w_scale = float(row[10]) / float(row[8])
            if not h_scale:
                h_scale = float(row[11]) / float(row[9])

            if not x_min or x_curr < x_min:
                x_min = x_curr
            if not y_min or y_curr < y_min:
                y_min = y_curr

            coord = (f"Tile{int(row[0]):06d}.{ds.tile_ext}", x_curr, y_curr)
            layers.setdefault(z_curr, []).append(coord)

    if not x_min or not y_min:
        raise ValueError("x_min or y_min not set from CSV data")
    if not w_scale or not h_scale:
        raise ValueError("w_scale or h_scale not set from CSV data")

    for k, v in layers.items():
        with open(ds.tc_path(k), "w") as f:
            f.write("dim = 2\n")

            for coord in v:
                f.write(
                    f"{coord[0]}; ; ({round((coord[1] - x_min) * w_scale)}, {round((coord[2] - y_min) * h_scale)})\n"
                )


def make_new_dir(ds: DigiSlide):
    if not os.path.exists(ds.new_dir):
        os.makedirs(ds.new_dir)

    for z in range(ds.min_z, ds.max_z + 1):
        z_dir = ds.new_z_dir(z)
        if not os.path.exists(z_dir):
            os.makedirs(z_dir)
