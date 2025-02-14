import sys
from datetime import datetime

from d10n.basic import archive, convert, metadata_prep, setup
from d10n.classes.digislide import DigiSlide

# Notes from Theo on getting this to run:
# - pyimagej installed as Python dep via uv (see pyproject.toml)
# - Need Java installation (I chose openjdk-17-jre-headless)
# - Need Maven (just `apt install maven`)
# - Need bioformats2raw and raw2ometiff, downloaded from GitHub
# - Those binaries (with their deps) are in my home folder
# - I put scripts in /usr/local/bin to call the binaries

# Other notes from Theo:
# - Script takes one arg, a directory path
# - That dir should *not* be at the bottom level, but one up
# - Script wants a dir that contains another dir by the same name
# - Output consists of a new dir with combined images,
#   a zip of that same dir, and a JSON file with metadata


def main() -> None:
    print(f"start: {datetime.now()}")
    ds: DigiSlide = setup(sys.argv[1])
    metadata_prep(ds)
    convert(ds)
    archive(ds)
    print(f"stop: {datetime.now()}")


if __name__ == "__main__":
    main()
