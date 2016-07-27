import sys
import os
from PIL import Image
import time

img_path = sys.argv[1]

images = os.listdir(img_path)
for img_name in images:
    with Image.open(os.path.join(img_path, img_name)) as img:
        print "Resize: {0}".format(img_name)
        nim = img.resize((960, 1440), Image.BILINEAR )
    nim.save(os.path.join(img_path, img_name))

    # to avoid hang issue
    time.sleep(0.5)

