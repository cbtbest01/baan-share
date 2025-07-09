#!/usr/bin/env bash

# สร้างและใช้งาน virtualenv
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# รันแอป
python -m gunicorn app:app