from backend import homomorpher
import torchvision.transforms as transform
from torchvision.utils import make_grid


if __name__ == '__main__':

    z = homomorpher.generate_random_z()
    image = homomorpher.generate_img(z, 205)
    im = transform.ToPILImage()(make_grid(image,
                                          nrow=8,
                                          normalize=True,
                                          padding=5).cpu())
    print(type(im))
    im.save('gen.png')
    # image.save('gen.png')
    _gaa, trans = homomorpher.transform_img(z, 205, 'SVM_summerlakes')
    tr = transform.ToPILImage()(make_grid(trans,
                                          nrow=8,
                                          normalize=True,
                                          padding=5).cpu())
    tr.save('transform.png')
