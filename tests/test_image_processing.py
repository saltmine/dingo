import os
import sys

from nose.tools import eq_
import yaml

from dingo import image_processing

class TestImageProcessing(object):
  """Test the image processing module.
  """

  test_images_dir = 'test_images'
  # all transforms in our test config
  transforms = []
  # will hold all expected checksums
  expected_results = {}
  # if there's not expected result listed, save them here.
  no_expected = {}

  @classmethod
  def setUpClass(cls):
    #load all the transforms from test_transforms.yaml
    tc = {}
    with open(os.path.join('tests', 'test_transforms.yaml'), 'r') as y:
      tc = yaml.load(y)
    # for each transform in the config, generate an ImageSizeDefinition
    for name, t in tc.items():
      cls.transforms.append(
        image_processing.ImageTransform(name,
          t['width'], t['height'], t['fit_type'], t.get('min_height'),
          t.get('max_height'), t.get('transparency_mask_file')))
    # just for convinience.
    cls.orig_dir = os.path.join('tests', cls.test_images_dir, 'orig')
    cls.originals = os.listdir(cls.orig_dir)

    #set up the expected checksums
    with open(os.path.join('tests', 'expected_results.yaml'), 'r') as y:
      cls.expected_results = yaml.load(y)
      if not cls.expected_results:
        cls.expected_results = {}


  @classmethod
  def tearDownClass(cls):
    """check if there were missing results, write them to the
       generated_results.yaml file
    """
    if cls.no_expected:
      with open('tests/generated_results.yaml', 'w') as f:
        f.write('# make sure that the images in tests/test_images/generated '
            'are as expected before copying these values to '
            'tests/expected_results.yaml\n')
        for k, v in cls.no_expected.items():
          f.write("%s: %s\n" % (k, v))


  def test_transforms(self):
    # cool stuff; it's a test generator!  For each transform, yield a
    # test for it for each image.
    for t in self.transforms:
      for i in self.originals:
        yield self._test_transform, t, i


  def _test_transform(self, trans, img):
    # build the transform definition
    # process the file we're on using the transform specified, and save
    # the data in a string.
    out_file_data = ""
    with open(os.path.join(self.orig_dir, img), 'rb') as in_file:
      out_file_data = image_processing.process_image(in_file, trans)[0].read()
    # store the image, creating generated dir if needed.
    generated_dir = os.path.join('tests', self.test_images_dir, 'generated',
      trans.name)
    if not os.path.exists(generated_dir):
      os.makedirs(generated_dir)
    with open(os.path.join(generated_dir, img), 'wb') as out_file:
      out_file.write(out_file_data)
    # make sure that the expected is the same as the generated.
    hashed_out = hash(out_file_data)
    expected_hash = self.expected_results.get("%s_%s" % (trans.name, img))
    if not expected_hash:
      # couldn't find it!
      self.no_expected["%s_%s" % (trans.name, img)] = hashed_out
      raise AssertionError("%s_%s not in expected results yaml" % (trans, img))
    eq_(hashed_out, expected_hash)
