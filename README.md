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

## Usage



## Install

1) clone and create & activate  conda environment
2) install pretorched-x:
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




