from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
from backend import homomorpher
import torchvision.transforms as transform
from torchvision.utils import make_grid
from helper import pil2base64


class ImageRequest(BaseModel):
    category: int
    zs: List[List[float]]


class TransformRequest(BaseModel):
    category: int
    zs: List[List[float]]
    transformID: str


prefix = os.getenv('OPENAPI_PREFIX', '/')
app = FastAPI(openapi_prefix=prefix)
search_projects = True

app.mount("/static", StaticFiles(directory="client/dist"), name="static")


# TODO: Be more restrictive !!
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


places_categories = []
with open('categories_places365.txt', 'r') as cat:
    for line in cat.readlines():
        places_categories.append(line.rstrip().split(' '))


@app.get('/all_transitions')
def read_root():
    global search_projects
    projects = [
        {"id": 'SVM_closet_emptyfull',
         'descr': 'closet: empty to full', "type": 'original'},
        {"id": 'SVM_lakereeflection',
         'descr': 'lake reflection', "type": 'original'},
        {"id": 'SVM_summerlakes',
         'descr': 'lakes to summer lakes', "type": 'original'}
    ]
    if search_projects:
        pass  # TODO: !!!

    return projects


@ app.get('/random_z')
def random_z(seed: int = 100):
    rz = homomorpher.generate_random_z()
    return rz.tolist()


@app.get('/random_images')
def random_images(count: int, category: int):
    res = []
    for i in range(count):
        rz = homomorpher.generate_random_z()
        image_np = homomorpher.generate_img(rz, category)
        im = convert_im_np(image_np)
        res.append({
            "z": rz.tolist(),
            "image": im
        })
    return res


@ app.get('/categories')
def get_cats():
    return places_categories


def convert_im_np(image_np):
    '''
    Convert NP image to base64
    '''
    im = transform.ToPILImage()(make_grid(image_np,
                                          nrow=8,
                                          normalize=True,
                                          padding=5).cpu())
    return pil2base64(im)


@ app.post('/images')
def post_images(re: ImageRequest):
    '''
    Generate image
    '''
    image_np = homomorpher.generate_img(re.zs, re.category)
    im = convert_im_np(image_np)

    return {"request": re, "res": im}


@ app.post('/transform')
def post_transform(re: TransformRequest):
    image_in, image_out = homomorpher.transform_img(
        re.zs, re.category, re.transformID)
    im_in = convert_im_np(image_in)
    im_out = convert_im_np(image_out)

    return {"request": re, "res": {"in": im_in, "out": im_out}}
