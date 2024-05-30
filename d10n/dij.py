import imagej
import os
import shutil
from .classes import DigiSlide
ij = imagej.init([
    'ch.epfl.biop:ijp-kheops',
    'sc.fiji:Stitching_'
    ])

def error_check(func, clean, tries, *argv):
    for i in range(tries):
        try:
            func(*argv)
            return True
        except Exception as e:
            print(f"Attempt {i} failed because: {e}")
            if i + 1 < tries:
                clean(*argv)
            else:
                return False

def _stitch(ds : DigiSlide, z : int):
    config = [
        "type=[Positions from file]",
        "order=[Defined by TileConfiguration]",
        f"directory=[{ds.data_path}]",
        f"layout_file=[TileConfiguration_{z}.txt]",
        "fusion_method=Average",
        "regression_threshold=0.30",
        "max/avg_displacement_threshold=2.50",
        "absolute_displacement_threshold=3.50",
        "computation_parameters=[Save computation time (but use more RAM)]",
        "image_output=[Write to disk]",
        f"output_directory=[{ds.new_dir}]"
        ]
    ij.IJ.run("Grid/Collection stitching", " ".join(config))

def _stitch_clean(ds : DigiSlide, z : int):
    folder = ds.new_dir
    for f in os.listdir(folder):
        f_path = os.path.join(folder, f)
        try:
            if os.path.isfile(f_path) or os.path.islink(f_path):
                os.unlink(f_path)
            elif os.path.isdir(f_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def stitch(ds : DigiSlide, z : int):
    error_check(_stitch, _stitch_clean, 3, ds, z)
