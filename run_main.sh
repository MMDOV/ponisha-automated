#! /usr/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $SCRIPTPATH/venv/bin/activate
pip install -r $SCRIPTPATH/requirements.txt
python $SCRIPTPATH/main.py
