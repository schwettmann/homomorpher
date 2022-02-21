# Homomorpher <br><sub>Used to create the [Latent Compass](https:latentcompass.com)</sub>
[**Paper**](https://arxiv.org/abs/2012.14283)  |
[**Website**](http://latentcompass.com/#/) |
[**Video**](https://youtu.be/50fzBwa9Z1I)<br>

_Latent Compass: Creation by Navigation_ <br>
[Sarah Schwettmann](https://cogconfluence.com) *, [Hendrik Strobelt](http://hendrik.strobelt.com/) *, [Mauro Martino](https://www.mamartino.com/) <br>
MIT CSAIL, MIT BCS, MIT-IBM Watson AI Lab, IBM Research <br>
In [NeurIPS Workshop for Creativity and Design, 2020](https://neurips2020creativity.github.io/)


![overview](https://github.com/HendrikStrobelt/homomorpher/blob/master/z_L1_schematic_updated.png?raw=true)

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


## server:
```
 OPENAPI_PREFIX=/frankenstein uvicorn server:app --port 5005 --reload
 ```




