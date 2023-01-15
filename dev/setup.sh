#!/usr/bin/env bash

set -e
python3 -m venv env  # create virtual environment
source env/bin/activate  # activate virtual environment
python3 -m pip install -r requirements.txt  # install dependencies
mkdir work  # create new directory
mv .git* * work  # move all files to work directory
