#!/bin/sh
source ./credential_export
export FLASK_APP=aggregator.py
export FLASK_DEBUG=True
flask shell
