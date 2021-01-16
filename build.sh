#!/bin/bash
export PYTHONPATH=$PWD/src &&
export MYPYPATH=$PYTHONPATH &&
pip3 install -r requirements.txt &&
mypy src && mypy tests &&
flake8 src && flake8 tests &&
pytest tests &&
printf "\n\n ---Build successfully completed--- \n\n"