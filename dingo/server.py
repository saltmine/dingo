from flask import Flask, make_response
import cStringIO
import mimetypes

from image_processing import process_image
from files import get_file
from config import transforms

app = Flask(__name__)

@app.route('/<transform_name>/<path:img_name>')
def transform_image(transform_name, img_name):
  transform = transforms.get(transform_name)
  if transform:
    img_content = get_file(img_name)
    resp_content = ""
    if img_content:
      f = cStringIO.StringIO(img_content)
      outf, encoding = process_image(f, transform)
      content_type = mimetypes.guess_type("a.%s" % encoding)
      return make_response((outf.read(), 200, {'Content-Type': content_type}))
  return "404", 404

