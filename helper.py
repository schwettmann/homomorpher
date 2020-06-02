from PIL import Image
from io import BytesIO
import base64
import re
import numpy


def np2base64(imgarray, for_html=True, image_format='jpeg'):
    '''
    Converts a numpy array to a jpeg base64 url
    '''

    return pil2base64(Image.fromarray(imgarray), for_html, image_format)


def pil2base64(img: Image, for_html=True, image_format="jpeg"):
    input_image_buff = BytesIO()
    img.save(input_image_buff, image_format,
             quality=99, optimize=True, progressive=True)
    res = base64.b64encode(input_image_buff.getvalue()).decode('ascii')
    if for_html:
        return 'data:image/' + image_format + ';base64,' + res
    else:
        return res


def base642np(stringdata):
    stringdata = re.sub('^(?:data:)?image/\\w+;base64,', '', stringdata)
    im = Image.open(BytesIO(base64.b64decode(stringdata)))
    return numpy.array(im)
