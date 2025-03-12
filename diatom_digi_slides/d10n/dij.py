import csv
import os
import shutil
import subprocess

import imagej  # type: ignore
import scyjava  # type: ignore

from .classes.digislide import DigiSlide

stitch_file = "img_t1_z1_c1"


def error_check(func, clean, tries, *argv):
    for i in range(tries):
        ij = imagej.init(["ch.epfl.biop:ijp-kheops", "sc.fiji:Stitching_"])
        try:
            func(ij, *argv)
            return True
        except Exception as e:
            print(f"Attempt {i + 1} failed because: {e}")
            if i + 1 < tries:
                clean(*argv)
            else:
                return False
        finally:
            ij.dispose()
            System = scyjava.jimport("java.lang.System")
            System.gc()


def _stitch(ij, ds: DigiSlide, z: int):
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
        f"output_directory=[{ds.new_z_dir(z)}]",
    ]
    ij.IJ.run("Grid/Collection stitching", " ".join(config))


def _clean(ds: DigiSlide, z: int):
    folder = ds.new_z_dir(z)
    for f in os.listdir(folder):
        f_path = os.path.join(folder, f)
        try:
            if os.path.isfile(f_path) or os.path.islink(f_path):
                os.unlink(f_path)
            elif os.path.isdir(f_path):
                shutil.rmtree(f_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (f_path, e))


def stitch(ds: DigiSlide, z: int):
    out_path = f"{ds.new_dir}/{ds.new_z_tif(z)}"
    ome_path = f"{ds.new_dir}/{ds.new_z_name(z)}.ome.tiff"
    exist = os.path.exists(out_path) or os.path.exists(ome_path)
    if not exist:
        error_check(_stitch, _clean, 3, ds, z)
        os.rename(f"{ds.new_z_dir(z)}/{stitch_file}", out_path)


def _con_ome_tif(ij, ds: DigiSlide, z: int):
    rp_path = f"{ds.new_z_dir(z)}/raw_pyramid"
    ot_path = f"{ds.new_dir}/{ds.new_z_name(z)}.ome.tiff"
    max_workers = 4
    try:
        Runtime = scyjava.jimport("java.lang.Runtime")

        runtime = Runtime.getRuntime()
        res = runtime.availableProcessors()
        if res > max_workers:
            max_workers = res
    except ImportError:
        pass
    except IOError:
        pass
    if not os.path.exists(rp_path) and not os.path.exists(ot_path):
        subprocess.run(
            [
                "bioformats2raw",
                f"{ds.new_dir}/{ds.new_z_tif(z)}",
                rp_path,
                "--max_workers",
                str(max_workers),
            ],
            check=True,
        )
    if not os.path.exists(ot_path):
        subprocess.run(
            [
                "raw2ometiff",
                rp_path,
                ot_path,
                "--compression",
                "JPEG-2000",
                "--max_workers",
                str(max_workers),
            ],
            check=True,
        )


def con_ome_tif(ds: DigiSlide, z: int) -> None:
    error_check(_con_ome_tif, _clean, 3, ds, z)
    _clean(ds, z)


def last_clean(ds: DigiSlide, z: int) -> None:
    dir_path = ds.new_z_dir(z)
    old_path = f"{ds.new_dir}/{ds.new_z_tif(z)}"
    if os.path.isfile(old_path) or os.path.islink(old_path):
        os.unlink(old_path)
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


def move_metadata(ds: DigiSlide) -> None:
    new_xyz = f"{ds.new_dir}/XYZPositions.csv"
    new_sws = f"{ds.new_dir}/{ds.new_meta_str}.sws"

    if not os.path.exists(new_xyz):
        with open(ds.xy_path, newline="", encoding="utf_16_le") as old_csvf:
            r = csv.DictReader(old_csvf, delimiter=",", skipinitialspace=True)
            fieldnames = r.fieldnames
            if not fieldnames:
                raise ValueError("No CSV field names found")

            with open(new_xyz, "w", newline="") as new_csvf:
                writer = csv.DictWriter(new_csvf, fieldnames=fieldnames)
                writer.writeheader()

                for row in r:
                    writer.writerow(row)

    if not os.path.exists(new_sws):
        shutil.copyfile(ds.sws_path, new_sws)
