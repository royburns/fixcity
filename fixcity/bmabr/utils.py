from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_info(img):
    """
    Get EXIF information from a PIL.Image instance.
    Found this code at:
    http://wolfram.kriesing.de/blog/index.php/2006/reading-out-exif-data-via-python
    """
    result = {}
    try:
        info = img._getexif() or {}
    except AttributeError:
        info = {}
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        result[decoded] = value
    return result

def rotate_image_by_exif(img):
    """
    Rotate a PIL.Image instance according to its EXIF rotation information.

    Based on code from: http://stackoverflow.com/questions/1606587/how-to-use-pil-to-resize-and-apply-rotation-exif-information-to-the-file

    NOTE, this is a LOSSY transformation. Probably fine for our
    purposes.  We could use something like
    http://ebiznisz.hu/python-jpegtran/ if we change our minds about
    that.

    XXX Now we just need to write migration code like so:

>>> from fixcity.bmabr.utils import *
>>> from fixcity.bmabr.models import *
>>> r  = Rack.objects.get(id=163)
>>> r.photo.path
'/home/pw/builds/fixcity/builds/20091211/src/fixcity/fixcity/uploads/images/racks/IMG_0080.JPG'
>>> rotated = rotate_image_by_exif(Image.open(r.photo.path))
>>> rotated
<PIL.Image.Image instance at 0x2c01dd0>
>>> rotated.show()

    XXX what to do on upload? and where to do it? a clean method?
    
    """
    exif_info = get_exif_info(img)
    # We rotate regarding to the EXIF orientation information
    orientation = exif_info.get('Orientation', 1)
    if orientation == 1:
        rotated = img
    elif orientation == 2:
        # Vertical Mirror
        rotated = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        # Rotation 180
        rotated = img.transpose(Image.ROTATE_180)
    elif orientation == 4:
        # Horizontal Mirror
        rotated = img.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        # Horizontal Mirror + Rotation 270
        rotated = img.transpose(Image.FLIP_TOP_BOTTOM).transpose(
            Image.ROTATE_270)
    elif orientation == 6:
        # Rotation 270
        rotated = img.transpose(Image.ROTATE_270)
    elif orientation == 7:
        # Vertical Mirror + Rotation 270
        rotated = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(
            Image.ROTATE_270)
    elif orientation == 8:
        # Rotation 90
        rotated = img.transpose(Image.ROTATE_90)
    else:
        # unknown? do nothing.
        rotated = img

    return rotated

