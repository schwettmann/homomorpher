# Homomorpher <br><sub>Used to create the [Latent Compass](https:latentcompass.com)</sub>
[**Paper**](https://arxiv.org/abs/2012.14283)  |
[**Website**](http://latentcompass.com/#/) |
[**Video**](https://youtu.be/50fzBwa9Z1I)<br>

This repo contains code for the Latent Compass server (if you're interested in the client, please get in touch).

_Latent Compass: Creation by Navigation_ <br>
[Sarah Schwettmann](https://cogconfluence.com) *, [Hendrik Strobelt](http://hendrik.strobelt.com/) *, [Mauro Martino](https://www.mamartino.com/) <br>
MIT CSAIL, MIT BCS, MIT-IBM Watson AI Lab, IBM Research <br>
In [NeurIPS Workshop for Creativity and Design, 2020](https://neurips2020creativity.github.io/)


![overview](https://github.com/HendrikStrobelt/homomorpher/blob/master/z_L1_schematic_updated.png?raw=true)

## Install

1) To run the code yourself, start by cloning the repository:
```bash
git clone https://github.com/HendrikStrobelt/homomorpher
```
You will probably want to create a conda environment or virtual environment instead of installing the dependencies globally. E.g., to create a new virtual environment you can run:
```bash
python3 -m venv env
source env/bin/activate
```
2) This code loads a pretrained BigGAN. For this model you will need to install pretorched-x:
```bash
cd ..
git clone https://github.com/alexandonian/pretorched-x.git
cd pretorched-x
git checkout dev
python setup.py install
```
3)  install deps
4) install fastapi: `pip install fastapi[all] && pip install aiofiles`
4) run server: `uvicorn server:app --reload`

## Server setup:
```
 OPENAPI_PREFIX=/frankenstein uvicorn server:app --port 5005 --reload
 ```

## Usage: 

Our method works by training a linear model on noise vectors in the latent space of BigGAN, or activations of intermediate layers, that are associated with images. The images are sorted into two classes by a user. The beauty of this method is that you only need a few examples! We can then learn a direction that transforms any new image from one class into the other, by steering through latent space or activation space using that learned direction. Code for implementing this method is in the `homomorpher` module in `backend`.

You can try generating images from BigGAN and capturing perceptual dimensions you find salient by sorting the images (minimum 10!) into two classes (with labels `1` and `0`). To train a model and learn a direction corresponding to the distinction between the two classes, first decide whether you are going to work in Z-space or in the space of intermediate layer activations (layers closer to the image output control increasingly fine-grained image features). `homomorpher.train_model(z, z_lbl)` learns a model in Z-space and `homomorpher.train_model_layer(z, z_lbl, l)` learns a model in featurespace in layer `l`. The `homomorpher` module also contains code for using learned models to transform images.

The [Latent Compass](https://latentcompass.com) makes navigating the model's concept space easy with an interface for sorting generated images, learning directions, and using those directions to steer through visual space. 

Example "fullness" direction found using the Latent Compass, applied to images across classes: 

![overview](https://github.com/HendrikStrobelt/homomorpher/blob/master/example_latentcompass.png?raw=true)


## Citation

If you use this code for your research, please cite [our paper](https://arxiv.org/abs/2012.14283) : 

```bibtex
@misc{schwettmann2020latent,
      title={Latent Compass: Creation by Navigation}, 
      author={Sarah Schwettmann and Hendrik Strobelt and Mauro Martino},
      year={2020},
      eprint={2012.14283},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```




