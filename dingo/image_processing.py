"""This contains all the functionality for image manipulation.
"""
from __future__ import division
import cStringIO as StringIO
import os
import sys

from lipstick.utils import transform_exception
from PIL import Image, ExifTags
import requests

from .exceptions import ImageException


class ImageTransform(object):
  """Just a container class for organizing an image transform.
    Pretty bare-bones, but slightly more reliable than a dict.
  """
  def __init__(self, name, width, height, fit_type, min_height=None,
      max_height=None, transparency_mask_file=None):
    self.name = name
    self.width = width
    self.height = height
    self.apsect = sys.maxint
    self.fit_type = fit_type
    self.min_height = min_height
    self.max_height = max_height
    self.transparency_mask_file = transparency_mask_file

  @property
  def aspect(self):
    try:
      _aspect = self.width / self.height
    except ZeroDivisionError:
      _aspect = sys.maxint
    return _aspect


def process_image(image_file, transform):
  """given a file-like object and an image transform definition, resize
  the image and return a new file-like object as well as the encoding.
  """
  # go to the start of the image file if we're not there already
  image_file.seek(0)
  # load the file into a PIL image object
  with transform_exception(ImageException, exceptions=(IOError,)):
    im = Image.open(image_file)

  im = _upright_image(im)
  orig_width, orig_height = im.size
  orig_format = im.format
  if im.mode == "P":
    im.convert("RGB")
  # going to build a switch statement here, so shorten our 'case' variable
  if transform.fit_type == "fitwidth":
    # we make the width to whatever's specified and the height ends between
    # min_height and max_height, if specified.
    # First, let's calculate what the height would be if we did the transform.
    scale = transform.width / orig_width
    potential_height = scale * orig_height

    if potential_height < transform.min_height:
      # scale height to min_height, then crop the sides to width.
      im = _resize_image(im, None, transform.min_height)
      im = _crop_image(im, transform.width, transform.min_height)
    elif potential_height > transform.max_height:
      # scale the image to the right width, then crop the top and bottom.
      im = _resize_image(im, transform.width, None)
      im = _crop_image(im, transform.width, transform.max_height)
    else:
      # piece of cake, we're not in trouble in terms of cropping
      im = _resize_image(im, transform.width, None)

  elif transform.fit_type in ("crop", "zoomcrop"):
    # scale, then crop the excess.
    # first apply the correct scale.
    orig_aspect = orig_width / orig_height
    new_aspect = transform.width / transform.height
    if orig_aspect > new_aspect:
      # it's too wide for the new aspect ratio, fit height then crop.
      im = _resize_image(im, None, transform.height)
    else:
      # it's too tall (or exactly right), so we fit width then crop.
      im = _resize_image(im, transform.width, None)
    # crop it!
    im = _crop_image(im, transform.width, transform.height)

  elif transform.fit_type == "limitwidth":
    # width can be between 0 and the width specified, height scaled.
    if orig_width > transform.width:
      im = _resize_image(im, transform.width, None)
  else:
    message = "transform type %s not handled." % transform.fit_type
    raise ValueError(message)

  # now shove it in a stringio buffer and return it.
  if transform.transparency_mask_file is not None:
    im = _apply_transparency_mask(im, transform.transparency_mask_file)
  content = StringIO.StringIO()
  # write it as a jpg, or if we added transparency, as a png.
  fmt = orig_format
  if transform.transparency_mask_file:
    fmt = "PNG"
  im.save(content, format=fmt)
  content.seek(0)
  return content, fmt


def _resize_image(im, width, height):
  """resize an image to exactly a new width and height, if both are specified.
     If one is null, it's whatever the image comes out to after scaling to the
     other.
  """
  im_width, im_height = im.size
  if height and not width:
    # Resize the image using height only.  Calc the new width.
    width = int((height / im_height) * im_width)
  elif width and not height:
    # Resize the image using width only. Calc height
    height = int((width / im_width) * im_height)
  if width and height:
    im = im.resize((width, height), Image.ANTIALIAS)
  return im


def _crop_image(im, new_width, new_height):
  """crop an image to width and height, using the center as the focus.
  """
  width, height = im.size
  new_width = min(width, new_width)
  new_height = min(height, new_height)
  left = (width - new_width) // 2
  top = (height - new_height) // 2
  right = (width + new_width) // 2
  bottom = (height + new_height) // 2
  return im.crop((left, top, right, bottom))


def _upright_image(im):
  """If the given image has exif data telling us how to upright it,
     upright the image in-place.
  """
  if im.format == 'JPEG':
    # ignore bad EXIF data
    raw_exif = None
    try:
      raw_exif = im._getexif()
    except:
      # on ANY error in getting exif data
      raw_exif = None
    if raw_exif:
      exif = {ExifTags.TAGS.get(k, 'UNKNOWN'): v for k, v in raw_exif.items()}
      # see: http://sylvana.net/jpegcrop/exif_orientation.html
      # 1 means it's correct, 5 and 7 involve transpose/transverse operations
      # that PIL can't fix easily
      orientation = exif.get("Orientation", 1)
      # PIL Loses the image format after transpose, so save it and put it back
      fmt = im.format
      if orientation == 2:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
      elif orientation == 3:
        im = im.transpose(Image.ROTATE_180)
      elif orientation == 4:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
      elif orientation == 6:
        im = im.transpose(Image.ROTATE_270)
      elif orientation == 8:
        im = im.transpose(Image.ROTATE_90)
      im.format = fmt
  return im


def _apply_transparency_mask(im, transparency_mask_file):
  """apply the alpha channel from the mask file to the image.
     IF THEY ARENT EXACTLY THE SAME SIZE THE MASK FILE GETS
     RESIZED, IGNORING ASPECT RATIO AND SCALE!!!
  """
  f_name = os.path.join(os.path.dirname(__file__), 'masks',
      transparency_mask_file)
  if not os.path.exists(f_name):
    return im
  im.convert("RGBA")
  im_mask = Image.open(f_name).resize(im.size, Image.ANTIALIAS)
  alpha = im_mask.split()[-1] # (r, g, b, a)
  im.putalpha(alpha)
  return im
