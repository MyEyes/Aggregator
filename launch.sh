#!/bin/sh
source ./credential_export
export FLASK_APP=aggregator.py
export FLASK_HOST=0.0.0.0
export FLASK_DEBUG=True
flask run -h 0.0.0.0
