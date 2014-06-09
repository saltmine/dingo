import sys

class ImageSizeDefinition(object):
  """Just a container class for organizing an image transform.
     Pretty bare-bones, but slightly more reliable than a dict.
  """
  def __init__(self, name, width, height, fit_type, min_height=None,
      max_height=None, transparency_mask_file=None):
    self.name = name
    self.width = width
    self.height = height
    self.apsect = sys.maxint
    if height > 0:
      self.aspect = width/float(height)
    self.fit_type = fit_type
    self.min_height = min_height
    self.max_height = max_height
    self.transparency_mask_file = transparency_mask_file
