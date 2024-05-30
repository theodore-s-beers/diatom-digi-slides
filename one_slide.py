import sys
from d10n import *

# breakpoint()
ds : DigiSlide = setup(sys.argv[1])
metadata_prep(ds)
convert(ds)
