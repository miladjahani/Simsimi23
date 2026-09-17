#!/bin/sh
exec gunicorn main:app --bind 0.0.0.0:${PORT:-2095} --workers 2 --timeout 120
