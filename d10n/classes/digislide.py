import re
import csv

class DigiSlide:
    def __init__(self, dir_name, slide, metadata):
        self.dir_name = dir_name
        self.slide = slide
        self.sample = metadata[0]
        self.metadata = metadata
        self.orig_meta_str = f"{slide}_{'_'.join(metadata)}"
        self.path = f"{dir_name}/{self.orig_meta_str}"
        self.sws_path = f"{self.path}/{self.orig_meta_str}.sws"
        self.data_path = f"{self.path}/{self.orig_meta_str}"
        self.xy_path = f"{self.data_path}/XYZPositions.txt"
        self.min_z = 0
        self.max_z = 0
        self.zoom = None
        self.illumination = None
        self.z_dist = None
        self._z_stack()
        self._parse_meta()
        short_meta = [self.zoom, self.illumination, f"{(self.max_z - self.min_z + 1):02d}z"]
        self.short_meta = filter(bool, short_meta)
        self.new_meta_str = f"{slide}_{'_'.join(short_meta)}"
        self.new_dir = f"{dir_name}/{self.new_meta_str}"

    def tc_path(self, layer):
        return f"{self.data_path}/TileConfiguration_{layer}.txt"

    def new_z_name(self, z):
        z_norm = z - self.min_z + 1
        return f"{self.new_meta_str}_Z{(z_norm):02d}"

    def new_z_dir(self, z):
        z_norm = z - self.min_z + 1
        return f"{self.new_dir}/{self.new_z_name(z)}"

    def new_z_tif(self, z):
        z_norm = z - self.min_z + 1
        return f"{self.new_z_name(z)}.tif"

    def _z_stack(self):
        with open(self.xy_path, newline='', encoding="utf_16_le") as csvfile:
            r = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
            next(r)
            z_found = set()
            for row in r:
                z = int(row[7])
                if z in z_found:
                    break

                if z < self.min_z:
                    self.min_z = z

                if z > self.max_z:
                    self.max_z = z

                z_found.add(z)

    def _parse_meta(self):
        for field in self.metadata:
            if re.fullmatch(r'[A-Z]{2,4}', field):
                self.illumination = field
            elif re.fullmatch(r'\d{2}x', field):
                self.zoom = field
            elif re.fullmatch(r'\d*\.?\d*um', field):
                self.z_dist = field

    def simple_dict(self):
        return {
            "slideID": self.slide,
            "sampleID": self.sample,
            "min_z": self.min_z,
            "max_z": self.max_z,
            "num_z": (self.max_z - self.min_z + 1),
            "magnification": self.zoom,
            "illumination": self.illumination,
            "z_distance": self.z_dist,
            "original_metadata": self.orig_meta_str
            }

