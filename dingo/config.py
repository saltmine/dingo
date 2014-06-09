import os

import yaml

from dingo.image_size_definition import ImageSizeDefinition

_etc_dir = os.path.join(os.path.dirname(__file__), 'etc')

settings = {}
settings['url_prefix'] = ''

transforms = {}
with open(os.path.join(_etc_dir, 'transforms.yaml'), 'r') as y:
  tc = yaml.load(y)
  for name, t in tc.items():
    transforms[name] = ImageSizeDefinition(name, t['width'], t['height'],
        t['fit_type'], t.get('min_height'), t.get('max_height'),
        t.get('transparency_mask_file'))

