import sys
from d10n import *
from datetime import datetime

# Need to install mamba, pyimagej, and then bioformats2raw, and raw2ometiff in pyimagej side of mamba

# breakpoint()
print(f'start: {datetime.now()}')
ds : DigiSlide = setup(sys.argv[1])
metadata_prep(ds)
convert(ds)
archive(ds)
print(f'stop: {datetime.now()}')
