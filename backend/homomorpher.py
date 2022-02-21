

import functools
import torch
# from pretorched import gans
from pretorched.gans import BigGAN, utils
# from pretorched import visualizers as vutils
# import torchvision.transforms as transforms
import backend.path_fixes as pf
import os
import uuid
from datetime import datetime
import yaml
import torch.nn as nn
import backend.nethook as nethook

print(torch.cuda.is_available())
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

res = 256
batch_size = 30
pretrained = 'places365'
n_classes = {'places365': 365, 'imagenet': 1000}.get(pretrained)
class_idx = 205  # lake with trees
G = None
g = None
batch_size = 1


def get_gs():
    global G, g
    if G is None:
        G = BigGAN(resolution=res, pretrained=pretrained,
                   load_ema=True).to(device)
        g = functools.partial(G, embed=True)


def generate_random_z():
    """
    generate random z vector
    :return: z
    """
    get_gs()
    z, _ = utils.prepare_z_y(batch_size, G.dim_z, n_classes, device=device,
                             z_var=0.5)
    # generate random z, do this multiple times to find z you like
    return z


def generate_img(z, class_idx):
    """
    for some z and some class (in Places365), generates image
    :param z: seed vector
    :param class_idx: class ID
    :return: generated image
    """

    if isinstance(z, list):
        z = torch.tensor(z).to(device)

    get_gs()

    y = class_idx * torch.ones(batch_size, device=device).long()
    with torch.no_grad():
        G_z = utils.elastic_gan(g, z, y)
        # Allows for batches larger than what fits in memory.
    # vutils.visualize_samples(G_z)  # Visualizes the image

    return G_z


def train_model(z, z_lbl):
    """
    for some z and some user labels on those z, trains SVM
    :param z: seed vector
    :param z_lbl: user-labels
    :return: trained model
    """
    X = z.to(device)
    y = z_lbl.to(device)  # should be size(z), binary
    num_features = 119  # may need to be changed based on image resolution
    n_iterations = 50000
    model = nn.Linear(num_features, 1).cuda()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)

    for i in range(n_iterations):
        optimizer.zero_grad()
        output = model(X).flatten()
        loss = torch.mean(torch.clamp(1 - output * (2*y-1), min=0))  # SVM loss
        loss.backward()
        optimizer.step()

    return model


def train_and_safe_model(X, y, l=0, descr=None, m_id=None):
    """
    train model (see doc)
    - adds description (descr) as meta-info
    - if id given - saves under given id (can be used for updating)
    """
    if l == 0:
        model = train_model(X, y)
    else:
        # TODO: Only L1 implemented yet
        model = train_model_layer(X, y, 1)

    if m_id is None:
        m_id = str(uuid.uuid1())
    if descr is None:
        descr = m_id

    meta_info = {
        "id": "OWN_L" + str(l) +"_" + m_id,
        # "file": "OWN_" + m_id,
        "descr": descr,
        "type": "OWN",
        "layer": l,
        "utc_created": str(datetime.utcnow())
    }

    path_yaml = os.path.join(pf.MODEL_DATA_ROOT, meta_info["id"]+'.yaml')
    path_model = os.path.join(pf.MODEL_DATA_ROOT,  meta_info["id"])

    with open(path_yaml, 'w') as f_yaml:
        yaml.dump(meta_info, f_yaml)
    torch.save(model, path_model)

    return meta_info


def train_model_layer(z, z_lbl, l):
    """
    for some z and some user labels on those z, trains SVM on activations in layer l
    :param z: seed vector
    :param z_lbl: user-labels
    :param l: layer to train on
    :return: trained model
    """
    get_gs()
    y = z_lbl.long().to(device)

    print(type(z), type(z_lbl))

    # .to(device)  # should be size(z), binary
    z = z.to(device)

    # # grab activations. l+1 because of BigGAN's layer numbering.
    activations = G.forward(z, y, embed=True, layer=l+1)
    activations_reshaped = activations.view(activations.size(0), -1)
    X = activations_reshaped.detach()

    num_features = 262144  # for L1. based on activations.size()
    n_iterations = 50000  # toggle this

    model = nn.Linear(num_features, 1).cuda()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)

    for i in range(n_iterations):
        optimizer.zero_grad()
        output = model(X).flatten()
        loss = torch.mean(torch.clamp(1 - output * (2*y-1), min=0))  # SVM loss
        loss.backward()
        optimizer.step()

    return model


