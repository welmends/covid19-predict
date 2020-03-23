#!/bin/bash

virtualenv .env -p python3 --no-site-packages
. .env/bin/activate
pip install -r requirements.txt
#deactivate
