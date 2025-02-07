import sys
from datetime import datetime

from d10n.basic import archive, convert, metadata_prep, setup
from d10n.classes.digislide import DigiSlide

# Need to install mamba, pyimagej, and then bioformats2raw, and raw2ometiff in pyimagej side of mamba


def main() -> None:
    print(f"start: {datetime.now()}")
    ds: DigiSlide = setup(sys.argv[1])
    metadata_prep(ds)
    convert(ds)
    archive(ds)
    print(f"stop: {datetime.now()}")


if __name__ == "__main__":
    main()
