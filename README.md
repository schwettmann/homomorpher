# homomorpher


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




