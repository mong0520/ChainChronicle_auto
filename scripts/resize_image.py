import sys
import os
from PIL import Image
"""
If you are running under MacOS, please install:
0) xcode-select --install (not sure)
1) brew install libjpeg zlib
2) pip install pillow
"""
img_path = sys.argv[1]
images = os.listdir(img_path)


for img_name in images:
    if not img_name.lower().endswith('jpg'):
        continue
    org_filename = os.path.join(img_path, img_name)
    updated_filename = os.path.join(img_path, img_name)
    print org_filename
    with Image.open(os.path.join(img_path, img_name)) as img:
        new_img = img.resize((960, 1440))
    new_img.save(updated_filename, 'jpeg')