def transform_img(z, class_idx, svm_lbl, num_steps=500, direction=-1, onlyTransform=False):
    """
    from z + orig category, name of SVM to use; return original image
    and transformed image
    :param z: random vector
    :param class_idx: category in places 365
    :param num_steps: (how much to transform)
    :param direction: toward or away from target class (1 or -1)
    :param svm_lbl:  'SVM_summerlakes' or 'SVM_lakereeflection'
    :return: original image and transformed image
    """

    if isinstance(z, list):
        z = torch.tensor(z).to(device)

    get_gs()
    y = class_idx * torch.ones(batch_size, device=device).long()

    # Don't produce original image if not needed
    if onlyTransform:
        G_z = ''
    else:
        with torch.no_grad():
            G_z = utils.elastic_gan(g, z, y)
            # Allows for batches larger than what fits in memory.
    current_z = torch.nn.Parameter(z,
                                   requires_grad=True)
    # makes space to hold gradients - z is the kind of thing we can optimize
    # parameters = [current_z]
    # yes we are still shifting z, this time based on the SVM value.
    # num_steps = 500  # sure
    optimizer = torch.optim.Adam([current_z])
    loss_vec = []

    def elastic_gan_with_grad(model, *input):
        error_msg = 'CUDA out of memory.'

        def chunked_forward(f, *x, chunk_size=1):
            out = []
            for xcs in zip(*[xc.chunk(chunk_size) for xc in x]):
                o = f(*xcs)
                out.append(o)
            return torch.cat(out)

        cs, fit = 1, False
        while not fit:
            try:
                return chunked_forward(model, *input, chunk_size=cs)
            except RuntimeError as e:
                if error_msg in str(e):
                    torch.cuda.empty_cache()
                    cs *= 2
                else:
                    raise e

    path = os.path.join(pf.MODEL_DATA_ROOT, svm_lbl)
    model = torch.load(path)
    model.eval()

    with torch.enable_grad():
        for step_num in (range(num_steps + 1)):
            optimizer.zero_grad()
            # outputs = model(current_z)
            loss = direction*model(current_z)
            # flip this sign to change direction across
            # the decision boundary
            loss_vec.append(loss)
            loss.backward()
            optimizer.step()

    G_z2 = utils.elastic_gan(g, current_z, y)  # generate transformed image
    # vutils.visualize_samples(G_z)
    # vutils.visualize_samples(G_z2)
    return G_z, G_z2


def transform_img_layer1(z, class_idx, svm_lbl, num_steps=500, direction=-1, onlyTransform=False):
    """
    from z + orig category, name of SVM to use; return original image
    and transformed image
    :param z: random vector
    :param class_idx: category in places 365
    :param num_steps: (how much to transform)
    :param direction: toward or away from target class (1 or -1)
    :param svm_lbl:  'SVM_summerlakes' or 'SVM_lakereeflection'
    :return: original image and transformed image
    """

    # return None

    if isinstance(z, list):
        z = torch.tensor(z).to(device)

    get_gs()
    y = class_idx * torch.ones(batch_size, device=device).long()
    # G = BigGAN(resolution=res, pretrained=pretrained, load_ema=True).to(device)
    # g = functools.partial(G, embed=True)
    #
    # Don't produce original image if not needed
    if onlyTransform:
        G_z = ''
    else:
        with torch.no_grad():
            G_z = utils.elastic_gan(g, z, y)
    #     # Allows for batches larger than what fits in memory. #run generator on current z
    #
    # indexed as 2 because of BigGAN labeling (actually L1)
    old_activations = G.forward(z, y, embed=True, layer=2)
    old_activations_reshaped = old_activations.view(
        old_activations.size(0), -1)
    G_editable = nethook.InstrumentedModel(G).cuda()
    current_activations = torch.nn.Parameter(
        old_activations_reshaped, requires_grad=True)
    #
    optimizer = torch.optim.Adam([current_activations])
    loss_fn = torch.nn.CrossEntropyLoss(
        weight=None, size_average=None, ignore_index=-100, reduce=None, reduction='mean')
    loss_vec = []
    #

    def optim_G(x, *args):  # edit layer function
        x[:] = new_activations
        print('The image was edited!')
        return x
    #
    path = os.path.join(pf.MODEL_DATA_ROOT, svm_lbl)  # make sure this was an SVM trained on L1
    model = torch.load(path)
    model.eval()
    #
    with torch.enable_grad():
        for step_num in (range(num_steps + 1)):
            optimizer.zero_grad()
            outputs = model(current_activations)
            loss = direction*model(current_activations)
            loss_vec.append(loss)
            loss.backward()
            optimizer.step()

    new_activations = current_activations.view(1, 1024, 16, 16)
    # now edit the generator using the new activations
    G_editable.edit_layer('blocks.1.0', rule=optim_G)

    # Allows for batches larger than what fits in memory.
    G_z2 = utils.elastic_gan(g, z, y)
    
    # reset 
    G_editable.remove_edits()

    return G_z, G_z2  # original and modified image(s)
