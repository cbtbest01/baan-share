#!/usr/bin/env bash
export PATH=$HOME/.local/bin:$PATH
python -m gunicorn app:app