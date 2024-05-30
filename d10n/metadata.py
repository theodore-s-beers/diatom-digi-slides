import csv
import os
from .classes import DigiSlide

def make_tile_config(ds : DigiSlide):
    im_coords = []
    layers = {}
    x_min = None
    y_min = None
    w_scale = None
    h_scale = None
    with open(ds.xy_path, newline='', encoding="utf_16_le") as csvfile:
        r = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        r.__next__()
        for row in r:
            # breakpoint()
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
            coord = [f"Tile{int(row[0]):06d}.tif", x_curr, y_curr]
            if z_curr not in layers:
                layers[z_curr] = []
            layers[z_curr].append(coord)

    # breakpoint()
    for k, v in layers.items():
        with open(ds.tc_path(k), 'w') as f:
            f.write("dim = 2\n")
            for coord in v:
                f.write(
                    f"{coord[0]}; ; ({round((coord[1] - x_min) * w_scale)}, {round((coord[2] - y_min) * h_scale)})\n")

def make_new_dir(ds : DigiSlide):
    if not os.path.exists(ds.new_dir):
        os.makedirs(ds.new_dir)
