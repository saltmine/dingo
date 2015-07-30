from __future__ import absolute_import
import logging
import os

import yaml
from lipstick.utils import apath

from .lib import ImageTransform


log = logging.getLogger(__name__)


ROOT_DIR = os.path.dirname(__file__)
_ETC_DIR = apath(ROOT_DIR, 'etc')


log.info('Root directory: "%s"', ROOT_DIR)


settings = {}
settings['url_prefix'] = ''


transforms = {}
with open(apath(_ETC_DIR, 'transforms.yaml')) as y:
  for name, transform in yaml.load(y).iteritems():
    try:
      transforms[name] = ImageTransform(name, **transform)
      log.debug('Loaded transform "%s"', name)
    except TypeError:
      raise TypeError('Invalid transformation definition: "%s"' % name)
