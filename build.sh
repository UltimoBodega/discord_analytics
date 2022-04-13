#!/bin/bash
set -e
export PYTHONPATH=$PWD/src
export MYPYPATH=$PYTHONPATH
#pip3 install --upgrade pip wheel
pip3 install -r requirements.txt
mypy src tests
flake8 src tests
pytest tests
printf "\n\n ---Build successfully completed--- \n\n"