#! /usr/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $SCRIPTPATH/venv/bin/activate
python $SCRIPTPATH/main.py
