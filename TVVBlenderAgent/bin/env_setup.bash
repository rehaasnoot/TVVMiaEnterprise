#!/bin/bash

rm -rf venv
virtualenv -p /usr/bin/python venv/
source venv/bin/activate

pip install -r requirements.txt

### Running
python blagent_injector.py