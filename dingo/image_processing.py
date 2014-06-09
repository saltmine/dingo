"""This contains all the functionality for image manipulation.
"""

import logging
import sys
import cStringIO as StringIO

from PIL import Image, ExifTags

from exceptions import ImageException

def process_image(image_file, image_size_def):
  """given a file-like object and an image size definition, resize the image
     and return a new file-like object as well as the encoding.
  """
  # go to the start of the image file if we're not there already
  image_file.seek(0)
  # load the file into a PIL image object
  try:
    im = Image.open(image_file)
  except IOError:
    t, v, tb = sys.exc_info()
    raise ImageException, \
          ImageException("File doesn't contain a known image format."), \
          tb
  im = _upright_image(im)
  orig_width = im.size[0]
  orig_height = im.size[1]
  orig_format = im.format
  if im.mode == "P":
    im.convert("RGB")
  orig_aspect = orig_width/float(orig_height)
  # going to build a switch statement here, so shorten our 'case' variable
  t = image_size_def.fit_type
  if t == "fitwidth":
    # we make the width to whatever's specified and the height ends between
    # min_height and max_height, if specified.
    # First, let's calculate what the height would be if we did the transform.
    scale = image_size_def.width / float(orig_width)
    potential_height = scale * orig_height
    if potential_height < image_size_def.min_height:
      # scale height to min_height, then crop the sides to width.
      im = _resize_image(im, None, image_size_def.min_height)
      im = _crop_image(im, image_size_def.width, image_size_def.min_height)
    elif potential_height > image_size_def.max_height:
      # scale the image to the right width, then crop the top and bottom.
      im = _resize_image(im, image_size_def.width, None)
      im = _crop_image(im, image_size_def.width, image_size_def.max_height)
    else:
      # piece of cake, we're not in trouble in terms of cropping
      im = _resize_image(im, image_size_def.width, None)

  elif t in ("crop", "zoomcrop"):
    # scale, then crop the excess.
    # first apply the correct scale.
    if orig_aspect > image_size_def.width/float(image_size_def.height):
      # it's too wide for the new aspect ratio, fit height then crop.
      im = _resize_image(im, None, image_size_def.height)
    else:
      # it's too tall (or exactly right), so we fit width then crop.
      im = _resize_image(im, image_size_def.width, None)
    #crop it!
    im = _crop_image(im, image_size_def.width, image_size_def.height)

  elif t == "limitwidth":
    # width can be between 0 and the width specified, height scaled.
    if orig_width > image_size_def.width:
      im = _resize_image(im, image_size_def.width, None)
  else:
    raise ValueError("transform type %s not handled." % t)
  #TODO: deal with transparency masks.
  # now shove it in a stringio buffer and return it.
  content = StringIO.StringIO()
  # write it as a jpg, or if we added transparency, as a png.
  fmt = orig_format
  if image_size_def.transparency_mask_file:
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
    width = int((height/float(im_height)) * im_width)
  elif width and not height:
    # Resize the image using width only. Calc height
    height = int((width/float(im_width)) * im_height)
  if width and height:
    im = im.resize((width, height), Image.ANTIALIAS)
  return im


def _crop_image(im, new_width, new_height):
  """crop an image to width and height, using the center as the focus.
  """
  width, height = im.size
  new_width = min(width, new_width)
  new_height = min(height, new_height)
  left = (width - new_width)/2
  top = (height - new_height)/2
  right = (width + new_width)/2
  bottom = (height + new_height)/2
  return im.crop((left, top, right, bottom))


def _upright_image(im):
  """If the given image has exif data telling us how to upright it,
     upright the image in-place.
  """
  if im.format == 'JPEG':
    #ignore bad EXIF data
    raw_exif = None
    try:
      raw_exif = im._getexif()
    except:
      #on ANY error in getting exif data
      raw_exif = None
    if raw_exif:
      exif = {ExifTags.TAGS.get(k, 'UNKNOWN'): v for k, v in raw_exif.items()}
      # see: http://sylvana.net/jpegcrop/exif_orientation.html
      # 1 means it's correct, 5 and 7 involve transpose/transverse operations
      # that PIL can't fix easily
      orientation = exif.get("Orientation", 1)
      # PIL Loses the image format after a transpose, so save it and put it back
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
  pass


