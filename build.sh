#!/bin/bash
pip3 install -r requirements.txt &&
mypy . &&
flake8 . &&
pytest tests &&
printf "\n\n ---Build successfully completed--- \n\n"