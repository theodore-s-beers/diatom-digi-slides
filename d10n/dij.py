import scyjava
import imagej
import os
import shutil
import subprocess
from .classes import DigiSlide

stitch_file = "img_t1_z1_c1"


def error_check(func, clean, tries, *argv):
    for i in range(tries):
        ij = imagej.init([
            'ch.epfl.biop:ijp-kheops',
            'sc.fiji:Stitching_'
            ])
        try:
            func(ij, *argv)
            return True
        except Exception as e:
            print(f"Attempt {i+1} failed because: {e}")
            if i + 1 < tries:
                clean(*argv)
            else:
                return False
        finally:
            ij.dispose()
            System = scyjava.jimport('java.lang.System')
            System.gc()

def _stitch(ij, ds : DigiSlide, z : int):
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
        f"output_directory=[{ds.new_z_dir(z)}]"
        ]
    ij.IJ.run("Grid/Collection stitching", " ".join(config))

def _clean(ds : DigiSlide, z : int):
    folder = ds.new_z_dir(z)
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
    out_path = f"{ds.new_dir}/{ds.new_z_tif(z)}"
    exist = os.path.exists(out_path)
    if not exist:
        error_check(_stitch, _clean, 3, ds, z)
        os.rename(f"{ds.new_z_dir(z)}/{stitch_file}", out_path)

def _con_ome_tif(ij, ds : DigiSlide, z : int):
    # breakpoint()
    rp_path = f'{ds.new_z_dir(z)}/raw_pyramid'
    ot_path = f'{ds.new_dir}/{ds.new_z_name(z)}.ome.tiff'
    if not os.path.exists(rp_path):
        subprocess.run([
            'bioformats2raw',
            f'{ds.new_dir}/{ds.new_z_tif(z)}',
            rp_path], check=True)
    if not os.path.exists(ot_path):
        subprocess.run([
            'raw2ometiff',
            rp_path,
            ot_path,
            '--compression',
            'JPEG-2000'], check=True)

    # Attempt 2
    #temp_dir = f"{ds.new_z_dir(z)}/temp"
    #if not os.path.exists(temp_dir):
        #os.makedirs(temp_dir)
    #if not os.path.exists(f"{ds.new_z_dir(z)}/{ds.new_z_tif(z)}"):
        #os.rename(f"{ds.new_dir}/{ds.new_z_tif(z)}", f"{ds.new_z_dir(z)}/{ds.new_z_tif(z)}")
    #config = [
        #f"input_path=[{ds.new_z_dir(z)}/{ds.new_z_tif(z)}]",
        #f"output_dir=[{temp_dir}]",
        #"compression=JPEG-2000",
        #"override_voxel_size=false"
        #]
    #ij.IJ.run(
        #"Kheops - Convert File to Pyramidal OME TIFF",
        #' '.join(config))

    # Attempt 1
    #config = [
        #f"output_dir=[{ds.new_z_dir(z)}]",
        #"compression=JPEG-2000",
        #"subset_channels=",
        #"subset_slices=",
        #"subset_frames=",
        #"compress_temp_files=false"]
    ## breakpoint()
    #imp = ij.IJ.openImage(f"{ds.new_dir}/{ds.new_z_tif(z)}")
    #ij.IJ.run(
        #imp,
        #"Kheops - Convert Image to Pyramidal OME TIFF",
        #" ".join(config))

def con_ome_tif(ds : DigiSlide, z : int):
    error_check(_con_ome_tif, _clean, 3, ds, z)
